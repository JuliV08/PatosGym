# PatosGym - Gimnasio Premium + CMS Dinámico

Sistema completo con Django + PostgreSQL para el gimnasio PatosGym en Villa Lugano, CABA. Incluye landing premium con diseño moderno (negro/naranja) y sistema administrable para galería y equipo.

## Características

- **Landing Premium**: Diseño moderno con TailwindCSS, gradientes, glassmorphism
- **Galería Administrable**: CRUD completo de fotos con thumbnails automáticos y categorías
- **Staff con Videos**: Miembros del equipo con videos de entrevistas embebidos desde YouTube
- **Categorías de Galería**: Vestuarios, Cardio, El Gym, Musculación, Transformaciones, Atletas
- **Seguridad**: Validaciones de tamaño/tipo, sanitización de nombres, settings de producción
- **Infraestructura Aislada**: Network y volúmenes únicos, no interfiere con otros proyectos

## Stack Tecnológico

- Django 4.2.9
- PostgreSQL 15
- Gunicorn
- Docker + Docker Compose
- TailwindCSS (CDN)
- GLightbox (galería con lightbox)
- Swiper.js (carousel para staff)

## Estructura del Proyecto

```
patosgym/
├── manage.py
├── requirements.txt
├── Dockerfile
├── docker-compose.prod.yml
├── docker-entrypoint.sh
├── .env.prod.example
├── .env.prod.db.example
├── patosgym_project/
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
│   ├── models.py (TeamMember con videos, HeroImage)
│   ├── admin.py
│   ├── views.py
│   └── urls.py
└── templates/
    ├── landing/
    │   ├── base.html
    │   ├── home.html
    │   └── partials/
    │       ├── hero.html
    │       ├── team.html (con carousel y modals de video)
    │       ├── gallery.html
    │       ├── contact.html
    │       └── ...
    └── gallery/
        └── gallery.html
```

## Deployment en VPS Compartido (Bind Mounts)

Este proyecto está diseñado para deployarse en un VPS que ya tiene otros proyectos (Villex, DyM Cosméticos) corriendo con `villex_nginx` como reverse proxy centralizado.

### Arquitectura de Deployment

- **PatosGym Backend**: Corre en puerto `18081` (container Docker independiente)
- **PostgreSQL**: Base de datos propia aislada (no compartida con otros proyectos)
- **Static/Media Files**: Servidos por `villex_nginx` vía bind mounts desde `/srv/patosgym/volumes/`
- **SSL/Reverse Proxy**: Manejado por `villex_nginx` compartido

**Ventajas de esta arquitectura:**
- ✅ No interfiere con Villex, DyM Cosméticos ni otros proyectos
- ✅ Fácil rollback si algo falla
- ✅ Cada proyecto tiene su propia DB y network
- ✅ Un solo nginx para SSL y routing

### Pre-requisitos

1. VPS con Docker y Docker Compose instalados
2. Acceso SSH al VPS
3. `villex_nginx` ya configurado y corriendo
4. Dominio configurado (cuando se compre)

### Paso 1: Preparar directorios en el VPS

```bash
# SSH al VPS
ssh root@72.60.63.105

# Crear estructura de directorios aislada para PatosGym
mkdir -p /srv/patosgym/volumes/{static,media,pgdata}

# Verificar que no haya conflictos con otros proyectos
ls -la /srv/

# Expected output:
# /srv/villex/
# /srv/dymcosmeticos/ (si existe)
# /srv/patosgym/ (recién creado)
```

### Paso 2: Subir código al VPS

```bash
# Opción A: Git (recomendado)
cd /root
git clone [TU_REPO_PATOSGYM_URL] patosgym
cd patosgym

# Opción B: SCP desde tu PC local
# scp -r c:/Users/JULI/PatosGym root@72.60.63.105:/root/patosgym
```

### Paso 3: Configurar variables de entorno

```bash
cd /root/patosgym

# Copiar plantillas
cp .env.prod.example .env.prod
cp .env.prod.db.example .env.prod.db

# Generar SECRET_KEY
python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'

# Editar .env.prod
nano .env.prod
```

**Contenido de `.env.prod`:**
```bash
COMPOSE_PROJECT_NAME=patosgym_prod
DEBUG=0
SECRET_KEY=[TU_SECRET_KEY_GENERADA_ARRIBA]
ALLOWED_HOSTS=patosgym.com.ar,www.patosgym.com.ar  # Cambiar cuando compres dominio
CSRF_TRUSTED_ORIGINS=https://patosgym.com.ar,https://www.patosgym.com.ar
DATABASE_URL=postgres://patosgym_user:[PASSWORD_SEGURA]@db:5432/patosgym_db
```

**Contenido de `.env.prod.db`:**
```bash
POSTGRES_DB=patosgym_db
POSTGRES_USER=patosgym_user
POSTGRES_PASSWORD=[MISMO_PASSWORD_QUE_ARRIBA]
```

> **⚠️ IMPORTANTE**: Los passwords deben coincidir entre `.env.prod` y `.env.prod.db`

### Paso 4: Verificar disponibilidad del puerto

```bash
# Verificar que puerto 18081 esté libre
netstat -tuln | grep 18081
# Si devuelve algo, el puerto está ocupado, cambia el puerto en docker-compose.prod.yml

# Ver qué puertos están en uso por otros proyectos
docker ps --format "table {{.Names}}\t{{.Ports}}"
```

### Paso 5: Construir y levantar containers

```bash
cd /root/patosgym

# Verificar que no existan conflictos de nombres
docker volume ls | grep patosgym  # debe estar vacío
docker network ls | grep patosgym  # debe estar vacío

# Build de la imagen
docker compose -f docker-compose.prod.yml build

# Levantar servicios
docker compose -f docker-compose.prod.yml up -d

# Verificar que estén corriendo
docker compose -f docker-compose.prod.yml ps
# Expected: web (healthy), db (healthy)

# Ver logs en tiempo real
docker compose -f docker-compose.prod.yml logs -f
```

### Paso 6: Migraciones y superusuario

```bash
# Aplicar migraciones
docker compose -f docker-compose.prod.yml exec web python manage.py migrate

# Crear superusuario para el admin
docker compose -f docker-compose.prod.yml exec web python manage.py createsuperuser
# Username: admin
# Email: [tu_email]
# Password: [password_segura]

# Collectstatic (recolectar archivos estáticos)
docker compose -f docker-compose.prod.yml exec web python manage.py collectstatic --noinput

# Verificar que los archivos se copiaron
ls -la /srv/patosgym/volumes/static/
ls -la /srv/patosgym/volumes/media/
```

### Paso 7: Integrar con villex_nginx

**7.1 - Backup de configuración actual**

```bash
# Hacer backup antes de modificar
cd /root/Villex
cp docker-compose.prod.yml docker-compose.prod.yml.backup.$(date +%Y%m%d)
cp -r nginx/conf.d nginx/conf.d.backup.$(date +%Y%m%d)
```

**7.2 - Agregar bind mounts a villex_nginx**

Editar `/root/Villex/docker-compose.prod.yml`:

```bash
nano /root/Villex/docker-compose.prod.yml
```

Agregar estos volúmenes al servicio `nginx`:

```yaml
services:
  nginx:
    # ... configuración existente NO TOCAR ...
    volumes:
      # ... volúmenes existentes de Villex y DyM NO TOCAR ...
      
      # PatosGym bind mounts (AGREGAR AL FINAL)
      - /srv/patosgym/volumes/static:/opt/patosgym/static:ro
      - /srv/patosgym/volumes/media:/opt/patosgym/media:ro
```

**7.3 - Crear server block para PatosGym**

```bash
nano /root/Villex/nginx/conf.d/patosgym.conf
```

**Contenido** (actualizar dominio cuando lo compres):

```nginx
# PatosGym - Server Block
server {
    listen 80;
    server_name patosgym.com.ar www.patosgym.com.ar;  # CAMBIAR cuando compres dominio

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
    server_name patosgym.com.ar www.patosgym.com.ar;  # CAMBIAR cuando compres dominio

    # SSL (generar con certbot después de configurar DNS)
    ssl_certificate /etc/letsencrypt/live/patosgym.com.ar/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/patosgym.com.ar/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers 'ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256';
    ssl_prefer_server_ciphers off;

    # Upload size para imágenes y videos
    client_max_body_size 20M;

    # Compresión
    gzip on;
    gzip_types text/plain text/css application/json application/javascript;

    # Static files
    location /static/ {
        alias /opt/patosgym/static/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Media files
    location /media/ {
        alias /opt/patosgym/media/;
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

**7.4 - Reiniciar nginx con nuevos mounts**

```bash
cd /root/Villex

# Bajar solo nginx (NO tocar DB ni otros servicios)
docker compose -f docker-compose.prod.yml stop nginx

# Levantar nginx con los nuevos bind mounts
docker compose -f docker-compose.prod.yml up -d nginx

# Verificar logs
docker logs villex_nginx --tail 50

# Verificar que los bind mounts se montaron
docker inspect villex_nginx | grep patosgym
```

### Paso 8: Verificar conectividad

```bash
# Desde dentro de villex_nginx, verificar que llega al backend
docker exec villex_nginx curl -I http://172.17.0.1:18081/
# Expected: HTTP/1.1 200 OK o 302 (redirect)

# Test de configuración de nginx
docker exec villex_nginx nginx -t
# Expected: syntax is ok, test is successful

# Si el test pasa, recargar nginx
docker exec villex_nginx nginx -s reload
```

### Paso 9: Generar certificado SSL (cuando tengas dominio)

```bash
# Una vez que el dominio esté apuntando al VPS:
docker exec villex_nginx certbot certonly --webroot \
  -w /var/www/certbot \
  -d patosgym.com.ar \
  -d www.patosgym.com.ar \
  --email tu_email@example.com \
  --agree-tos \
  --no-eff-email

# Reload nginx para usar el nuevo certificado
docker exec villex_nginx nginx -s reload
```

### Paso 10: Verificación final

```bash
# 1. Verificar que PatosGym está corriendo
curl -I http://172.17.0.1:18081/
# Expected: HTTP/1.1 200 OK

# 2. Acceder al admin (una vez que tengas dominio configurado)
# https://patosgym.com.ar/admin/

# 3. Subir imágenes de prueba y miembros del staff

# 4. Verificar que se sirven correctamente
curl -I https://patosgym.com.ar/media/gallery/test.jpg
curl -I https://patosgym.com.ar/static/css/main.css
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
docker compose -f docker-compose.prod.yml exec db psql -U patosgym_user patosgym_db
```

### Backup de base de datos

```bash
docker compose -f docker-compose.prod.yml exec db pg_dump -U patosgym_user patosgym_db > backup_$(date +%Y%m%d_%H%M%S).sql
```

### Restore de base de datos

```bash
cat backup.sql | docker compose -f docker-compose.prod.yml exec -T db psql -U patosgym_user patosgym_db
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
grep POSTGRES_PASSWORD .env.prod
grep POSTGRES_PASSWORD .env.prod.db
```

### Nginx test falla

```bash
# Ver el error exacto
docker exec villex_nginx nginx -t

# Ver logs de nginx
docker logs villex_nginx

# Verificar sintaxis del conf
docker exec villex_nginx cat /etc/nginx/conf.d/patosgym.conf
```

### Imágenes no se cargan

```bash
# Verificar permisos en /srv/patosgym/volumes/media
ls -la /srv/patosgym/volumes/media

# Verificar que villex_nginx tiene montado el volumen
docker inspect villex_nginx | grep patosgym

# Verificar que la imagen existe
ls -la /srv/patosgym/volumes/media/gallery/
```

### Puerto 18081 ya está en uso

```bash
# Ver qué está usando el puerto
netstat -tuln | grep 18081
docker ps | grep 18081

# Si necesitas cambiar el puerto, edita docker-compose.prod.yml
# Y actualiza la configuración de nginx (proxy_pass)
```

## Mantenimiento

### Actualizar código

```bash
# Pull de cambios (si usas git)
cd /root/patosgym
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

- **Admin**: Cambiar la ruta `/admin/` a algo custom editando `patosgym_project/urls.py`
- **Rate Limiting**: Implementar en Nginx para `/admin/`
- **Backups**: Automatizar con cron el backup de PostgreSQL
- **Actualizaciones**: Mantener Django y dependencias actualizadas
- **Firewall**: Solo permitir puertos 22 (SSH), 80 (HTTP), 443 (HTTPS)

## Desarrollo Local

Para trabajar en local sin Docker:

```bash
# Activar entorno virtual
.\venv\Scripts\Activate.ps1  # Windows
source venv/bin/activate      # Linux/Mac

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar migraciones
python manage.py migrate

# Crear superusuario
python manage.py createsuperuser

# Correr servidor de desarrollo
python manage.py runserver

# Acceder a:
# http://127.0.0.1:8000/
# http://127.0.0.1:8000/admin/
```

## Features Implementados

- ✅ Landing page premium con diseño moderno
- ✅ Sección de galería con categorías y lightbox
- ✅ Sección de equipo con carousel responsivo
- ✅ Videos de entrevistas del staff (YouTube embebidos en modal)
- ✅ Formulario de contacto con integración WhatsApp
- ✅ Admin de Django personalizado
- ✅ Deployment con Docker + Nginx
- ✅ SSL con Let's Encrypt

## Contacto

Para consultas sobre el proyecto PatosGym, contactar al equipo de desarrollo.
