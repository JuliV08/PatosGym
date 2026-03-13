import paramiko

def final_db_fix():
    host = '72.60.63.105'
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, 22, 'root', 'VpSH4rd2026K9zX7q')

    print("--- 1. STOPPING STACK ---")
    ssh.exec_command('cd /root/Villex && docker compose down')

    # Since the user said it's a small gallery and works is more important than data right now,
    # we will wipe the DB volume to let it re-init with 'patosgym_user' exactly as in the compose.
    print("--- 2. WIPING DB DATA FOR CLEAN INIT ---")
    ssh.exec_command('rm -rf /srv/patosgym/volumes/db_data/*')

    print("--- 3. STARTING STACK ---")
    ssh.exec_command('cd /root/Villex && docker compose up -d')

    ssh.close()

if __name__ == "__main__":
    final_db_fix()
