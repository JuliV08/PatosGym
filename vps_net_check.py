import paramiko
import json

def net_diag():
    host = '72.60.63.105'
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, 22, 'root', 'VpSH4rd2026K9zX7q')

    def run(cmd):
        stdin, out, err = ssh.exec_command(cmd)
        return out.read().decode('utf-8', 'ignore'), err.read().decode('utf-8', 'ignore')

    print("=== 1. NGINX NETWORK INFO ===")
    out, _ = run("docker inspect villex_nginx --format '{{json .NetworkSettings.Networks}}'")
    print(out)

    print("\n=== 2. WEB NETWORK INFO ===")
    out, _ = run("docker inspect patosgym_prod_web --format '{{json .NetworkSettings.Networks}}'")
    print(out)

    print("\n=== 3. NETWORK LIST ===")
    out, _ = run("docker network ls")
    print(out)

    print("\n=== 4. TESTING PING BY IP ===")
    # Extract IP of web from JSON
    try:
        inspect, _ = run("docker inspect patosgym_prod_web")
        data = json.loads(inspect)[0]
        villex_net = data['NetworkSettings']['Networks'].get('villex_network', {})
        ip = villex_net.get('IPAddress')
        if ip:
            print(f"Pinging {ip} from nginx...")
            p_out, p_err = run(f"docker exec villex_nginx ping -c 1 {ip}")
            print(p_out or p_err)
        else:
            print("No IP found for patosgym_prod_web on villex_network")
    except Exception as e:
        print(f"Error extracting IP: {e}")

    ssh.close()

if __name__ == "__main__":
    net_diag()
