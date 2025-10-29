FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=.

WORKDIR /app

# requirements.txt está junto a docker-compose (raíz del contexto de build)
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# Copia el código fuente (asume contexto de build en la raíz del proyecto)
COPY src/ /app/

EXPOSE 8000

CMD ["uvicorn", "backend.app.api.main:app", "--reload"]