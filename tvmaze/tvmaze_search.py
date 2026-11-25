"""Search TVMaze for television shows.

This module provides functionality to search the TVMaze API for television shows
and display results with genres and ratings. It demonstrates logging, error handling,
and comprehensive type checking.
"""

import argparse
import json
import logging
import math
import sys
from pathlib import Path
from typing import TypedDict, cast

import requests

logger = logging.getLogger(__name__)


class Constants(TypedDict):
    """Application constants loaded from JSON configuration file.

    Attributes:
        api_url: TVMaze API endpoint for show search.
        user_agent: User agent string for API requests.
        timeout_seconds: Request timeout in seconds.
        source_url: Attribution URL for TVMaze.
        missing_value: Text to display when data is unavailable.
        rating_max: Maximum rating scale value.
    """

    api_url: str
    user_agent: str
    timeout_seconds: float
    source_url: str
    missing_value: str
    rating_max: int


class ConstantsLoadError(Exception):
    """Raised when constants file cannot be loaded or validated."""

    pass


class InvalidResponseError(Exception):
    """Raised when TVMaze returns an unexpected response format."""

    pass


def load_constants() -> Constants:
    """Load and validate application constants from beside this script.

    Returns:
        Constants: Validated configuration dictionary.

    Raises:
        ConstantsLoadError: If constants file is missing, invalid JSON,
            or contains invalid values.
    """
    constants_path = Path(__file__).with_name("constants.json")
    logger.debug(f"Loading constants from {constants_path}")

    try:
        with constants_path.open(encoding="utf-8") as file:
            data: object = json.load(file)
    except FileNotFoundError as exc:
        logger.error(f"Constants file not found at {constants_path}")
        raise ConstantsLoadError(
            f"constants file not found at {constants_path}"
        ) from exc
    except json.JSONDecodeError as exc:
        logger.error(f"Invalid JSON in constants file: {exc}")
        raise ConstantsLoadError(
            f"constants file contains invalid JSON: {exc}"
        ) from exc

    if not isinstance(data, dict):
        logger.error("Constants root must be a JSON object")
        raise ConstantsLoadError("constants must be a JSON object")

    values = cast(dict[object, object], data)
    strings: dict[str, str] = {}

    for key in ("api_url", "user_agent", "source_url", "missing_value"):
        value = values.get(key)
        if not isinstance(value, str) or not value.strip():
            logger.error(f"Invalid value for {key}: must be a non-empty string")
            raise ConstantsLoadError(
                f"{key} must be a non-empty string"
            )
        strings[key] = value

    timeout = values.get("timeout_seconds")
    if (isinstance(timeout, bool) or not isinstance(timeout, (int, float))
            or not math.isfinite(timeout) or timeout <= 0):
        logger.error(
            f"Invalid timeout_seconds: {timeout} (must be positive finite number)"
        )
        raise ConstantsLoadError(
            "timeout_seconds must be a positive finite number"
        )

    rating_max = values.get("rating_max")
    if isinstance(rating_max, bool) or not isinstance(rating_max, int) or rating_max <= 0:
        logger.error(f"Invalid rating_max: {rating_max} (must be positive integer)")
        raise ConstantsLoadError("rating_max must be a positive integer")

    logger.info("Constants loaded successfully")
    return Constants(
        api_url=strings["api_url"],
        user_agent=strings["user_agent"],
        timeout_seconds=timeout,
        source_url=strings["source_url"],
        missing_value=strings["missing_value"],
        rating_max=rating_max,
    )


def search_shows(query: str, constants: Constants) -> list[object]:
    """Fetch and decode the ranked show search results from TVMaze.

    Args:
        query: Show name to search for.
        constants: Application constants with API configuration.

    Returns:
        list[object]: List of show search results from TVMaze API.

    Raises:
        requests.RequestException: If the API request fails.
        InvalidResponseError: If the response format is invalid.
    """
    logger.info(f"Searching TVMaze for query: '{query}'")

    try:
        response = requests.get(
            constants["api_url"],
            params={"q": query},
            headers={"User-Agent": constants["user_agent"]},
            timeout=constants["timeout_seconds"],
        )
        response.raise_for_status()
    except requests.Timeout as exc:
        logger.error(f"Request timeout after {constants['timeout_seconds']}s")
        raise requests.RequestException(
            f"Request timed out after {constants['timeout_seconds']} seconds"
        ) from exc
    except requests.HTTPError as exc:
        status_code = exc.response.status_code if exc.response else "unknown"
        logger.error(f"HTTP error from TVMaze: {status_code} {exc}")
        raise
    except requests.RequestException as exc:
        logger.error(f"Network error communicating with TVMaze: {exc}")
        raise

    try:
        results: object = response.json()
    except ValueError as exc:
        logger.error(f"TVMaze returned invalid JSON: {exc}")
        raise InvalidResponseError("TVMaze returned invalid JSON") from exc

    if not isinstance(results, list):
        logger.error(f"Expected list response, got {type(results).__name__}")
        raise InvalidResponseError("TVMaze returned an unexpected response format")

    results_list: list[object] = cast(list[object], results)
    logger.debug(f"Retrieved {len(results_list)} results for query: '{query}'")
    return results_list


def format_show(result: object, constants: Constants) -> str:
    """Format the fields used from one TVMaze search result.

    Args:
        result: A single search result object from TVMaze API.
        constants: Application constants with display configuration.

    Returns:
        str: Formatted show information with name, genres, and rating.

    Raises:
        InvalidResponseError: If the result format is invalid or unexpected.
    """
    if not isinstance(result, dict):
        logger.warning(f"Expected dict result, got {type(result).__name__}")
        raise InvalidResponseError("TVMaze returned an unexpected show format")

    result_data = cast(dict[object, object], result)
    raw_show = result_data.get("show")
    if not isinstance(raw_show, dict):
        logger.warning("Missing or invalid 'show' field in result")
        raise InvalidResponseError("TVMaze returned an unexpected show format")

    show = cast(dict[object, object], raw_show)
    name = show.get("name")
    genres = show.get("genres")
    rating = show.get("rating")

    if not isinstance(name, str) or not name:
        logger.warning("Show missing valid name field")
        raise InvalidResponseError("TVMaze returned a show without a valid name")

    genre_strings: list[str] = []
    if genres is not None:
        if not isinstance(genres, list):
            logger.warning(f"Expected list for genres, got {type(genres).__name__}")
            raise InvalidResponseError("TVMaze returned invalid genres")
        genre_values = cast(list[object], genres)
        for genre in genre_values:
            if not isinstance(genre, str):
                logger.warning(f"Non-string genre encountered: {type(genre).__name__}")
                raise InvalidResponseError("TVMaze returned invalid genres")
            genre_strings.append(genre)

    if rating is not None and not isinstance(rating, dict):
        logger.warning(f"Expected dict for rating, got {type(rating).__name__}")
        raise InvalidResponseError("TVMaze returned an invalid rating")

    rating_data = cast(dict[object, object], rating) if rating is not None else {}
    average = rating_data.get("average")
    if average is not None and (
        isinstance(average, bool) or not isinstance(average, (int, float))
    ):
        logger.warning(f"Invalid rating average: {type(average).__name__}")
        raise InvalidResponseError("TVMaze returned an invalid average rating")

    genre_text = (
        ", ".join(genre_strings) if genre_strings else constants["missing_value"]
    )
    rating_text = (
        f"{average}/{constants['rating_max']}"
        if average is not None
        else constants["missing_value"]
    )
    logger.debug(f"Formatted show: {name}")
    return f"Show: {name}\nGenres: {genre_text}\nRating: {rating_text}"


def main() -> int:
    """Main entry point for the TVMaze search application.

    Parses command-line arguments, loads configuration, queries TVMaze API,
    and displays formatted results.

    Returns:
        int: 0 on success, 1 on error.
    """
    logging.basicConfig(
        level=logging.WARNING,
        format="%(name)s: %(levelname)s: %(message)s",
    )

    parser = argparse.ArgumentParser(description="Search TVMaze for television shows.")
    parser.add_argument("name", nargs="+", help="show name to search for")
    args = parser.parse_args()
    query = " ".join(args.name).strip()

    if not query:
        logger.error("No show name provided")
        parser.error("the show name must not be empty")

    try:
        constants = load_constants()
    except ConstantsLoadError as exc:
        logger.error(f"Failed to load constants: {exc}")
        print(f"Could not load application constants: {exc}", file=sys.stderr)
        return 1

    try:
        results = search_shows(query, constants)
        shows = [format_show(result, constants) for result in results]
    except requests.RequestException as exc:
        logger.error(f"Failed to retrieve shows from TVMaze: {exc}")
        print(f"Could not retrieve shows from TVMaze: {exc}", file=sys.stderr)
        return 1
    except InvalidResponseError as exc:
        logger.error(f"Invalid TVMaze response format: {exc}")
        print(f"Could not read the TVMaze response: {exc}", file=sys.stderr)
        return 1

    if shows:
        logger.info(f"Found {len(shows)} show(s) for query: '{query}'")
        print("\n\n".join(shows))
    else:
        logger.info(f"No shows found for query: '{query}'")
        print(f"No shows found for: {query}")

    print(f"\nData provided by TVMaze: {constants['source_url']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
