import paramiko
import time

def final_health_definitive_final():
    host = '72.60.63.105'
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, 22, 'root', 'VpSH4rd2026K9zX7q')

    print("--- WAITING 45s FOR FINAL STARTUP ---")
    time.sleep(45)

    print("--- DOCKER PS (ALL HEALTH) ---")
    _, out, _ = ssh.exec_command('docker ps --format "{{.Names}} | {{.Status}}"')
    print(out.read().decode())

    print("--- PATOSGYM STATUS CODE ---")
    cmd = 'docker exec villex_nginx curl -s -o /dev/null -w "%{http_code}" -H "Host: patosgym.com.ar" http://localhost'
    _, out, _ = ssh.exec_command(cmd)
    print(f"PATOSGYM: {out.read().decode().strip()}")

    print("--- VILLEX STATUS CODE ---")
    cmd_v = 'docker exec villex_nginx curl -s -o /dev/null -w "%{http_code}" -H "Host: villex.com.ar" http://localhost'
    _, out_v, _ = ssh.exec_command(cmd_v)
    print(f"VILLEX: {out_v.read().decode().strip()}")

    ssh.close()

if __name__ == "__main__":
    final_health_definitive_final()
