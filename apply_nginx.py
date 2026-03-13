import paramiko

host = '72.60.63.105'
port = 22
user = 'root'
password = 'VpSH4rd2026K9zX7q'

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    ssh.connect(host, port, user, password)
    
    # Check what is written in the conf
    _,out,_ = ssh.exec_command('cat /root/Villex/nginx/conf.d/patosgym.conf')
    # Use latin-1 or ignore errors to avoid crash
    print('CONF:', out.read().decode('utf-8', 'ignore'))
    
    # Hard rewrite the config to ensure docker0 route 172.17.0.1
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
        proxy_pass http://172.17.0.1:18082;
        proxy_set_header Host $http_host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto https;
    }
}
"""
    sftp = ssh.open_sftp()
    with open('cf_nginx_fixed.conf', 'w') as f:
        f.write(nginx_block)
    sftp.put('cf_nginx_fixed.conf', '/root/Villex/nginx/conf.d/patosgym.conf')
    sftp.close()
    
    # Reload and test
    ssh.exec_command('docker exec villex_nginx nginx -s reload')
    
    _,out2,err2 = ssh.exec_command('docker exec villex_nginx curl -s -I http://172.17.0.1:18082')
    print('TEST:', out2.read().decode('utf-8', 'ignore'))
    
except Exception as e:
    print(f"Error: {e}")
finally:
    ssh.close()
