.PHONY: test
test:
	python -m unittest

.PHONY: lint
lint: # Lint code
	flake8 --exclude tests/test_text_history.py .
	mypy .
	black --line-length 79 --skip-string-normalization --check --exclude tests .

.PHONY: check
check: lint test