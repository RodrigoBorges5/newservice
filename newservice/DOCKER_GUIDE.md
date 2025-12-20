# 🐳 Guia de Uso com Docker

## Configuração Inicial

### 1. Variáveis de Ambiente

O ficheiro `.env` já está configurado. Certifique-se de que contém:

```env
SUPABASE_URL=https://aztasjhrilyrlnynktns.supabase.co
SUPABASE_KEY=<sua_chave_anon>
DB_HOST=aws-1-eu-west-1.pooler.supabase.com
DEBUG=True
```

## Comandos Docker

### Build da Imagem

```powershell
docker-compose build
```

### Iniciar o Serviço

```powershell
docker-compose up
```

### Executar Comandos Django

```powershell
# Migrations
docker-compose exec backend python manage.py makemigrations
docker-compose exec backend python manage.py migrate

# Criar superuser
docker-compose exec backend python manage.py createsuperuser

# Shell Django
docker-compose exec backend python manage.py shell

#Database
docker-compose exec backend python manage.py dbshell (\dt, \d)

# Bash no container
docker-compose exec backend bash
```

### Parar o Serviço

```powershell
# Parar (preserva containers)
docker-compose stop

# Parar e remover containers
docker-compose down

# Parar, remover containers e volumes
docker-compose down -v
```

### Rebuild (após mudanças em requirements)

```powershell
docker-compose up --build
```

## Desenvolvimento

### Hot Reload

O volume está configurado para hot reload automático:

- Alterações no código Python são detectadas automaticamente
- O servidor Django reinicia automaticamente

### Acesso à Aplicação

- **URL**: http://localhost:8000
- **Admin**: http://localhost:8000/admin (após migrations)
- **API**: http://localhost:8000/api/

## Troubleshooting

### Erro de Conexão com Supabase

```powershell
# Verificar variáveis de ambiente no container
docker-compose exec backend env | grep SUPABASE
```

### Limpar Cache do Docker

```powershell
# Limpar tudo
docker system prune -a

# Rebuild do zero
docker-compose down -v
docker-compose build --no-cache
docker-compose up
```

### Ver Consumo de Recursos

```powershell
docker stats
```

## Produção

Para produção, altere o `Dockerfile` para usar Gunicorn:

```dockerfile
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "4", "newservice.wsgi:application"]
```

E adicione ao `r.txt`:

```
gunicorn>=21.2.0
```

## Status do Container

```powershell
# Ver containers a correr
docker-compose ps

# Ver todos os containers
docker ps -a

# Inspecionar container
docker inspect newservice-backend
```
