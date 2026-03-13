import paramiko
import time

def verify_site():
    host = '72.60.63.105'
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, 22, 'root', 'VpSH4rd2026K9zX7q')

    print("--- 1. WEB CONTAINER LOGS (GUNICORN) ---")
    _, out, _ = ssh.exec_command('docker logs patosgym_prod_web --tail 20')
    print(out.read().decode())

    print("--- 2. INTERNAL NGINX PROXY TEST ---")
    # Simulate a request from the proxy to the backend
    _, out, _ = ssh.exec_command('docker exec villex_nginx curl -I -H "Host: patosgym.com.ar" http://localhost')
    print(out.read().decode())

    print("--- 3. CHECKING ALL SERVICES STATUS ---")
    _, out, _ = ssh.exec_command('cd /root/Villex && docker compose ps')
    print(out.read().decode())

    ssh.close()

if __name__ == "__main__":
    verify_site()
