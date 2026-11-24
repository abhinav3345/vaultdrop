PORT ?= 3000
TEST_DATABASE_PORT ?= 55433

.PHONY: install db test dev run down build clean

install:
	uv sync

db:
	docker compose up -d --wait db

test:
	TEST_DATABASE_PORT=$(TEST_DATABASE_PORT) docker compose up -d --wait test-db
	TEST_DATABASE_URL=postgresql://postgres:postgres@127.0.0.1:$(TEST_DATABASE_PORT)/vaultdrop_test uv run --locked pytest -v

dev:
	uv run uvicorn src.main:app --port $(PORT)

build:
	docker compose build

run:
	docker compose up --build

down:
	docker compose down

clean:
	find . -name '*.un~' -delete
	find . -name '__pycache__' -type d -exec rm -rf {} +
	rm -rf .pytest_cache
