"""
Online fast inference engine and latency benchmarking harness.
Evaluates prediction latency empirically against target (< 0.05 ms per query).
"""

import time
from typing import Any, Dict, List, Optional
import numpy as np
import pandas as pd


class FastInferenceEngine:
    """
    Lightweight prediction engine executing trained models with high performance.
    """

    def __init__(self, model: Any):
        self.model = model

    def benchmark_latency(
        self,
        sample_input: pd.DataFrame,
        n_warmup: int = 50,
        n_queries: int = 1000,
    ) -> Dict[str, float]:
        """
        Benchmark single-query and batch inference latency.
        Strictly measures runtime rather than assuming target < 0.05 ms is met.
        """
        # Warm-up phase
        for _ in range(n_warmup):
            _ = self.model.predict(sample_input.iloc[[0]])

        # Single-query latency benchmark
        single_row = sample_input.iloc[[0]]
        start = time.perf_counter()
        for _ in range(n_queries):
            _ = self.model.predict(single_row)
        total_time = time.perf_counter() - start

        avg_latency_ms = (total_time / n_queries) * 1000.0

        return {
            "n_queries": n_queries,
            "total_benchmark_time_s": total_time,
            "mean_latency_ms_per_query": avg_latency_ms,
            "target_latency_ms": 0.05,
            "target_met": avg_latency_ms < 0.05,
        }
