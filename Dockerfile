###############################################
# Base Image
###############################################
FROM python:3.11-slim-bullseye AS python-base

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    POETRY_VERSION=1.6.1 \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1 \
    PYSETUP_PATH="/opt/pysetup" \
    VENV_PATH="/opt/pysetup/.venv"

# prepend poetry and venv to path
ENV PATH="$POETRY_HOME/bin:$VENV_PATH/bin:$PATH"

# Install dependencies for poetry and build
RUN apt-get update && apt-get install --no-install-recommends -y \
    curl \
    build-essential \
    git \
    && apt-get clean

# Install poetry
RUN curl -sSL https://install.python-poetry.org | python3 -

###############################################
# Builder Image
###############################################
FROM python-base AS builder-base

# copy project requirement files here to ensure they will be cached.
WORKDIR $PYSETUP_PATH
COPY poetry.lock pyproject.toml ./

# install runtime deps - uses $POETRY_VIRTUALENVS_IN_PROJECT internally
RUN poetry install --no-root

###############################################
# Production Image
###############################################
FROM python-base AS production
COPY --from=builder-base $PYSETUP_PATH $PYSETUP_PATH

# Copy project files
ENV PROJECT_DIR /app
WORKDIR ${PROJECT_DIR}
COPY . ${PROJECT_DIR}/

# Copy the entrypoint script
COPY bin/docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

# Expose necessary ports
EXPOSE 8501 8000

# Entrypoint and CMD for running both FastAPI and Streamlit
ENTRYPOINT ["/docker-entrypoint.sh"]
CMD ["sh", "-c", "uvicorn src.main:app --host 0.0.0.0 --port 8000 & streamlit run src/app/app.py --server.port 8501 --server.address 0.0.0.0"]
