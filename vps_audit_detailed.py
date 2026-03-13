import paramiko
import json

def audit_vps():
    host = '72.60.63.105'
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, 22, 'root', 'VpSH4rd2026K9zX7q')

    def run(cmd):
        _, out, err = ssh.exec_command(cmd)
        return out.read().decode('utf-8', 'ignore')

    results = {}

    results['nginx_files'] = run('ls -la /root/Villex/nginx/conf.d/')
    
    files = run('ls /root/Villex/nginx/conf.d/').strip().split()
    results['configs'] = {}
    for f in files:
        if f.endswith('.conf'):
            results['configs'][f] = run(f'cat /root/Villex/nginx/conf.d/{f}')

    results['docker_networks'] = run('docker network ls')
    results['nginx_inspect'] = run('docker inspect villex_nginx')
    results['patosgym_inspect'] = run('docker inspect patosgym_prod_web')
    
    ssh.close()
    
    with open('vps_audit_detailed.json', 'w') as f:
        json.dump(results, f, indent=4)

if __name__ == "__main__":
    audit_vps()
