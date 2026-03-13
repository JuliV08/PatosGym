import paramiko
import os

def sync_project():
    host = '72.60.63.105'
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, 22, 'root', 'VpSH4rd2026K9zX7q')

    print("--- 1. CLEANING MESS ON VPS ---")
    ssh.exec_command('rm -rf /srv/patosgym/patosgym_project/settings /srv/patosgym/patosgym_project/settings.py /srv/patosgym/patosgym_project/base.py')

    sftp = ssh.open_sftp()
    
    local_dir = r'C:\Users\Villex\dev\PatosGym\patosgym_project'
    remote_dir = '/srv/patosgym/patosgym_project'

    def put_dir(local_path, remote_path):
        try:
            sftp.mkdir(remote_path)
        except IOError:
            pass
        
        for item in os.listdir(local_path):
            if item == '__pycache__': continue
            l_item = os.path.join(local_path, item)
            r_item = os.path.join(remote_path, item).replace('\\', '/')
            if os.path.isfile(l_item):
                print(f"Uploading {item}")
                sftp.put(l_item, r_item)
            elif os.path.isdir(l_item):
                put_dir(l_item, r_item)

    print("--- 2. UPLOADING PROJECT FILES ---")
    put_dir(local_dir, remote_dir)
    sftp.close()

    print("--- 3. RESTARTING WEB ---")
    # We rebuild because the files changed on the host and are copied into image
    ssh.exec_command('cd /root/Villex && docker compose build patosgym_web && docker compose up -d patosgym_web')

    ssh.close()

if __name__ == "__main__":
    sync_project()
