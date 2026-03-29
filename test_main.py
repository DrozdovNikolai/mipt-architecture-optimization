from __future__ import annotations

import unittest

from benchmark import baseline_count_word_frequencies_in_text
from main import count_word_frequencies_in_text, iter_split_tokens


class IterSplitTokensTests(unittest.TestCase):
    def test_matches_split_for_single_chunk(self) -> None:
        text = "  alpha beta\tgamma\ndelta  "
        self.assertEqual(list(iter_split_tokens((text,))), text.split())

    def test_matches_split_for_multiple_chunks(self) -> None:
        chunks = ("  al", "pha be", "ta\tga", "mma\ndel", "ta  ")
        joined = "".join(chunks)
        self.assertEqual(list(iter_split_tokens(chunks)), joined.split())

    def test_handles_long_tail_without_whitespace(self) -> None:
        chunks = ("par", "tial", "_token")
        joined = "".join(chunks)
        self.assertEqual(list(iter_split_tokens(chunks)), joined.split())


class CountWordFrequenciesTests(unittest.TestCase):
    def test_matches_original_algorithm(self) -> None:
        text = "a b a c b a c c a"
        words_to_count = ["a", "c", "a", "missing"]

        self.assertEqual(
            count_word_frequencies_in_text(text, words_to_count),
            baseline_count_word_frequencies_in_text(text, words_to_count),
        )


if __name__ == "__main__":
    unittest.main()
