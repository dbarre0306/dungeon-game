# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project state

This is a freshly scaffolded `uv`-managed Python project (`src/dungeon_game/`) with a single
placeholder entry point. The `.env` file provisions API keys for OpenAI, Anthropic, Google, and
LangSmith, indicating the intended direction is an LLM-driven ("agentic AI") dungeon game, but no
game or agent logic has been implemented yet. There is no existing architecture to preserve —
treat early additions as establishing the project's structure rather than fitting into one.

## Commands

This project uses `uv` for dependency management and packaging (Python >=3.13, src layout).

- Install/sync dependencies: `uv sync`
- Run the CLI entry point: `uv run dungeon-game`
- Run all tests: `uv run pytest`
- Run a single test: `uv run pytest tests/test_main.py::test_main_runs`
- Lint: `uv run ruff check .`
- Format: `uv run ruff format .`

## Code style

Ruff is configured in `pyproject.toml` with `line-length = 100` and lint rules `E, F, I, UP, B`
(pycodestyle, pyflakes, isort, pyupgrade, bugbear). Keep new code compatible with these.

## Structure

- `src/dungeon_game/` — the package; `main()` in `__init__.py` is registered as the
  `dungeon-game` console script in `pyproject.toml`.
- `tests/` — pytest tests (`testpaths = ["tests"]`), mirroring the package layout.
