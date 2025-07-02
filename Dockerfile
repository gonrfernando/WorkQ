FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/root/.local/bin:$PATH"

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential gcc \
        libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

# 👇 Instalamos con --user para que los binarios vayan a ~/.local/bin
RUN pip install --no-cache-dir --user -r requirements.txt

COPY . .

EXPOSE 6543

CMD ["python", "-m", "pyramid.scripts.pserve", "production.ini", "--reload"]
