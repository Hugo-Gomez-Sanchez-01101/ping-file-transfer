#!/usr/bin/env python3
"""
Servidor TCP que recibe archivos en chunks y los reconstruye localmente.
Compatible con Windows y Linux.
"""

import socket
import sys
import os
import platform

def confirm_action(message="¿Estás seguro? (s/n): "):
    """Pedir confirmación al usuario."""
    while True:
        try:
            response = input(message).strip().lower()
            if response in ['s', 'si', 'yes', 'y']:
                return True
            elif response in ['n', 'no']:
                return False
            else:
                print("Por favor, responde 's' o 'n'")
        except KeyboardInterrupt:
            print()
            return False

def main():
    port = 9999
    reconstructed_data = bytearray()
    packet_count = 0

    system = platform.system()
    print(f"Servidor TCP (Sistema: {system})")
    print(f"Puerto: {port}")
    print("Esperando conexiones...\n")

    try:
        # Crear socket TCP
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind(('0.0.0.0', port))
        server_socket.listen(1)

        print(f"Escuchando en 0.0.0.0:{port}")
        print("Presiona Ctrl+C para detener\n")

        while True:
            try:
                print("Esperando conexión...")
                client_socket, client_address = server_socket.accept()
                print(f"✓ Cliente conectado desde {client_address[0]}:{client_address[1]}\n")

                reconstructed_data = bytearray()
                packet_count = 0

                while True:
                    try:
                        # Recibir datos
                        data = client_socket.recv(1024)

                        if not data:
                            # Conexión cerrada
                            print("Conexión cerrada por el cliente")
                            break

                        packet_count += 1
                        reconstructed_data.extend(data)

                        hex_str = data.hex()
                        print(f"[Paquete {packet_count}] Bytes: {len(data)}, Datos: {hex_str[:32]}...")

                    except KeyboardInterrupt:
                        raise
                    except Exception as e:
                        print(f"Error recibiendo datos: {e}")
                        break

                client_socket.close()

                # Guardar archivo si se recibió data
                if reconstructed_data:
                    output_file = f'received_file_{packet_count}bytes'
                    with open(output_file, 'wb') as f:
                        f.write(reconstructed_data)
                    print(f"✓ Archivo guardado: {output_file}")
                    print(f"✓ Bytes recibidos: {len(reconstructed_data)}\n")

            except KeyboardInterrupt:
                raise

    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupción detectada")
        if confirm_action("¿Cerrar servidor? (s/n): "):
            print("Cerrando servidor...")
            server_socket.close()
        else:
            print("Continuando...\n")
            # Reintentar
            main()

if __name__ == '__main__':
    main()
