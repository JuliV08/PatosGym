import paramiko
import json

host = '72.60.63.105'
port = 22
user = 'root'
password = 'VpSH4rd2026K9zX7q'

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    ssh.connect(host, port, user, password)
    
    # Get PatosGym Container IP
    _,out,_ = ssh.exec_command("docker inspect patosgym_prod_web")
    data = json.loads(out.read().decode('utf-8'))[0]
    
    patosgym_ip = ""
    for net, info in data['NetworkSettings']['Networks'].items():
        patosgym_ip = info['IPAddress']
        print(f"PatosGym Web is on network '{net}' with IP '{patosgym_ip}'")
    
    if not patosgym_ip:
        print("Could not find PatosGym IP.")
        exit(1)
        
    print(f"Applying IP {patosgym_ip} to Nginx...")
    nginx_block = f"""server {{
    listen 80;
    server_name patosgym.com.ar www.patosgym.com.ar;

    client_max_body_size 100M;
    gzip on;
    gzip_types text/plain text/css application/json application/javascript;

    location /static/ {{
        alias /srv/patosgym/volumes/static/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }}
    location /media/ {{
        alias /srv/patosgym/volumes/media/;
        expires 7d;
    }}
    location / {{
        proxy_pass http://{patosgym_ip}:8000;
        proxy_set_header Host $http_host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto https;
    }}
}}
"""
    sftp = ssh.open_sftp()
    with open('cf_nginx_fixed2.conf', 'w') as f:
        f.write(nginx_block)
    sftp.put('cf_nginx_fixed2.conf', '/root/Villex/nginx/conf.d/patosgym.conf')
    sftp.close()
    
    ssh.exec_command('docker exec villex_nginx nginx -s reload')
    
    import time
    time.sleep(2)
    _,out2,err2 = ssh.exec_command(f'docker exec villex_nginx curl -s -I http://{patosgym_ip}:8000')
    print('TEST:', out2.read().decode('utf-8', 'ignore'))
    
except Exception as e:
    print(f"Error: {e}")
finally:
    ssh.close()
