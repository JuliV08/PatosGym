import paramiko
import time

def get_traceback_surgical():
    host = '72.60.63.105'
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, 22, 'root', 'VpSH4rd2026K9zX7q')

    # Trigger a request
    ssh.exec_command('docker exec villex_nginx curl -s -I -H "Host: patosgym.com.ar" http://localhost')
    time.sleep(1)

    # Get logs
    _, out, err = ssh.exec_command('docker logs patosgym_prod_web --tail 20')
    output = out.read().decode()
    errors = err.read().decode()
    
    print("=== FINAL LOGS ===")
    print(output)
    print(errors)

    ssh.close()

if __name__ == "__main__":
    get_traceback_surgical()
