FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=.

WORKDIR /app

# requirements.txt está junto a docker-compose (raíz del contexto de build)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential gcc libpq-dev python3-dev \
    libgl1 libglib2.0-0 libsm6 libxext6 libxrender1 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /tmp/requirements.txt
RUN python -m pip install --upgrade pip && \
    pip install --no-cache-dir -r /tmp/requirements.txt

# Copia el código fuente (asume contexto de build en la raíz del proyecto)
COPY src/ /app/

EXPOSE 8000

CMD ["uvicorn", "backend.app.api.main:app", "--reload"]