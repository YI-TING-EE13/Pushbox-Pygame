# Development Guide

## Prerequisites

- Python 3.9+
- `uv` installed (recommended)
- A desktop environment for running Pygame

## Install Dependencies

```bash
uv sync
uv sync --extra dev
```

Fallback (if `uv` is not available):

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -e ".[dev]"
```

## Run the Game

```bash
uv run python main.py
```

## Tests

```bash
uv run pytest
```

## Lint and Format

```bash
uv run ruff check .
uv run ruff format .
```

## Type Check

```bash
uv run mypy src/
```

## Suggested Workflow

1. Sync dependencies with `uv sync`
2. Run the game to reproduce or validate changes
3. Update or add tests as needed
4. Run `ruff` and `mypy` before opening a PR

## Runtime Data and Caches

- Runtime progress files are stored in `data/progress.json` and `data/scores.json`
- These files are gitignored; example formats live in `examples/`
- Local caches are stored in `.pytest_cache/`, `.ruff_cache/`, and `.mypy_cache/`
- Local environments live in `.venv/`

## Troubleshooting

- If Pygame fails to initialize, verify you have a desktop session
- If `uv sync` fails, use the fallback pip install steps above
