FROM python:3.11-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    cmake \
    libopenblas-dev \
    liblapack-dev \
    libx11-dev \
    libgtk-3-dev \
    libboost-all-dev \
    libxrender1 \
    libxext6 \
    libsm6 \
    libffi-dev \
    libssl-dev \
    python3-dev \
    ca-certificates \
    wget \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install python packages as a separate layer
COPY requirements.txt /app/requirements.txt
RUN python -m pip install --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r /app/requirements.txt

# Copy application code
COPY . /app

# Create non-root user
RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser
RUN chown -R appuser:appgroup /app

ENV FLASK_ENV=production
ENV FLASK_APP=run.py
ENV FLASK_PORT=5000

EXPOSE 5000

USER appuser

ENTRYPOINT ["/app/entrypoint.sh"]

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "run:app"]
