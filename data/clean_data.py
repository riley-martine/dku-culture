#!/usr/bin/env python3
"""Clean up the raw data into something easier to work with."""
# I did this with python because I was too lazy to
#   spend 5 minutes doing it by hand

import csv
import itertools
import re
from typing import Dict, List

from autocorrect import NLP_COUNTS, known, spell


# We could use a mypy_extensions.TypedDict here, but I think it's
#   not warranted for such a small program
def get_raw_rows() -> Dict[str, List[str]]:
    """Get the rows for HOPE, FEAR, and THINK questions."""
    rows = {"hope": [], "fear": [], "think": []}  # type: Dict[str, List[str]]
    with open("raw_responses.csv", newline="") as csvfile:
        reader = csv.reader(csvfile)
        next(reader)  # Skip headers
        for row in reader:
            # One person put one "hope" adjective in each field
            if row[0] == "14bd49ff1028ecdd9adf80269591b1f0":
                rows["hope"].extend(row[1:4])
                continue
            rows["hope"].append(row[1])
            rows["fear"].append(row[2])
            rows["think"].append(row[3])
    return rows


def row_to_words(row: List[str]) -> List[str]:
    """Extract the words from a row."""
    # Match word boundary, but also ' and -
    token = re.compile(r"[\w'-]+")
    ignore = ["but", "and"]
    words = list(itertools.chain(*[token.findall(cell) for cell in row]))
    return [word for word in words if not word.lower() in ignore]


def handle_hyphenated_word(word: str) -> str:
    """Figure out how to correct a hyphenated word."""
    de_hyphenated = word.replace("-", "")

    # The possibilities for what could be correct
    permutations = [word, de_hyphenated, spell(word), spell(de_hyphenated)]
    known_words = list(known(permutations))

    if not known_words:  # Uh oh
        print(permutations)
        resp = input(f"Correct {word} to: ")
        if not resp:  # User just hits enter
            return word
        if resp in permutations:
            return resp
        return cleanup_word(resp)

    if len(known_words) == 1:
        if input(f"Correct {word} to {known_words[0]}? (Y/n): ") == "n":
            return word
        return known_words[0]

    print("This is interesting. This part of the code is untested.")
    return max([(NLP_COUNTS[word], word) for word in known_words], key=lambda x: x[0])[
        1
    ]


def cleanup_word(word: str) -> str:
    """Lowercase word and make sure it's spelled correctly."""
    lower = word.lower()
    if "-" in lower:
        return handle_hyphenated_word(lower)

    if known([lower]):
        return lower

    correct = spell(lower)
    if correct == lower:  # Failed to autocorrect
        return input(f"Correct {lower} to: ")

    if input(f"Correct {lower} to {correct}? (Y/n): ") == "n":
        if input("leave as is? (Y/n): ") == "n":
            return input("Correct to: ")
        return lower
    return correct


def write_csv(data: Dict[str, List[str]]) -> None:
    """Write the cleaned data to a new file"""
    rows = list(itertools.zip_longest(*data.values()))
    with open("cleaned_responses.csv", "w") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["hope", "fear", "think"])
        writer.writerows(rows)


if __name__ == "__main__":
    all_rows = get_raw_rows()
    words = {
        header: sorted([cleanup_word(word) for word in row_to_words(row)])
        for header, row in all_rows.items()
    }
    write_csv(words)
