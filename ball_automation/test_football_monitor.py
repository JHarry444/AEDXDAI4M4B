"""Tests for the football match monitor."""

import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, mock_open, patch

import requests

import football_monitor


def sample_response() -> dict[str, object]:
    """Return a small ESPN-style scoreboard response."""
    return {
        "events": [
            {
                "name": "Celtic at Rangers",
                "status": {"type": {"detail": "Final"}},
                "competitions": [
                    {
                        "competitors": [
                            {
                                "homeAway": "home",
                                "team": {"displayName": "Rangers"},
                                "score": "1",
                            },
                            {
                                "homeAway": "away",
                                "team": {"displayName": "Celtic"},
                                "score": "2",
                            },
                        ]
                    }
                ],
            }
        ]
    }


class FootballMonitorTests(unittest.TestCase):
    """Test suite for configuration, filtering, output and errors."""

    def test_team_filter_is_case_insensitive(self) -> None:
        matches = football_monitor.extract_matches(sample_response())
        filtered = football_monitor.filter_matches(matches, "celtic")
        self.assertEqual(len(filtered), 1)
        self.assertEqual(filtered[0].home_team, "Rangers")
        self.assertEqual(filtered[0].away_team, "Celtic")
        self.assertEqual(filtered[0].score, "1 - 2")

    def test_invalid_team_returns_no_matches(self) -> None:
        matches = football_monitor.extract_matches(sample_response())
        self.assertEqual(football_monitor.filter_matches(matches, "Aberdeen"), [])

    def test_format_match_is_readable(self) -> None:
        match = football_monitor.extract_matches(sample_response())[0]
        self.assertEqual(
            football_monitor.format_match(match),
            "Rangers 1 - 2 Celtic\nStatus: Final",
        )

    def test_scottish_and_english_urls(self) -> None:
        constants = football_monitor.load_constants()
        self.assertEqual(
            football_monitor.build_api_url("sco.1", constants),
            "https://site.api.espn.com/apis/site/v2/sports/soccer/sco.1/scoreboard",
        )
        self.assertEqual(
            football_monitor.build_api_url("eng.1", constants),
            "https://site.api.espn.com/apis/site/v2/sports/soccer/eng.1/scoreboard",
        )

    def test_main_creates_report_and_logs(self) -> None:
        response = Mock()
        response.json.return_value = sample_response()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            config = root / "config.json"
            config.write_text(
                json.dumps({
                    "league": "sco.1",
                    "team_filter": "Celtic",
                    "output_file": "report.txt",
                }),
                encoding="utf-8",
            )
            stdout = io.StringIO()
            stderr = io.StringIO()
            with patch.object(football_monitor.requests, "get", return_value=response), \
                    patch.object(football_monitor, "CONFIG_PATH", config), \
                    patch.object(football_monitor, "LOG_PATH", root / "automation.log"), \
                    contextlib.redirect_stdout(stdout), \
                    contextlib.redirect_stderr(stderr):
                status = football_monitor.main([])

            self.assertEqual(status, 0)
            self.assertEqual(stderr.getvalue(), "")
            self.assertIn("Rangers 1 - 2 Celtic", stdout.getvalue())
            self.assertIn("Rangers 1 - 2 Celtic", (root / "report.txt").read_text(encoding="utf-8"))
            log_text = (root / "automation.log").read_text(encoding="utf-8")
            self.assertIn("Script started", log_text)
            self.assertIn("League selected: sco.1", log_text)
            self.assertIn("Matches processed: 1", log_text)
            self.assertIn("Output file created", log_text)

    def test_missing_config_is_reported(self) -> None:
        stderr = io.StringIO()
        with patch.object(football_monitor, "CONFIG_PATH", Path("missing-config.json")), \
                contextlib.redirect_stderr(stderr):
            status = football_monitor.main([])
        self.assertEqual(status, 1)
        self.assertIn("Could not load configuration", stderr.getvalue())

    def test_missing_config_does_not_call_api(self) -> None:
        with patch.object(football_monitor, "CONFIG_PATH", Path("missing-config.json")), \
                patch.object(football_monitor.requests, "get") as get:
            status = football_monitor.main([])
        self.assertEqual(status, 1)
        get.assert_not_called()

    def test_invalid_json_response_is_reported(self) -> None:
        response = Mock()
        response.json.return_value = {"events": "invalid"}
        stderr = io.StringIO()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            config = root / "config.json"
            config.write_text(
                json.dumps({
                    "league": "eng.1",
                    "team_filter": "Arsenal",
                    "output_file": "report.txt",
                }),
                encoding="utf-8",
            )
            with patch.object(football_monitor.requests, "get", return_value=response), \
                    patch.object(football_monitor, "CONFIG_PATH", config), \
                    patch.object(football_monitor, "LOG_PATH", root / "automation.log"), \
                    contextlib.redirect_stderr(stderr):
                status = football_monitor.main([])
        self.assertEqual(status, 1)
        self.assertIn("Could not read ESPN response", stderr.getvalue())

    def test_request_failure_is_logged_and_reported(self) -> None:
        stderr = io.StringIO()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            config = root / "config.json"
            config.write_text(
                json.dumps({
                    "league": "sco.1",
                    "team_filter": "",
                    "output_file": "report.txt",
                }),
                encoding="utf-8",
            )
            with patch.object(
                football_monitor.requests,
                "get",
                side_effect=requests.Timeout("timed out"),
            ), patch.object(football_monitor, "CONFIG_PATH", config), \
                    patch.object(football_monitor, "LOG_PATH", root / "automation.log"), \
                    contextlib.redirect_stderr(stderr):
                status = football_monitor.main([])
            log_text = (root / "automation.log").read_text(encoding="utf-8")
        self.assertEqual(status, 1)
        self.assertIn("timed out", stderr.getvalue())
        self.assertIn("Request timed out", log_text)


if __name__ == "__main__":
    unittest.main()
