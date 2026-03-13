import paramiko
import time

def diag_500_internal():
    host = '72.60.63.105'
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, 22, 'root', 'VpSH4rd2026K9zX7q')

    print("--- 1. CHECKING ALLOWED_HOSTS ---")
    _, out, _ = ssh.exec_command('grep -r "ALLOWED_HOSTS" /srv/patosgym/patosgym_project/')
    print(out.read().decode())

    print("--- 2. TESTING DB ACCESS VIA MANAGE.PY ---")
    cmd = 'docker exec patosgym_prod_web python manage.py shell -c "from django.db import connection; cursor = connection.cursor(); cursor.execute(\'SELECT 1\'); print(\'DB_CONNECT_SUCCESS\')"'
    _, out, err = ssh.exec_command(cmd)
    o = out.read().decode()
    e = err.read().decode()
    print("OUT:", o)
    print("ERR:", e)

    print("--- 3. CHECKING INSTALLED APPS AND TEMPLATES ---")
    # Maybe a missing app or template processor
    _, out, _ = ssh.exec_command('cat /srv/patosgym/patosgym_project/base.py || cat /srv/patosgym/patosgym_project/settings.py')
    print(out.read().decode()[:2000]) # First 2k lines

    ssh.close()

if __name__ == "__main__":
    diag_500_internal()
