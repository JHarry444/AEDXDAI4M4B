# Football Match Monitor

The Football Match Monitor retrieves football scoreboard data from the ESPN API, optionally filters matches by team, writes a text report, and records activity in `automation.log`.

## Setup

Install Python 3.9 or later and dependencies:

```powershell
cd ball_automation
python -m pip install -r requirements.txt
```

For tests and strict type checking:

```powershell
python -m pip install -r requirements-dev.txt
python -m unittest -v test_football_monitor
python -m mypy --strict football_monitor.py test_football_monitor.py
```

## Run

Run with the settings in `config.json`:

```powershell
python football_monitor.py
```

Override the league or team without editing configuration:

```powershell
python football_monitor.py --league eng.1 --team Arsenal
```

Use an alternate configuration file:

```powershell
python football_monitor.py --config C:\path\to\config.json
```

## Configuration

`config.json` contains:

- `league`: ESPN league identifier. Examples include `sco.1` for the Scottish Premiership and `eng.1` for the English Premier League.
- `team_filter`: Team name to include. An empty string disables team filtering.
- `output_file`: Report filename. It must be relative to the configuration file directory.

`constants.json` contains the ESPN API base URL, HTTP user agent, request timeout, missing-value text and log filename.

## Inputs and outputs

Inputs are the JSON configuration, optional command-line overrides, and live ESPN scoreboard JSON.

Outputs are:

- Console match report.
- `football_report.txt` or another configured report file.
- `automation.log`, containing startup, league, match count, report creation and error entries.

## Match processing

The application extracts home team, away team, score and match status from ESPN events. It applies a case-insensitive team filter when `team_filter` is not empty.

## Error handling

Missing or malformed configuration, network and HTTP failures, invalid JSON and unexpected ESPN response structures are reported on standard error and logged. Failures return a non-zero process status.

## Testing

The unit suite uses mocked ESPN responses and filesystem paths to test URL selection, team filtering, report generation, logging, invalid responses and missing configuration.

## Known limitations

- ESPN scoreboard data is schedule-dependent, so a selected team or league may legitimately produce no matches.
- The default endpoint does not require an API key but may be unavailable or change without notice.
- The automation retrieves the current ESPN scoreboard rather than historical or future date ranges.
- Team matching compares ESPN display names exactly and case-insensitively.
- The report is plain text.
