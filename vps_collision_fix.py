import paramiko

def fix_collision():
    host = '72.60.63.105'
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, 22, 'root', 'VpSH4rd2026K9zX7q')

    def run(cmd):
        stdin, out, err = ssh.exec_command(cmd)
        return out.read().decode('utf-8', 'ignore'), err.read().decode('utf-8', 'ignore')

    print("--- 1. NGINX ERROR LOGS (conflicts/upstream) ---")
    out, _ = run("docker exec villex_nginx grep -E 'conflicting|upstream|denied' /var/log/nginx/error.log | tail -n 20")
    print(out)

    print("\n--- 2. NGINX CONFIG DUMP (Resolution) ---")
    out, _ = run("docker exec villex_nginx nginx -T | grep -E 'server_name|listen'")
    print(out)

    print("\n--- 3. CHECKING IF CLOUDFLARE IS HITTING 443 OR 80 ---")
    # I'll look for recent requests to patosgym and see their port
    out, _ = run("docker exec villex_nginx grep 'patosgym' /var/log/nginx/access.log | tail -n 10")
    print(out)

    ssh.close()

if __name__ == "__main__":
    fix_collision()
