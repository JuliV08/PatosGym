import paramiko

host = '72.60.63.105'
port = 22
user = 'root'
password = 'VpSH4rd2026K9zX7q'

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    ssh.connect(host, port, user, password)
    
    cmd_up = "cd /srv/patosgym && docker compose -f docker-compose.prod.yml up -d"
    _,out,err = ssh.exec_command(cmd_up)
    
    print('COMPOSE OUT:\n', out.read().decode('utf-8'))
    print('COMPOSE ERR:\n', err.read().decode('utf-8'))

    cmd_ps = "docker ps -a | grep patosgym"
    _,out2,_ = ssh.exec_command(cmd_ps)
    print('PS:\n', out2.read().decode('utf-8'))

except Exception as e:
    print(f"Error: {e}")
finally:
    ssh.close()
