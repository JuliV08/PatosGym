import paramiko

host = '72.60.63.105'
port = 22
user = 'root'
password = 'VpSH4rd2026K9zX7q'

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    ssh.connect(host, port, user, password)
    
    # Update docker-compose to bind to 0.0.0.0 instead of 127.0.0.1
    cmd1 = "sed -i 's/127.0.0.1/0.0.0.0/g' /srv/patosgym/docker-compose.prod.yml"
    ssh.exec_command(cmd1)
    
    # Restart the container to apply port binding
    cmd2 = "cd /srv/patosgym && docker compose -f docker-compose.prod.yml up -d"
    ssh.exec_command(cmd2)
    
    # Update Nginx to point to the host's actual IP (or docker0 gateway)
    cmd3 = "sed -i 's/patosgym_prod_web:8000/72.60.63.105:18082/g' /root/Villex/nginx/conf.d/patosgym.conf"
    ssh.exec_command(cmd3)
    
    # Reload Nginx
    cmd4 = "docker exec villex_nginx nginx -s reload"
    _,out,err = ssh.exec_command(cmd4)
    print("NGINX RELOAD OUT:", out.read().decode('utf-8'))
    print("NGINX RELOAD ERR:", err.read().decode('utf-8'))
    
except Exception as e:
    print(f"Error: {e}")
finally:
    ssh.close()
