import paramiko
import time

def debug_500():
    host = '72.60.63.105'
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, 22, 'root', 'VpSH4rd2026K9zX7q')

    print("--- TRIGGERING REQUEST AND TAILING LOGS ---")
    # We run a tail in background or just run request and then check logs
    ssh.exec_command('docker exec villex_nginx curl -s -I -H "Host: patosgym.com.ar" http://localhost')
    time.sleep(2)
    
    _, out, err = ssh.exec_command('docker logs patosgym_prod_web --tail 100')
    output = out.read().decode()
    errors = err.read().decode()
    
    print("=== STDOUT ===")
    print(output)
    print("=== STDERR ===")
    print(errors)

    ssh.close()

if __name__ == "__main__":
    debug_500()
