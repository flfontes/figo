[group: 'Ruff']
check:
    ruff check --select I --fix


[group: 'Ruff']
format: check
    ruff format


[group: 'Test']
test: check format
    uv run python -m pytest
