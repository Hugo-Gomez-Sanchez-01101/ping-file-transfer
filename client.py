#!/usr/bin/env python3
"""
Cliente que envía un archivo a través de paquetes ICMP (ping).
Compatible con Windows, Linux y macOS.
"""

import socket
import struct
import sys
import os
import time
import platform

def create_icmp_packet(id_, sequence, payload):
    """Crear paquete ICMP echo request con payload."""
    checksum = 0
    header = struct.pack('!BBHHH', 8, 0, checksum, id_, sequence)

    # Calcular checksum
    packet = header + payload
    if len(packet) % 2:
        packet += b'\0'

    sum_ = 0
    for i in range(0, len(packet), 2):
        sum_ += (packet[i] << 8) + packet[i + 1]

    sum_ = (sum_ >> 16) + (sum_ & 0xffff)
    sum_ += sum_ >> 16
    checksum = (~sum_) & 0xffff

    header = struct.pack('!BBHHH', 8, 0, checksum, id_, sequence)
    return header + payload

def send_file(filename, target='127.0.0.1', chunk_size=4):
    """Enviar archivo vía paquetes ICMP."""

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
        if system == "Windows":
            sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
            sock.bind((socket.gethostbyname(socket.gethostname()), 0))
            sock.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
        else:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_ICMP)

        packet_id = os.getpid() & 0xffff
        sequence = 0

        for idx, chunk in enumerate(chunks, 1):
            try:
                payload = bytes.fromhex(chunk)
                packet = create_icmp_packet(packet_id, sequence, payload)

                if system == "Windows":
                    sock.sendto(packet, (target, 1))
                else:
                    sock.sendto(packet, (target, 0))

                print(f"[{idx}/{len(chunks)}] Seq: {sequence}, Datos: {chunk[:16]}...")
                sequence += 1
                time.sleep(0.05)

            except Exception as e:
                print(f"Error en paquete {idx}: {e}")
                continue

        # Paquete de fin
        print("\nEnviando marcador de fin...")
        final_packet = create_icmp_packet(packet_id, 0xFFFF, b'END')
        sock.sendto(final_packet, (target, 1 if system == "Windows" else 0))

        sock.close()
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
        sys.exit(1)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Uso: python3 client.py <archivo> [destino]")
        print("Ejemplo: python3 client.py myfile.txt 127.0.0.1")
        sys.exit(1)

    filename = sys.argv[1]
    target = sys.argv[2] if len(sys.argv) > 2 else '127.0.0.1'

    send_file(filename, target)
