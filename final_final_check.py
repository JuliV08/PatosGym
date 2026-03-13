import paramiko
import time

def final_final_check():
    host = '72.60.63.105'
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, 22, 'root', 'VpSH4rd2026K9zX7q')

    print("--- 1. RUNNING MIGRATIONS (DEFINITIVE) ---")
    _, out, err = ssh.exec_command('docker exec patosgym_prod_web python manage.py migrate')
    print('OUT:', out.read().decode())
    print('ERR:', err.read().decode())

    print("--- 2. CHECKING HTTP STATUS ---")
    cmd = 'docker exec villex_nginx curl -s -o /dev/null -w "%{http_code}" -H "Host: patosgym.com.ar" http://localhost'
    _, out, _ = ssh.exec_command(cmd)
    code = out.read().decode().strip()
    print(f"STATUS CODE: {code}")

    print("--- 3. CHECKING VILLEX STATUS ---")
    cmd_v = 'docker exec villex_nginx curl -s -o /dev/null -w "%{http_code}" -H "Host: villex.com.ar" http://localhost'
    _, out_v, _ = ssh.exec_command(cmd_v)
    print(f"VILLEX CODE: {out_v.read().decode().strip()}")

    ssh.close()

if __name__ == "__main__":
    final_final_check()
