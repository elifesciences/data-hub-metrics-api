# Data Hub Metrics API

Provides an API similar to `elife-metrics` but powered by Data Hub.

## Development Using Virtual Environment

### Pre-requisites (Virtual Environment)

* Python, ideally using `pyenv` (see `.python-version`)
* Docker to run Redis

### First Setup (Virtual Environment)

```bash
make dev-venv
```

### Update Dependencies (Virtual Environment)

```bash
make dev-install
```

### Run Tests (Virtual Environment)

```bash
make dev-test
```

### Start Server Redis Only (using Docker)

```bash
make start-redis
```

The server will be available on port 6379.

### Start Server (Virtual Environment)

This will require redis to be available on `localhost` (port `6379`).

```bash
make dev-start
```

The server will be available on port 8000.

You can access the API Docs via [/docs](http://localhost:8000/docs)

### Refresh Data (Virtual Environment)

This will require redis to be available on `localhost` (port `6379`).

```bash
make dev-refresh-data
```

This will load data from BigQuery into Redis.

## Development Using Docker

### Pre-requisites (Docker)

* Docker

### Run Tests (Docker)

```bash
make build-dev test
```

### Start Server (Docker)

```bash
make build start logs
```

The server will be available on port 8000.

You can access the API Docs via [/docs](http://localhost:8000/docs)

### Stop Server (Docker)

```bash
make stop
```
