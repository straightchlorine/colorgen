FROM python:3.12-slim AS builder

# Install system dependencies
RUN apt-get update && apt-get install -y \
    --no-install-recommends \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
ENV POETRY_VERSION=1.8.3 \
    POETRY_HOME="/opt/poetry" \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

RUN pip install --no-cache-dir poetry==${POETRY_VERSION}

# Set working directory
WORKDIR /app

# Copy dependency files
COPY pyproject.toml poetry.lock ./

# Install dependencies
RUN poetry install --without dev --no-root && rm -rf $POETRY_CACHE_DIR

# Runtime stage
FROM python:3.12-slim AS runtime

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    --no-install-recommends \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd -m -u 1000 colorgen && \
    mkdir -p /app && \
    chown -R colorgen:colorgen /app

WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder --chown=colorgen:colorgen /app/.venv /app/.venv

# Copy application code
COPY --chown=colorgen:colorgen . .

# Activate virtual environment
ENV VIRTUAL_ENV=/app/.venv \
    PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1

# Switch to non-root user
USER colorgen

# Create volume mount points for configs and output
VOLUME ["/config", "/output"]

# Set entrypoint
ENTRYPOINT ["python", "colorgen.py"]
CMD ["--help"]

# Labels
LABEL org.opencontainers.image.title="colorgen" \
      org.opencontainers.image.description="Effortless image-based colorscheme generation" \
      org.opencontainers.image.authors="Piotr Krzysztof Lis <piotr@codextechnologies.org>" \
      org.opencontainers.image.source="https://codeberg.org/piotrkrzysztof/colorgen" \
      org.opencontainers.image.licenses="GPL-3.0-or-later"
