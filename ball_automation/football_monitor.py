"""ESPN football match monitor.

Retrieves a scoreboard, applies an optional team filter, writes a report,
and records operational activity and errors.
"""

import argparse
import json
import logging
import math
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import TypedDict, cast

import requests

__all__ = ["requests"]


class Config(TypedDict):
    """User configuration for the football monitor."""

    league: str
    team_filter: str
    output_file: str


class Constants(TypedDict):
    """Application constants loaded from JSON."""

    api_base_url: str
    user_agent: str
    timeout_seconds: float
    missing_value: str
    log_file: str


class ConfigurationError(Exception):
    """Raised when configuration or constants cannot be loaded."""


class InvalidResponseError(Exception):
    """Raised when ESPN returns an unexpected response shape."""


@dataclass(frozen=True)
class Match:
    """Display fields for one football match."""

    home_team: str
    away_team: str
    status: str
    score: str


SCRIPT_DIRECTORY = Path(__file__).resolve().parent
CONFIG_PATH = SCRIPT_DIRECTORY / "config.json"
CONSTANTS_PATH = SCRIPT_DIRECTORY / "constants.json"
LOG_PATH = SCRIPT_DIRECTORY / "automation.log"


def load_config(path: Path = CONFIG_PATH) -> Config:
    """Load and validate user configuration.

    Args:
        path: Configuration JSON file path.

    Returns:
        Config: Validated configuration values.

    Raises:
        ConfigurationError: If the file is missing, invalid, or incomplete.
    """
    try:
        with path.open(encoding="utf-8") as file:
            data: object = json.load(file)
    except FileNotFoundError as exc:
        raise ConfigurationError(f"configuration file not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ConfigurationError(f"invalid JSON in configuration file: {exc}") from exc
    except OSError as exc:
        raise ConfigurationError(f"could not read configuration file: {exc}") from exc

    if not isinstance(data, dict):
        raise ConfigurationError("configuration root must be a JSON object")

    values = cast(dict[object, object], data)
    league = values.get("league")
    team_filter = values.get("team_filter")
    output_file = values.get("output_file")

    if not isinstance(league, str) or not league.strip():
        raise ConfigurationError("league must be a non-empty string")
    if not isinstance(team_filter, str):
        raise ConfigurationError("team_filter must be a string")
    if not isinstance(output_file, str) or not output_file.strip():
        raise ConfigurationError("output_file must be a non-empty string")
    if Path(output_file).is_absolute():
        raise ConfigurationError("output_file must be a filename, not an absolute path")

    return Config(
        league=league.strip(),
        team_filter=team_filter.strip(),
        output_file=output_file.strip(),
    )


def load_constants(path: Path = CONSTANTS_PATH) -> Constants:
    """Load and validate application constants.

    Args:
        path: Constants JSON file path.

    Returns:
        Constants: Validated application constants.

    Raises:
        ConfigurationError: If constants are missing or invalid.
    """
    try:
        with path.open(encoding="utf-8") as file:
            data: object = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError, OSError) as exc:
        raise ConfigurationError(f"could not load constants from {path}: {exc}") from exc

    if not isinstance(data, dict):
        raise ConfigurationError("constants root must be a JSON object")

    values = cast(dict[object, object], data)
    string_keys = ("api_base_url", "user_agent", "missing_value", "log_file")
    strings: dict[str, str] = {}
    for key in string_keys:
        value = values.get(key)
        if not isinstance(value, str) or not value.strip():
            raise ConfigurationError(f"{key} must be a non-empty string")
        strings[key] = value

    timeout = values.get("timeout_seconds")
    if (
        isinstance(timeout, bool)
        or not isinstance(timeout, (int, float))
        or not math.isfinite(timeout)
        or timeout <= 0
    ):
        raise ConfigurationError("timeout_seconds must be a positive finite number")

    return Constants(
        api_base_url=strings["api_base_url"],
        user_agent=strings["user_agent"],
        timeout_seconds=timeout,
        missing_value=strings["missing_value"],
        log_file=strings["log_file"],
    )


def build_api_url(league: str, constants: Constants) -> str:
    """Build an ESPN league scoreboard URL.

    Args:
        league: ESPN league identifier such as ``sco.1``.
        constants: Application constants.

    Returns:
        str: Complete scoreboard URL.
    """
    return f"{constants['api_base_url'].rstrip('/')}/{league}/scoreboard"


def extract_matches(data: object) -> list[Match]:
    """Extract displayable matches from an ESPN scoreboard response.

    Args:
        data: Decoded ESPN JSON value.

    Returns:
        list[Match]: Extracted matches.

    Raises:
        InvalidResponseError: If the response structure is invalid.
    """
    if not isinstance(data, dict):
        raise InvalidResponseError("ESPN response root must be a JSON object")

    root = cast(dict[object, object], data)
    events = root.get("events")
    if not isinstance(events, list):
        raise InvalidResponseError("ESPN response must contain an events list")

    matches: list[Match] = []
    for raw_event in cast(list[object], events):
        if not isinstance(raw_event, dict):
            raise InvalidResponseError("ESPN event must be a JSON object")
        event = cast(dict[object, object], raw_event)

        status_value = event.get("status")
        status = "Not available"
        if isinstance(status_value, dict):
            status_object = cast(dict[object, object], status_value)
            status_type = status_object.get("type")
            if isinstance(status_type, dict):
                status_detail = cast(dict[object, object], status_type).get("detail")
                if isinstance(status_detail, str) and status_detail:
                    status = status_detail

        competitions = event.get("competitions")
        if not isinstance(competitions, list) or not competitions:
            continue
        competition_values = cast(list[object], competitions)
        competition = competition_values[0]
        if not isinstance(competition, dict):
            raise InvalidResponseError("ESPN competition must be a JSON object")
        competitors = cast(dict[object, object], competition).get("competitors")
        if not isinstance(competitors, list):
            raise InvalidResponseError("ESPN competition must contain competitors")

        teams: dict[str, tuple[str, str]] = {}
        for raw_competitor in cast(list[object], competitors):
            if not isinstance(raw_competitor, dict):
                raise InvalidResponseError("ESPN competitor must be a JSON object")
            competitor = cast(dict[object, object], raw_competitor)
            home_away = competitor.get("homeAway")
            team_value = competitor.get("team")
            team_name = "Not available"
            if isinstance(team_value, dict):
                display_name = cast(dict[object, object], team_value).get("displayName")
                if isinstance(display_name, str) and display_name:
                    team_name = display_name
            raw_score = competitor.get("score")
            score = str(raw_score) if isinstance(raw_score, (str, int, float)) else "Not available"
            if isinstance(home_away, str):
                teams[home_away] = (team_name, score)

        home_team, home_score = teams.get("home", ("Not available", "Not available"))
        away_team, away_score = teams.get("away", ("Not available", "Not available"))
        if teams:
            matches.append(Match(
                home_team=home_team,
                away_team=away_team,
                status=status,
                score=f"{home_score} - {away_score}",
            ))

    return matches


def fetch_matches(league: str, constants: Constants) -> list[Match]:
    """Fetch and decode ESPN matches.

    Args:
        league: ESPN league identifier.
        constants: Application constants.

    Returns:
        list[Match]: Decoded matches.

    Raises:
        requests.RequestException: If the HTTP request fails.
        InvalidResponseError: If JSON or its shape is invalid.
    """
    url = build_api_url(league, constants)
    try:
        response = requests.get(
            url,
            headers={"User-Agent": constants["user_agent"]},
            timeout=constants["timeout_seconds"],
        )
        response.raise_for_status()
    except requests.Timeout as exc:
        raise requests.RequestException("Request timed out") from exc
    except requests.RequestException:
        raise

    try:
        data: object = response.json()
    except ValueError as exc:
        raise InvalidResponseError("ESPN returned invalid JSON") from exc
    return extract_matches(data)


def filter_matches(matches: list[Match], team_filter: str) -> list[Match]:
    """Filter matches to those involving one team.

    Args:
        matches: Matches to filter.
        team_filter: Team name or empty string to disable filtering.

    Returns:
        list[Match]: Filtered matches.
    """
    team = team_filter.strip().casefold()
    if not team:
        return matches
    return [
        match
        for match in matches
        if team in (match.home_team.casefold(), match.away_team.casefold())
    ]


def format_match(match: Match) -> str:
    """Format one match for console and report output.

    Args:
        match: Match to format.

    Returns:
        str: Human-readable match text.
    """
    return f"{match.home_team} {match.score} {match.away_team}\nStatus: {match.status}"


def configure_logging(log_path: Path) -> None:
    """Configure file logging for the automation.

    Args:
        log_path: Destination for automation log entries.
    """
    root_logger = logging.getLogger()
    for handler in list(root_logger.handlers):
        handler.close()
        root_logger.removeHandler(handler)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        handlers=[logging.FileHandler(log_path, encoding="utf-8")],
        force=True,
    )


def close_logging() -> None:
    """Close and detach file handlers so log files can be moved or deleted."""
    root_logger = logging.getLogger()
    for handler in list(root_logger.handlers):
        handler.close()
        root_logger.removeHandler(handler)


def parse_args(args: list[str] | None = None) -> argparse.Namespace:
    """Parse command-line overrides.

    Args:
        args: Optional argument list used for testing.

    Returns:
        argparse.Namespace: Parsed arguments.
    """
    parser = argparse.ArgumentParser(description="Monitor football matches through ESPN.")
    parser.add_argument("--league", help="ESPN league identifier, for example eng.1")
    parser.add_argument("--team", help="Only show matches involving this team")
    parser.add_argument("--config", help="Path to configuration JSON")
    return parser.parse_args(args)


def main(args: list[str] | None = None) -> int:
    """Run the football match monitor.

    Args:
        args: Optional command-line argument list.

    Returns:
        int: Zero on success and non-zero on failure.
    """
    parsed = parse_args(args)
    config_path = Path(parsed.config).resolve() if parsed.config else CONFIG_PATH
    configure_logging(LOG_PATH)
    logger = logging.getLogger(__name__)
    logger.info("Script started")

    try:
        config = load_config(config_path)
        constants = load_constants(CONSTANTS_PATH)
    except ConfigurationError as exc:
        logger.error("Could not load configuration: %s", exc)
        print(f"Could not load configuration: {exc}", file=sys.stderr)
        close_logging()
        return 1

    league = parsed.league.strip() if parsed.league and parsed.league.strip() else config["league"]
    team_filter = parsed.team if parsed.team is not None else config["team_filter"]
    logger.info("League selected: %s", league)
    if team_filter:
        logger.info("Team filter selected: %s", team_filter)

    try:
        matches = fetch_matches(league, constants)
    except requests.RequestException as exc:
        logger.error("ESPN request failed: %s", exc)
        print(f"Could not retrieve football data: {exc}", file=sys.stderr)
        close_logging()
        return 1
    except InvalidResponseError as exc:
        logger.error("Could not read ESPN response: %s", exc)
        print(f"Could not read ESPN response: {exc}", file=sys.stderr)
        close_logging()
        return 1

    filtered = filter_matches(matches, team_filter)
    logger.info("Matches processed: %d", len(filtered))

    report_lines = [
        f"Football Match Monitor - League: {league}",
        "",
    ]
    if filtered:
        report_lines.extend(
            [format_match(match) for match in filtered]
        )
    else:
        report_lines.append(
            f"No matches found for team filter: {team_filter}"
            if team_filter
            else "No matches found."
        )
    report = "\n\n".join(report_lines) + "\n"

    report_path = config_path.parent / config["output_file"]
    try:
        report_path.write_text(report, encoding="utf-8")
    except OSError as exc:
        logger.error("Could not create output file %s: %s", report_path, exc)
        print(f"Could not create output file: {exc}", file=sys.stderr)
        close_logging()
        return 1

    logger.info("Output file created: %s", report_path)
    close_logging()
    print(report, end="")
    return 0


if __name__ == "__main__":
    sys.exit(main())
