from dataclasses import dataclass
import os


@dataclass(frozen=True)
class AppConfig:
    processes: int = 8
    threads: int = 8
    cpu_tokens: int = 4
    gpu_tokens: int = 2
    waiting_room_capacity: int = 256
    resize_width: int = 256
    resize_height: int = 256
    histogram_bins: int = 16

    @staticmethod
    def from_env() -> "AppConfig":
        return AppConfig(
            processes=int(os.getenv("PP_PROCESSES", "8")),
            threads=int(os.getenv("PP_THREADS", "8")),
            cpu_tokens=int(os.getenv("PP_CPU_TOKENS", "4")),
            gpu_tokens=int(os.getenv("PP_GPU_TOKENS", "2")),
            waiting_room_capacity=int(os.getenv("PP_WAITING_ROOM", "256")),
            resize_width=int(os.getenv("PP_RESIZE_WIDTH", "256")),
            resize_height=int(os.getenv("PP_RESIZE_HEIGHT", "256")),
            histogram_bins=int(os.getenv("PP_HIST_BINS", "16")),
        )
