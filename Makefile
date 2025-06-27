#!/usr/bin/make -f

DOCKER_COMPOSE_DEV = docker compose
DOCKER_COMPOSE_CI = docker compose -f docker-compose.yml
DOCKER_COMPOSE = $(DOCKER_COMPOSE_DEV)

VENV = venv
PIP = $(VENV)/bin/pip
PYTHON = $(VENV)/bin/python

PYTEST_WATCH_MODULES = tests/unit_test

NUMBER_OF_DAYS = 1
NUMBER_OF_MONTHS = 1

venv-clean:
	@if [ -d "$(VENV)" ]; then \
		rm -rf "$(VENV)"; \
	fi

venv-create:
	python3 -m venv $(VENV)

dev-install:
	$(PIP) install --disable-pip-version-check -r requirements.build.txt
	$(PIP) install --disable-pip-version-check \
		-r requirements.txt \
		-r requirements.dev.txt

dev-venv: venv-create dev-install


dev-flake8:
	$(PYTHON) -m flake8 data_hub_metrics_api tests

dev-pylint:
	$(PYTHON) -m pylint data_hub_metrics_api tests

dev-mypy:
	$(PYTHON) -m mypy --check-untyped-defs data_hub_metrics_api tests

dev-lint: dev-flake8 dev-pylint dev-mypy

dev-unittest:
	$(PYTHON) -m pytest -p no:cacheprovider -vv $(ARGS) tests/unit_test

dev-test: dev-lint dev-unittest

dev-watch:
	$(PYTHON) -m pytest_watcher \
		--runner=$(VENV)/bin/python \
		. \
		-m pytest -vv $(PYTEST_WATCH_MODULES)


dev-start:
	$(PYTHON) -m uvicorn \
		data_hub_metrics_api.main:create_app \
		--reload \
		--factory \
		--host 127.0.0.1 \
		--port 8000 \
		--log-config=config/logging.yaml


dev-refresh-citations:
	$(PYTHON) -m data_hub_metrics_api.refresh_data.citations_cli

dev-refresh-page-views:
	$(PYTHON) -m data_hub_metrics_api.refresh_data.page_views_cli \
		--number-of-days=$(NUMBER_OF_DAYS)

dev-refresh-page-views-monthy:
	$(PYTHON) -m data_hub_metrics_api.refresh_data.page_views_monthly_cli \
		--number-of-months=$(NUMBER_OF_MONTHS)

dev-refresh-page-view-and-download-totals:
	$(PYTHON) -m data_hub_metrics_api.refresh_data.page_view_and_download_totals_cli


build:
	$(DOCKER_COMPOSE) build data-hub-metrics-api

build-dev:
	$(DOCKER_COMPOSE) build data-hub-metrics-api-dev

flake8:
	$(DOCKER_COMPOSE) run --rm data-hub-metrics-api-dev \
		python -m flake8 data_hub_metrics_api tests

pylint:
	$(DOCKER_COMPOSE) run --rm data-hub-metrics-api-dev \
		python -m pylint data_hub_metrics_api tests

mypy:
	$(DOCKER_COMPOSE) run --rm data-hub-metrics-api-dev \
		python -m mypy --check-untyped-defs data_hub_metrics_api tests

lint: flake8 pylint mypy

pytest:
	$(DOCKER_COMPOSE) run --rm data-hub-metrics-api-dev \
		python -m pytest data_hub_metrics_api tests

test: lint pytest


start:
	$(DOCKER_COMPOSE) up -d data-hub-metrics-api

stop:
	$(DOCKER_COMPOSE) down

logs:
	$(DOCKER_COMPOSE) logs -f


start-redis:
	$(DOCKER_COMPOSE) up -d redis

stop-redis:
	$(DOCKER_COMPOSE) down redis


ci-build:
	$(MAKE) DOCKER_COMPOSE="$(DOCKER_COMPOSE_CI)" build

ci-build-dev:
	$(MAKE) DOCKER_COMPOSE="$(DOCKER_COMPOSE_CI)" build-dev

ci-lint:
	$(MAKE) DOCKER_COMPOSE="$(DOCKER_COMPOSE_CI)" lint

ci-unittest:
	$(MAKE) DOCKER_COMPOSE="$(DOCKER_COMPOSE_CI)" pytest
