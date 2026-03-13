import paramiko

def fix_and_start():
    host = '72.60.63.105'
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, 22, 'root', 'VpSH4rd2026K9zX7q')

    # 1. Stop PatosGym
    print("--- STOPPING PATOSGYM ---")
    ssh.exec_command('cd /srv/patosgym && docker compose down')

    # 2. Fix Permissions (definitive)
    print("--- FIXING PERMISSIONS ---")
    ssh.exec_command('chown -R 1000:1000 /srv/patosgym/volumes')

    # 3. Simplify docker-compose.prod.yml
    # We will make villex_network the ONLY and DEFAULT network
    print("--- SIMPLIFYING COMPOSE ---")
    new_compose = """
services:
  db:
    image: postgres:15-alpine
    container_name: patosgym_prod_db
    volumes:
      - /srv/patosgym/volumes/db_data:/var/lib/postgresql/data:rw
    environment:
      - POSTGRES_DB=patosgym
      - POSTGRES_USER=patos
      - POSTGRES_PASSWORD=patosgym_prod_pass_2024
    restart: unless-stopped
    networks:
      - default

  web:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: patosgym_prod_web
    volumes:
      - /srv/patosgym/volumes/static:/app/staticfiles:rw
      - /srv/patosgym/volumes/media:/app/media:rw
    environment:
      - DEBUG=0
      - SECRET_KEY=dummy_for_now_or_change_me
      - DATABASE_URL=postgres://patos:patosgym_prod_pass_2024@patosgym_prod_db:5432/patosgym
    depends_on:
      - db
    restart: unless-stopped
    networks:
      - default

networks:
  default:
    external: true
    name: villex_network
"""
    sftp = ssh.open_sftp()
    with sftp.open('/srv/patosgym/docker-compose.prod.yml', 'w') as f:
        f.write(new_compose.strip())
    sftp.close()

    # 4. Start PatosGym
    print("--- STARTING PATOSGYM ---")
    ssh.exec_command('cd /srv/patosgym && docker compose up -d')

    print("--- SUCCESS ---")
    ssh.close()

if __name__ == "__main__":
    fix_and_start()
