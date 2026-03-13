import paramiko
import time

host = '72.60.63.105'
port = 22
user = 'root'
password = 'VpSH4rd2026K9zX7q'

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    ssh.connect(host, port, user, password)
    
    cmd1 = "sed -i 's/72.60.63.105/172.17.0.1/g' /root/Villex/nginx/conf.d/patosgym.conf"
    ssh.exec_command(cmd1)
    
    cmd2 = "docker exec villex_nginx nginx -s reload"
    ssh.exec_command(cmd2)
    time.sleep(2)
    
    cmd3 = "docker exec villex_nginx curl -s -I http://172.17.0.1:18082 -H 'Host: patosgym.com.ar'"
    stdin, out, err = ssh.exec_command(cmd3)
    
    print("CURL RESULT:\n", out.read().decode('utf-8'))
    print("ERRORS:\n", err.read().decode('utf-8'))
    
except Exception as e:
    print(f"Error: {e}")
finally:
    ssh.close()
