import paramiko
import os

def upload_templates():
    host = '72.60.63.105'
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, 22, 'root', 'VpSH4rd2026K9zX7q')

    sftp = ssh.open_sftp()
    
    local_base = r'C:\Users\Villex\dev\PatosGym\templates'
    remote_base = '/srv/patosgym/templates'

    # Function to recursively upload a directory
    def put_dir(local_path, remote_path):
        try:
            sftp.mkdir(remote_path)
        except IOError:
            pass # Directory might exist
        
        for item in os.listdir(local_path):
            l_item = os.path.join(local_path, item)
            r_item = os.path.join(remote_path, item).replace('\\', '/')
            if os.path.isfile(l_item):
                print(f"Uploading {l_item} -> {r_item}")
                sftp.put(l_item, r_item)
            elif os.path.isdir(l_item):
                put_dir(l_item, r_item)

    put_dir(local_base, remote_base)
    sftp.close()

    print("--- REBUILDING IMAGE ---")
    ssh.exec_command('cd /root/Villex && docker compose build patosgym_web && docker compose up -d patosgym_web')

    ssh.close()

if __name__ == "__main__":
    upload_templates()
