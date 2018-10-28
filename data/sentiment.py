#!/usr/bin/env python3
"""Sentiment analysis of words given as survey responses."""

import csv
import json
import os
import statistics
import subprocess
from typing import Dict, List

from mypy_extensions import TypedDict

Probability = TypedDict("Probability", {"neg": float, "pos": float, "neutral": float})
Sentiment = TypedDict("Sentiment", {"probability": Probability, "label": str})

INFILE = "individual_words.csv"
OUTFILE = "sentiments.csv"


def get_sentiment(word: str) -> Sentiment:
    """Get sentiment percentages for a word."""
    resp = (
        subprocess.Popen(
            f'curl -s -d "text={word}" http://text-processing.com/api/sentiment/',
            shell=True,
            stdout=subprocess.PIPE,
        )
        .stdout.read()
        .decode("utf-8")
    )
    print(f"{word}: {resp}")
    return json.loads(resp)


def write_responses(responses: Dict[str, Sentiment]) -> None:
    """Save sentiments to disk."""
    with open(OUTFILE, "w") as outfile:
        writer = csv.writer(outfile)
        writer.writerow(["word", "pos", "neg", "neutral", "label"])
        for word, sent in responses.items():
            prob = sent["probability"]
            writer.writerow(
                [word, prob["pos"], prob["neg"], prob["neutral"], sent["label"]]
            )


def get_words() -> List[str]:
    """Read in words to classify."""
    with open(INFILE, "r", newline="") as infile:
        reader = csv.reader(infile)
        items = [row[0] for row in reader]
    return items


def calculate_sentiment() -> None:
    """Calculate sentiment for words and store on disk."""
    WORDS = get_words()
    sentiments = {}
    for word in WORDS:
        try:
            sentiments[word] = get_sentiment(word)
        except Exception as ex:
            print(f"Error on {word}. This shouldn't happen!")
            print(ex)

    write_responses(sentiments)


def disk_sentiment() -> Dict[str, Sentiment]:
    """Get cached sentiments for words."""
    rows = {}
    with open(OUTFILE, "r", newline="") as csvfile:
        reader = csv.reader(csvfile)
        next(reader)  # Skip headers
        for row in reader:
            probability = {
                "pos": float(row[1]),
                "neg": float(row[2]),
                "neutral": float(row[3]),
            }  # type: Probability
            sentiment = {"probability": probability, "label": row[4]}  # type: Sentiment
            rows[row[0]] = sentiment
    return rows


def get_rows() -> Dict[str, List[str]]:
    """Get the rows for HOPE, FEAR, and THINK questions."""
    rows = {"hope": [], "fear": [], "think": []}  # type: Dict[str, List[str]]
    with open("normalized_responses.csv", newline="") as csvfile:
        reader = csv.reader(csvfile)
        next(reader)  # Skip headers
        for row in reader:
            if row[0]:
                rows["hope"].append(row[0])
            if row[1]:
                rows["fear"].append(row[1])
            if row[2]:
                rows["think"].append(row[2])
    return rows


def calculate_mean_sentiments(
    rows: Dict[str, List[str]], sentiment: Dict[str, Sentiment]
) -> Dict[str, float]:
    """Calculate some mean numbers."""
    out = {}
    keys = ["pos", "neg", "neutral"]
    banned = ["intense"]
    for header, words in rows.items():
        means = {}
        for key in keys:
            word_sent = [
                sentiment[word]["probability"][key]
                for word in words
                if word not in banned
            ]
            means[key] = statistics.mean(word_sent)
        out[header] = means
    return out


if __name__ == "__main__":
    if not os.path.exists(OUTFILE):
        calculate_sentiment()

    sent_dict = disk_sentiment()
    rows_to_calc = get_rows()
    print(calculate_mean_sentiments(rows_to_calc, sent_dict))
