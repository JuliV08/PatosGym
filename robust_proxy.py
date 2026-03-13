import paramiko

host = '72.60.63.105'
port = 22
user = 'root'
password = 'VpSH4rd2026K9zX7q'

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    ssh.connect(host, port, user, password)
    
    # Check if PatosGym itself is alive on 0.0.0.0 mapping
    _,out,_ = ssh.exec_command("docker exec patosgym_prod_web curl -s -I http://0.0.0.0:8000")
    print("PATOSGYM ALIVE:\n", out.read().decode('utf-8'))
    
    # We must explicitly define the host IP mapping for Nginx on Hostinger
    nginx_block = """server {
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
        # Directly pass to the bound Host IP
        proxy_pass http://72.60.63.105:18082;
        
        # Cloudflare compatibility headers
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Stop Nginx from intercepting redirects unexpectedly
        proxy_redirect off;
    }
}
"""
    sftp = ssh.open_sftp()
    with open('cf_nginx_robust.conf', 'w') as f:
        f.write(nginx_block)
    sftp.put('cf_nginx_robust.conf', '/root/Villex/nginx/conf.d/patosgym.conf')
    sftp.close()
    
    # Reload proxy
    ssh.exec_command('docker exec villex_nginx nginx -s reload')
    
    import time
    time.sleep(2)
    
    # Test curl from the NGINX container context to the HOST IP context
    _,out2,err2 = ssh.exec_command('docker exec villex_nginx curl -s -I http://72.60.63.105:18082')
    print('PROXY CURL:\n', out2.read().decode('utf-8', 'ignore'))
    print('PROXY ERR:\n', err2.read().decode('utf-8', 'ignore'))
    
except Exception as e:
    print(f"Error: {e}")
finally:
    ssh.close()
