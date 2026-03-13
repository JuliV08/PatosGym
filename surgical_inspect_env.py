import paramiko
import json

def get_inspect():
    host = '72.60.63.105'
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, 22, 'root', 'VpSH4rd2026K9zX7q')

    print("--- DB INSPECT ---")
    _, out, _ = ssh.exec_command('docker inspect patosgym_prod_db')
    data = json.loads(out.read().decode())
    env = data[0]['Config']['Env']
    for e in env:
        print(e)
    
    print("\n--- WEB INSPECT ---")
    _, out, _ = ssh.exec_command('docker inspect patosgym_prod_web')
    data = json.loads(out.read().decode())
    env = data[0]['Config']['Env']
    for e in env:
        print(e)

    ssh.close()

if __name__ == "__main__":
    get_inspect()
