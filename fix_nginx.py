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
    
    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }
    
    location / {
        proxy_pass http://172.17.0.1:18082;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
"""

try:
    ssh.connect(host, port, user, password)
    sftp = ssh.open_sftp()
    
    with open('temp_nginx.conf', 'w') as f:
        f.write(nginx_block)
        
    sftp.put('temp_nginx.conf', '/root/Villex/nginx/conf.d/patosgym.conf')
    sftp.close()
    
    _,out,err = ssh.exec_command('docker exec villex_nginx nginx -s reload')
    print('RELOAD OUT:', out.read().decode('utf-8'))
    print('RELOAD ERR:', err.read().decode('utf-8'))
    
except Exception as e:
    print(f"Error: {e}")
finally:
    ssh.close()
