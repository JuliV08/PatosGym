import paramiko
import time

def sync_infrastructure():
    host = '72.60.63.105'
    port = 22
    user = 'root'
    password = 'VpSH4rd2026K9zX7q'

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        ssh.connect(host, port, user, password)
        sftp = ssh.open_sftp()

        print("--- 1. READING VILLEX COMPOSE ---")
        remote_path = '/root/Villex/docker-compose.prod.yml'
        with sftp.open(remote_path, 'r') as f:
            compose_content = f.read().decode('utf-8')

        print("--- 2. MODIFYING COMPOSE (Adding PatosGym Volumes) ---")
        # I'll look for the nginx volume section and inject the new binds
        # We know villex_nginx has volumes. I'll search for the first occurrence of 'volumes:' under 'nginx:'
        
        # Robust replacement logic
        target_marker = "dym-cosmeticos_media_volume:/opt/dym-cosmeticos/media:ro"
        new_binds = "\n      - /srv/patosgym/volumes/static:/srv/patosgym/volumes/static:ro\n      - /srv/patosgym/volumes/media:/srv/patosgym/volumes/media:ro"
        
        if target_marker in compose_content:
            new_compose = compose_content.replace(target_marker, target_marker + new_binds)
        else:
            # Fallback if marker changed
            print("Warning: Target marker not found, using generic search")
            if "villex_nginx" in compose_content:
                 # Search for the volumes section related to nginx
                 # This is tricky without a full parser, but I'll try to find the binds list
                 new_compose = compose_content.replace(
                     "- /etc/letsencrypt:/etc/letsencrypt:ro",
                     "- /etc/letsencrypt:/etc/letsencrypt:ro" + new_binds
                 )

        with sftp.open(remote_path, 'w') as f:
            f.write(new_compose)

        print("--- 3. RESTARTING NGINX ROUTER ---")
        ssh.exec_command('cd /root/Villex && docker compose -f docker-compose.prod.yml up -d')
        time.sleep(5)

        print("--- 4. RELOADING NGINX CONFIG ---")
        stdin, out, err = ssh.exec_command('docker exec villex_nginx nginx -t')
        print("NGINX TEST OUT:", out.read().decode())
        print("NGINX TEST ERR:", err.read().decode())

        ssh.exec_command('docker exec villex_nginx nginx -s reload')
        time.sleep(2)

        print("--- 5. FINAL VERIFICATION ---")
        # Internally from the proxy to the app
        stdin, out, err = ssh.exec_command("docker exec villex_nginx curl -I -H 'Host: patosgym.com.ar' http://localhost")
        print("FINAL CURL HEADERS:\n", out.read().decode())

        sftp.close()
    except Exception as e:
        print(f"Error: {e}")
    finally:
        ssh.close()

if __name__ == "__main__":
    sync_infrastructure()
