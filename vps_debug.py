import paramiko

def diagnose():
    host = '72.60.63.105'
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, 22, 'root', 'VpSH4rd2026K9zX7q')

    def run(cmd):
        stdin, out, err = ssh.exec_command(cmd)
        return out.read().decode('utf-8', 'ignore'), err.read().decode('utf-8', 'ignore')

    print("=== 1. NGINX ERROR LOGS (upstream focus) ===")
    out, _ = run("docker exec villex_nginx grep 'upstream' /var/log/nginx/error.log | tail -n 20")
    print(out)

    print("\n=== 2. NGINX ACCESS LOGS (patosgym focus) ===")
    out, _ = run("docker exec villex_nginx grep 'patosgym' /var/log/nginx/access.log | tail -n 20")
    print(out)

    print("\n=== 3. DOCKER NETWORK INSPECT (villex_network) ===")
    out, _ = run("docker network inspect villex_network")
    print(out)

    print("\n=== 4. TEST PING FROM PROXY TO WEB ===")
    out, err = run("docker exec villex_nginx ping -c 1 patosgym_prod_web")
    print(out or err)

    print("\n=== 5. CHECK NGINX patosgym.conf CONTENT AGAIN ===")
    out, _ = run("cat /root/Villex/nginx/conf.d/patosgym.conf")
    print(out)

    ssh.close()

if __name__ == "__main__":
    diagnose()
