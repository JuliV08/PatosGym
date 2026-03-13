import paramiko
import json

def verify():
    host = '72.60.63.105'
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, 22, 'root', 'VpSH4rd2026K9zX7q')

    def run(cmd):
        stdin, out, err = ssh.exec_command(cmd)
        return out.read().decode('utf-8', 'ignore'), err.read().decode('utf-8', 'ignore')

    print("=== 1. CONTAINER STATUS ===")
    out, _ = run('docker ps --filter name=patosgym')
    print(out)

    print("\n=== 2. NGINX CONFIG TEST ===")
    out, err = run('docker exec villex_nginx nginx -t')
    print("STDOUT:", out)
    print("STDERR:", err)

    print("\n=== 3. NETWORK IPS ON VILLEX_NETWORK ===")
    out, _ = run("docker network inspect villex_network --format '{{json .Containers}}'")
    try:
        containers = json.loads(out)
        for cid, info in containers.items():
            print(f"Container: {info['Name']} | IP: {info['IPv4Address']}")
    except Exception as e:
        print(f"Error parsing network: {e}")

    print("\n=== 4. CURL BACKEND FROM NGINX CONTAINER ===")
    out, err = run('docker exec villex_nginx curl -s -I http://patosgym_prod_web:8000')
    print("Header Result:", out or err)

    print("\n=== 5. NGINX RELOAD ===")
    out, err = run('docker exec villex_nginx nginx -s reload')
    print("Reload Result:", out or err)

    ssh.close()

if __name__ == "__main__":
    verify()
