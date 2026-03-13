import paramiko
import json

def definitive_audit():
    host = '72.60.63.105'
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, 22, 'root', 'VpSH4rd2026K9zX7q')

    def run(cmd):
        stdin, out, err = ssh.exec_command(cmd)
        return out.read().decode('utf-8', 'ignore'), err.read().decode('utf-8', 'ignore')

    print("=== 1. DOCKER PS ===")
    out, _ = run("docker ps --format '{{.Names}} | {{.Status}}'")
    print(out)

    print("=== 2. DB USERS DEFINITIVE ===")
    # We try to use the superuser to list users. Usually 'postgres' or whoever was set.
    # If the container was re-init with POSTGRES_USER=patosgym_user, then that might be the superuser.
    out, err = run("docker exec patosgym_prod_db psql -U patosgym_user -c '\du' patosgym")
    print("AS patosgym_user:", out or err)
    
    out, err = run("docker exec patosgym_prod_db psql -U postgres -c '\du'")
    print("AS postgres:", out or err)

    print("=== 3. WEB ENVIRONMENT DEFINITIVE ===")
    out, _ = run("docker exec patosgym_prod_web env | grep DATABASE")
    print(out)

    print("=== 4. SETTINGS FILE ON DISK ===")
    # Check what's actually in the container
    out, _ = run("docker exec patosgym_prod_web cat /app/patosgym_project/settings/production.py")
    print(out)

    ssh.close()

if __name__ == "__main__":
    definitive_audit()
