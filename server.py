#!/usr/bin/env python3
"""
Servidor que recibe datos a través de paquetes ICMP echo (ping)
y reconstruye el archivo localmente.
"""

import socket
import struct
import textwrap
import sys
import os

# Estructura de cabecera ICMP
ICMP_ECHO_REQUEST = 8
ICMP_ECHO_REPLY = 0

def format_ipv4(bytes_ip):
    bytes_str = map('{:3}'.format, bytes_ip)
    return '.'.join(bytes_str).replace(' ', '0')

def format_icmp(data):
    checksum, id_, sequence, = struct.unpack('! H H H', data[:6])
    return checksum, id_, sequence

def format_ipv4_packet(version_header_length, ttl, proto, src, target, data):
    version = version_header_length >> 4
    header_length = (version_header_length & 15) * 4
    ttl_proto = f'{ttl},{proto}'
    data_size = len(data)
    return f'IPv4 Version: {version}, Header Length: {header_length} bytes, TTL: {ttl}, Protocol: {proto}, Src: {src}, Target: {target}, Data Size: {data_size} bytes'

def recv_icmp(sock):
    raw_buffer = sock.recvfrom(65535)
    raw_packet = raw_buffer[0]

    # En Linux con AF_PACKET, los primeros 14 bytes son la cabecera Ethernet
    # En Linux con AF_INET, los primeros 20 bytes son la cabecera IPv4
    # En Windows, depende de la configuración

    # Intentar detectar el offset basado en la longitud y contenido
    offset = 0
    if len(raw_packet) > 20 and raw_packet[0] & 0xf0 != 0x40:
        # Probablemente es una cabecera Ethernet (AF_PACKET en Linux)
        offset = 14
    elif len(raw_packet) > 20:
        # IPv4 directo
        offset = 20

    if offset + 8 > len(raw_packet):
        return None, 0, 0

    # Saltar cabecera IPv4 o Ethernet+IPv4
    ipv4_packet = raw_packet[offset:offset+20] if offset == 14 else raw_packet[offset-20:offset]

    if len(ipv4_packet) < 20:
        return None, 0, 0

    version_header_length, ttl, proto, src, target = struct.unpack('! B B 2x 4s 4s', ipv4_packet)

    icmp_start = offset + 20 if offset == 14 else 20
    icmp_packet = raw_packet[icmp_start:icmp_start+8]

    if len(icmp_packet) < 8:
        return None, 0, 0

    checksum, id_, sequence = format_icmp(icmp_packet)

    # El payload está después de la cabecera ICMP (8 bytes)
    payload = raw_packet[icmp_start+8:]

    return payload, id_, sequence

def main():
    print("Servidor ICMP esperando paquetes ping...")
    print("(Requiere permisos de administrador)")

    if os.name == 'nt':  # Windows
        sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
        sock.bind((socket.gethostbyname(socket.gethostname()), 0))
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
        sock.ioctl(socket.SIO_RCVALL, socket.RCVALL_ON)
    else:  # Linux/Mac
        sock = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.htons(3))

    try:
        reconstructed_data = bytearray()
        packet_count = 0

        while True:
            result = recv_icmp(sock)
            if result[0] is None:
                continue

            payload, id_, sequence = result

            if payload:
                packet_count += 1
                # Convertir payload a hex y agregarlo
                hex_str = payload.hex()
                reconstructed_data.extend(bytes.fromhex(hex_str))

                print(f"[Paquete {packet_count}] ID: {id_}, Seq: {sequence}, Datos: {hex_str[:32]}...")

                # Si el usuario presiona Ctrl+C, guardar los datos
                if sequence == 0xFFFF:  # Marcador de fin
                    break

    except KeyboardInterrupt:
        pass
    finally:
        if os.name == 'nt':
            sock.ioctl(socket.SIO_RCVALL, socket.RCVALL_OFF)
        sock.close()

        if reconstructed_data:
            output_file = 'received_file'
            with open(output_file, 'wb') as f:
                f.write(reconstructed_data)
            print(f"\n✓ Archivo reconstruido: {output_file}")
            print(f"✓ Bytes recibidos: {len(reconstructed_data)}")

if __name__ == '__main__':
    main()
