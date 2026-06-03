import time
import multiprocessing


class TokenPair:
    def __init__(
        self,
        cpu_tokens: multiprocessing.Semaphore,
        gpu_tokens: multiprocessing.Semaphore,
    ) -> None:
        self._cpu = cpu_tokens
        self._gpu = gpu_tokens

    def acquire_pair(self, timeout: float = 0.2) -> bool:
        acquired_cpu = self._cpu.acquire(timeout=timeout)
        if not acquired_cpu:
            return False

        acquired_gpu = self._gpu.acquire(timeout=timeout)
        if not acquired_gpu:
            self._cpu.release()
            time.sleep(0.01)
            return False

        return True

    def release_pair(self) -> None:
        self._gpu.release()
        self._cpu.release()
