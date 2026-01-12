.PHONY: install lint ruff-check black-check isort-check type-check check \
        ruff-format black-format isort-format format test requirements help

PIP=pip
RUFF=ruff
BLACK=black
ISORT=isort
MYPY=mypy
PYTEST=pytest
MAKE = make

install:
	# pip 25.3 does not work with pip-compile
	python.exe -m $(PIP) install pip==25.2
	$(PIP) install -r requirements.txt
	$(PIP) install ruff black isort mypy pytest pip-tools ipykernel
	$(MYPY) --install-types

lint:
	$(RUFF) check --preview .

ruff-check:
	$(RUFF) format --check --diff .

black-check:
	$(BLACK) --check --diff .

isort-check:
	$(ISORT) --check --diff .

type-check:
	$(MYPY) .

check:
	-@echo "=== Ruff lint ==="
	-@$(RUFF) check --preview .
	-@echo "=== Ruff format (dry run) ==="
	-@$(RUFF) format --check --diff .
	-@echo "=== Black (dry run) ==="
	-@$(BLACK) --check --diff .
	-@echo "=== isort (dry run) ==="
	-@$(ISORT) --check --diff .
	-@echo "=== mypy type check ==="
	-@$(MYPY) .
	-@echo "=== End ==="

ruff-format:
	$(RUFF) format .

black-format:
	$(BLACK) .

isort-format:
	$(ISORT) .

format:
	-$(MAKE) ruff-format
	-$(MAKE) black-format
	-$(MAKE) isort-format

test:
	$(PYTEST)

requirements:
	pip-compile --all-extras pyproject.toml

help:
	@echo "Usage: make <target>"
	@echo "Available targets :"
	@echo "  install        Install libraries for dev"
	@echo "  lint           Lint with Ruff"
	@echo "  ruff-check     Check for Ruff formatting"
	@echo "  black-check    Check for Black formatting"
	@echo "  isort-check    Check for isort"
	@echo "  type-check     Type-check with mypy"
	@echo "  check          All checks (lint + format-check + type-check)"
	@echo "  ruff-format    Format with Ruff"
	@echo "  black-format   Format with Black"
	@echo "  isort-format   Format with isort"
	@echo "  format         All formatting (ruff + black + isort)"
	@echo "  test           Run all tests"
	@echo "  requirements   Compile requirements"
	@echo "  help           Show this help"
