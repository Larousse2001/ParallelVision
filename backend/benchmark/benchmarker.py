from dataclasses import dataclass
from typing import Dict, List, Tuple
import csv
import time

from app.config import AppConfig
from app.controller import MasterController


@dataclass
class BenchmarkResult:
    processes: int
    threads: int
    total_time: float
    avg_time_per_image: float
    cpu_percent: float
    speedup: float
    efficiency: float


def compute_speedup(baseline_time: float, total_time: float) -> float:
    if total_time <= 0:
        return 0.0
    return baseline_time / total_time


def compute_efficiency(speedup: float, processes: int, threads: int) -> float:
    parallel_units = max(1, processes * threads)
    return speedup / float(parallel_units)


def write_csv(results: List[BenchmarkResult], path: str) -> None:
    with open(path, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(
            [
                "processes",
                "threads",
                "total_time",
                "avg_time_per_image",
                "cpu_percent",
                "speedup",
                "efficiency",
            ]
        )
        for item in results:
            writer.writerow(
                [
                    item.processes,
                    item.threads,
                    item.total_time,
                    item.avg_time_per_image,
                    item.cpu_percent,
                    item.speedup,
                    item.efficiency,
                ]
            )


def run_suite(
    images: Dict[str, bytes],
    filenames: Dict[str, str],
    base_config: AppConfig,
    configs: List[Tuple[int, int]],
    csv_path: str,
) -> List[BenchmarkResult]:
    results: List[BenchmarkResult] = []
    baseline_time = 0.0

    for processes, threads in configs:
        config = AppConfig(
            processes=processes,
            threads=threads,
            cpu_tokens=base_config.cpu_tokens,
            gpu_tokens=base_config.gpu_tokens,
            waiting_room_capacity=base_config.waiting_room_capacity,
            resize_width=base_config.resize_width,
            resize_height=base_config.resize_height,
            histogram_bins=base_config.histogram_bins,
        )

        controller = MasterController(config, images, filenames)
        controller.start_workers()
        start_time = time.perf_counter()
        controller.enqueue_images()
        controller.start_collector()

        while True:
            stats = controller.snapshot()
            if int(stats["processed"]) >= len(images):
                break
            time.sleep(0.1)

        total_time = time.perf_counter() - start_time
        snapshot = controller.snapshot()
        controller.stop()

        if not baseline_time:
            baseline_time = total_time

        avg_time = float(snapshot["avg_time"])
        cpu_percent = float(snapshot["cpu_percent"])
        speedup = compute_speedup(baseline_time, total_time)
        efficiency = compute_efficiency(speedup, processes, threads)

        results.append(
            BenchmarkResult(
                processes=processes,
                threads=threads,
                total_time=total_time,
                avg_time_per_image=avg_time,
                cpu_percent=cpu_percent,
                speedup=speedup,
                efficiency=efficiency,
            )
        )

    write_csv(results, csv_path)
    return results
