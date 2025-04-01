FROM python:3.12-slim

COPY requirements.build.txt ./
RUN pip install --disable-pip-version-check \
    -r requirements.build.txt

COPY requirements.txt ./
RUN pip install --disable-pip-version-check \
    -r requirements.txt

COPY requirements.dev.txt ./
ARG install_dev=n
RUN if [ "${install_dev}" = "y" ]; then \
    pip install --disable-pip-version-check --user \
        -r requirements.txt \
        -r requirements.dev.txt; \
    fi

COPY data_hub_metrics_api ./data_hub_metrics_api
COPY static ./static
COPY config ./config

COPY tests ./tests
COPY .flake8 .pylintrc pyproject.toml ./

CMD ["python3", "-m", "uvicorn", "data_hub_metrics_api.main:create_app", "--factory", "--host", "0.0.0.0", "--port", "8000", "--log-config=config/logging.yaml"]
