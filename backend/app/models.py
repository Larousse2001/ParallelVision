from typing import List, Dict, Optional

from pydantic import BaseModel


class UploadResponse(BaseModel):
    image_ids: List[str]
    total_images: int


class StartRequest(BaseModel):
    processes: Optional[int] = None
    threads: Optional[int] = None
    benchmark: bool = False


class StatusResponse(BaseModel):
    state: str
    total_images: int
    processed_images: int
    in_flight: int


class ResultItem(BaseModel):
    image_id: str
    resize_shape: List[int]
    gray_mean: float
    edges_nonzero: int
    histogram: List[int]
    faces: int
    faces_bboxes: List[List[int]] = []   # [[x, y, w, h], ...]
    images: Dict[str, str]               # gray | edges | faces_annotated
    duration_ms: float


class ResultsResponse(BaseModel):
    results: List[ResultItem]


class BenchmarkRow(BaseModel):
    processes: int
    threads: int
    total_time_s: float
    avg_time_ms: float
    cpu_usage_pct: float
    speedup: float
    efficiency: float


class BenchmarkResponse(BaseModel):
    rows: List[BenchmarkRow]
    csv_path: Optional[str]
