#!/usr/bin/env python3
"""Get frequency of words used."""

import csv
from collections import Counter, defaultdict
from itertools import zip_longest
from typing import Dict, List, Tuple

from tabulate import tabulate

CSV_FILE = "normalized_responses.csv"


def get_column(header: str) -> List[str]:
    """Get the values of a column as a list."""
    with open(CSV_FILE, "r", newline="") as csvfile:
        reader = csv.DictReader(csvfile)
        entries = [row[header] for row in reader if row[header]]
    return entries


def get_count(header: str) -> List[Tuple[str, int]]:
    """Get pairs of word, number of occurences from a header."""
    word_counter = Counter(get_column(header))
    counter_tuples = [(k, v) for k, v in word_counter.items()]
    sorted_words = sorted(counter_tuples, key=lambda x: 0 - x[1])
    return sorted_words


def limit(count: List[Tuple[str, int]], max_frequency: int) -> List[Tuple[str, int]]:
    """Limit a count to a certain frequency."""
    return [x for x in count if x[1] >= max_frequency]


def combine(first: List[Tuple], second: List[Tuple]) -> List[Tuple]:
    """Zip two frequency counts next to each other."""
    return [x[0] + x[1] for x in list(zip_longest(first, second, fillvalue=("", 0)))]


def get_common(first_hdr: str, second_hdr: str) -> List[Tuple]:
    """Find overlapping words."""
    first = get_count(first_hdr)
    second = get_count(second_hdr)
    out = defaultdict(dict)  # type: Dict[str, Dict[str, int]]
    for word, count in first:
        out[word][first_hdr] = count
    for word, count in second:
        out[word][second_hdr] = count

    common = {k: v for k, v in out.items() if len(v.keys()) == 2}
    return sorted(
        [(k, v[first_hdr], v[second_hdr]) for k, v in common.items()],
        key=lambda x: x[1] + x[2],
        reverse=True,
    )


if __name__ == "__main__":
    HOPE_COUNT = limit(get_count("hope"), 3)
    THINK_COUNT = limit(get_count("think"), 3)
    FEAR_COUNT = limit(get_count("fear"), 3)
    COMBINED = combine(combine(HOPE_COUNT, THINK_COUNT), FEAR_COUNT)
    print(tabulate(COMBINED, headers=["Hope", "#", "Think", "#", "Fear", "#"]))

    print()
    print(tabulate(get_common("think", "fear"), headers=["word", "think", "fear"]))
    print()
    print(tabulate(get_common("think", "hope"), headers=["word", "think", "hope"]))

    # print(get_common("hope", "think"))
