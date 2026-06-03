from __future__ import annotations

import time
import uuid
from typing import List

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.config import AppConfig
from app.controller import MasterController
from app.models import (
    UploadResponse,
    StatusResponse,
    ResultItem,
    ResultsResponse,
    StartRequest,
    BenchmarkResponse,
    BenchmarkRow,
)
from app.state import AppState
from benchmark.benchmarker import run_suite


app = FastAPI(title="Parallel Vision")
state = AppState()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/upload", response_model=UploadResponse)
async def upload_images(files: List[UploadFile] = File(...)) -> UploadResponse:
    if not files:
        raise HTTPException(status_code=400, detail="No files uploaded")

    image_ids = []
    with state.lock:
        state.uploaded_images.clear()
        state.filenames.clear()
        state.results.clear()
        state.job.status = "idle"
        for file in files:
            image_id = str(uuid.uuid4())
            image_bytes = await file.read()
            state.uploaded_images[image_id] = image_bytes
            state.filenames[image_id] = file.filename or image_id
            image_ids.append(image_id)

    return UploadResponse(image_ids=image_ids, total_images=len(image_ids))


@app.post("/start", response_model=StatusResponse)
async def start_processing(payload: StartRequest) -> StatusResponse:
    if not state.uploaded_images:
        raise HTTPException(status_code=400, detail="No images uploaded")

    with state.lock:
        if state.controller and state.job.status == "running":
            return _status_response()

        base_config = AppConfig.from_env()
        config = AppConfig(
            processes=payload.processes or base_config.processes,
            threads=payload.threads or base_config.threads,
            cpu_tokens=base_config.cpu_tokens,
            gpu_tokens=base_config.gpu_tokens,
            waiting_room_capacity=base_config.waiting_room_capacity,
            resize_width=base_config.resize_width,
            resize_height=base_config.resize_height,
            histogram_bins=base_config.histogram_bins,
        )

        controller = MasterController(config, state.uploaded_images, state.filenames)
        controller.start_workers()
        controller.enqueue_images()
        controller.start_collector()
        state.controller = controller
        state.job.status = "running"
        state.job.started_at = time.time()

    return _status_response()


@app.get("/status", response_model=StatusResponse)
def status() -> StatusResponse:
    return _status_response()


@app.get("/results", response_model=ResultsResponse)
def results() -> ResultsResponse:
    with state.lock:
        if not state.controller:
            return ResultsResponse(
                results=_build_result_items_from_cache(),
            )

        stats = state.controller.snapshot()
        if int(stats["processed"]) >= len(state.uploaded_images):
            _finalize_job()

        return ResultsResponse(results=_build_result_items_from_cache())


def _build_result_items_from_cache() -> List[ResultItem]:
    items: List[ResultItem] = []
    result_source = state.controller.results if state.controller else state.results
    for image_id, result in result_source.items():
        if "error" in result:
            continue

        items.append(
            ResultItem(
                image_id=image_id,
                resize_shape=result["resize_shape"],
                gray_mean=result["gray_mean"],
                edges_nonzero=result["edges_nonzero"],
                histogram=result["histogram"],
                faces=result["faces"],
                faces_bboxes=result.get("faces_bboxes", []),
                images=result["images"],
                duration_ms=result["duration_ms"],
            )
        )
    return items


@app.get("/benchmark", response_model=BenchmarkResponse)
def benchmark(run: bool = False) -> BenchmarkResponse:
    with state.lock:
        if run:
            _run_benchmark_locked()

        rows = [
            BenchmarkRow(
                processes=item["processes"],
                threads=item["threads"],
                total_time_s=item["total_time_s"],
                avg_time_ms=item["avg_time_ms"],
                cpu_usage_pct=item["cpu_usage_pct"],
                speedup=item["speedup"],
                efficiency=item["efficiency"],
            )
            for item in state.last_benchmarks
        ]

        return BenchmarkResponse(rows=rows, csv_path="benchmark/results.csv")


def _status_response() -> StatusResponse:
    if not state.controller:
        return StatusResponse(
            state="idle",
            total_images=len(state.uploaded_images),
            processed_images=0,
            in_flight=0,
        )

    stats = state.controller.snapshot()
    processed = int(stats["processed"])
    total = int(stats["total"])

    if processed >= total and total > 0:
        _finalize_job()
        return StatusResponse(
            state="completed",
            total_images=total,
            processed_images=processed,
            in_flight=0,
        )

    return StatusResponse(
        state="running",
        total_images=total,
        processed_images=processed,
        in_flight=state.controller.barber_shop.in_flight(),
    )


def _finalize_job() -> None:
    if not state.controller:
        return

    state.results = state.controller.results
    state.controller.stop()
    state.job.status = "completed"
    state.job.finished_at = time.time()
    state.controller = None


def _run_benchmark_locked() -> None:
    if not state.uploaded_images:
        return

    if state.controller:
        raise HTTPException(status_code=409, detail="Job running")

    configs = [(1, 1), (1, 4), (2, 4), (4, 4), (8, 8)]
    base_config = AppConfig.from_env()
    results = run_suite(
        state.uploaded_images,
        state.filenames,
        base_config,
        configs,
        "benchmark/results.csv",
    )

    state.last_benchmarks = [
        {
            "processes": item.processes,
            "threads": item.threads,
            "total_time_s": item.total_time,
            "avg_time_ms": item.avg_time_per_image * 1000.0,
            "cpu_usage_pct": item.cpu_percent,
            "speedup": item.speedup,
            "efficiency": item.efficiency,
        }
        for item in results
    ]
