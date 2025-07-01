FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
# Exponemos 6543 porque pserve lo usa por defecto
EXPOSE 6543

CMD ["pserve", "production.ini", "--reload"]
