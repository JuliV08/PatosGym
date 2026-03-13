import paramiko
import os

host = '72.60.63.105'
port = 22
user = 'root'
password = 'VpSH4rd2026K9zX7q'
remote_dir = '/srv/patosgym'

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    ssh.connect(host, port, user, password)
    sftp = ssh.open_sftp()
    
    file = 'patosgym_deploy.zip'
    print(f"Uploading {file} to {remote_dir}/{file}...")
    sftp.put(file, f"{remote_dir}/{file}")
            
    sftp.close()
    print("Deployment zip successfully transferred.")
except Exception as e:
    print(f"Deployment failed: {e}")
finally:
    ssh.close()
