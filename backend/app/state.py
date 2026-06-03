from dataclasses import dataclass, field
import threading
from typing import Any, Dict, List, Optional

from app.controller import MasterController


@dataclass
class JobState:
    status: str = "idle"
    started_at: Optional[float] = None
    finished_at: Optional[float] = None
    message: str = ""


@dataclass
class AppState:
    lock: threading.Lock = field(default_factory=threading.Lock)
    uploaded_images: Dict[str, bytes] = field(default_factory=dict)
    filenames: Dict[str, str] = field(default_factory=dict)
    results: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    last_benchmarks: List[Dict[str, Any]] = field(default_factory=list)
    job: JobState = field(default_factory=JobState)
    controller: Optional[MasterController] = None
