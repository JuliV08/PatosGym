import paramiko
import json

def get_full_state():
    host = '72.60.63.105'
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, 22, 'root', 'VpSH4rd2026K9zX7q')

    print("=== DOCKER PS (concise) ===")
    _, out, _ = ssh.exec_command('docker ps --format "{{.Names}}"')
    print(out.read().decode())

    print("=== DOCKER NETWORKS ===")
    _, out, _ = ssh.exec_command('docker network ls')
    print(out.read().decode())

    print("=== PATOSGYM COMPOSE === ")
    _, out, _ = ssh.exec_command('cat /srv/patosgym/docker-compose.prod.yml')
    print(out.read().decode())

    print("=== NGINX CONFIG TEST ERROR ===")
    _, out, err = ssh.exec_command('docker exec villex_nginx nginx -t')
    print(err.read().decode())

    ssh.close()

if __name__ == "__main__":
    get_full_state()
