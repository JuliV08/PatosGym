import paramiko
import json

def get_vps_data():
    host = '72.60.63.105'
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, 22, 'root', 'VpSH4rd2026K9zX7q')

    data = {}

    # 1. Container Names and IDs
    _, out, _ = ssh.exec_command('docker ps --format "{{.ID}}|{{.Names}}|{{.Image}}"')
    data['containers'] = [line.split('|') for line in out.read().decode().strip().splitlines()]

    # 2. Detailed Inspect of all running containers
    _, out, _ = ssh.exec_command('docker inspect $(docker ps -q)')
    data['inspect'] = json.loads(out.read().decode())

    # 3. Network List
    _, out, _ = ssh.exec_command('docker network ls --format "{{.Name}}|{{.Driver}}|{{.ID}}"')
    data['networks'] = [line.split('|') for line in out.read().decode().strip().splitlines()]

    # 4. Nginx patosgym.conf
    _, out, _ = ssh.exec_command('cat /root/Villex/nginx/conf.d/patosgym.conf')
    data['patosgym_conf'] = out.read().decode()

    # 5. Nginx default.conf
    _, out, _ = ssh.exec_command('cat /root/Villex/nginx/conf.d/default.conf')
    data['default_conf'] = out.read().decode()

    # Save to local file
    with open('vps_full_state.json', 'w') as f:
        json.dump(data, f, indent=4)

    ssh.close()

if __name__ == "__main__":
    get_vps_data()
