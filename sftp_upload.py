import paramiko
import os

host = '72.60.63.105'
port = 22
user = 'root'
password = 'VpSH4rd2026K9zX7q'
remote_dir = '/srv/patosgym'

files_to_upload = [
    'docker-compose.prod.yml',
    'Dockerfile',
    'nginx_patosgym.conf'
]

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    ssh.connect(host, port, user, password)
    ssh.exec_command(f'mkdir -p {remote_dir}')
    sftp = ssh.open_sftp()
    
    for file in files_to_upload:
        if os.path.exists(file):
            print(f"Uploading {file} to {remote_dir}/{file}")
            sftp.put(file, f"{remote_dir}/{file}")
        else:
            print(f"Skipping {file}, local file not found.")
            
    sftp.close()
    print("Deployment files successfully transferred.")
except Exception as e:
    print(f"Deployment failed: {e}")
finally:
    ssh.close()
