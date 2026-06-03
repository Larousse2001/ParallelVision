import multiprocessing as mp
import threading
import time
from typing import Dict, List

import psutil

from app.config import AppConfig
from ipc.pipes import create_pipes
from ipc.shared_memory import SharedStats
from synchronization.dining_philosophers import TokenPair
from synchronization.sleeping_barber import BarberShop
from workers.worker import WorkerProcess


class MasterController:
    def __init__(self, config: AppConfig, images: Dict[str, bytes], filenames: Dict[str, str]) -> None:
        self.config = config
        self.images = images
        self.filenames = filenames
        self.ctx = mp.get_context("spawn")
        self.barber_shop = BarberShop(self.ctx, config.waiting_room_capacity)
        self.result_queue = self.ctx.Queue()
        self.tokens = TokenPair(
            self.ctx.Semaphore(config.cpu_tokens),
            self.ctx.Semaphore(config.gpu_tokens),
        )
        self.stats_lock = self.ctx.Lock()
        self.shared_stats = SharedStats.create(self.stats_lock)
        self.pipes = create_pipes(config.processes)
        self.processes: List[WorkerProcess] = []
        self.collector_thread: threading.Thread | None = None
        self.results: Dict[str, Dict[str, object]] = {}
        self.total_images = len(images)
        self._stop_event = threading.Event()

    def start_workers(self) -> None:
        for index, (_, child_conn) in enumerate(self.pipes):
            worker = WorkerProcess(
                worker_id=index,
                config=self.config,
                barber_shop=self.barber_shop,
                result_queue=self.result_queue,
                tokens=self.tokens,
                control_conn=child_conn,
            )
            worker.start()
            time.sleep(0.02)
            if not worker.is_alive():
                raise RuntimeError(
                    f"Worker {index} failed to start (exitcode={worker.exitcode})"
                )
            self.processes.append(worker)

    def enqueue_images(self) -> None:
        self.shared_stats.set_total(self.total_images)
        for image_id, image_bytes in self.images.items():
            task = {
                "image_id": image_id,
                "filename": self.filenames.get(image_id, image_id),
                "bytes": image_bytes,
            }
            while not self.barber_shop.add_task(task):
                time.sleep(0.01)

    def _collector_loop(self) -> None:
        processed = 0
        psutil.cpu_percent(interval=None)
        while not self._stop_event.is_set() and processed < self.total_images:
            try:
                payload = self.result_queue.get(timeout=0.2)
            except Exception:
                continue

            if payload is None:
                continue

            image_id = payload.get("image_id")
            if payload.get("error"):
                result = {"error": payload["error"]}
            else:
                result = payload["result"]

            self.results[image_id] = {
                "filename": payload.get("filename", image_id),
                **result,
            }

            processed += 1
            cpu_percent = psutil.cpu_percent(interval=None)
            duration_ms = float(result.get("duration_ms", 0.0))
            self.shared_stats.update_processed(duration_ms / 1000.0, cpu_percent)

        self._stop_event.set()

    def start_collector(self) -> None:
        self.collector_thread = threading.Thread(
            target=self._collector_loop, name="result-collector", daemon=True
        )
        self.collector_thread.start()

    def stop(self) -> None:
        self._stop_event.set()
        for parent_conn, _ in self.pipes:
            try:
                parent_conn.send("STOP")
            except Exception:
                pass
        self.barber_shop.wake_all(self.config.processes * max(1, self.config.threads))
        for process in self.processes:
            process.join(timeout=2.0)

        self.shared_stats.close()
        try:
            self.shared_stats.unlink()
        except FileNotFoundError:
            pass

    def snapshot(self) -> Dict[str, float]:
        return self.shared_stats.snapshot()
