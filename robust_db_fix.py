import paramiko

def fix_db():
    host = '72.60.63.105'
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, 22, 'root', 'VpSH4rd2026K9zX7q')

    print("--- 1. CHECKING CURRENT DB STATUS ---")
    _, out, _ = ssh.exec_command('docker logs patosgym_prod_db --tail 10')
    print(out.read().decode())

    # Try to create user if it doesn't exist, and reset password.
    # We use the default 'postgres' user to execute admin commands.
    # Note: If the container was initialized with a different POSTGRES_USER, we might need that.
    
    commands = [
        # Check if user 'patosgym_user' exists, if not create it.
        "docker exec patosgym_prod_db psql -U postgres -c \"DO $$ BEGIN IF NOT EXISTS (SELECT FROM pg_catalog.pg_user WHERE usename = 'patosgym_user') THEN CREATE USER patosgym_user WITH PASSWORD 'patosgym_prod_pass_2024'; END IF; END $$;\"",
        # Ensure it has permissions on the database 'patosgym'
        "docker exec patosgym_prod_db psql -U postgres -c \"GRANT ALL PRIVILEGES ON DATABASE patosgym TO patosgym_user;\"",
        # Set the password again just in case
        "docker exec patosgym_prod_db psql -U postgres -c \"ALTER USER patosgym_user WITH PASSWORD 'patosgym_prod_pass_2024';\""
    ]

    for cmd in commands:
        print(f"Running: {cmd}")
        _, out, err = ssh.exec_command(cmd)
        print('OUT:', out.read().decode())
        print('ERR:', err.read().decode())

    print("--- 2. RESTARTING WEB CONTAINER ---")
    ssh.exec_command('docker restart patosgym_prod_web')

    ssh.close()

if __name__ == "__main__":
    fix_db()
