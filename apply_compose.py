import paramiko

host = '72.60.63.105'
port = 22
user = 'root'
password = 'VpSH4rd2026K9zX7q'

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    ssh.connect(host, port, user, password)
    
    # Check original compose content
    _,out,_ = ssh.exec_command("cat /srv/patosgym/docker-compose.prod.yml")
    compose_content = out.read().decode('utf-8')
    
    # We replace the local patosgym_prod_net with the external villex_network that Nginx uses
    new_compose = compose_content.replace(
        "networks:\n  patosgym_prod_net:\n    name: patosgym_prod_net\n    driver: bridge",
        "networks:\n  patosgym_prod_net:\n    external: true\n    name: dym_network"
    ).replace(
        "patosgym_prod_net: null", 
        "patosgym_prod_net:"
    )
    
    # Write it back
    sftp = ssh.open_sftp()
    with open('remote_compose_temp.yml', 'w') as f:
        f.write(new_compose)
    sftp.put('remote_compose_temp.yml', '/srv/patosgym/docker-compose.prod.yml')
    sftp.close()
    
    # Restart the stack
    ssh.exec_command("cd /srv/patosgym && docker compose -f docker-compose.prod.yml down && docker compose -f docker-compose.prod.yml up -d")
    
    import time
    time.sleep(5)
    
    # Fix Nginx back to internal Docker DNS name
    cmd_nginx = """cat << 'EOF' > /root/Villex/nginx/conf.d/patosgym.conf
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
        proxy_set_header Host $http_host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto https;
    }
}
EOF
docker exec villex_nginx nginx -s reload
"""
    ssh.exec_command(cmd_nginx)
    
    # Test curl
    time.sleep(2)
    _,out2,err2 = ssh.exec_command("docker exec villex_nginx curl -s -I http://patosgym_prod_web:8000")
    print("FINAL CURL:\n", out2.read().decode('utf-8'))
    print("FINAL ERR:\n", err2.read().decode('utf-8'))
    
except Exception as e:
    print(f"Error: {e}")
finally:
    ssh.close()
