import paramiko

def get_final_status_surgical():
    host = '72.60.63.105'
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, 22, 'root', 'VpSH4rd2026K9zX7q')

    cmd = 'docker exec villex_nginx curl -s -o /dev/null -w "%{http_code}" -H "Host: patosgym.com.ar" http://localhost'
    _, out, _ = ssh.exec_command(cmd)
    code = out.read().decode().strip()
    print(f"ULTIMATE_CODE: {code}")

    ssh.close()

if __name__ == "__main__":
    get_final_status_surgical()
