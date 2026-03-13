import paramiko

def get_nginx_error():
    host = '72.60.63.105'
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, 22, 'root', 'VpSH4rd2026K9zX7q')

    # Run nginx -t and capture stderr specifically
    print("--- 1. NGINX TEST ERROR ---")
    _, out, err = ssh.exec_command('docker exec villex_nginx nginx -t')
    print("OUT:", out.read().decode())
    print("ERR:", err.read().decode())

    print("\n--- 2. CURRENT patosgym.conf CONTENT ---")
    _, out, _ = ssh.exec_command('cat /root/Villex/nginx/conf.d/patosgym.conf')
    print(out.read().decode())

    print("\n--- 3. CHECKING IF PORT 80 IS CLASHING INSIDE CONTAINER ---")
    _, out, _ = ssh.exec_command('docker exec villex_nginx netstat -tlnp')
    print(out.read().decode())

    ssh.close()

if __name__ == "__main__":
    get_nginx_error()
