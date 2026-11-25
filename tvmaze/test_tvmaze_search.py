"""Tests for tvmaze_search module."""

import contextlib
import io
import json
import unittest
from typing import Union
from unittest.mock import AsyncMock, MagicMock, Mock, mock_open, patch

import requests

if __package__:
    from . import tvmaze_search
else:
    import tvmaze_search


class SearchTests(unittest.TestCase):
    """Test suite for TVMaze search functionality."""

    def run_main(
        self, args: list[str], response: Mock
    ) -> tuple[int, str, str, Union[MagicMock, AsyncMock]]:
        """Run main() with mocked arguments and requests.

        Args:
            args: Command-line arguments (without program name).
            response: Mocked requests.Response object.

        Returns:
            tuple: (exit_code, stdout, stderr, mock_get_call)
        """
        stdout, stderr = io.StringIO(), io.StringIO()
        with patch("sys.argv", ["tvmaze_search.py", *args]), \
                patch.object(tvmaze_search.requests, "get", return_value=response) as get, \
                contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            status = tvmaze_search.main()
        return status, stdout.getvalue(), stderr.getvalue(), get

    def test_multiple_matches_and_missing_values(self) -> None:
        """Test formatting multiple results with missing values."""
        response = Mock()
        response.json.return_value = [
            {"score": 1.0, "show": {"name": "First", "genres": ["Drama", "Crime"],
                                     "rating": {"average": 8.5}}},
            {"score": 0.5, "show": {"name": "Second", "genres": [],
                                     "rating": {"average": None}}},
        ]
        status, stdout, stderr, get = self.run_main(["some", "show"], response)
        self.assertEqual(status, 0)
        self.assertEqual(stderr, "")
        self.assertIn("Show: First\nGenres: Drama, Crime\nRating: 8.5/10", stdout)
        self.assertIn("Show: Second\nGenres: Not available\nRating: Not available", stdout)
        self.assertLess(stdout.index("First"), stdout.index("Second"))
        self.assertIn("https://www.tvmaze.com/", stdout)
        self.assertEqual(get.call_args.kwargs["params"], {"q": "some show"})
        self.assertEqual(get.call_args.kwargs["timeout"], 10)

    def test_no_matches(self) -> None:
        """Test handling of empty search results."""
        response = Mock()
        response.json.return_value = []
        status, stdout, stderr, _ = self.run_main(["no-match"], response)
        self.assertEqual(status, 0)
        self.assertIn("No shows found for: no-match", stdout)
        self.assertEqual(stderr, "")

    def test_http_failure_is_reported(self) -> None:
        """Test HTTP errors are caught and reported."""
        response = Mock()
        response.raise_for_status.side_effect = requests.HTTPError("429 Too Many Requests")
        status, stdout, stderr, _ = self.run_main(["test"], response)
        self.assertEqual(status, 1)
        self.assertEqual(stdout, "")
        self.assertIn("429 Too Many Requests", stderr)

    def test_connection_failure_is_reported(self) -> None:
        """Test connection timeouts are caught and reported."""
        stdout, stderr = io.StringIO(), io.StringIO()
        with patch("sys.argv", ["tvmaze_search.py", "test"]), \
                patch.object(tvmaze_search.requests, "get", side_effect=requests.Timeout("timed out")), \
                contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            status = tvmaze_search.main()
        self.assertEqual(status, 1)
        self.assertEqual(stdout.getvalue(), "")
        self.assertIn("timed out", stderr.getvalue())

    def test_missing_rating_and_zero_rating(self) -> None:
        """Test handling of missing and zero ratings."""
        constants = tvmaze_search.load_constants()
        self.assertIn("Rating: Not available", tvmaze_search.format_show(
            {"show": {"name": "Unrated"}}, constants))
        self.assertIn("Rating: 0/10", tvmaze_search.format_show(
            {"show": {"name": "Rated", "rating": {"average": 0}}}, constants))

    def test_invalid_json_and_response_shape_are_reported(self) -> None:
        """Test various invalid response formats are caught and reported."""
        for value in (ValueError("bad JSON"), {"show": "not a list"},
                      [{"show": {"name": "Broken", "genres": "Drama"}}],
                      [{"show": {"name": "Broken", "genres": ["Drama", 42]}}],
                      [{"show": {"name": "Broken", "rating": "high"}}]):
            with self.subTest(value=value):
                response = Mock()
                if isinstance(value, ValueError):
                    response.json.side_effect = value
                else:
                    response.json.return_value = value
                status, stdout, stderr, _ = self.run_main(["test"], response)
                self.assertEqual(status, 1)
                self.assertEqual(stdout, "")
                self.assertIn("Could not read the TVMaze response", stderr)

    def test_constants_from_json_are_used(self) -> None:
        """Test that custom constants are loaded and used correctly."""
        constants = {
            "api_url": "https://example.test/search",
            "user_agent": "TestApp/1.0",
            "timeout_seconds": 3,
            "source_url": "https://example.test/",
            "missing_value": "Unavailable",
            "rating_max": 20,
        }
        response = Mock()
        response.json.return_value = [{"show": {"name": "Example"}}]
        with patch("pathlib.Path.open", mock_open(read_data=json.dumps(constants))):
            status, stdout, stderr, get = self.run_main(["example"], response)
        self.assertEqual(status, 0)
        self.assertEqual(stderr, "")
        self.assertIn("Genres: Unavailable\nRating: Unavailable", stdout)
        self.assertIn("Data provided by TVMaze: https://example.test/", stdout)
        self.assertEqual(get.call_args.args[0], constants["api_url"])
        self.assertEqual(get.call_args.kwargs["headers"]["User-Agent"], "TestApp/1.0")
        self.assertEqual(get.call_args.kwargs["timeout"], 3)
        with patch("pathlib.Path.open", mock_open(read_data=json.dumps(constants))):
            self.assertIn("Rating: 8/20", tvmaze_search.format_show(
                {"show": {"name": "Rated", "rating": {"average": 8}}},
                tvmaze_search.load_constants()))

    def test_invalid_or_missing_constants_are_reported(self) -> None:
        """Test that invalid or missing constants are reported as errors."""
        invalid_timeout = {
            "api_url": "https://example.test/search", "user_agent": "TestApp/1.0",
            "timeout_seconds": -1, "source_url": "https://example.test/",
            "missing_value": "Unavailable", "rating_max": 10,
        }
        for contents in ("not json", "{}", json.dumps(invalid_timeout)):
            with self.subTest(contents=contents):
                response = Mock()
                with patch("pathlib.Path.open", mock_open(read_data=contents)):
                    status, stdout, stderr, get = self.run_main(["test"], response)
                self.assertEqual(status, 1)
                self.assertEqual(stdout, "")
                self.assertIn("Could not load application constants", stderr)
                get.assert_not_called()
        with patch("pathlib.Path.open", side_effect=FileNotFoundError("missing file")):
            status, stdout, stderr, get = self.run_main(["test"], Mock())
        self.assertEqual(status, 1)
        self.assertEqual(stdout, "")
        self.assertIn("Could not load application constants", stderr)
        get.assert_not_called()


if __name__ == "__main__":
    unittest.main()
