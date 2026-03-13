import paramiko

def merge_stacks():
    host = '72.60.63.105'
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, 22, 'root', 'VpSH4rd2026K9zX7q')

    # 1. Stop PatosGym
    print("--- STOPPING PATOSGYM STACK ---")
    ssh.exec_command('cd /srv/patosgym && docker compose down')

    # 2. Read Villex Compose
    print("--- READING VILLEX COMPOSE ---")
    sftp = ssh.open_sftp()
    with sftp.open('/root/Villex/docker-compose.prod.yml', 'r') as f:
        villex_content = f.read().decode('utf-8')

    # 3. Prepare the Merge
    # I'll append the patosgym services to the Villex compose
    patosgym_services = """
  patosgym_db:
    image: postgres:15-alpine
    container_name: patosgym_prod_db
    volumes:
      - /srv/patosgym/volumes/db_data:/var/lib/postgresql/data:rw
    environment:
      - POSTGRES_DB=patosgym
      - POSTGRES_USER=patos
      - POSTGRES_PASSWORD=patosgym_prod_pass_2024
    restart: unless-stopped

  patosgym_web:
    build:
      context: /srv/patosgym
      dockerfile: Dockerfile
    container_name: patosgym_prod_web
    volumes:
      - /srv/patosgym/volumes/static:/app/staticfiles:rw
      - /srv/patosgym/volumes/media:/app/media:rw
    environment:
      - DEBUG=0
      - SECRET_KEY=dummy_for_now_or_change_me
      - DATABASE_URL=postgres://patos:patosgym_prod_pass_2024@patosgym_db:5432/patosgym
    depends_on:
      - patosgym_db
    restart: unless-stopped
"""
    # Simple injection before the 'networks:' section
    if 'networks:' in villex_content:
        new_content = villex_content.replace('networks:', patosgym_services + '\nnetworks:')
    else:
        new_content = villex_content + patosgym_services

    with sftp.open('/root/Villex/docker-compose.prod.yml', 'w') as f:
        f.write(new_content)
    sftp.close()

    # 4. Restart All
    print("--- RESTARTING MERGED STACK ---")
    ssh.exec_command('cd /root/Villex && docker compose up -d')

    ssh.close()

if __name__ == "__main__":
    merge_stacks()
