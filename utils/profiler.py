import time
from collections import defaultdict
from utils.logger import logger


class Profiler:
    """Tracks per-stage latency for pipeline performance monitoring."""

    def __init__(self):
        self._start_times: dict[str, float] = {}
        self._totals: dict[str, float] = defaultdict(float)
        self._counts: dict[str, int] = defaultdict(int)

    def start(self, stage: str) -> None:
        self._start_times[stage] = time.perf_counter()

    def end(self, stage: str) -> float:
        if stage not in self._start_times:
            return 0.0
        elapsed = time.perf_counter() - self._start_times.pop(stage)
        self._totals[stage] += elapsed
        self._counts[stage] += 1
        return elapsed

    def get_average(self, stage: str) -> float:
        count = self._counts.get(stage, 0)
        if count == 0:
            return 0.0
        return self._totals[stage] / count

    def log_summary(self) -> None:
        for stage in sorted(self._totals):
            avg_ms = self.get_average(stage) * 1000
            total_ms = self._totals[stage] * 1000
            count = self._counts[stage]
            logger.info(
                "⏱ {} — avg: {:.1f}ms, total: {:.1f}ms, calls: {}",
                stage, avg_ms, total_ms, count,
            )

    def reset(self) -> None:
        self._start_times.clear()
        self._totals.clear()
        self._counts.clear()
