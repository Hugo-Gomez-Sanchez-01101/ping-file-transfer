#!/bin/bash
#
# Cliente que envía un archivo a través de paquetes ICMP (ping)
# Basado en: cat file | xxd -p -c 4 | while read line; do ping -c 1 127.0.0.1 -p $line; done
#

if [ $# -lt 1 ]; then
    echo "Uso: $0 <archivo> [destino]"
    echo "Ejemplo: $0 myfile.txt 127.0.0.1"
    exit 1
fi

FILE="$1"
TARGET="${2:-127.0.0.1}"
CHUNK_SIZE=4  # Tamaño de chunk en bytes (8 caracteres hex)

if [ ! -f "$FILE" ]; then
    echo "Error: El archivo '$FILE' no existe."
    exit 1
fi

FILE_SIZE=$(stat -f%z "$FILE" 2>/dev/null || stat -c%s "$FILE" 2>/dev/null || wc -c < "$FILE")

echo "Archivo: $FILE"
echo "Tamaño: $FILE_SIZE bytes"
echo "Destino: $TARGET"
echo "Tamaño de chunk: $CHUNK_SIZE bytes"
echo ""

# Convertir archivo a hex y dividir en chunks
HEX_DATA=$(xxd -p -c $CHUNK_SIZE "$FILE")

TOTAL_CHUNKS=$(echo "$HEX_DATA" | wc -l)
echo "Total de paquetes a enviar: $TOTAL_CHUNKS"
echo ""

PACKET_COUNT=0

# Enviar cada línea como payload en un ping
echo "$HEX_DATA" | while read line; do
    PACKET_COUNT=$((PACKET_COUNT + 1))

    # Enviar ping con datos en el payload
    # El flag -p especifica los datos hexadecimales a enviar
    ping -c 1 -p "$line" "$TARGET" > /dev/null 2>&1

    echo "[$PACKET_COUNT/$TOTAL_CHUNKS] Paquete enviado - Datos: $line"

    # Pequeña pausa entre paquetes
    sleep 0.05
done

echo ""
echo "✓ Transmisión completada"
