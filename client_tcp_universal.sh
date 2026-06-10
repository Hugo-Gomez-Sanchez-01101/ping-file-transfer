#!/bin/bash
#
# Cliente TCP Universal - usa múltiples métodos
# Intenta: /dev/tcp, nc, telnet, socat
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

echo "=========================================="
echo "Cliente TCP Universal - Transferencia"
echo "=========================================="
echo "Archivo:  $FILE"
echo "Tamaño:   $FILE_SIZE bytes"
echo "Destino:  $HOST:$PORT"
echo ""

# Método 1: /dev/tcp (bash built-in)
echo "Intentando método 1: /dev/tcp..."
if timeout 2 bash -c "cat < /dev/null > /dev/tcp/$HOST/$PORT" 2>/dev/null; then
    echo "✓ /dev/tcp disponible"
    if cat "$FILE" | timeout 30 bash -c "cat > /dev/tcp/$HOST/$PORT" 2>/dev/null; then
        echo "✓ Archivo enviado exitosamente"
        exit 0
    fi
fi

# Método 2: netcat (nc)
echo "Intentando método 2: netcat (nc)..."
if command -v nc &> /dev/null; then
    if timeout 2 nc -zv "$HOST" "$PORT" > /dev/null 2>&1; then
        echo "✓ nc disponible"
        if cat "$FILE" | timeout 30 nc "$HOST" "$PORT" 2>/dev/null; then
            echo "✓ Archivo enviado exitosamente"
            exit 0
        fi
    fi
fi

# Método 3: telnet
echo "Intentando método 3: telnet..."
if command -v telnet &> /dev/null; then
    echo "✓ telnet disponible"
    (cat "$FILE"; sleep 0.1) | timeout 30 telnet "$HOST" "$PORT" 2>/dev/null | head -1 > /dev/null
    if [ $? -eq 0 ]; then
        echo "✓ Archivo enviado exitosamente"
        exit 0
    fi
fi

# Método 4: socat
echo "Intentando método 4: socat..."
if command -v socat &> /dev/null; then
    echo "✓ socat disponible"
    if timeout 30 socat - TCP:$HOST:$PORT < "$FILE" 2>/dev/null; then
        echo "✓ Archivo enviado exitosamente"
        exit 0
    fi
fi

# Si nada funciona
echo ""
echo "Error: No se pudo usar ningún método"
echo ""
echo "Herramientas disponibles en tu sistema:"
echo "  /dev/tcp:  NO"
echo "  nc:        $(command -v nc &> /dev/null && echo "SÍ" || echo "NO")"
echo "  telnet:    $(command -v telnet &> /dev/null && echo "SÍ" || echo "NO")"
echo "  socat:     $(command -v socat &> /dev/null && echo "SÍ" || echo "NO")"
echo ""
echo "Soluciones:"
echo "  1. Ubuntu/Debian: sudo apt-get install netcat-openbsd"
echo "  2. RHEL/CentOS:   sudo yum install nmap-ncat"
echo "  3. macOS:         brew install netcat"
echo ""
exit 1
