import paramiko
import time

def deep_diagnose():
    host = '72.60.63.105'
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, 22, 'root', 'VpSH4rd2026K9zX7q')

    def run(cmd):
        stdin, out, err = ssh.exec_command(cmd)
        return out.read().decode('utf-8', 'ignore'), err.read().decode('utf-8', 'ignore')

    print("=== 1. NGINX CONFIG RELOAD & TEST ===")
    out, err = run("docker exec villex_nginx nginx -t")
    print(err) # nginx -t output goes to stderr usually

    print("\n=== 2. TAILING ERROR LOG DURING INTERNAL CURL ===")
    # Clear logs or just get last few
    run("docker exec villex_nginx truncate -s 0 /var/log/nginx/error.log")
    
    # Try internal curl again to see if it generates an error now
    run("docker exec villex_nginx curl -s -I -H 'Host: patosgym.com.ar' http://localhost")
    
    out, _ = run("docker exec villex_nginx cat /var/log/nginx/error.log")
    print("Errors after internal curl:\n", out)

    print("\n=== 3. CHECKING UPSTREAM DNS RESOLUTION INSIDE NGINX ===")
    out, _ = run("docker exec villex_nginx getent hosts patosgym_prod_web")
    print("DNS Lookup for web container:", out)

    print("\n=== 4. INSPECTING NGINX CONTAINER NETWORKS AGAIN ===")
    out, _ = run("docker inspect villex_nginx --format '{{json .NetworkSettings.Networks}}'")
    print("Networks:", out)

    print("\n=== 5. CHECKING IF PORT 8000 IS ACCESSIBLE FROM NGINX CONTAINER VIA IP ===")
    # Get backend IP
    backend_inspect, _ = run("docker inspect patosgym_prod_web --format '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}'")
    backend_ip = backend_inspect.strip()
    print(f"Backend IP: {backend_ip}")
    if backend_ip:
        out, err = run(f"docker exec villex_nginx curl -s -I http://{backend_ip}:8000")
        print(f"Curl to {backend_ip}:8000:", out or err)
    else:
         # Maybe it's not on the same network as I thought?
         print("Backend IP not found via direct inspect. Showing all networks.")
         out, _ = run("docker inspect patosgym_prod_web --format '{{json .NetworkSettings.Networks}}'")
         print(out)

    ssh.close()

if __name__ == "__main__":
    deep_diagnose()
