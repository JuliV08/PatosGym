import paramiko

host = '72.60.63.105'
port = 22
user = 'root'
password = 'VpSH4rd2026K9zX7q'

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    ssh.connect(host, port, user, password)
    script = """
    cd /srv/patosgym
    echo "Installing unzip if needed..."
    apt-get update -qq && apt-get install -y unzip -qq
    
    echo "Extracting project..."
    unzip -q -o patosgym_deploy.zip
    
    echo "Setting up media volume mapping..."
    mkdir -p /srv/patosgym/volumes/media
    cp -rn /srv/patosgym/media/* /srv/patosgym/volumes/media/ 2>/dev/null || true
    
    echo "Ensuring .env files exist..."
    echo "DEBUG=0" > .env.prod
    echo "SECRET_KEY=dummy_for_now_or_change_me" >> .env.prod
    echo "POSTGRES_DB=db" > .env.prod.db
    echo "POSTGRES_USER=user" >> .env.prod.db
    echo "POSTGRES_PASSWORD=pass" >> .env.prod.db
    
    echo "Building and starting Docker Compose..."
    docker compose -f docker-compose.prod.yml down
    docker compose -f docker-compose.prod.yml up -d --build
    
    echo "Waiting for DB to be healthy..."
    sleep 5
    
    echo "Running migrations..."
    docker exec patosgym_prod_web python manage.py migrate
    
    echo "Loading data dump..."
    if [ -f "datadump.json" ]; then
        docker exec patosgym_prod_web python manage.py loaddata datadump.json
    fi
    
    echo "Collecting static files..."
    docker exec patosgym_prod_web python manage.py collectstatic --noinput
    """
    stdin, stdout, stderr = ssh.exec_command(script)
    for line in stdout:
        print(line, end="")
    for line in stderr:
        print("ERR:", line, end="")
except Exception as e:
    print(f"Error: {e}")
finally:
    ssh.close()
