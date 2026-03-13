import paramiko
import json

def get_containers():
    host = '72.60.63.105'
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, 22, 'root', 'VpSH4rd2026K9zX7q')

    # Get all container info in JSON
    _, out, _ = ssh.exec_command('docker inspect $(docker ps -q)')
    data = out.read().decode()
    containers = json.loads(data)
    
    print("=== DOCKER CONTAINERS ===")
    for c in containers:
        name = c['Name'].lstrip('/')
        networks = c['NetworkSettings']['Networks']
        print(f"Container: {name}")
        for net_name, net_info in networks.items():
            print(f"  - Network: {net_name}, IP: {net_info['IPAddress']}")
    
    ssh.close()

if __name__ == "__main__":
    get_containers()
