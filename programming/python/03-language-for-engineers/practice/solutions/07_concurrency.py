"""07 — Concurrency. Run: python3 07_concurrency.py

The "network" is simulated with sleeps, so it runs offline and the timings are predictable."""

import asyncio
import time
from collections.abc import Awaitable, Callable
from concurrent.futures import ThreadPoolExecutor


def slow_square(x: int) -> int:
    """Given. A blocking call that takes 0.1 s."""
    time.sleep(0.1)
    return x * x


async def fake_fetch(url: str) -> str:
    """Given. An async call that takes 0.1 s; URLs containing 'bad' fail."""
    await asyncio.sleep(0.1)
    if "bad" in url:
        raise ConnectionError(url)
    return f"<html>{url}</html>"


def squares_threaded(xs: list[int], workers: int = 8) -> list[int]:
    """Q1. slow_square over xs with a ThreadPoolExecutor, results in input order."""
    with ThreadPoolExecutor(max_workers=workers) as pool:
        return list(pool.map(slow_square, xs))


async def fetch_all(urls: list[str]) -> dict[str, str | Exception]:
    """Q2. Fetch every URL concurrently. Map each URL to its body, or to the exception it raised.
    One failure must not stop the others (gather with return_exceptions)."""
    results = await asyncio.gather(*(fake_fetch(u) for u in urls), return_exceptions=True)
    return dict(zip(urls, results))


async def fetch_limited(urls: list[str], limit: int) -> tuple[list[str], int]:
    """Q3. Fetch all URLs with at most `limit` in flight (asyncio.Semaphore). Return the bodies
    in input order and the highest number of concurrent calls you observed."""
    sem = asyncio.Semaphore(limit)
    in_flight = peak = 0

    async def one(url: str) -> str:
        nonlocal in_flight, peak
        async with sem:
            in_flight += 1
            peak = max(peak, in_flight)
            try:
                return await fake_fetch(url)
            finally:
                in_flight -= 1

    async with asyncio.TaskGroup() as tg:
        tasks = [tg.create_task(one(u)) for u in urls]
    return [t.result() for t in tasks], peak


async def with_timeout[T](make: Callable[[], Awaitable[T]], seconds: float, default: T) -> T:
    """Q4. Await make() but give up after `seconds`, returning `default` instead (asyncio.timeout)."""
    try:
        async with asyncio.timeout(seconds):
            return await make()
    except TimeoutError:
        return default


async def run_blocking(xs: list[int]) -> list[int]:
    """Q5. Call the BLOCKING slow_square for each x without blocking the event loop
    (asyncio.to_thread), all concurrently."""
    return list(await asyncio.gather(*(asyncio.to_thread(slow_square, x) for x in xs)))


if __name__ == "__main__":
    t = time.perf_counter()
    assert squares_threaded(list(range(8))) == [x * x for x in range(8)]
    assert time.perf_counter() - t < 0.5, "threads should overlap the sleeps"

    t = time.perf_counter()
    res = asyncio.run(fetch_all(["a", "bad", "c"]))
    assert res["a"] == "<html>a</html>" and isinstance(res["bad"], ConnectionError)
    assert time.perf_counter() - t < 0.3

    bodies, peak = asyncio.run(fetch_limited([f"u{i}" for i in range(10)], limit=3))
    assert bodies[0] == "<html>u0</html>" and len(bodies) == 10 and peak == 3

    assert asyncio.run(with_timeout(lambda: fake_fetch("x"), 1, "late")) == "<html>x</html>"
    assert asyncio.run(with_timeout(lambda: fake_fetch("x"), 0.01, "late")) == "late"

    t = time.perf_counter()
    assert asyncio.run(run_blocking([1, 2, 3, 4])) == [1, 4, 9, 16]
    assert time.perf_counter() - t < 0.35
    print("all good")
