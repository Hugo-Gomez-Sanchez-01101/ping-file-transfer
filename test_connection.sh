#!/bin/bash
# Script para verificar que todo funciona antes de transferir

HOST="${1:-192.168.1.151}"
PORT="${2:-9999}"

echo "=========================================="
echo "Verificador de Conexión TCP"
echo "=========================================="
echo ""

# Verificar bash
echo "1. Verificando bash..."
if [ -z "$BASH_VERSION" ]; then
    echo "   ✗ No estás usando bash"
    echo "   Ejecuta: bash test_connection.sh"
    exit 1
fi
echo "   ✓ Bash OK"

# Verificar /dev/tcp
echo ""
echo "2. Verificando /dev/tcp (bash built-in)..."
if (exec 3<>/dev/tcp/127.0.0.1/22) 2>/dev/null; then
    exec 3>&-
    echo "   ✓ /dev/tcp disponible"
else
    echo "   ✗ /dev/tcp no disponible en este bash"
    exit 1
fi

# Verificar conectividad ping
echo ""
echo "3. Verificando ping a $HOST..."
if ping -c 1 -W 2 "$HOST" > /dev/null 2>&1; then
    echo "   ✓ Host responde"
else
    echo "   ⚠️  Host no responde (pero continuaremos)"
fi

# Verificar puerto TCP
echo ""
echo "4. Verificando puerto TCP $HOST:$PORT..."
if timeout 2 bash -c "cat < /dev/null > /dev/tcp/$HOST/$PORT" 2>/dev/null; then
    echo "   ✓ Puerto TCP accesible"
    echo ""
    echo "=========================================="
    echo "✓ Todo verificado - Listo para transferir"
    echo "=========================================="
    exit 0
else
    echo "   ✗ No se puede conectar a $HOST:$PORT"
    echo ""
    echo "Soluciones:"
    echo "  1. ¿El servidor está ejecutándose?"
    echo "     Windows: python3 .\\server_tcp.py"
    echo "  2. ¿Firewall bloqueando puerto 9999?"
    echo "  3. ¿IP correcta? (esperado: $HOST)"
    exit 1
fi
