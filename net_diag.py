import paramiko
import json

host = '72.60.63.105'
port = 22
user = 'root'
password = 'VpSH4rd2026K9zX7q'

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    ssh.connect(host, port, user, password)
    
    print("--- Villex Nginx Networks ---")
    _,out,_ = ssh.exec_command("docker inspect villex_nginx")
    data = json.loads(out.read().decode('utf-8'))[0]
    networks = data['NetworkSettings']['Networks']
    for net, info in networks.items():
        print(f"Network: {net}, IP: {info['IPAddress']}")
        
    print("\n--- Connecting patosgym_prod_web to Nginx network ---")
    nginx_net = list(networks.keys())[0] # Usar la primera red (probablemente bridge/villex)
    _,out2,err2 = ssh.exec_command(f"docker network connect {nginx_net} patosgym_prod_web")
    print("Connect OUT:", out2.read().decode('utf-8'))
    print("Connect ERR:", err2.read().decode('utf-8'))
    
except Exception as e:
    print(f"Error: {e}")
finally:
    ssh.close()
