import paramiko, json

host = '72.60.63.105'
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(host, 22, 'root', 'VpSH4rd2026K9zX7q')

def run(cmd):
    _, out, err = ssh.exec_command(cmd)
    return out.read().decode('utf-8', 'ignore')

print("=" * 70)
print("1. TODOS LOS CONTENEDORES CORRIENDO")
print("=" * 70)
print(run("docker ps --format 'table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}'"))

print("=" * 70)
print("2. TODAS LAS REDES DOCKER")
print("=" * 70)
print(run("docker network ls"))

print("=" * 70)
print("3. DETALLE DE TODAS LAS REDES (IPs de contenedores)")
print("=" * 70)
networks_raw = run("docker network ls --format '{{.Name}}'").strip().split('\n')
for net in networks_raw:
    detail = run(f"docker network inspect {net}")
    try:
        data = json.loads(detail)
        containers = data[0].get('Containers', {})
        if containers:
            print(f"\n  Red: {net}")
            for cid, info in containers.items():
                print(f"    > {info['Name']} --> {info['IPv4Address']}")
    except:
        pass

print("=" * 70)
print("4. PUERTOS ABIERTOS EN EL HOST")
print("=" * 70)
print(run("ss -tlnp | grep -E 'docker|nginx|gunicorn|:80|:443|:8000|:18082|:18080'"))

print("=" * 70)
print("5. TODOS LOS .conf EN /root/Villex/nginx/conf.d/")
print("=" * 70)
print(run("ls -la /root/Villex/nginx/conf.d/"))

print("=" * 70)
print("6. CONTENIDO DE CADA .conf EN conf.d")
print("=" * 70)
conf_files = run("ls /root/Villex/nginx/conf.d/").strip().split()
for f in conf_files:
    if f.endswith('.conf'):
        print(f"\n  --- {f} ---")
        print(run(f"cat /root/Villex/nginx/conf.d/{f}"))

print("=" * 70)
print("7. NGINX CONTAINER NAME Y BINDINGS")
print("=" * 70)
print(run("docker inspect villex_nginx --format '{{.Name}} | Ports: {{json .HostConfig.PortBindings}}'"))

print("=" * 70)
print("8. DOCKER-COMPOSE.PROD DE PATOSGYM")
print("=" * 70)
print(run("cat /srv/patosgym/docker-compose.prod.yml"))

print("=" * 70)
print("9. .env.prod de PatosGym")
print("=" * 70)
print(run("cat /srv/patosgym/.env.prod"))

print("=" * 70)
print("10. LOGS ULTIMOS 30 LINEAS DE PATOSGYM WEB")
print("=" * 70)
print(run("docker logs patosgym_prod_web --tail 30 2>&1"))

ssh.close()
