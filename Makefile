.PHONY: help install dev test run migrate lint format clean

help:
	@echo "Available commands:"
	@echo "  install    Install project dependencies"
	@echo "  dev        Setup development environment"
	@echo "  test       Run tests"
	@echo "  run        Run development server"
	@echo "  migrate    Run database migrations"
	@echo "  lint       Run linting"
	@echo "  format     Format code"
	@echo "  clean      Clean up temporary files"

install:
	pip install -r requirements.txt

dev:
	pip install -r requirements-dev.txt
	pre-commit install

test:
	pytest

run:
	python lms_platform/manage.py runserver

migrate:
	python lms_platform/manage.py makemigrations
	python lms_platform/manage.py migrate

lint:
	flake8 lms_platform/
	mypy lms_platform/

format:
	black lms_platform/
	isort lms_platform/

clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf htmlcov/
