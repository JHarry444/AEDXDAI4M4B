# Development instructions

## Core Development Practices

- Build all applications in Python.
- Use test-driven development: write a failing test before implementing each behavior, then make it pass and refactor.
- Extract all application constants into a JSON file and load them from there.

## Type Checking

- Implement strict type checking using pylance.
- Configure the Python language server to enforce strict type checking.
- Ensure that all type hints are accurate and complete throughout the codebase.
- Use mypy or a similar tool to verify type correctness as part of the development workflow.
- Treat all type checking warnings and errors as blockers that must be resolved before merging code.
- Regularly review and update type hints to reflect any changes in the codebase.
- Ensure that all new code includes appropriate type annotations from the outset.

## Error Handling

- Use try-except blocks to handle expected errors gracefully.
- Raise specific exception types (avoid bare `except` clauses).
- Include meaningful error messages that describe what went wrong and suggest remediation.
- Never silently ignore exceptions—log them or propagate them up the call stack.
- Handle external service failures (API calls, file I/O) with appropriate retry logic and fallbacks where applicable.

## Logging

- Use the `logging` module for all log output; never use `print()` for operational logs.
- Configure logging with appropriate log levels: DEBUG, INFO, WARNING, ERROR, and CRITICAL.
- Log at INFO level for significant events (application start, major operations).
- Log at WARNING level for recoverable issues (retries, degraded behavior).
- Log at ERROR level for failures that need attention.
- Include contextual information in log messages (function names, parameters, state) to aid debugging.
- Ensure sensitive data (passwords, API keys, tokens) is never logged.

## Documentation

- Write docstrings for all modules, classes, and functions using the Google or NumPy docstring format.
- Docstrings must include a one-line summary, description, arguments, return values, and raised exceptions (where applicable).
- Keep README files up-to-date with setup instructions, usage examples, and project overview.
- Document any configuration requirements or environment variables needed to run the application.
- Include inline comments for complex logic or non-obvious decisions, but prefer clear code over heavy commenting.
- Document external dependencies and their purpose in `requirements.txt` or equivalent.
