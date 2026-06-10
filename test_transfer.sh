#!/bin/bash
# Test de transferencia completa

HOST="${1:-192.168.1.151}"
PORT="${2:-9999}"

echo "=========================================="
echo "Test de Transferencia Completa"
echo "=========================================="
echo ""

# Crear archivo de test
TEST_FILE="/tmp/test_transfer_$(date +%s).txt"
TEST_CONTENT="Test file created at $(date)"
TEST_SIZE=100

echo "Preparando test..."
echo "Creando archivo de prueba..."

# Generar archivo de test
dd if=/dev/urandom of="$TEST_FILE" bs=1 count=$TEST_SIZE 2>/dev/null

if [ ! -f "$TEST_FILE" ]; then
    echo "Error: No se pudo crear archivo de test"
    exit 1
fi

ACTUAL_SIZE=$(wc -c < "$TEST_FILE")
echo "✓ Archivo de test creado: $TEST_FILE"
echo "  Tamaño: $ACTUAL_SIZE bytes"
echo ""

# Calcular checksum
ORIGINAL_MD5=$(md5sum "$TEST_FILE" | awk '{print $1}')
echo "Checksum original: $ORIGINAL_MD5"
echo ""

echo "=========================================="
echo "Enviando archivo a $HOST:$PORT..."
echo "=========================================="
echo ""

# Enviar archivo
if cat "$TEST_FILE" | timeout 10 bash -c "cat > /dev/tcp/$HOST/$PORT" 2>/dev/null; then
    echo ""
    echo "✓ Archivo enviado exitosamente"
    echo ""
    echo "=========================================="
    echo "Próximos pasos en el servidor:"
    echo "=========================================="
    echo ""
    echo "1. Busca el archivo 'received_file_*' en Windows"
    echo "2. Verifica que el tamaño sea: $ACTUAL_SIZE bytes"
    echo "3. Calcula el MD5 y compáralo:"
    echo "   Original: $ORIGINAL_MD5"
    echo ""
    echo "En Windows (PowerShell):"
    echo "  Get-FileHash received_file_* -Algorithm MD5 | Format-List"
    echo ""
else
    echo "✗ Error al enviar archivo"
    exit 1
fi

# Limpiar
rm -f "$TEST_FILE"
