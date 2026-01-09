# PowerGYM - Modernización + Gallery CMS

Sistema completo con Django + PostgreSQL para PowerGym.ar con landing premium (negro/blanco/rojo) y galería administrable.

## Características

- **Landing Premium**: Diseño moderno con TailwindCSS, gradientes, glassmorphism
- **Galería Administrable**: CRUD completo de fotos con thumbnails automáticos
- **Categorías**: Vestuarios, Cardio, El Gym, Musculación
- **Seguridad**: Validaciones de tamaño/tipo, sanitización de nombres, settings de producción
- **Infraestructura Aislada**: Network y volúmenes únicos, no interfiere con otros proyectos

## Stack Tecnológico

- Django 4.2.9
- PostgreSQL 15
- Gunicorn
- Docker + Docker Compose
- TailwindCSS (CDN)
- GLightbox (galería con lightbox)

## Estructura del Proyecto

```
powergym/
├── manage.py
├── requirements.txt
├── Dockerfile
├── docker-compose.prod.yml
├── docker-entrypoint.sh
├── .env.prod.example
├── .env.prod.db.example
├── powergym_project/
│   ├── settings/
│   │   ├── base.py
│   │   └── production.py
│   ├── urls.py
│   └── wsgi.py
├── gallery/
│   ├── models.py (GalleryPhoto con validaciones)
│   ├── admin.py (admin customizado con previews)
│   ├── views.py
│   └── urls.py
├── landing/
│   ├── views.py
│   └── urls.py
└── templates/
    ├── landing/
    │   ├── base.html
    │   └── home.html
    └── gallery/
        └── gallery.html
```

## Deployment en VPS

### Pre-requisitos

1. DNS de powergym.ar delegado a Cloudflare
2. VPS con Docker y Docker Compose instalados
3. Acceso SSH al VPS

### Paso 1: Preparar el proyecto en el VPS

```bash
# SSH al VPS
ssh root@72.60.63.105

# Crear estructura de directorios
mkdir -p /srv/powergym/volumes/{static,media,pgdata}
cd /root

# Clonar/copiar el proyecto
# (Puedes usar git clone, scp, etc.)
```

### Paso 2: Configurar variables de entorno

```bash
cd /root/powergym  # o donde hayas copiado el proyecto

# Copiar ejemplos y editar
cp .env.prod.example .env.prod
cp .env.prod.db.example .env.prod.db

# Editar .env.prod y cambiar:
# - SECRET_KEY (generar uno aleatorio de 50 caracteres)
# - POSTGRES_PASSWORD en DATABASE_URL

# Editar .env.prod.db y cambiar:
# - POSTGRES_PASSWORD (mismo que en .env.prod)
```

**Generar SECRET_KEY:**

```bash
python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
```

### Paso 3: Construir y levantar los containers

```bash
# Verificar que no existan conflictos
docker volume ls | grep powergym  # debe estar vacío
docker network ls | grep powergym  # debe estar vacío

# Build y up
docker compose -f docker-compose.prod.yml build
docker compose -f docker-compose.prod.yml up -d

# Ver logs
docker compose -f docker-compose.prod.yml logs -f
```

### Paso 4: Migraciones y superusuario

```bash
# Ejecutar migraciones (ya se hacen en entrypoint, pero por si acaso)
docker compose -f docker-compose.prod.yml exec web python manage.py migrate

# Crear superusuario
docker compose -f docker-compose.prod.yml exec web python manage.py createsuperuser

# Collectstatic (ya se hace en entrypoint)
docker compose -f docker-compose.prod.yml exec web python manage.py collectstatic --noinput
```

### Paso 5: Integrar con villex_nginx

**5.1 - Agregar volúmenes a villex_nginx**

Editar `/root/Villex/docker-compose.prod.yml`:

```yaml
services:
  nginx:
    # ... configuración existente ...
    volumes:
      # ... volúmenes existentes ...
      - /srv/powergym/volumes/static:/opt/powergym/static:ro
      - /srv/powergym/volumes/media:/opt/powergym/media:ro
```

**5.2 - Crear server block para powergym**

```bash
nano /root/Villex/nginx/conf.d/powergym.conf
```

Contenido:

```nginx
# PowerGYM - Server Block
server {
    listen 80;
    server_name powergym.ar www.powergym.ar;

    # ACME challenge para Certbot
    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }

    location / {
        return 301 https://$server_name$request_uri;
    }
}

server {
    listen 443 ssl http2;
    server_name powergym.ar www.powergym.ar;

    # SSL (generar con certbot)
    ssl_certificate /etc/letsencrypt/live/powergym.ar/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/powergym.ar/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers 'ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256';
    ssl_prefer_server_ciphers off;

    # Upload size para imágenes
    client_max_body_size 20M;

    # Compresión
    gzip on;
    gzip_types text/plain text/css application/json application/javascript;

    # Static files
    location /static/ {
        alias /opt/powergym/static/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Media files
    location /media/ {
        alias /opt/powergym/media/;
        expires 7d;
    }

    # Proxy al container de Django
    location / {
        proxy_pass http://172.17.0.1:18081;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

**5.3 - Reiniciar villex_nginx con los nuevos mounts**

```bash
cd /root/Villex
docker compose -f docker-compose.prod.yml down nginx
docker compose -f docker-compose.prod.yml up -d nginx
```

### Paso 6: Verificar conectividad ANTES de configurar Nginx

```bash
# Desde dentro de villex_nginx, verificar que llega al backend
docker exec villex_nginx curl -I http://172.17.0.1:18081/health/
# Esperado: HTTP/1.1 200 OK
```

### Paso 7: Probar y recargar Nginx

```bash
# Test de configuración
docker exec villex_nginx nginx -t
# Esperado: syntax is ok, test is successful

# Si el test pasa, recargar (SIN restart)
docker exec villex_nginx nginx -s reload

# Verificar que no hay errores
docker logs villex_nginx --tail 50
```

### Paso 8: Generar certificado SSL con Certbot

```bash
# Dentro del container de nginx o desde donde tengas certbot
docker exec villex_nginx certbot --nginx -d powergym.ar -d www.powergym.ar
# O si tienes certbot en el host:
certbot certonly --webroot -w /var/www/certbot -d powergym.ar -d www.powergym.ar
```

### Paso 9: Verificación final

```bash
# 1. Acceder al admin
curl -I https://powergym.ar/admin/
# Esperado: HTTP/2 200 o 302

# 2. Subir una imagen de prueba en el admin
# https://powergym.ar/admin/gallery/galleryphoto/add/

# 3. Verificar que la imagen se sirve correctamente
curl -I https://powergym.ar/media/gallery/nombre-imagen.jpg
# Esperado: HTTP/2 200
```

## Comandos Útiles

### Ver logs

```bash
docker compose -f docker-compose.prod.yml logs -f
docker compose -f docker-compose.prod.yml logs web
docker compose -f docker-compose.prod.yml logs db
```

### Entrar al container

```bash
docker compose -f docker-compose.prod.yml exec web bash
docker compose -f docker-compose.prod.yml exec db psql -U powergym_user powergym_db
```

### Backup de base de datos

```bash
docker compose -f docker-compose.prod.yml exec db pg_dump -U powergym_user powergym_db > backup_$(date +%Y%m%d_%H%M%S).sql
```

### Restore de base de datos

```bash
cat backup.sql | docker compose -f docker-compose.prod.yml exec -T db psql -U powergym_user powergym_db
```

### Reiniciar servicios

```bash
docker compose -f docker-compose.prod.yml restart web
docker compose -f docker-compose.prod.yml restart db
```

### Ver estado de containers

```bash
docker compose -f docker-compose.prod.yml ps
docker compose -f docker-compose.prod.yml top
```

## Troubleshooting

### Error de conexión a base de datos

```bash
# Verificar que el container de DB está corriendo
docker compose -f docker-compose.prod.yml ps db

# Ver logs de DB
docker compose -f docker-compose.prod.yml logs db

# Verificar que el password coincide entre .env.prod y .env.prod.db
```

### Nginx test falla

```bash
# Ver el error exacto
docker exec villex_nginx nginx -t

# Ver logs de nginx
docker logs villex_nginx

# Verificar sintaxis del conf
docker exec villex_nginx cat /etc/nginx/conf.d/powergym.conf
```

### Imágenes no se cargan

```bash
# Verificar permisos en /srv/powergym/volumes/media
ls -la /srv/powergym/volumes/media

# Verificar que villex_nginx tiene montado el volumen
docker inspect villex_nginx | grep powergym

# Verificar que la imagen existe
ls -la /srv/powergym/volumes/media/gallery/
```

## Mantenimiento

### Actualizar código

```bash
# Pull de cambios (si usas git)
cd /root/powergym
git pull

# Rebuild y recreate
docker compose -f docker-compose.prod.yml build
docker compose -f docker-compose.prod.yml up -d

# Migraciones si hay cambios en modelos
docker compose -f docker-compose.prod.yml exec web python manage.py migrate
docker compose -f docker-compose.prod.yml exec web python manage.py collectstatic --noinput
```

### Limpiar volúmenes huérfanos

```bash
docker volume prune
```

### Optimizar imágenes Docker

```bash
docker system prune -a
```

## Seguridad

- **Admin**: Cambiar la ruta `/admin/` a algo custom editando `powergym_project/urls.py`
- **Rate Limiting**: Implementar en Nginx para `/admin/`
- **Backups**: Automatizar con cron el backup de PostgreSQL
- **Actualizaciones**: Mantener Django y dependencias actualizadas

## Contacto

Para soporte técnico, contactar al desarrollador del sistema.
