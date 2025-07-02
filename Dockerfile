FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/root/.local/bin:$PATH"

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential gcc \
        libpq-dev \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip==25.1.1

COPY requirements.txt .

RUN pip install --no-cache-dir --user -r requirements.txt

COPY . .

EXPOSE 6543

CMD ["python", "-m", "pyramid.scripts.pserve", "production.ini", "--reload"]
