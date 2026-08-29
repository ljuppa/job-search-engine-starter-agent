.PHONY: setup dev stop test eval lint migrate seed clean

setup:
	docker compose build

# Starts local dependencies/services. Application containers are scaffolds until implementation lands.
dev:
	docker compose up -d

stop:
	docker compose down

test:
	docker compose run --rm backend pytest -q

eval:
	docker compose run --rm backend python -m evals.runner

lint:
	docker compose run --rm backend ruff check .

migrate:
	docker compose run --rm backend alembic upgrade head

seed:
	@echo "Seed command will be implemented with persistence milestone."

clean:
	docker compose down -v --remove-orphans
