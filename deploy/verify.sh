#!/usr/bin/env bash
# verify.sh — Verifica que el despliegue en el servidor está correcto
# Ejecutar después de setup.sh: bash /var/www/mxbaseball/deploy/verify.sh

set -euo pipefail

APP_DIR="/var/www/mxbaseball"
PYTHON="$APP_DIR/venv/bin/python"
DOMAIN="mxbaseball.com"
PASS=0
FAIL=0

ok()   { echo "  [OK]  $1"; ((PASS++)) || true; }
fail() { echo "  [FAIL] $1"; ((FAIL++)) || true; }

echo ""
echo "=== Verificacion del despliegue mxbaseball.com ==="
echo ""

# 1. Servicio Gunicorn
echo "-- Servicios --"
if systemctl is-active --quiet gunicorn-mxbaseball; then
    ok "Gunicorn activo"
else
    fail "Gunicorn NO esta activo (systemctl status gunicorn-mxbaseball)"
fi

if systemctl is-active --quiet nginx; then
    ok "Nginx activo"
else
    fail "Nginx NO esta activo"
fi

# 2. Puerto 8000 escuchando
echo ""
echo "-- Red --"
if ss -tlnp | grep -q ':8000'; then
    ok "Gunicorn escuchando en 127.0.0.1:8000"
else
    fail "Nada escucha en el puerto 8000"
fi

# 3. Django system check
echo ""
echo "-- Django --"
if sudo -u mxbaseball "$PYTHON" "$APP_DIR/manage.py" check --deploy > /tmp/django_check.txt 2>&1; then
    ok "Django check --deploy sin errores"
else
    fail "Django check --deploy reporto problemas:"
    cat /tmp/django_check.txt | grep -E "ERROR|WARNING" | head -10
fi

# 4. Migraciones pendientes
if sudo -u mxbaseball "$PYTHON" "$APP_DIR/manage.py" migrate --check > /dev/null 2>&1; then
    ok "Sin migraciones pendientes"
else
    fail "Hay migraciones pendientes (ejecuta: manage.py migrate)"
fi

# 5. Archivos estáticos
echo ""
echo "-- Archivos estaticos --"
STATIC_DIR="$APP_DIR/staticfiles"
if [ -d "$STATIC_DIR" ] && [ "$(ls -A $STATIC_DIR)" ]; then
    COUNT=$(find "$STATIC_DIR" -type f | wc -l)
    ok "staticfiles/ existe con $COUNT archivos"
else
    fail "staticfiles/ vacio o no existe (ejecuta: manage.py collectstatic)"
fi

# 6. Ejecutivos en static
for img in enrique-mayorga ricardo-bravo jorge-campillo rodrigo-lopez jorge-marquez luis-tovar cesar-marquez ramon-leon; do
    if [ -f "$STATIC_DIR/landing/img/$img.jpeg" ]; then
        ok "Imagen $img.jpeg presente"
    else
        fail "Imagen $img.jpeg FALTANTE en staticfiles/landing/img/"
    fi
done

# 7. Peticion HTTP interna
echo ""
echo "-- HTTP --"
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8000/ 2>/dev/null || echo "000")
if [ "$HTTP_CODE" = "200" ] || [ "$HTTP_CODE" = "301" ] || [ "$HTTP_CODE" = "302" ]; then
    ok "App responde localmente (HTTP $HTTP_CODE)"
else
    fail "App no responde en http://127.0.0.1:8000/ (HTTP $HTTP_CODE)"
fi

# 8. HTTPS publico
HTTPS_CODE=$(curl -s -o /dev/null -w "%{http_code}" "https://$DOMAIN/" 2>/dev/null || echo "000")
if [ "$HTTPS_CODE" = "200" ]; then
    ok "https://$DOMAIN/ responde 200"
else
    fail "https://$DOMAIN/ retorna HTTP $HTTPS_CODE"
fi

WWW_CODE=$(curl -s -o /dev/null -w "%{http_code}" -L "https://www.$DOMAIN/" 2>/dev/null || echo "000")
if [ "$WWW_CODE" = "200" ]; then
    ok "https://www.$DOMAIN/ redirige correctamente a apex"
else
    fail "https://www.$DOMAIN/ no redirige bien (HTTP $WWW_CODE)"
fi

# 9. SSL
echo ""
echo "-- SSL --"
CERT_EXPIRY=$(echo | openssl s_client -connect "$DOMAIN:443" -servername "$DOMAIN" 2>/dev/null \
    | openssl x509 -noout -enddate 2>/dev/null | cut -d= -f2 || echo "")
if [ -n "$CERT_EXPIRY" ]; then
    ok "Certificado SSL valido hasta: $CERT_EXPIRY"
else
    fail "No se pudo leer el certificado SSL"
fi

# 10. Logs
echo ""
echo "-- Logs --"
LOG_DIR="/var/log/mxbaseball"
if [ -d "$LOG_DIR" ]; then
    ERRORS=$(grep -c "ERROR\|Exception\|Traceback" "$LOG_DIR/error.log" 2>/dev/null || echo "0")
    if [ "$ERRORS" = "0" ]; then
        ok "Sin errores en error.log"
    else
        fail "$ERRORS errores encontrados en error.log (revisa $LOG_DIR/error.log)"
    fi
else
    fail "Directorio de logs no existe: $LOG_DIR"
fi

# Resumen
echo ""
echo "==================================="
echo "  Resultado: $PASS OK  |  $FAIL FALLOS"
echo "==================================="
echo ""

[ "$FAIL" -eq 0 ]
