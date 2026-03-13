import paramiko

def definitive_fix():
    host = '72.60.63.105'
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, 22, 'root', 'VpSH4rd2026K9zX7q')

    # 1. Stop the unified stack
    print("--- STOPPING UNIFIED STACK ---")
    ssh.exec_command('cd /root/Villex && docker compose down')

    # 2. Hard-Fix Permissions on VPS
    # We use 777 for verification, then we can tighten it. 1000:1000 is for Gunicorn user.
    print("--- FIXING PERMISSIONS (777) ---")
    ssh.exec_command('mkdir -p /srv/patosgym/volumes/static /srv/patosgym/volumes/media /srv/patosgym/volumes/db_data')
    ssh.exec_command('chmod -R 777 /srv/patosgym/volumes')
    ssh.exec_command('chown -R 1000:1000 /srv/patosgym/volumes')

    # 3. Upload truly clean docker-compose.prod.yml
    clean_yml = """
services:
  # --- VILLEX ---
  db:
    image: postgres:15-alpine
    container_name: villex_db
    restart: unless-stopped
    volumes:
      - villex_postgres_data:/var/lib/postgresql/data
    environment:
      - POSTGRES_DB=${POSTGRES_DB:-villex_leads}
      - POSTGRES_USER=${POSTGRES_USER:-postgres}
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD:?POSTGRES_PASSWORD is required}
    healthcheck:
      test: [ "CMD-SHELL", "pg_isready -U ${POSTGRES_USER:-postgres} -d ${POSTGRES_DB:-villex_leads}" ]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - villex_network

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: villex_backend
    restart: unless-stopped
    depends_on:
      db:
        condition: service_healthy
    env_file:
      - .env
      - backend/.env
    environment:
      - POSTGRES_HOST=db
      - POSTGRES_PORT=5432
      - CALENDLY_BASE_URL=${CALENDLY_BASE_URL:-https://calendly.com/villellijulian/30min}
    volumes:
      - villex_static_files:/home/app/web/staticfiles
    networks:
      - villex_network

  nginx:
    build:
      context: .
      dockerfile: frontend.Dockerfile
      args:
        - VITE_API_URL=${VITE_API_URL:-/api}
        - VITE_WHATSAPP_NUMBER=${VITE_WHATSAPP_NUMBER:-5491100000000}
    container_name: villex_nginx
    restart: unless-stopped
    depends_on:
      - backend
      - patosgym_web
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/conf.d:/etc/nginx/conf.d:ro
      - villex_static_files:/usr/share/nginx/static:ro
      - /etc/letsencrypt:/etc/letsencrypt:ro
      - dym-cosmeticos_static_volume:/opt/dym-cosmeticos/staticfiles:ro
      - dym-cosmeticos_media_volume:/opt/dym-cosmeticos/media:ro
      - /srv/patosgym/volumes/static:/srv/patosgym/volumes/static:ro
      - /srv/patosgym/volumes/media:/srv/patosgym/volumes/media:ro
    networks:
      - villex_network

  # --- PATOSGYM ---
  patosgym_db:
    image: postgres:15-alpine
    container_name: patosgym_prod_db
    restart: unless-stopped
    volumes:
      - /srv/patosgym/volumes/db_data:/var/lib/postgresql/data:rw
    environment:
      - POSTGRES_DB=patosgym
      - POSTGRES_USER=patos
      - POSTGRES_PASSWORD=patosgym_prod_pass_2024
    networks:
      - villex_network

  patosgym_web:
    build:
      context: /srv/patosgym
      dockerfile: Dockerfile
    container_name: patosgym_prod_web
    restart: unless-stopped
    depends_on:
      - patosgym_db
    environment:
      - DEBUG=0
      - SECRET_KEY=dummy_for_now_or_change_me
      - DATABASE_URL=postgres://patos:patosgym_prod_pass_2024@patosgym_db:5432/patosgym
    volumes:
      - /srv/patosgym/volumes/static:/app/staticfiles:rw
      - /srv/patosgym/volumes/media:/app/media:rw
    networks:
      - villex_network

volumes:
  villex_postgres_data:
    name: villex_postgres_data
  villex_static_files:
    name: villex_static_files
  dym-cosmeticos_static_volume:
    external: true
  dym-cosmeticos_media_volume:
    external: true

networks:
  villex_network:
    name: villex_network
    driver: bridge
"""
    sftp = ssh.open_sftp()
    with sftp.open('/root/Villex/docker-compose.prod.yml', 'w') as f:
        f.write(clean_yml.strip())
    sftp.close()

    # 4. Starting stack
    print("--- STARTING UNIFIED STACK ---")
    ssh.exec_command('cd /root/Villex && docker compose up -d')

    ssh.close()

if __name__ == "__main__":
    definitive_fix()
