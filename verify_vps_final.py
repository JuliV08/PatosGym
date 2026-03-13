import paramiko

def verify():
    host = '72.60.63.105'
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, 22, 'root', 'VpSH4rd2026K9zX7q')

    print("--- 1. CONTAINER STATUS ---")
    _, out, _ = ssh.exec_command("docker ps | grep patosgym")
    print(out.read().decode())

    print("--- 2. NGINX INTERNAL TEST (patosgym.com.ar) ---")
    # We simulate a request to port 80 with the correct Host header
    _, out, err = ssh.exec_command("docker exec villex_nginx curl -s -I -H 'Host: patosgym.com.ar' http://localhost")
    print(out.read().decode())
    print(err.read().decode())

    print("--- 3. PATOSGYM LOGS (last 5) ---")
    _, out, _ = ssh.exec_command("docker logs patosgym_prod_web --tail 5")
    print(out.read().decode())

    ssh.close()

if __name__ == "__main__":
    verify()
