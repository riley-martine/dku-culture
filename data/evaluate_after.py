#!/usr/bin/env python3
"""Find out some things about how people feel after 7 weeks."""

import csv
from collections import Counter
from typing import Any, List, Tuple

from tabulate import tabulate

from frequency import limit

CSV_FILE = "evaluation.csv"


def get_responses() -> List[List[str]]:
    """Pull responses from csv."""
    with open(CSV_FILE, "r") as csvfile:
        reader = csv.reader(csvfile)
        next(reader)  # Skip header
        next(reader)  # Skip question
        next(reader)  # Skip metadata
        items = [row[1].split(",") for row in reader]
    return items


def flatten(xs: List[List[Any]]) -> List[Any]:
    """Squish a list down a layer."""
    return [item for sublist in xs for item in sublist]


def count(xs: List[Any]) -> List[Tuple[str, int]]:
    """Get pairs of word, number of occurences."""
    word_counter = Counter(xs)
    counter_tuples = [(k, v) for k, v in word_counter.items()]
    sorted_words = sorted(counter_tuples, key=lambda x: 0 - x[1])
    return sorted_words


def incidence(xs: List[List[str]]) -> None:
    """Find out if people said challenging, difficult, or both."""
    both = [x for x in xs if ("Challenging" in x) and ("Difficult" in x)]
    chal = [x for x in xs if ("Challenging" in x) and ("Difficult" not in x)]
    diff = [x for x in xs if ("Challenging" not in x) and ("Difficult" in x)]
    print(f"Both: {len(both)}")
    print(f"Chal: {len(chal)}")
    print(f"Diff: {len(diff)}")
    print(f"{'&'*len(chal)}{'@'*len(both)}{'#'*len(diff)}")


RANKED_HOPES = {
    "inclusive": 0,
    "diverse": 1,
    "friendly": 2,
    "dynamic": 3,
    "harmonious": 3,
    "supportive": 3,
}


if __name__ == "__main__":
    ALL_RESPONSES = flatten(get_responses())
    COUNTED = count(ALL_RESPONSES)
    print(tabulate(COUNTED, headers=["Word", "#"], tablefmt="html"))

    common = [x[0] for x in Counter([x.lower() for x in ALL_RESPONSES]).most_common()]
    ranks = []
    for word, rank in RANKED_HOPES.items():
        ranks.append([word, rank, common.index(word)])
    print()
    print(tabulate(ranks, headers=["Word", "Original", "New"]))

    print()
    incidence(get_responses())
    NUM_GLOBAL = len(
        [
            xs
            for xs in get_responses()
            if ("Multicultural" in xs) or ("Diverse" in xs) or ("Global" in xs)
        ]
    )
    print(NUM_GLOBAL)
