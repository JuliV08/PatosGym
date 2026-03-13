import paramiko
import time

def capture_500_full():
    host = '72.60.63.105'
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, 22, 'root', 'VpSH4rd2026K9zX7q')

    print("--- 1. TRIGGERING REQUEST ---")
    cmd = 'docker exec villex_nginx curl -s -D - -H "Host: patosgym.com.ar" http://localhost'
    _, out, _ = ssh.exec_command(cmd)
    full_resp = out.read().decode()
    print("--- RESPONSE HEADERS/BODY ---")
    print(full_resp[:2000])

    print("\n--- 2. CHECKING WEB LOGS IMMEDIATELY ---")
    _, out, _ = ssh.exec_command('docker logs patosgym_prod_web --tail 20')
    print(out.read().decode())

    ssh.close()

if __name__ == "__main__":
    capture_500_full()
