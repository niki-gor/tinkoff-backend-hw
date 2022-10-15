PYTHONPATH = PYTHONPATH=./

.PHONY: test
test: # Runs pytest
	$(PYTHONPATH) pytest tests/*

.PHONY: lint
lint: # Lint code
	flake8 --exclude tests/ .
	mypy .
	black --line-length 79 --skip-string-normalization --check .

.PHONY: check
check: lint test