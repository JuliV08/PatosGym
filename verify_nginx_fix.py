import paramiko

def verify():
    host = '72.60.63.105'
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, 22, 'root', 'VpSH4rd2026K9zX7q')

    print("--- 1. NGINX STATUS & ERROR LOGS ---")
    _, out, err = ssh.exec_command('docker exec villex_nginx nginx -t')
    print("NGINX T ERR (should show ok):\n", err.read().decode())

    print("\n--- 2. INTERNAL CURL TEST (STATUS CODE) ---")
    # Using -s -o /dev/null -w "%{http_code}" to get just the code
    _, out, _ = ssh.exec_command('docker exec villex_nginx curl -s -o /dev/null -w "%{http_code}" -H "Host: patosgym.com.ar" http://localhost')
    print("HTTP STATUS CODE:", out.read().decode())

    print("\n--- 3. PATOSGYM WEB LOGS ---")
    _, out, _ = ssh.exec_command('docker logs patosgym_prod_web --tail 20')
    print(out.read().decode())

    print("\n--- 4. CHECKING NGINX SITE ENABLED LINKS ---")
    # Just to be sure it's reading from conf.d
    _, out, _ = ssh.exec_command('docker exec villex_nginx ls /etc/nginx/conf.d/')
    print("Files in conf.d inside container:\n", out.read().decode())

    ssh.close()

if __name__ == "__main__":
    verify()
