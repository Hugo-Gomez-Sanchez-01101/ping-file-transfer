#!/usr/bin/env python3
"""
Cliente que envía un archivo a través de paquetes ICMP (ping).
Compatible con Windows, Linux y macOS.
Usa scapy para mejor compatibilidad con Npcap en Windows.
"""

import sys
import os
import time
import platform

try:
    from scapy.all import IP, ICMP, send, conf
except ImportError:
    print("Instalando scapy...")
    os.system('pip3 install scapy')
    from scapy.all import IP, ICMP, send, conf

def send_file(filename, target='127.0.0.1', chunk_size=4):
    """Enviar archivo vía paquetes ICMP usando scapy."""

    if not os.path.exists(filename):
        print(f"Error: Archivo '{filename}' no existe")
        sys.exit(1)

    try:
        with open(filename, 'rb') as f:
            file_data = f.read()
    except Exception as e:
        print(f"Error al leer archivo: {e}")
        sys.exit(1)

    system = platform.system()
    print(f"Sistema: {system}")
    print(f"Archivo: {filename}")
    print(f"Tamaño: {len(file_data)} bytes")
    print(f"Destino: {target}")
    print(f"Tamaño de chunk: {chunk_size} bytes\n")

    hex_data = file_data.hex()
    chunks = [hex_data[i:i+chunk_size*2] for i in range(0, len(hex_data), chunk_size*2)]

    print(f"Total de paquetes: {len(chunks)}\n")

    try:
        packet_id = os.getpid() & 0xffff
        sequence = 0

        # En Windows, deshabilitar output de Scapy
        if system == "Windows":
            conf.verb = 0

        for idx, chunk in enumerate(chunks, 1):
            try:
                payload = bytes.fromhex(chunk)

                # Crear paquete ICMP con scapy
                ip_layer = IP(dst=target)
                icmp_layer = ICMP(type=8, id=packet_id, seq=sequence) / payload

                packet = ip_layer / icmp_layer

                # Enviar paquete
                send(packet, verbose=False)

                print(f"[{idx}/{len(chunks)}] Seq: {sequence}, Datos: {chunk[:16]}...")
                sequence += 1
                time.sleep(0.05)

            except Exception as e:
                print(f"Error en paquete {idx}: {e}")
                continue

        # Paquete de fin
        print("\nEnviando marcador de fin...")
        ip_layer = IP(dst=target)
        icmp_layer = ICMP(type=8, id=packet_id, seq=0xFFFF) / b'END'
        packet = ip_layer / icmp_layer
        send(packet, verbose=False)

        print("✓ Transmisión completada")

    except PermissionError:
        print("Error: Se requieren permisos de administrador/root")
        if system == "Windows":
            print("Ejecuta PowerShell como Administrador")
        else:
            print("Usa: sudo python3 client.py ...")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Uso: python3 client.py <archivo> [destino]")
        print("Ejemplo: python3 client.py myfile.txt 127.0.0.1")
        sys.exit(1)

    filename = sys.argv[1]
    target = sys.argv[2] if len(sys.argv) > 2 else '127.0.0.1'

    send_file(filename, target)
