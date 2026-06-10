#!/bin/bash
#
# Cliente TCP (bash) que envía archivos
# Sin dependencias Python - usa solo bash built-in
#

if [ $# -lt 2 ]; then
    echo "Uso: $0 <archivo> <host> [puerto]"
    echo "Ejemplo: $0 myfile.txt 192.168.1.151 9999"
    echo ""
    echo "Requisitos:"
    echo "  - bash (no sh)"
    echo "  - ping (para verificar conectividad)"
    exit 1
fi

FILE="$1"
HOST="$2"
PORT="${3:-9999}"

# Verificar que es bash
if [ -z "$BASH_VERSION" ]; then
    echo "Error: Este script requiere bash, no sh"
    echo "Ejecuta: bash $0 ..."
    exit 1
fi

if [ ! -f "$FILE" ]; then
    echo "Error: El archivo '$FILE' no existe"
    exit 1
fi

# Obtener tamaño del archivo (portable)
FILE_SIZE=$(wc -c < "$FILE")

echo "=========================================="
echo "Cliente TCP - Transferencia de Archivos"
echo "=========================================="
echo "Archivo:  $FILE"
echo "Tamaño:   $FILE_SIZE bytes"
echo "Destino:  $HOST:$PORT"
echo ""

# Verificar conectividad ping
echo "Verificando conectividad..."
if ! ping -c 1 -W 2 "$HOST" > /dev/null 2>&1; then
    echo "⚠️  Advertencia: Host no responde a ping"
    echo "Continuando de todas formas..."
fi

# Verificar conexión TCP
echo "Probando conexión TCP..."
if timeout 2 bash -c "cat < /dev/null > /dev/tcp/$HOST/$PORT" 2>/dev/null; then
    echo "✓ Conexión TCP exitosa"
else
    echo "Error: No se puede conectar a $HOST:$PORT"
    echo ""
    echo "Soluciones:"
    echo "  1. Verificar que el servidor está ejecutándose"
    echo "  2. Verificar firewall en $HOST"
    echo "  3. Verificar IP y puerto: $HOST:$PORT"
    exit 1
fi

echo ""
echo "Enviando archivo..."

# Enviar archivo por TCP
if cat "$FILE" | timeout 30 bash -c "cat > /dev/tcp/$HOST/$PORT" 2>/dev/null; then
    echo "✓ Archivo enviado exitosamente"
    echo "✓ Transmisión completada"
    echo ""
    echo "El archivo debe estar en el servidor como 'received_file_*'"
    exit 0
else
    echo "✗ Error durante la transmisión"
    exit 1
fi
