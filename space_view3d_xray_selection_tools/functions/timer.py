import time


class Timer:
    ENABLED = False

    def __init__(self):
        if self.ENABLED:
            self.time_start = time.perf_counter()

    def add(self, label):
        if self.ENABLED:
            exec_time = time.perf_counter() - self.time_start
            print(f"{label}: {exec_time:.4f} sec")
            self.time_start = time.perf_counter()
