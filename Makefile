.PHONY: help install dev up down logs test clean migrate format lint

help:
	@echo "GTM Asset Generator - Make Commands"
	@echo ""
	@echo "install     - Install dependencies"
	@echo "dev         - Start development environment"
	@echo "up          - Start all services"
	@echo "down        - Stop all services"
	@echo "logs        - View logs"
	@echo "test        - Run tests"
	@echo "clean       - Clean up containers and volumes"
	@echo "migrate     - Run database migrations"
	@echo "format      - Format code with black"
	@echo "lint        - Run linters"

install:
	pip install -r requirements.txt

dev:
	docker-compose up -d
	@echo "API: http://localhost:8000"
	@echo "Docs: http://localhost:8000/docs"
	@echo "Flower: http://localhost:5555"

up:
	docker-compose up -d

down:
	docker-compose down

logs:
	docker-compose logs -f

test:
	docker-compose exec api pytest

clean:
	docker-compose down -v
	rm -rf __pycache__ .pytest_cache .coverage htmlcov

migrate:
	docker-compose exec api alembic upgrade head

format:
	docker-compose exec api black app/

lint:
	docker-compose exec api flake8 app/
	docker-compose exec api mypy app/

shell:
	docker-compose exec api bash

db-shell:
	docker-compose exec db psql -U gtmuser -d gtm_assets
