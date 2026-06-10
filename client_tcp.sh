#!/bin/bash
#
# Cliente TCP - Envía archivo con nombre
# Métodos: /dev/tcp, nc, telnet, socat
#

if [ $# -lt 2 ]; then
    echo "Uso: $0 <archivo> <host> [puerto]"
    exit 1
fi

FILE="$1"
HOST="$2"
PORT="${3:-9999}"

if [ ! -f "$FILE" ]; then
    echo "Error: El archivo '$FILE' no existe"
    exit 1
fi

FILE_SIZE=$(wc -c < "$FILE")
FILENAME=$(basename "$FILE")

echo "=========================================="
echo "Cliente TCP - Transferencia con Nombre"
echo "=========================================="
echo "Archivo:  $FILENAME"
echo "Tamaño:   $FILE_SIZE bytes"
echo "Destino:  $HOST:$PORT"
echo ""

# Método 1: /dev/tcp
echo "Intentando método 1: /dev/tcp..."
if timeout 2 bash -c "cat < /dev/null > /dev/tcp/$HOST/$PORT" 2>/dev/null; then
    echo "✓ /dev/tcp disponible"
    # Enviar: longitud nombre (1 byte) + nombre + contenido
    NAME_LEN=${#FILENAME}
    if (printf "\\$(printf '%03o' $NAME_LEN)$FILENAME" && cat "$FILE") | timeout 30 bash -c "cat > /dev/tcp/$HOST/$PORT" 2>/dev/null; then
        echo "✓ Archivo enviado exitosamente"
        exit 0
    fi
fi

# Método 2: netcat (nc)
echo "Intentando método 2: netcat (nc)..."
if command -v nc &> /dev/null; then
    if timeout 2 nc -zv "$HOST" "$PORT" > /dev/null 2>&1; then
        echo "✓ nc disponible"
        NAME_LEN=${#FILENAME}
        if (printf "\\$(printf '%03o' $NAME_LEN)$FILENAME" && cat "$FILE") | timeout 30 nc "$HOST" "$PORT" 2>/dev/null; then
            echo "✓ Archivo enviado exitosamente"
            exit 0
        fi
    fi
fi

# Método 3: telnet
echo "Intentando método 3: telnet..."
if command -v telnet &> /dev/null; then
    echo "✓ telnet disponible"
    NAME_LEN=${#FILENAME}
    if (printf "\\$(printf '%03o' $NAME_LEN)$FILENAME" && cat "$FILE") | timeout 30 telnet "$HOST" "$PORT" 2>/dev/null | head -1 > /dev/null; then
        echo "✓ Archivo enviado exitosamente"
        exit 0
    fi
fi

# Método 4: socat
echo "Intentando método 4: socat..."
if command -v socat &> /dev/null; then
    echo "✓ socat disponible"
    NAME_LEN=${#FILENAME}
    if (printf "\\$(printf '%03o' $NAME_LEN)$FILENAME" && cat "$FILE") | timeout 30 socat - TCP:$HOST:$PORT 2>/dev/null; then
        echo "✓ Archivo enviado exitosamente"
        exit 0
    fi
fi

echo ""
echo "Error: No se pudo usar ningún método"
exit 1
