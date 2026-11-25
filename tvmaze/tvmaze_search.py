"""Search TVMaze for television shows."""

import argparse
import json
import math
import sys
from pathlib import Path
from typing import TypedDict, cast

import requests


class Constants(TypedDict):
    api_url: str
    user_agent: str
    timeout_seconds: float
    source_url: str
    missing_value: str
    rating_max: int


def load_constants() -> Constants:
    """Load and validate application constants from beside this script."""
    with Path(__file__).with_name("constants.json").open(encoding="utf-8") as file:
        data: object = json.load(file)
    if not isinstance(data, dict):
        raise ValueError("constants must be a JSON object")
    values = cast(dict[object, object], data)
    strings: dict[str, str] = {}
    for key in ("api_url", "user_agent", "source_url", "missing_value"):
        value = values.get(key)
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{key} must be a non-empty string")
        strings[key] = value
    timeout = values.get("timeout_seconds")
    if (isinstance(timeout, bool) or not isinstance(timeout, (int, float))
            or not math.isfinite(timeout) or timeout <= 0):
        raise ValueError("timeout_seconds must be a positive finite number")
    rating_max = values.get("rating_max")
    if isinstance(rating_max, bool) or not isinstance(rating_max, int) or rating_max <= 0:
        raise ValueError("rating_max must be a positive integer")
    return Constants(
        api_url=strings["api_url"],
        user_agent=strings["user_agent"],
        timeout_seconds=timeout,
        source_url=strings["source_url"],
        missing_value=strings["missing_value"],
        rating_max=rating_max,
    )


def search_shows(query: str, constants: Constants) -> list[object]:
    """Fetch and decode the ranked show search results."""
    response = requests.get(
        constants["api_url"],
        params={"q": query},
        headers={"User-Agent": constants["user_agent"]},
        timeout=constants["timeout_seconds"],
    )
    response.raise_for_status()
    try:
        results: object = response.json()
    except ValueError as exc:
        raise ValueError("TVMaze returned invalid JSON.") from exc
    if not isinstance(results, list):
        raise ValueError("TVMaze returned an unexpected response format.")
    return cast(list[object], results)


def format_show(result: object, constants: Constants) -> str:
    """Format the fields used from one TVMaze search result."""
    if not isinstance(result, dict):
        raise ValueError("TVMaze returned an unexpected show format.")
    result_data = cast(dict[object, object], result)
    raw_show = result_data.get("show")
    if not isinstance(raw_show, dict):
        raise ValueError("TVMaze returned an unexpected show format.")
    show = cast(dict[object, object], raw_show)
    name = show.get("name")
    genres = show.get("genres")
    rating = show.get("rating")
    if not isinstance(name, str) or not name:
        raise ValueError("TVMaze returned a show without a valid name.")
    genre_strings: list[str] = []
    if genres is not None:
        if not isinstance(genres, list):
            raise ValueError("TVMaze returned invalid genres.")
        genre_values = cast(list[object], genres)
        for genre in genre_values:
            if not isinstance(genre, str):
                raise ValueError("TVMaze returned invalid genres.")
            genre_strings.append(genre)
    if rating is not None and not isinstance(rating, dict):
        raise ValueError("TVMaze returned an invalid rating.")
    rating_data = cast(dict[object, object], rating) if rating is not None else {}
    average = rating_data.get("average")
    if average is not None and (isinstance(average, bool) or not isinstance(average, (int, float))):
        raise ValueError("TVMaze returned an invalid average rating.")

    genre_text = ", ".join(genre_strings) if genre_strings else constants["missing_value"]
    rating_text = f"{average}/{constants['rating_max']}" if average is not None else constants["missing_value"]
    return f"Show: {name}\nGenres: {genre_text}\nRating: {rating_text}"


def main() -> int:
    parser = argparse.ArgumentParser(description="Search TVMaze for television shows.")
    parser.add_argument("name", nargs="+", help="show name to search for")
    args = parser.parse_args()
    query = " ".join(args.name).strip()
    if not query:
        parser.error("the show name must not be empty")

    try:
        constants = load_constants()
    except (OSError, ValueError) as exc:
        print(f"Could not load application constants: {exc}", file=sys.stderr)
        return 1

    try:
        results = search_shows(query, constants)
        shows = [format_show(result, constants) for result in results]
    except requests.RequestException as exc:
        print(f"Could not retrieve shows from TVMaze: {exc}", file=sys.stderr)
        return 1
    except ValueError as exc:
        print(f"Could not read the TVMaze response: {exc}", file=sys.stderr)
        return 1

    if shows:
        print("\n\n".join(shows))
    else:
        print(f"No shows found for: {query}")
    print(f"\nData provided by TVMaze: {constants['source_url']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
