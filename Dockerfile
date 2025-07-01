# syntax=docker/dockerfile:1
FROM python:3.11-slim

# ── Opciones básicas de Python ─────────────────────────
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# ── Lugar donde vivirá tu código ───────────────────────
WORKDIR /app

# ── Paquetes nativos necesarios para compilar dependencias de BD / Pillow, etc. ──
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential gcc \
        libpq-dev              \
    && rm -rf /var/lib/apt/lists/*

# ── Instalar dependencias Python ───────────────────────
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ── Copiar el proyecto completo ────────────────────────
COPY . .

# ── Puerto donde Pyramid (pserve) escucha ──────────────
EXPOSE 6543

# ── Arranque ───────────────────────────────────────────
CMD ["pserve", "production.ini", "--reload"]
