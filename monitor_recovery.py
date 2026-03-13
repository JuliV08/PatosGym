import paramiko
import time

def monitor_recovery():
    host = '72.60.63.105'
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, 22, 'root', 'VpSH4rd2026K9zX7q')

    print("--- 1. WEB LOGS (CHECKING MIGRATIONS/BOOT) ---")
    _, out, _ = ssh.exec_command('docker logs patosgym_prod_web --tail 50')
    print(out.read().decode())

    print("--- 2. DB LOGS (CHECKING AUTH) ---")
    _, out, _ = ssh.exec_command('docker logs patosgym_prod_db --tail 20')
    print(out.read().decode())

    print("--- 3. HTTP STATUS CHECK ---")
    cmd = 'docker exec villex_nginx curl -s -o /dev/null -w "%{http_code}" -H "Host: patosgym.com.ar" http://localhost'
    _, out, _ = ssh.exec_command(cmd)
    code = out.read().decode().strip()
    print(f"STATUS CODE: {code}")

    ssh.close()

if __name__ == "__main__":
    monitor_recovery()
