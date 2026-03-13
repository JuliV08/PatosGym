import paramiko
import json

def surgical_diag():
    host = '72.60.63.105'
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, 22, 'root', 'VpSH4rd2026K9zX7q')

    def run(cmd):
        stdin, out, err = ssh.exec_command(cmd)
        return out.read().decode('utf-8', 'ignore'), err.read().decode('utf-8', 'ignore')

    print("=== DOCKER PS (ALL) ===")
    out, _ = run("docker ps --format '{{.Names}} | {{.Image}} | {{.Status}}'")
    print(out)

    print("=== NGINX ERROR LOGS (LAST 50) ===")
    out, _ = run("docker exec villex_nginx tail -n 50 /var/log/nginx/error.log")
    print(out)

    print("=== PATOSGYM WEB LOGS (LAST 100) ===")
    out, err = run("docker logs patosgym_prod_web")
    print(out[-2000:]) # Last 2k chars
    print(err[-2000:])

    print("=== NETSTAT INSIDE WEB ===")
    out, err = run("docker exec patosgym_prod_web netstat -tlnp")
    print(out or err)

    print("=== TRYING TO CURL WEB BY SERVICE NAME FROM NGINX ===")
    out, err = run("docker exec villex_nginx curl -I http://patosgym_web:8000")
    print(out or err)

    ssh.close()

if __name__ == "__main__":
    surgical_diag()
