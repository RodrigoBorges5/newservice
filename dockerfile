# Imagem base
FROM python:3.12-slim

# Impedir que o Python crie ficheiros .pyc e buffer de stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Definir diretório de trabalho dentro do container
WORKDIR /app

# Instalar dependências do sistema (ex: para psycopg2 / compilação)
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       build-essential \
       libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements e instalar dependências Python
COPY backend/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copiar o código do backend para dentro do container
COPY backend/ /app/

# Porta em que o Django/Gunicorn vai correr
EXPOSE 8000

# Comando de arranque (DEV: runserver)
# Para produção, o ideal é usar gunicorn (ver alternativa abaixo)
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]