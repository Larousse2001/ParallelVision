import multiprocessing as mp
from multiprocessing.connection import Connection
import queue
import threading
import time
from typing import Any, Dict

from app.config import AppConfig
from app.processing import process_image
from synchronization.dining_philosophers import TokenPair
from synchronization.sleeping_barber import BarberShop


class WorkerProcess(mp.Process):
    def __init__(
        self,
        worker_id: int,
        config: AppConfig,
        barber_shop: BarberShop,
        result_queue: mp.Queue,
        tokens: TokenPair,
        control_conn: Connection,
    ) -> None:
        super().__init__(name=f"worker-{worker_id}")
        self.worker_id = worker_id
        self.config = config
        self.barber_shop = barber_shop
        self.result_queue = result_queue
        self.tokens = tokens
        self.control_conn = control_conn
        self.stop_event = mp.Event()

    def _thread_loop(self, local_queue: queue.Queue) -> None:
        while not self.stop_event.is_set():
            task = local_queue.get()
            if task is None:
                break

            while not self.tokens.acquire_pair():
                if self.stop_event.is_set():
                    return

            try:
                result = process_image(task["bytes"], self.config)
                payload: Dict[str, Any] = {
                    "image_id": task["image_id"],
                    "filename": task["filename"],
                    "result": result,
                }
                self.result_queue.put(payload)
            except Exception as exc:
                self.result_queue.put(
                    {
                        "image_id": task["image_id"],
                        "filename": task["filename"],
                        "error": str(exc),
                    }
                )
            finally:
                self.tokens.release_pair()
                local_queue.task_done()

    def _start_threads(self, local_queue: queue.Queue) -> list[threading.Thread]:
        threads: list[threading.Thread] = []
        for index in range(self.config.threads):
            thread = threading.Thread(
                target=self._thread_loop,
                args=(local_queue,),
                name=f"worker-{self.worker_id}-thread-{index}",
                daemon=True,
            )
            thread.start()
            threads.append(thread)
        return threads

    def run(self) -> None:
        print(f"{self.name} started", flush=True)
        local_queue: queue.Queue = queue.Queue()
        threads = self._start_threads(local_queue)

        while not self.stop_event.is_set():
            if self.control_conn.poll():
                command = self.control_conn.recv()
                if command == "STOP":
                    self.stop_event.set()
                    break

            task = self.barber_shop.get_task()
            if task is None:
                time.sleep(0.01)
                continue
            local_queue.put(task)

        for _ in threads:
            local_queue.put(None)
        for thread in threads:
            thread.join(timeout=1.0)
