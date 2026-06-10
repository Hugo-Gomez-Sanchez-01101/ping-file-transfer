#!/bin/bash
#
# Cliente TCP puro (bash/sh) que envía archivos
# Sin dependencias - usa solo herramientas estándar
#

if [ $# -lt 2 ]; then
    echo "Uso: $0 <archivo> <host> [puerto]"
    echo "Ejemplo: $0 myfile.txt 192.168.1.151 9999"
    exit 1
fi

FILE="$1"
HOST="$2"
PORT="${3:-9999}"

if [ ! -f "$FILE" ]; then
    echo "Error: El archivo '$FILE' no existe"
    exit 1
fi

FILE_SIZE=$(stat -f%z "$FILE" 2>/dev/null || stat -c%s "$FILE" 2>/dev/null || wc -c < "$FILE")

echo "Archivo: $FILE"
echo "Tamaño: $FILE_SIZE bytes"
echo "Destino: $HOST:$PORT"
echo ""

# Verificar conectividad
echo "Verificando conectividad..."
if ! timeout 2 bash -c "cat < /dev/null > /dev/tcp/$HOST/$PORT" 2>/dev/null; then
    echo "Error: No se puede conectar a $HOST:$PORT"
    exit 1
fi

echo "✓ Conectado a $HOST:$PORT"
echo ""

# Enviar archivo
echo "Enviando archivo..."

# Usar cat para enviar el archivo por TCP
(cat "$FILE"; sleep 0.1) | timeout 30 bash -c "cat > /dev/tcp/$HOST/$PORT" 2>/dev/null

if [ $? -eq 0 ]; then
    echo "✓ Transmisión completada"
else
    echo "Error durante la transmisión"
    exit 1
fi
