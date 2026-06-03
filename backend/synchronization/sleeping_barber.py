import multiprocessing
from typing import Any


class BarberShop:
    def __init__(self, ctx: multiprocessing.context.BaseContext, capacity: int) -> None:
        self.capacity = capacity
        self.queue = ctx.Queue()
        self.waiting_room = ctx.Semaphore(0)
        self.lock = ctx.Lock()
        self.count = ctx.Value("i", 0)

    def add_task(self, task: Any) -> bool:
        with self.lock:
            if self.count.value >= self.capacity:
                return False
            self.queue.put(task)
            self.count.value += 1
            self.waiting_room.release()
            return True

    def get_task(self) -> Any:
        self.waiting_room.acquire()
        task = self.queue.get()
        with self.lock:
            self.count.value = max(0, self.count.value - 1)
        return task

    def wake_all(self, count: int) -> None:
        for _ in range(count):
            self.waiting_room.release()

    def in_flight(self) -> int:
        with self.lock:
            return int(self.count.value)
