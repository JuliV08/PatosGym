import paramiko

host = '72.60.63.105'
port = 22
user = 'root'
password = 'VpSH4rd2026K9zX7q'

commands = [
    'docker ps -a',
    'docker network ls',
    'docker volume ls',
    'ss -tuln'
]

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    ssh.connect(host, port, user, password)
    with open('audit_output.txt', 'w') as f:
        for cmd in commands:
            f.write(f"--- {cmd} ---\n")
            stdin, stdout, stderr = ssh.exec_command(cmd)
            f.write(stdout.read().decode('utf-8'))
            f.write("\n")
finally:
    ssh.close()
