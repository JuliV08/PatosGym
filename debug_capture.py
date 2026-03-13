import paramiko
import time

def debug_enable():
    host = '72.60.63.105'
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, 22, 'root', 'VpSH4rd2026K9zX7q')

    print("--- 1. ENABLING DEBUG IN COMPOSE ---")
    ssh.exec_command('sed -i "s/DEBUG=0/DEBUG=1/g" /root/Villex/docker-compose.prod.yml')
    ssh.exec_command('cd /root/Villex && docker compose up -d patosgym_web')
    
    print("--- 2. WAITING FOR RESTART ---")
    time.sleep(10)

    print("--- 3. FETCHING THE ERROR ---")
    # We curl and get the body. Since it's HTML from Django debug, we'll just grep for the title/exception
    cmd = 'docker exec villex_nginx curl -s -H "Host: patosgym.com.ar" http://localhost | grep -A 5 "exception_value"'
    _, out, _ = ssh.exec_command(cmd)
    print(out.read().decode())

    ssh.close()

if __name__ == "__main__":
    debug_enable()
