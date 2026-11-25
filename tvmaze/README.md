# TVMaze show search

Search for television programmes by name and display the name, genres and average rating of each match.

## Setup and usage

Run the following commands from the `tvmaze` directory:

```powershell
cd tvmaze
```

Install Python 3.9 or later and the dependency:

```powershell
python -m pip install -r requirements.txt
```

Run a search (no API key is needed):

```powershell
python tvmaze_search.py "Breaking Bad"
```

Matches are displayed in TVMaze's relevance order. Missing genres or ratings appear as `Not available`. Network, HTTP and response-format errors are reported on standard error; a failed request exits with a nonzero status. TVMaze may return HTTP 429 when rate-limited; wait and try again.

The application loads its constants from `constants.json` beside the script, regardless of the current working directory. Keep this file with the script. It contains the API URL, user agent, request timeout, attribution URL, missing-value text and rating scale. A missing or invalid file is reported as an error.

## Sample output

The following is an example of a live search; results and ratings can change.

```text
Show: Breaking Bad
Genres: Drama, Crime, Thriller
Rating: 9.2/10

Show: Breaking Bad: Original Minisodes
Genres: Comedy, Crime
Rating: 7/10

Show: Talking Bad
Genres: Not available
Rating: Not available

Show: Breaking Band
Genres: Music
Rating: Not available

Show: Breaking the Band
Genres: Not available
Rating: Not available

Show: Bradley Walsh & Son: Breaking Dad
Genres: Adventure, Travel
Rating: 5.2/10

Show: Breaking Dad: Britain's Unlikeliest Drug Dealer
Genres: Crime
Rating: Not available

Show: Baking Mad with Eric Lanlard
Genres: Food
Rating: Not available

Data provided by TVMaze: https://www.tvmaze.com/
```

## JSON structure (AI-written explanation)

The [TVMaze show search endpoint](https://www.tvmaze.com/api#show-search) returns a JSON array, which `requests` converts into a Python list of dictionaries. Each item contains a search relevance `score` and a nested `show` object. For example, with unrelated fields omitted:

```json
[
  {
    "score": 1.19,
    "show": {
      "name": "Breaking Bad",
      "genres": ["Drama", "Crime", "Thriller"],
      "rating": {"average": 9.2}
    }
  }
]
```

`name` is a string, `genres` is a list of strings, and `rating.average` is a number out of 10 or `null` when unavailable. The search `score` measures relevance, not the show's rating. An empty array means no shows matched. The actual response contains additional show information.

## Tests

```powershell
python -m unittest -v test_tvmaze_search
```

From the workspace root, run `python -m unittest -v tvmaze.test_tvmaze_search` instead. Workspace-wide discovery also finds these tests.

## Type checking

Install the development dependencies from the `tvmaze` directory:

```powershell
python -m pip install -r requirements-dev.txt
```

Run the strict workspace check from the workspace root:

```powershell
python -m pyright --warnings
```

The shared Pyright configuration checks against Python 3.9 and enables strict analysis. VS Code is also configured to use strict Pylance checking. The `--warnings` option makes warnings, as well as errors, fail the check.

Data provided by [TVMaze](https://www.tvmaze.com/). Its [API documentation](https://www.tvmaze.com/api#licensing) describes the CC BY-SA licensing and attribution requirements.
