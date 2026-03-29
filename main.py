from __future__ import annotations

from collections.abc import Iterable, Iterator
import re

import requests

DEFAULT_WORDS_FILE = "words.txt"
DEFAULT_URL = "https://eng.mipt.ru/why-mipt/"
CHUNK_SIZE = 8192
REQUEST_TIMEOUT = 30
TOKEN_PATTERN = re.compile(r"\S+")


def load_words(words_file: str) -> list[str]:
    with open(words_file, encoding="utf-8") as file:
        return list(dict.fromkeys(line.strip() for line in file if line.strip()))


def iter_split_tokens(chunks: Iterable[str]) -> Iterator[str]:
    tail = ""

    for chunk in chunks:
        if not chunk:
            continue

        merged_chunk = tail + chunk
        parts = merged_chunk.split()

        if merged_chunk and not merged_chunk[-1].isspace():
            if parts:
                tail = parts.pop()
            else:
                tail = merged_chunk
                continue
        else:
            tail = ""

        yield from parts

    if tail:
        yield tail


def count_word_frequencies_in_text(text: str, words_to_count: Iterable[str]) -> dict[str, int]:
    ordered_words = list(dict.fromkeys(words_to_count))
    frequencies = {word: 0 for word in ordered_words}

    if not frequencies:
        return frequencies

    target_words = set(frequencies)
    for match in TOKEN_PATTERN.finditer(text):
        token = match.group(0)
        if token in target_words:
            frequencies[token] += 1

    return frequencies


def count_word_frequencies(url: str, words_to_count: Iterable[str]) -> dict[str, int]:
    ordered_words = list(dict.fromkeys(words_to_count))
    frequencies = {word: 0 for word in ordered_words}

    if not frequencies:
        return frequencies

    target_words = set(frequencies)

    with requests.Session() as session:
        with session.get(url, stream=True, timeout=REQUEST_TIMEOUT) as response:
            response.raise_for_status()
            response.encoding = response.encoding or response.apparent_encoding or "utf-8"

            for token in iter_split_tokens(
                response.iter_content(chunk_size=CHUNK_SIZE, decode_unicode=True)
            ):
                if token in target_words:
                    frequencies[token] += 1

    return frequencies


def main() -> None:
    words_to_count = load_words(DEFAULT_WORDS_FILE)
    frequencies = count_word_frequencies(DEFAULT_URL, words_to_count)
    print(frequencies)


if __name__ == "__main__":
    main()
