#!/usr/bin/env bash
# update.sh — Actualizar la app en producción
# Ejecutar como root o con sudo: bash /var/www/mxbaseball/deploy/update.sh

set -euo pipefail

APP_DIR="/var/www/mxbaseball"
APP_USER="mxbaseball"

echo "==> Actualizando código..."
sudo -u "$APP_USER" git -C "$APP_DIR" pull

echo "==> Instalando dependencias nuevas..."
sudo -u "$APP_USER" "$APP_DIR/venv/bin/pip" install --quiet -r "$APP_DIR/requirements.txt"

echo "==> Migraciones..."
sudo -u "$APP_USER" "$APP_DIR/venv/bin/python" "$APP_DIR/manage.py" migrate --no-input

echo "==> Archivos estáticos..."
sudo -u "$APP_USER" "$APP_DIR/venv/bin/python" "$APP_DIR/manage.py" collectstatic --no-input

echo "==> Compilando traducciones..."
sudo -u "$APP_USER" "$APP_DIR/venv/bin/python" "$APP_DIR/manage.py" compilemessages

echo "==> Reiniciando Gunicorn..."
systemctl restart gunicorn-mxbaseball

echo "✓ Actualización completada."
