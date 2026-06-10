#!/usr/bin/env python3
"""
Servidor que recibe datos a través de paquetes ICMP echo (ping)
y reconstruye el archivo localmente.
"""

import sys
import os
import platform

try:
    from scapy.all import sniff, IP, ICMP, get_if_list, get_if_addr, conf
    SCAPY_AVAILABLE = True
except ImportError:
    SCAPY_AVAILABLE = False
    print("Instalando scapy...")
    os.system('pip3 install scapy')
    from scapy.all import sniff, IP, ICMP, get_if_list, get_if_addr, conf

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

def get_loopback_interface():
    """Detectar la interfaz loopback según el SO."""
    system = platform.system()
    interfaces = get_if_list()

    if system == "Windows":
        # En Windows, buscar interfaz loopback
        loopback_names = ['lo', 'Loopback', 'lo0']
        for name in loopback_names:
            if name in interfaces:
                return name
        # Si no encuentra, usar cualquier interfaz local
        return None
    else:  # Linux, macOS
        if 'lo' in interfaces:
            return 'lo'
        elif 'lo0' in interfaces:
            return 'lo0'
    return None

def get_interface_gateway():
    """Obtener el gateway desde la tabla de rutas de scapy."""
    try:
        # Buscar la ruta por defecto (destino 0.0.0.0)
        for route in conf.route.routes:
            if route[0] == 0:  # Ruta por defecto
                return route[2]  # Gateway (posición 2)
    except:
        pass
    return "N/A"

def list_interfaces():
    """Mostrar todas las interfaces disponibles con IP y gateway."""
    interfaces = get_if_list()
    gateway = get_interface_gateway()

    print("\n" + "=" * 70)
    print("INTERFACES DISPONIBLES")
    print("=" * 70)
    print(f"{'Nombre':<20} {'IP':<20} {'Gateway':<20}")
    print("-" * 70)

    for iface in interfaces:
        try:
            ip = get_if_addr(iface)
        except:
            ip = "N/A"

        print(f"{iface:<20} {ip:<20} {gateway:<20}")

    print("=" * 70 + "\n")

def main():
    global reconstructed_data, packet_count

    system = platform.system()
    print(f"Servidor ICMP (Sistema: {system})")
    print("Esperando paquetes ping...")
    print("(Requiere permisos de administrador/root)")
    print()

    # Argumentos de línea de comandos
    selected_iface = None
    if len(sys.argv) > 1:
        arg = sys.argv[1]
        if arg == "--list" or arg == "-l":
            list_interfaces()
            return
        elif arg == "--help" or arg == "-h":
            print("Uso: python3 server.py [interfaz]")
            print()
            print("Opciones:")
            print("  --list, -l      Listar interfaces disponibles")
            print("  --help, -h      Mostrar esta ayuda")
            print()
            print("Ejemplos:")
            print("  python3 server.py              # Auto-detectar loopback")
            print("  python3 server.py lo           # Usar interfaz 'lo'")
            print("  python3 server.py eth0         # Usar interfaz 'eth0'")
            print("  python3 server.py --list       # Listar interfaces")
            return
        else:
            selected_iface = arg

    # Detectar interfaz loopback si no se especificó
    if not selected_iface:
        selected_iface = get_loopback_interface()
        if selected_iface:
            print(f"Interfaz detectada automáticamente: {selected_iface}")
        else:
            print("No se detectó interfaz loopback. Mostrando interfaces disponibles:\n")
            list_interfaces()
            print("\nUso: python3 server.py <nombre_interfaz>")
            print("Ejemplo: python3 server.py lo")
            return

    try:
        print(f"Escuchando en interfaz: {selected_iface}\n")
        sniff(prn=packet_callback, filter="icmp", store=False, iface=selected_iface)

    except PermissionError:
        print("Error: Se requieren permisos de administrador/root")
        print("En Windows: Ejecutar como Administrador")
        print("En Linux/macOS: Usar 'sudo python3 server.py'")
        sys.exit(1)
    except OSError as e:
        if "Npcap" in str(e) or "WinPcap" in str(e):
            print("Error: Npcap no está instalado")
            print("Descárgalo desde: https://npcap.com/")
            sys.exit(1)
        raise
    except KeyboardInterrupt:
        pass
    finally:
        if reconstructed_data:
            output_file = 'received_file'
            with open(output_file, 'wb') as f:
                f.write(reconstructed_data)
            print(f"\n✓ Archivo reconstruido: {output_file}")
            print(f"✓ Bytes recibidos: {len(reconstructed_data)}")
        else:
            print("\nNo se recibió ningún dato")

if __name__ == '__main__':
    main()
