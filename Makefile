UV := uv

HOST ?= 0.0.0.0
PORT ?= 8000

PY_SRC := src

dev:
	$(UV) run uvicorn main:app --reload --host $(HOST) --port $(PORT)


migrate:
	$(UV) run alembic upgrade head

rev:
	$(UV) run alembic revision --autogenerate -m "$(msg)"

format:
	$(UV) run ruff check $(PY_SRC) --select I --fix
	$(UV) run black $(PY_SRC)

lint:
	$(UV) run ruff check $(PY_SRC)

lint-fix:
	$(UV) run ruff check $(PY_SRC) --fix

typecheck:
	$(UV) run mypy $(PY_SRC)


help:
	@echo "make dev                 - run API with reload (uvicorn --reload)"
	@echo "make rev msg=\"message\" - alembic revision --autogenerate -m \"message\""
	@echo "make migrate             - alembic upgrade head"
	@echo "make format              - run ruff import sort + black"
	@echo "make lint                - run ruff check"
	@echo "make lint-fix             - run ruff check --fix"
	@echo "make typecheck           - run mypy"
