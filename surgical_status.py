import paramiko

def get_patosgym_status():
    host = '72.60.63.105'
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, 22, 'root', 'VpSH4rd2026K9zX7q')

    cmd = 'docker exec villex_nginx curl -s -o /dev/null -w "%{http_code}" -H "Host: patosgym.com.ar" http://localhost'
    _, out, _ = ssh.exec_command(cmd)
    code = out.read().decode().strip()
    print(f"PATOSGYM_CODE: {code}")

    cmd_v = 'docker exec villex_nginx curl -s -o /dev/null -w "%{http_code}" -H "Host: villex.com.ar" http://localhost'
    _, out_v, _ = ssh.exec_command(cmd_v)
    code_v = out_v.read().decode().strip()
    print(f"VILLEX_CODE: {code_v}")

    ssh.close()

if __name__ == "__main__":
    get_patosgym_status()
