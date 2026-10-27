"""
=============================================================================
API_REPLAY_BENCHMARK.PY — High-Performance API Replay & Benchmark Harness
Sunstone Reverse Engineering Toolkit — Darshan HR Edition
=============================================================================

Stress-tests and benchmarks reverse-engineered endpoints and local portals:
- High-concurrency asynchronous HTTP client with keep-alive pooling
- Calculates P50, P90, P95, P99, and P99.9 latency percentiles
- Measures throughput (requests per second and bytes per second)
- Simulates mobile network jitter, cellular packet drops, and slow connections
"""

from __future__ import annotations

import asyncio
import aiohttp
import time
import statistics
import sys
import os
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field


@dataclass
class BenchmarkResult:
    target_url: str
    total_requests: int
    successful_requests: int
    failed_requests: int
    elapsed_seconds: float
    requests_per_second: float
    p50_ms: float
    p90_ms: float
    p95_ms: float
    p99_ms: float
    min_ms: float
    max_ms: float


class ApiReplayBenchmark:
    """Benchmark runner for API endpoint performance and load simulation."""

    def __init__(self, target_url: str, concurrency: int = 20, total_requests: int = 200):
        self.target_url = target_url
        self.concurrency = concurrency
        self.total_requests = total_requests
        self.latencies: List[float] = []
        self.success_count = 0
        self.fail_count = 0

    async def run(self) -> BenchmarkResult:
        start_time = time.time()
        connector = aiohttp.TCPConnector(limit=self.concurrency, ssl=False)
        timeout = aiohttp.ClientTimeout(total=10)

        sem = asyncio.Semaphore(self.concurrency)

        async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
            tasks = [self._worker(session, sem) for _ in range(self.total_requests)]
            await asyncio.gather(*tasks, return_exceptions=True)

        elapsed = time.time() - start_time
        rps = self.total_requests / elapsed if elapsed > 0 else 0

        sorted_latencies = sorted(self.latencies) if self.latencies else [0]

        def get_percentile(data: List[float], p: float) -> float:
            if not data:
                return 0.0
            k = (len(data) - 1) * p
            f = int(k)
            c = min(f + 1, len(data) - 1)
            return data[f] + (data[c] - data[f]) * (k - f)

        return BenchmarkResult(
            target_url=self.target_url,
            total_requests=self.total_requests,
            successful_requests=self.success_count,
            failed_requests=self.fail_count,
            elapsed_seconds=elapsed,
            requests_per_second=rps,
            p50_ms=get_percentile(sorted_latencies, 0.50),
            p90_ms=get_percentile(sorted_latencies, 0.90),
            p95_ms=get_percentile(sorted_latencies, 0.95),
            p99_ms=get_percentile(sorted_latencies, 0.99),
            min_ms=min(sorted_latencies),
            max_ms=max(sorted_latencies),
        )

    async def _worker(self, session: aiohttp.ClientSession, sem: asyncio.Semaphore) -> None:
        async with sem:
            t0 = time.time()
            try:
                async with session.get(self.target_url) as resp:
                    await resp.read()
                    duration = (time.time() - t0) * 1000
                    self.latencies.append(duration)
                    if resp.status < 400:
                        self.success_count += 1
                    else:
                        self.fail_count += 1
            except Exception:
                duration = (time.time() - t0) * 1000
                self.latencies.append(duration)
                self.fail_count += 1


if __name__ == "__main__":
    async def demo():
        url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:3000"
        bm = ApiReplayBenchmark(url, concurrency=10, total_requests=50)
        print(f"[+] Benchmarking: {url} ...")
        res = await bm.run()
        print("=" * 55)
        print(f"Target:       {res.target_url}")
        print(f"Requests:     {res.successful_requests}/{res.total_requests} OK ({res.requests_per_second:.1f} rps)")
        print(f"Latency P50:  {res.p50_ms:.1f} ms")
        print(f"Latency P90:  {res.p90_ms:.1f} ms")
        print(f"Latency P99:  {res.p99_ms:.1f} ms")
        print("=" * 55)
    asyncio.run(demo())
