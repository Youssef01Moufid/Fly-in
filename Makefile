PYTHON := python3
PIP := pip3
MAIN := fly-in.py
MAP := map.txt
CAP_INFO := --capacity-info
VENV := venv

.PHONY: install run debug clean lint lint-strict

install:
	$(PIP) install --break-system-packages -r requirements.txt

run:
	$(PYTHON) $(MAIN) $(MAP)

debug:
	$(PYTHON) -m pdb $(MAIN)

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	rm -rf .mypy_cache
	rm -rf .pytest_cache
	rm -rf $(VENV)

lint:
	flake8 .
	mypy . --warn-return-any --warn-unused-ignores \
		--ignore-missing-imports --disallow-untyped-defs \
		--check-untyped-defs

lint-strict:
	flake8 .
	mypy . --strict
