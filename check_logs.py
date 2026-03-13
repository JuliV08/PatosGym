import paramiko

host = '72.60.63.105'
port = 22
user = 'root'
password = 'VpSH4rd2026K9zX7q'

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    ssh.connect(host, port, user, password)
    
    _,out,_ = ssh.exec_command('docker ps --filter "name=patosgym_prod_web" --format "{{.Ports}}"')
    print('PORTS:\n', out.read().decode('utf-8'))
    
    _,out2,_ = ssh.exec_command('docker logs patosgym_prod_web --tail 10')
    print('GUNICORN LOGS:\n', out2.read().decode('utf-8'))

except Exception as e:
    print(f"Error: {e}")
finally:
    ssh.close()
