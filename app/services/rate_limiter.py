import time
from collections import defaultdict, deque
from threading import Lock


class InMemoryRateLimiter:
    def __init__(self, max_requests: int, window_seconds: int):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: dict[str, deque[float]] = defaultdict(deque)
        self.lock = Lock()

    def allow(self, key: str) -> bool:
        now = time.time()
        cutoff = now - self.window_seconds

        with self.lock:
            history = self.requests[key]

            while history and history[0] < cutoff:
                history.popleft()

            if len(history) >= self.max_requests:
                return False

            history.append(now)
            return True
