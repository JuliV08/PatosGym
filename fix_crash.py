import paramiko

host = '72.60.63.105'
port = 22
user = 'root'
password = 'VpSH4rd2026K9zX7q'

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    ssh.connect(host, port, user, password)
    
    _,out,_ = ssh.exec_command("cat /srv/patosgym/docker-compose.prod.yml")
    compose_content = out.read().decode('utf-8')
    
    # Fix the Gunicorn command string that was broken by sed
    import re
    # Fix command
    new_compose = compose_content.replace(
        "0.0.0.0:0.0.0.0:8000", "0.0.0.0:8000"
    ).replace(
        "0.0.0.0:127.0.0.1:8000", "0.0.0.0:8000"
    )
    
    sftp = ssh.open_sftp()
    with open('remote_compose_fix.yml', 'w') as f:
        f.write(new_compose)
    sftp.put('remote_compose_fix.yml', '/srv/patosgym/docker-compose.prod.yml')
    sftp.close()
    
    # Restart
    ssh.exec_command("cd /srv/patosgym && docker compose -f docker-compose.prod.yml down && docker compose -f docker-compose.prod.yml up -d")
    
    import time
    time.sleep(5)
    
    _,out2,err2 = ssh.exec_command("docker ps -a | grep patosgym")
    print('PS:\n', out2.read().decode('utf-8'))

    _,out3,_ = ssh.exec_command("docker exec villex_nginx curl -s -I http://172.17.0.1:18082 -H 'Host: patosgym.com.ar'")
    print('CURL OUT:\n', out3.read().decode('utf-8'))
    
except Exception as e:
    print(f"Error: {e}")
finally:
    ssh.close()
