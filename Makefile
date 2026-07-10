PYTHON = python3
PIP = pip3

MAIN = fly-in.py
MAP = map.txt
ARGS = 

.PHONY: install run debug clean lint lint-strict

install:
	$(PIP) install -r requirements.txt

run:
	$(PYTHON) $(MAIN) $(ARGS) $(MAP)

debug:
	$(PYTHON) -m pdb $(MAIN) $(ARGS) $(MAP)

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	rm -rf .mypy_cache
	rm -rf .pytest_cache

lint:
	flake8 .
	mypy . \
		--warn-return-any \
		--warn-unused-ignores \
		--disallow-untyped-defs \
		--check-untyped-defs

lint-strict:
	mypy . --strict