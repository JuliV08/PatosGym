import paramiko

host = '72.60.63.105'
port = 22
user = 'root'
password = 'VpSH4rd2026K9zX7q'

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

nginx_block = """server {
    listen 80;
    server_name patosgym.com.ar www.patosgym.com.ar;

    # Upload size para videos de staff
    client_max_body_size 100M;
    
    # Compresión
    gzip on;
    gzip_types text/plain text/css application/json application/javascript;

    # Static files (Asegúrate de mapear esta ruta en villex_nginx)
    location /static/ {
        alias /srv/patosgym/volumes/static/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Media files
    location /media/ {
        alias /srv/patosgym/volumes/media/;
        expires 7d;
    }

    # Proxy a Gunicorn (docker-compose: patosgym_prod_web)
    location / {
        proxy_pass http://172.17.0.1:18082;
        proxy_set_header Host $http_host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        
        # Le dice a Django que la conexion original de CF vino por HTTPS
        proxy_set_header X-Forwarded-Proto https;
    }
}
"""

try:
    ssh.connect(host, port, user, password)
    sftp = ssh.open_sftp()
    
    with open('cf_nginx.conf', 'w') as f:
        f.write(nginx_block)
        
    sftp.put('cf_nginx.conf', '/root/Villex/nginx/conf.d/patosgym.conf')
    sftp.close()
    
    _,out,err = ssh.exec_command('docker exec villex_nginx nginx -s reload')
    print('RELOAD OUT:', out.read().decode('utf-8'))
    print('RELOAD ERR:', err.read().decode('utf-8'))
    
except Exception as e:
    print(f"Error: {e}")
finally:
    ssh.close()
