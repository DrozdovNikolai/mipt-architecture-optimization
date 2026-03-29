from __future__ import annotations

import statistics
import time
import tracemalloc
from typing import Callable, TypeVar

from main import count_word_frequencies_in_text

T = TypeVar("T")
SNAPSHOT_FILE = "page_snapshot.html"


def load_raw_words(words_file: str) -> list[str]:
    with open(words_file, encoding="utf-8") as file:
        return [line.strip() for line in file if line.strip()]


def load_snapshot(snapshot_file: str) -> str:
    with open(snapshot_file, encoding="utf-8") as file:
        return file.read()


def baseline_count_word_frequencies_in_text(
    text: str, words_to_count: list[str]
) -> dict[str, int]:
    frequencies: dict[str, int] = {}

    for word in words_to_count:
        words = text.split()
        count = 0
        for token in words:
            if token == word:
                count += 1
        frequencies[word] = count

    return frequencies


def measure_time(
    func: Callable[..., T], *args: object, repeats: int = 5
) -> tuple[T, float]:
    timings: list[float] = []
    result: T | None = None

    for _ in range(repeats):
        start = time.perf_counter()
        result = func(*args)
        timings.append(time.perf_counter() - start)

    assert result is not None
    return result, statistics.median(timings)


def measure_peak_memory(func: Callable[..., T], *args: object) -> tuple[T, int]:
    tracemalloc.start()
    result = func(*args)
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return result, peak


def main() -> None:
    words_to_count = load_raw_words("words.txt")
    text = load_snapshot(SNAPSHOT_FILE)

    baseline_result, baseline_time = measure_time(
        baseline_count_word_frequencies_in_text, text, words_to_count
    )
    optimized_result, optimized_time = measure_time(
        count_word_frequencies_in_text, text, words_to_count
    )

    if baseline_result != optimized_result:
        raise RuntimeError("Optimized version changed the result set")

    _, baseline_peak = measure_peak_memory(
        baseline_count_word_frequencies_in_text, text, words_to_count
    )
    _, optimized_peak = measure_peak_memory(
        count_word_frequencies_in_text, text, words_to_count
    )

    speedup = baseline_time / optimized_time
    memory_ratio = baseline_peak / optimized_peak

    print(f"Input lines in words.txt: {len(words_to_count)}")
    print(f"Unique words in words.txt: {len(set(words_to_count))}")
    print(f"HTML snapshot: {SNAPSHOT_FILE}")
    print(f"HTTP requests in original app: {len(words_to_count)}")
    print("HTTP requests after optimization: 1")
    print(f"Baseline time (median): {baseline_time:.6f} s")
    print(f"Optimized time (median): {optimized_time:.6f} s")
    print(f"Speedup: {speedup:.2f}x")
    print(f"Baseline peak memory: {baseline_peak / 1024:.2f} KiB")
    print(f"Optimized peak memory: {optimized_peak / 1024:.2f} KiB")
    print(f"Memory reduction: {memory_ratio:.2f}x")


if __name__ == "__main__":
    main()
