from __future__ import annotations

from typing import Dict
import time

import numpy as np
from multiprocessing import shared_memory, Lock


STATS_FIELDS: Dict[str, int] = {
    "total": 0,
    "processed": 1,
    "total_time": 2,
    "avg_time": 3,
    "cpu_percent": 4,
    "last_update": 5,
}


class SharedStats:
    def __init__(self, shm: shared_memory.SharedMemory, lock: Lock):
        self._shm = shm
        self._lock = lock
        self._array = np.ndarray((len(STATS_FIELDS),), dtype=np.float64, buffer=shm.buf)

    @classmethod
    def create(cls, lock: Lock) -> SharedStats:
        size = len(STATS_FIELDS) * np.float64().nbytes
        shm = shared_memory.SharedMemory(create=True, size=size)
        stats = cls(shm, lock)
        with lock:
            stats._array[:] = 0.0
            stats._array[STATS_FIELDS["last_update"]] = time.time()
        return stats

    @classmethod
    def connect(cls, name: str, lock: Lock) -> SharedStats:
        shm = shared_memory.SharedMemory(name=name)
        return cls(shm, lock)

    @property
    def name(self) -> str:
        return self._shm.name

    def snapshot(self) -> Dict[str, float]:
        with self._lock:
            return {key: float(self._array[idx]) for key, idx in STATS_FIELDS.items()}

    def set_total(self, total: int) -> None:
        with self._lock:
            self._array[STATS_FIELDS["total"]] = float(total)
            self._array[STATS_FIELDS["last_update"]] = time.time()

    def update_processed(self, processing_time: float, cpu_percent: float) -> None:
        with self._lock:
            self._array[STATS_FIELDS["processed"]] += 1.0
            self._array[STATS_FIELDS["total_time"]] += float(processing_time)
            processed = self._array[STATS_FIELDS["processed"]]
            if processed > 0:
                self._array[STATS_FIELDS["avg_time"]] = (
                    self._array[STATS_FIELDS["total_time"]] / processed
                )
            self._array[STATS_FIELDS["cpu_percent"]] = float(cpu_percent)
            self._array[STATS_FIELDS["last_update"]] = time.time()

    def close(self) -> None:
        self._shm.close()

    def unlink(self) -> None:
        self._shm.unlink()
