# Ping File Transfer

Herramienta que permite transferir archivos a través de paquetes ICMP (ping). Los datos se incrustan en el payload de los paquetes ping y se reconstruyen en el servidor.

## Características

- **Cliente Python**: Lee un archivo y lo envía en chunks a través de paquetes ICMP echo
- **Servidor Python**: Captura paquetes ICMP y reconstruye el archivo original
- Compatible con Windows, Linux y macOS
- Chunks configurables (por defecto 4 bytes)

## Requisitos

- Python 3.6+
- Permisos de administrador (para acceso a raw sockets ICMP)

## Instalación

```bash
git clone <repository-url>
cd ping-file-transfer
```

## Requisitos adicionales

### En Windows
- Descargar e instalar **Npcap** desde https://npcap.com/
- Ejecutar PowerShell como Administrador

### En Linux/macOS
- Ejecutar con `sudo`

## Uso

### 1. Listar interfaces disponibles

**Linux/macOS:**
```bash
sudo python3 server.py --list
```

**Windows (PowerShell como Administrador):**
```powershell
python server.py --list
```

Output:
```
Interfaces disponibles:
--------------------------------------------------
  • lo
  • eth0
  • wlan0
  • docker0
--------------------------------------------------
```

### 2. Iniciar el servidor

#### Opción A: Auto-detectar loopback

**Linux/macOS:**
```bash
sudo python3 server.py
```

**Windows (PowerShell como Administrador):**
```powershell
python server.py
```

#### Opción B: Especificar interfaz

**Linux/macOS:**
```bash
sudo python3 server.py lo
# O cualquier otra interfaz:
sudo python3 server.py eth0
```

**Windows (PowerShell como Administrador):**
```powershell
python server.py Loopback
# O cualquier otra interfaz:
python server.py eth0
```

El servidor escuchará paquetes ICMP:

```
Servidor ICMP (Sistema: Linux)
Esperando paquetes ping...
Escuchando en interfaz: lo

[Paquete 1] ID: 1234, Seq: 0, Datos: 7f454c46...
[Paquete 2] ID: 1234, Seq: 1, Datos: 01010100...
...
✓ Archivo reconstruido: received_file
✓ Bytes recibidos: 5232
```

### 3. Enviar archivo (opción A - Python)

**Linux/macOS:**
```bash
sudo python3 client.py myfile.bin 127.0.0.1
```

**Windows (PowerShell como Administrador):**
```powershell
python client.py myfile.bin 127.0.0.1
```

### 3. Enviar archivo (opción B - Shell script, solo Linux/macOS)

```bash
bash client.sh myfile.bin 127.0.0.1
```

## Cómo funciona

1. **Cliente**: 
   - Lee el archivo en binario
   - Convierte a hexadecimal
   - Divide en chunks de 4 bytes (8 caracteres hex)
   - Envía cada chunk como payload en un paquete ICMP echo request

2. **Servidor**:
   - Captura paquetes ICMP entrantes
   - Extrae el payload de cada paquete
   - Reconstruye el archivo original

3. **Finalización**:
   - Presionar Ctrl+C en el servidor para detener y guardar
   - El cliente envía un paquete final con sequence = 0xFFFF como marcador

## Opciones del servidor

```
Uso: python3 server.py [interfaz]

Opciones:
  --list, -l      Listar interfaces disponibles
  --help, -h      Mostrar esta ayuda

Ejemplos:
  python3 server.py              # Auto-detectar loopback
  python3 server.py lo           # Usar interfaz 'lo'
  python3 server.py eth0         # Usar interfaz 'eth0'
  python3 server.py --list       # Listar interfaces
```

## Ejemplo completo

```bash
# Terminal 1 - Listar interfaces
sudo python3 server.py --list

# Terminal 1 - Iniciar servidor en loopback
sudo python3 server.py lo

# Terminal 2 - Enviar archivo
sudo python3 client.py photo.jpg 127.0.0.1
```

Resultado: `received_file` contendrá los datos de `photo.jpg`

## Notas de seguridad

- Este proyecto es educativo/experimental
- Requiere acceso a raw sockets (administrador)
- En redes reales, los firewalls pueden bloquear paquetes ICMP anómalos
- No usar para transferencias sensibles sin encriptación adicional

## Licencia

MIT

## Autor

Created as a proof-of-concept for data exfiltration via ICMP
