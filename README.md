# Data Hub Metrics API

Provides an API similar to `elife-metrics` but powered by Data Hub.

## Development Using Virtual Environment

### Pre-requisites (Virtual Environment)

* Python, ideally using `pyenv` (see `.python-version`)

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

### Start Server (Virtual Environment)

```bash
make dev-start
```

The server will be available on port 8000.

You can access the API Docs via [/docs](http://localhost:8000/docs)

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
