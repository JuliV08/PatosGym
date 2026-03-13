import paramiko

def fix_vps():
    host = '72.60.63.105'
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, 22, 'root', 'VpSH4rd2026K9zX7q')

    def run(cmd):
        print(f"Executing: {cmd}")
        stdin, out, err = ssh.exec_command(cmd)
        stdout = out.read().decode('utf-8', 'ignore')
        stderr = err.read().decode('utf-8', 'ignore')
        if stdout: print(f"STDOUT: {stdout}")
        if stderr: print(f"STDERR: {stderr}")
        return stdout, stderr

    # 1. Fix Permissions
    run('chown -R 1000:1000 /srv/patosgym/volumes')

    # 2. Correct Docker Compose
    # We remove the port mapping and use villex_network as external
    new_compose = """
services:
  db:
    image: postgres:15-alpine
    container_name: patosgym_prod_db
    volumes:
      - /srv/patosgym/volumes/db_data:/var/lib/postgresql/data
    env_file:
      - .env.prod.db
    networks:
      - patosgym_net
    restart: unless-stopped

  web:
    build: .
    container_name: patosgym_prod_web
    command: gunicorn --bind 0.0.0.0:8000 --workers 4 --timeout 120 patosgym_project.wsgi:application
    volumes:
      - /srv/patosgym/volumes/static:/app/staticfiles
      - /srv/patosgym/volumes/media:/app/media
    env_file:
      - .env.prod
    depends_on:
      - db
    networks:
      - patosgym_net
      - villex_proxy_net
    restart: unless-stopped

networks:
  patosgym_net:
    driver: bridge
  villex_proxy_net:
    external: true
    name: villex_network
"""
    sftp = ssh.open_sftp()
    with open('docker-compose.prod.yml.new', 'w') as f:
        f.write(new_compose.strip())
    sftp.put('docker-compose.prod.yml.new', '/srv/patosgym/docker-compose.prod.yml')

    # 3. Correct Nginx Config
    new_nginx = """
server {
    listen 80;
    server_name patosgym.com.ar www.patosgym.com.ar;

    client_max_body_size 100M;
    gzip on;
    gzip_types text/plain text/css application/json application/javascript;

    location /static/ {
        alias /srv/patosgym/volumes/static/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    location /media/ {
        alias /srv/patosgym/volumes/media/;
        expires 7d;
    }

    location / {
        proxy_pass http://patosgym_prod_web:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto https;
        proxy_redirect off;
    }
}
"""
    with open('patosgym.conf.new', 'w') as f:
        f.write(new_nginx.strip())
    sftp.put('patosgym.conf.new', '/root/Villex/nginx/conf.d/patosgym.conf')
    sftp.close()

    # 4. Restart everything
    run('cd /srv/patosgym && docker compose -f docker-compose.prod.yml down && docker compose -f docker-compose.prod.yml up -d')
    run('docker exec villex_nginx nginx -s reload')
    
    # 5. Verify
    time.sleep(5)
    run('docker ps | grep patosgym')
    run('docker exec villex_nginx curl -I http://patosgym_prod_web:8000')

    ssh.close()

if __name__ == "__main__":
    import time
    fix_vps()
