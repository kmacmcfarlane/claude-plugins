# Development Reference

## Adding a New Tool

1. Create a directory with the tool's Python script (e.g., `my_tool/my_tool.py`)
2. Add a shell wrapper in `bin/` following the existing pattern
3. If the tool has pip dependencies, add a `requirements.txt` and use venv management in the wrapper

### Shell Wrapper Pattern

See `bin/token_count.sh` for the reference implementation of venv management with hash-based dependency tracking. The wrapper:

1. Resolves the script directory
2. Creates/updates a `.venv` if `requirements.txt` has changed (tracked via hash)
3. Activates the venv
4. Invokes the Python script with all passed arguments

### Venv Management

- `token_count.sh` uses hash-based dependency tracking: it hashes `requirements.txt` and only reinstalls when the hash changes
- `llm_fetch` wrapper also manages its own venv
- Each tool's venv is independent (no shared venv)

## Project Conventions

### CLI Design

- Use `argparse` for argument parsing
- Provide both long flags (`--model`, `--input-dir`) and short flags where applicable
- Error output goes to `stderr`; normal output to `stdout`
- Exit code 0 for success, 1 for errors

### Security

- Subprocesses use list-based args (no `shell=True`) to avoid command injection
- Config files containing sensitive paths are gitignored

### Configuration

- Config files use YAML format
- Provide example config files (e.g., `llm_fetch.example.yaml`) as templates
- Actual config files are gitignored

### File Safety

- caption_util creates backup files automatically before overwriting

## Build / Test / Lint

No build step, test framework, or linter is configured. Tools are run directly as scripts.

## Dependencies

- Python 3.8+
- Per-tool dependencies managed independently via `requirements.txt` files
- No global requirements file (each tool is self-contained)

## Committing

- Do not include "co-authored by claude" messages when committing code
