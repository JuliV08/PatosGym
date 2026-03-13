import paramiko
import time

def verify_and_fix():
    host = '72.60.63.105'
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, 22, 'root', 'VpSH4rd2026K9zX7q')

    def run(cmd):
        stdin, out, err = ssh.exec_command(cmd)
        return out.read().decode('utf-8', 'ignore'), err.read().decode('utf-8', 'ignore')

    print("=== 1. CONTAINER STATUS ===")
    out, _ = run('docker ps --filter name=patosgym_prod_web --format "{{.Names}} | {{.Status}}"')
    print(out)

    print("=== 2. PING FROM NGINX TO WEB ===")
    out, err = run('docker exec villex_nginx ping -c 1 patosgym_prod_web')
    print(out or err)

    print("=== 3. NGINX CONFIG TEST ===")
    out, err = run('docker exec villex_nginx nginx -t')
    print(err) # nginx -t output is in stderr

    print("=== 4. ATTEMPT RELOAD ===")
    out, err = run('docker exec villex_nginx nginx -s reload')
    print(out or err)

    ssh.close()

if __name__ == "__main__":
    verify_and_fix()
