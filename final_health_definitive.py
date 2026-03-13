import paramiko
import time

def final_health_check_definitive():
    host = '72.60.63.105'
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, 22, 'root', 'VpSH4rd2026K9zX7q')

    print("--- WAITING 45s FOR FULL DEPLOYMENT ---")
    time.sleep(45)

    print("--- DOCKER PS (STATUS) ---")
    _, out, _ = ssh.exec_command('docker ps --format "{{.Names}} | {{.Status}}"')
    print(out.read().decode())

    print("--- WEB CONTAINER LOGS ---")
    _, out, _ = ssh.exec_command('docker logs patosgym_prod_web --tail 50')
    print(out.read().decode())

    print("--- INTERNAL HTTP TEST (PATOSGYM) ---")
    cmd = 'docker exec villex_nginx curl -s -I -H "Host: patosgym.com.ar" http://localhost'
    _, out, _ = ssh.exec_command(cmd)
    print(out.read().decode())

    print("--- INTERNAL HTTP TEST (VILLEX) ---")
    cmd = 'docker exec villex_nginx curl -s -I -H "Host: villex.com.ar" http://localhost'
    _, out, _ = ssh.exec_command(cmd)
    print(out.read().decode())

    ssh.close()

if __name__ == "__main__":
    final_health_check_definitive()
