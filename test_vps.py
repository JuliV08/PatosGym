import paramiko

host = '72.60.63.105'
port = 22
user = 'root'
password = 'VpSH4rd2026K9zX7q'

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    ssh.connect(host, port, user, password)
    script = """
    cd /srv/patosgym
    echo "DEBUG=0" > .env.prod
    echo "SECRET_KEY=dummy" >> .env.prod
    echo "POSTGRES_DB=db" > .env.prod.db
    echo "POSTGRES_USER=user" >> .env.prod.db
    echo "POSTGRES_PASSWORD=pass" >> .env.prod.db
    docker compose -f docker-compose.prod.yml config
    """
    stdin, stdout, stderr = ssh.exec_command(script)
    print(stdout.read().decode('utf-8'))
    print("ERRORS:", stderr.read().decode('utf-8'))
except Exception as e:
    print(f"Error: {e}")
finally:
    ssh.close()
