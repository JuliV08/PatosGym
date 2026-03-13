import paramiko

host = '72.60.63.105'
port = 22
user = 'root'
password = 'VpSH4rd2026K9zX7q'

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    ssh.connect(host, port, user, password)
    
    cmd_test = """
    IP=$(docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' patosgym_prod_web)
    echo "Found IP: $IP"
    docker exec villex_nginx curl -s -I http://$IP:8000
    """
    _,out,err = ssh.exec_command(cmd_test)
    print('OUT:\n', out.read().decode('utf-8'))
    print('ERR:\n', err.read().decode('utf-8'))

    # Final Nginx check to make sure patosgym.com.ar is strictly pointing to that IP
    cmd_fix = f"""
    IP=$(docker inspect -f '{{{{range .NetworkSettings.Networks}}}}{{{{.IPAddress}}}}{{{{end}}}}' patosgym_prod_web)
    sed -i "s/proxy_pass.*/proxy_pass http:\/\/$IP:8000;/g" /root/Villex/nginx/conf.d/patosgym.conf
    docker exec villex_nginx nginx -s reload
    """
    ssh.exec_command(cmd_fix)

except Exception as e:
    print(f"Error: {e}")
finally:
    ssh.close()
