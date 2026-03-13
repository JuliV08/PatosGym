# 🚀 PatosGym - Deployment Guide

## 📋 Pre-requisitos en VPS

✅ Docker y Docker Compose instalados  
✅ Nginx con villex_network funcionando  
✅ Dominio DNS configurado: patosgym.com.ar → 72.60.63.105  

---

## 🔧 Deployment en VPS (Producción)

### 1️⃣ Clonar o actualizar repositorio

```bash
# Si es primera vez:
cd /srv
git clone https://github.com/JuliV08/PatosGym.git patosgym
cd patosgym

# Si ya existe:
cd /srv/patosgym
git pull origin main
```

### 2️⃣ Configurar variables de entorno

```bash
# Copiar ejemplos
cp .env.prod.example .env.prod
cp .env.prod.db.example .env.prod.db

# Editar con valores reales:
nano .env.prod
```

**IMPORTANTE - `.env.prod` debe tener:**
```env
COMPOSE_PROJECT_NAME=patosgym_prod
DEBUG=0
SECRET_KEY=<GENERAR_SECRETO_SEGURO_50_CHARS>
ALLOWED_HOSTS=localhost,patosgym.com.ar,www.patosgym.com.ar
CSRF_TRUSTED_ORIGINS=https://patosgym.com.ar,https://www.patosgym.com.ar
DATABASE_URL=postgres://patosgym_user:TU_PASSWORD_SEGURO@db:5432/patosgym_db
```

**`.env.prod.db`:**
```env
POSTGRES_DB=patosgym_db
POSTGRES_USER=patosgym_user
POSTGRES_PASSWORD=<MISMO_PASSWORD_QUE_ARRIBA>
```

### 3️⃣ Crear directorios de volúmenes

```bash
mkdir -p /srv/patosgym/volumes/{static,media,pgdata}
chmod -R 755 /srv/patosgym/volumes
```

### 4️⃣ Levantar servicios

```bash
cd /srv/patosgym
docker compose -f docker-compose.prod.yml up -d --build
```

### 5️⃣ Ejecutar migraciones y collectstatic

```bash
docker compose -f docker-compose.prod.yml exec web python manage.py migrate
docker compose -f docker-compose.prod.yml exec web python manage.py collectstatic --noinput
docker compose -f docker-compose.prod.yml exec web python manage.py load_initial_images
```

### 6️⃣ Crear superusuario

```bash
docker compose -f docker-compose.prod.yml exec web python manage.py createsuperuser
```

---

## 🌐 Configurar Nginx (villex_nginx)

### 1️⃣ Agregar servidor patosgym al nginx

```bash
# En la VPS - editar el docker-compose.yml de Villex
nano /root/Villex/docker-compose.yml
```

Agregar en la sección de `villex_nginx` volumes:
```yaml
volumes:
  - /srv/patosgym/volumes/static:/srv/patosgym/volumes/static:ro
  - /srv/patosgym/volumes/media:/srv/patosgym/volumes/media:ro
```

### 2️⃣ Copiar configuración nginx

```bash
cp /srv/patosgym/nginx_patosgym.conf /root/Villex/nginx/conf.d/patosgym.conf
```

### 3️⃣ Reiniciar nginx

```bash
cd /root/Villex
docker compose restart villex_nginx
```

### 4️⃣ Generar certificado SSL

```bash
docker exec villex_nginx certbot certonly --webroot \
  -w /var/www/certbot \
  -d patosgym.com.ar \
  -d www.patosgym.com.ar \
  --email admin@patosgym.com.ar \
  --agree-tos \
  --non-interactive
```

---

## 🔍 Verificación

```bash
# Ver logs
docker compose -f docker-compose.prod.yml logs -f web

# Verificar salud
docker compose -f docker-compose.prod.yml ps
curl http://localhost:18082/health/

# Test desde nginx
docker exec villex_nginx curl -I http://172.17.0.1:18082/health/
```

---

## 🔄 Actualizar después de cambios en código

```bash
cd /srv/patosgym
git pull origin main
docker compose -f docker-compose.prod.yml up -d --build
docker compose -f docker-compose.prod.yml exec web python manage.py migrate
docker compose -f docker-compose.prod.yml exec web python manage.py collectstatic --noinput
```

---

## ⚠️ IMPORTANTE - NO afectar otros proyectos

- PatosGym usa puerto **18082** (DYM usa 18000, Villex usa 8000)
- PatosGym usa red **villex_network** (compartida, sin conflictos)
- Nginx de Villex actúa como proxy reverso común
- Volúmenes en `/srv/patosgym/` (aislados de otros proyectos)

---

## 🐛 Troubleshooting

### Container unhealthy
```bash
docker logs patosgym_prod_web
# Verificar ALLOWED_HOSTS en .env.prod
```

### Error de base de datos
```bash
# Verificar que DATABASE_URL coincida con .env.prod.db
docker compose -f docker-compose.prod.yml logs db
```

### Nginx 502 Bad Gateway
```bash
# Verificar que el contenedor esté saludable
docker ps
# Verificar conectividad desde nginx
docker exec villex_nginx curl http://172.17.0.1:18082/
```
