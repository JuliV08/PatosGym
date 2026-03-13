import paramiko

def fix_final():
    host = '72.60.63.105'
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, 22, 'root', 'VpSH4rd2026K9zX7q')

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
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
    }
}

server {
    listen 443 ssl;
    http2 on;
    server_name patosgym.com.ar www.patosgym.com.ar;

    # Using existing Villex certs for the handshake (Cloudflare to Proxy)
    ssl_certificate /etc/letsencrypt/live/villex.com.ar/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/villex.com.ar/privkey.pem;

    client_max_body_size 100M;

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
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
    }
}
"""
    sftp = ssh.open_sftp()
    with open('patosgym_final.conf', 'w') as f:
        f.write(new_nginx.strip())
    sftp.put('patosgym_final.conf', '/root/Villex/nginx/conf.d/patosgym.conf')
    sftp.close()

    print("--- RELOADING NGINX ---")
    ssh.exec_command('docker exec villex_nginx nginx -t && docker exec villex_nginx nginx -s reload')
    
    ssh.close()

if __name__ == "__main__":
    fix_final()
