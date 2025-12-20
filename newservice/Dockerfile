FROM python:3.12-slim

# Evitar criação de arquivos .pyc e buffering
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
WORKDIR /app
# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

    
COPY r.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r r.txt

COPY  5.txt .
COPY . .

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]