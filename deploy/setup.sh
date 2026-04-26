#!/usr/bin/env bash
# setup.sh — Configuración inicial del servidor Ubuntu para mxbaseball.com
# Ejecutar como root: bash setup.sh

set -euo pipefail

DOMAIN="mxbaseball.com"
APP_USER="mxbaseball"
APP_DIR="/var/www/mxbaseball"
LOG_DIR="/var/log/mxbaseball"
REPO_URL="https://github.com/cgallego17/mxpremier.git"

echo "==> Actualizando paquetes..."
apt-get update -q && apt-get upgrade -y -q

echo "==> Instalando dependencias..."
apt-get install -y -q \
    python3 python3-pip python3-venv \
    nginx certbot python3-certbot-nginx \
    git curl gettext

echo "==> Creando usuario de la app..."
id "$APP_USER" &>/dev/null || useradd --system --create-home --shell /bin/bash "$APP_USER"
usermod -aG www-data "$APP_USER"

echo "==> Creando directorios..."
mkdir -p "$APP_DIR" "$LOG_DIR"
chown "$APP_USER":"$APP_USER" "$APP_DIR" "$LOG_DIR"

echo "==> Clonando repositorio..."
sudo -u "$APP_USER" git clone "$REPO_URL" "$APP_DIR"

echo "==> Creando entorno virtual e instalando dependencias Python..."
sudo -u "$APP_USER" python3 -m venv "$APP_DIR/venv"
sudo -u "$APP_USER" "$APP_DIR/venv/bin/pip" install --quiet --upgrade pip
sudo -u "$APP_USER" "$APP_DIR/venv/bin/pip" install --quiet -r "$APP_DIR/requirements.txt"

echo "==> Configurando .env..."
if [ ! -f "$APP_DIR/.env" ]; then
    cp "$APP_DIR/.env.example" "$APP_DIR/.env"
    echo ""
    echo "  IMPORTANTE: Edita $APP_DIR/.env con los valores reales:"
    echo "    SECRET_KEY   → genera con: python3 -c \"from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())\""
    echo "    FB_PAGE_ACCESS_TOKEN → tu token de página de Facebook"
    echo ""
    read -rp "  Presiona ENTER cuando hayas editado el .env para continuar..."
fi
chown "$APP_USER":"$APP_USER" "$APP_DIR/.env"
chmod 600 "$APP_DIR/.env"

echo "==> Ejecutando migraciones y collectstatic..."
sudo -u "$APP_USER" "$APP_DIR/venv/bin/python" "$APP_DIR/manage.py" migrate --no-input
sudo -u "$APP_USER" "$APP_DIR/venv/bin/python" "$APP_DIR/manage.py" collectstatic --no-input

echo "==> Instalando servicio Gunicorn..."
cp "$APP_DIR/deploy/gunicorn.service" /etc/systemd/system/gunicorn-mxbaseball.service
systemctl daemon-reload
systemctl enable gunicorn-mxbaseball
systemctl start gunicorn-mxbaseball

echo "==> Configurando Nginx..."
cp "$APP_DIR/deploy/nginx.conf" /etc/nginx/sites-available/mxbaseball
ln -sf /etc/nginx/sites-available/mxbaseball /etc/nginx/sites-enabled/mxbaseball
rm -f /etc/nginx/sites-enabled/default

# Config temporal HTTP para que certbot pueda verificar el dominio
cat > /etc/nginx/sites-available/mxbaseball <<'NGINX_HTTP'
server {
    listen 80;
    server_name mxbaseball.com www.mxbaseball.com;

    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
NGINX_HTTP

nginx -t && systemctl reload nginx

echo "==> Obteniendo certificado SSL con Let's Encrypt..."
certbot --nginx \
    -d "$DOMAIN" \
    -d "www.$DOMAIN" \
    --non-interactive \
    --agree-tos \
    --email "admin@$DOMAIN" \
    --redirect

echo "==> Instalando config Nginx final con SSL..."
cp "$APP_DIR/deploy/nginx.conf" /etc/nginx/sites-available/mxbaseball
nginx -t && systemctl reload nginx

echo "==> Configurando renovación automática SSL..."
systemctl enable certbot.timer
systemctl start certbot.timer

echo ""
echo "✓ Despliegue completado."
echo "  Sitio: https://$DOMAIN"
echo "  Logs Gunicorn: $LOG_DIR/"
echo "  App: $APP_DIR/"
