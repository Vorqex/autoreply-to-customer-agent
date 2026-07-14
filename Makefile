.PHONY: install dev build up down logs test lint migrate clean

# ─── Installation ──────────────────────────────────────────────────────────────

install: install-backend install-frontend

install-backend:
	cd backend && python -m venv venv && \
		venv\Scripts\pip install -r requirements.txt

install-frontend:
	cd frontend && npm ci

# ─── Development ──────────────────────────────────────────────────────────────

dev:
	@echo "Starting backend and frontend for development..."
	@cd backend && start "" cmd /c "venv\Scripts\python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
	@cd frontend && start "" cmd /c "npm run dev"

# ─── Docker ────────────────────────────────────────────────────────────────────

build:
	docker compose -f docker-compose.yml build

up:
	docker compose -f docker-compose.yml up -d

down:
	docker compose -f docker-compose.yml down

logs:
	docker compose -f docker-compose.yml logs -f

# ─── Testing ──────────────────────────────────────────────────────────────────

test: test-backend test-frontend

test-backend:
	cd backend && venv\Scripts\pytest --verbose --cov=. --cov-report=term

test-frontend:
	cd frontend && npm test

# ─── Linting ──────────────────────────────────────────────────────────────────

lint: lint-backend lint-frontend

lint-backend:
	cd backend && venv\Scripts\black --check . && \
		venv\Scripts\flake8 . --max-line-length=100 --ignore=E203,W503 && \
		venv\Scripts\mypy . --ignore-missing-imports

lint-frontend:
	cd frontend && npm run lint

# ─── Database ─────────────────────────────────────────────────────────────────

migrate:
	cd backend && venv\Scripts\alembic upgrade head

# ─── Cleanup ──────────────────────────────────────────────────────────────────

clean:
	@echo "Cleaning up..."
	@if exist backend\__pycache__ rmdir /s /q backend\__pycache__
	@if exist backend\*.pyc del /s /q backend\*.pyc
	@if exist backend\.pytest_cache rmdir /s /q backend\.pytest_cache
	@if exist backend\.coverage del /q backend\.coverage
	@if exist backend\htmlcov rmdir /s /q backend\htmlcov
	@if exist frontend\node_modules rmdir /s /q frontend\node_modules
	@if exist frontend\.next rmdir /s /q frontend\.next
	@if exist .venv rmdir /s /q .venv
	@if exist *.log del /q *.log
	@echo "Clean complete."
