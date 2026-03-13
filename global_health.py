import paramiko

def final_health_check():
    host = '72.60.63.105'
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, 22, 'root', 'VpSH4rd2026K9zX7q')

    sites = {
        'PatosGym': 'patosgym.com.ar',
        'Villex': 'villex.com.ar',
        'DYM': 'dymcosmeticos.com.ar'
    }

    print("=== GLOBAL CLUSTER HEALTH CHECK ===")
    for name, domain in sites.items():
        cmd = f"docker exec villex_nginx curl -s -o /dev/null -w '%{{http_code}}' -H 'Host: {domain}' http://localhost"
        _, out, _ = ssh.exec_command(cmd)
        code = out.read().decode().strip()
        # Note: Villex/DYM might return 301 because of HTTP->HTTPS redirects defined in their configs
        print(f"{name} ({domain}): {code}")

    ssh.close()

if __name__ == "__main__":
    final_health_check()
