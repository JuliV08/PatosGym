import paramiko

host = '72.60.63.105'
port = 22
user = 'root'
password = 'VpSH4rd2026K9zX7q'

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    ssh.connect(host, port, user, password)
    
    cmd = """
    sed -i 's/172.17.0.1:18082/72.60.63.105:18082/g' /root/Villex/nginx/conf.d/patosgym.conf
    docker exec villex_nginx nginx -s reload
    sleep 2
    docker exec villex_nginx curl -s -I http://72.60.63.105:18082 -H "Host: patosgym.com.ar"
    """
    stdin, out, err = ssh.exec_command(cmd)
    
    print('CURL OUT:\n', out.read().decode('utf-8'))
    print('CURL ERR:\n', err.read().decode('utf-8'))

except Exception as e:
    print(f"Error: {e}")
finally:
    ssh.close()
