#!/usr/bin/env python3
"""
Servidor que recibe datos a través de paquetes ICMP echo (ping)
y reconstruye el archivo localmente.
"""

import sys
import os

try:
    from scapy.all import sniff, IP, ICMP
    SCAPY_AVAILABLE = True
except ImportError:
    SCAPY_AVAILABLE = False
    print("Instalando scapy...")
    os.system('pip3 install scapy')
    from scapy.all import sniff, IP, ICMP

reconstructed_data = bytearray()
packet_count = 0

def packet_callback(packet):
    global reconstructed_data, packet_count

    if packet.haslayer(ICMP):
        icmp_layer = packet[ICMP]

        # Solo procesar echo replies (tipo 0)
        if icmp_layer.type == 0:
            payload = icmp_layer.payload

            if payload:
                packet_count += 1
                payload_data = bytes(payload)
                hex_str = payload_data.hex()

                # Agregar datos
                reconstructed_data.extend(payload_data)

                print(f"[Paquete {packet_count}] ID: {icmp_layer.id}, Seq: {icmp_layer.seq}, Datos: {hex_str[:32]}...")

                # Marcador de fin
                if icmp_layer.seq == 0xFFFF:
                    print("\n✓ Fin de transmisión detectado")
                    raise KeyboardInterrupt

def main():
    global reconstructed_data, packet_count

    print("Servidor ICMP esperando paquetes ping...")
    print("(Requiere permisos de administrador)")
    print()

    try:
        # Capturar paquetes ICMP en interfaz loopback
        print("Escuchando en interfaz loopback (lo)...\n")
        sniff(prn=packet_callback, filter="icmp", store=False, iface='lo')

    except KeyboardInterrupt:
        pass
    finally:
        if reconstructed_data:
            output_file = 'received_file'
            with open(output_file, 'wb') as f:
                f.write(reconstructed_data)
            print(f"\n✓ Archivo reconstruido: {output_file}")
            print(f"✓ Bytes recibidos: {len(reconstructed_data)}")

if __name__ == '__main__':
    main()
