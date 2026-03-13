import paramiko

def deep_check():
    host = '72.60.63.105'
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, 22, 'root', 'VpSH4rd2026K9zX7q')

    def run(cmd):
        stdin, out, err = ssh.exec_command(cmd)
        return out.read().decode('utf-8', 'ignore'), err.read().decode('utf-8', 'ignore')

    print("=== 1. CHECKING IF GUNICORN IS LISTENING ===")
    out, err = run('docker exec patosgym_prod_web netstat -tulnp')
    print(out or err)

    print("\n=== 2. CHECKING DATABASE CONNECTIVITY FROM WEB ===")
    out, err = run('docker exec patosgym_prod_web python manage.py check')
    print(out, err)

    print("\n=== 3. CHECKING NGINX UPSTREAM LOGS ===")
    out, err = run('docker exec villex_nginx tail -n 20 /var/log/nginx/error.log')
    print(out)

    ssh.close()

if __name__ == "__main__":
    deep_check()
