#!/usr/bin/env python3
"""
Servidor TCP que recibe archivos con nombre y los reconstruye localmente.
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
    system = platform.system()

    print("=" * 50)
    print("SERVIDOR TCP - Transferencia de Archivos")
    print("=" * 50)
    print(f"Sistema: {system}")
    print(f"Puerto: {port}")
    print("")

    try:
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        try:
            server_socket.bind(('0.0.0.0', port))
        except OSError as e:
            print(f"Error al vincular puerto {port}: {e}")
            print("")
            print("Soluciones:")
            print("  1. El puerto está en uso - Usa otro puerto")
            print("  2. En Windows: Abre PowerShell como Administrador")
            print("  3. En Linux: Usa 'sudo python3 server_tcp.py'")
            sys.exit(1)

        server_socket.listen(1)

        print(f"✓ Escuchando en 0.0.0.0:{port}")
        print("✓ Esperando conexiones...")
        print("")
        print("Para enviar archivo:")
        print(f"  bash client_tcp.sh <archivo> <tu_ip> {port}")
        print("")
        print("Presiona Ctrl+C para detener\n")

        while True:
            try:
                print("Esperando conexión...")
                client_socket, client_address = server_socket.accept()
                print(f"✓ Cliente conectado desde {client_address[0]}:{client_address[1]}\n")

                # Recibir nombre del archivo (longitud + nombre)
                name_len_byte = client_socket.recv(1)
                if not name_len_byte:
                    print("Error: No se recibió longitud del nombre")
                    client_socket.close()
                    continue

                name_len = ord(name_len_byte)
                filename = client_socket.recv(name_len).decode('utf-8', errors='ignore')

                if not filename:
                    filename = "received_file"

                print(f"Nombre de archivo: {filename}")

                # Recibir datos del archivo
                reconstructed_data = bytearray()
                packet_count = 0

                while True:
                    try:
                        data = client_socket.recv(4096)

                        if not data:
                            print("Conexión cerrada por el cliente")
                            break

                        packet_count += 1
                        reconstructed_data.extend(data)

                        print(f"[Paquete {packet_count}] Bytes: {len(data)}")

                    except KeyboardInterrupt:
                        raise
                    except Exception as e:
                        print(f"Error recibiendo datos: {e}")
                        break

                client_socket.close()
                print("")

                # Guardar archivo
                if reconstructed_data:
                    output_file = filename
                    try:
                        with open(output_file, 'wb') as f:
                            f.write(reconstructed_data)
                        print(f"✓ Archivo guardado: {output_file}")
                        print(f"✓ Tamaño total: {len(reconstructed_data)} bytes")
                        print(f"✓ Paquetes recibidos: {packet_count}\n")
                    except Exception as e:
                        print(f"✗ Error al guardar archivo: {e}\n")
                else:
                    print("⚠️  No se recibió ningún dato\n")

            except KeyboardInterrupt:
                raise

    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupción detectada")
        if confirm_action("¿Cerrar servidor? (s/n): "):
            print("Cerrando servidor...")
            server_socket.close()
        else:
            print("Continuando...\n")
            main()

if __name__ == '__main__':
    main()
