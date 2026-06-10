#!/bin/bash
# Test rápido de una línea - ejecuta TODO

set -e

HOST="${1:-192.168.1.151}"
PORT="${2:-9999}"

echo "=========================================="
echo "QUICK TEST - Cliente y Servidor TCP"
echo "=========================================="
echo ""
echo "Host: $HOST"
echo "Puerto: $PORT"
echo ""

# 1. Verificar bash
if [ -z "$BASH_VERSION" ]; then
    echo "✗ Error: ejecuta con bash, no sh"
    echo "  bash quick_test.sh"
    exit 1
fi
echo "✓ Bash OK"

# 2. Verificar /dev/tcp
if ! (exec 3<>/dev/tcp/127.0.0.1/22) 2>/dev/null; then
    exec 3>&-
    echo "✗ /dev/tcp no disponible"
    exit 1
fi
echo "✓ /dev/tcp OK"

# 3. Crear archivo de prueba
TEST_FILE="/tmp/test_$RANDOM.bin"
dd if=/dev/urandom of="$TEST_FILE" bs=1 count=1000 2>/dev/null
ORIG_SIZE=$(wc -c < "$TEST_FILE")
ORIG_MD5=$(md5sum "$TEST_FILE" | awk '{print $1}')
echo "✓ Archivo de test creado: $ORIG_SIZE bytes"
echo "  MD5: $ORIG_MD5"

# 4. Verificar conectividad TCP
echo ""
echo "Verificando conexión a $HOST:$PORT..."
if ! timeout 2 bash -c "cat < /dev/null > /dev/tcp/$HOST/$PORT" 2>/dev/null; then
    echo "✗ No se puede conectar a $HOST:$PORT"
    echo ""
    echo "INSTRUCCIONES:"
    echo "  1. En Windows PowerShell (como Admin):"
    echo "     cd C:\\Users\\hugo.gomez-sanchez\\Desktop\\ping-file-transfer"
    echo "     python3 .\\server_tcp.py"
    echo ""
    echo "  2. Luego ejecuta de nuevo:"
    echo "     bash quick_test.sh $HOST $PORT"
    rm -f "$TEST_FILE"
    exit 1
fi
echo "✓ Conectado a $HOST:$PORT"

# 5. Enviar archivo
echo ""
echo "Enviando archivo..."
if ! cat "$TEST_FILE" | timeout 10 bash -c "cat > /dev/tcp/$HOST/$PORT" 2>/dev/null; then
    echo "✗ Error enviando archivo"
    rm -f "$TEST_FILE"
    exit 1
fi
echo "✓ Archivo enviado"

# 6. Limpiar
rm -f "$TEST_FILE"

# 7. Resultado
echo ""
echo "=========================================="
echo "✓ TEST COMPLETADO EXITOSAMENTE"
echo "=========================================="
echo ""
echo "En Windows, verifica:"
echo "  - Debería haber un archivo 'received_file_1000bytes'"
echo "  - Compara MD5: $ORIG_MD5"
echo ""
echo "En PowerShell:"
echo "  Get-FileHash received_file_1000bytes -Algorithm MD5"
echo ""
