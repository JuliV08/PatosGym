import paramiko
import time

def final_status_check():
    host = '72.60.63.105'
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, 22, 'root', 'VpSH4rd2026K9zX7q')

    print("--- WAITING 15s FOR STARTUP ---")
    time.sleep(15)

    print("--- DOCKER PS ---")
    _, out, _ = ssh.exec_command('docker ps --format "{{.Names}} | {{.Status}}"')
    print(out.read().decode())

    print("--- NGINX INTERNAL REQUEST TEST ---")
    # Verify PatosGym via Host header from Nginx
    cmd = 'docker exec villex_nginx curl -s -I -H "Host: patosgym.com.ar" http://localhost'
    _, out, _ = ssh.exec_command(cmd)
    print(out.read().decode())

    print("--- NGINX RELOAD STATUS ---")
    _, out, err = ssh.exec_command('docker exec villex_nginx nginx -t')
    print(err.read().decode())

    ssh.close()

if __name__ == "__main__":
    final_status_check()
