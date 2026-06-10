# File Transfer Tool

Herramienta para transferir archivos entre máquinas Windows y Linux.

**Versiones disponibles:**
- **TCP** (Recomendado): Funciona perfectamente en Windows y Linux. Cliente shell puro.
- **ICMP/Ping** (Legacy): Cliente Python, requiere scapy.

## Inicio Rápido (TCP)

### Servidor (Windows o Linux)
```bash
python3 server_tcp.py
```

### Cliente (Linux/macOS)
```bash
bash client_tcp.sh archivo.txt 192.168.1.151
```

El archivo se transfiere automáticamente al puerto 9999.

## Características

**Versión TCP (Recomendada):**
- Cliente bash puro (sin dependencias)
- Servidor Python multiplataforma
- Funciona entre Windows ↔ Linux
- Simple y confiable

**Versión ICMP (Legacy):**
- Cliente Python o shell script
- Usa paquetes ICMP (ping)
- Requiere scapy en el cliente
- Chunks configurables

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
================================================================================
INTERFACES DISPONIBLES
================================================================================
ID    Nombre               IP                   Gateway             
--------------------------------------------------------------------------------
1     lo                   127.0.0.1            192.168.1.1         
2     eth0                 192.168.1.100        192.168.1.1         
3     wlan0                192.168.1.105        192.168.1.1         
4     docker0              172.17.0.1           N/A                 
================================================================================
```

### 2. Iniciar el servidor

#### Opción A: Seleccionar interfaz interactivamente

**Linux/macOS:**
```bash
sudo python3 server.py
```

**Windows (PowerShell como Administrador):**
```powershell
python server.py
```

Salida:
```
================================================================================
INTERFACES DISPONIBLES
================================================================================
ID    Nombre               IP                   Gateway             
--------------------------------------------------------------------------------
1     lo                   127.0.0.1            192.168.1.1         
2     eth0                 192.168.1.100        192.168.1.1         
3     wlan0                192.168.1.105        192.168.1.1         
================================================================================

Selecciona una interfaz (por ID o nombre): 1
```

Puedes seleccionar por **ID** (1, 2, 3...) o por **nombre** (lo, eth0, wlan0...)

#### Opción B: Auto-detectar loopback

Si existe una interfaz loopback (lo/lo0), se detectará automáticamente.

#### Opción C: Especificar interfaz directamente

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
Uso: python3 server.py [opciones] [interfaz]

Opciones:
  --list, -l      Listar interfaces disponibles
  --help, -h      Mostrar esta ayuda

Ejemplos:
  python3 server.py              # Seleccionar interfaz interactivamente
  python3 server.py lo           # Usar interfaz 'lo'
  python3 server.py 1            # Usar ID de interfaz (si --list muestra ID)
  python3 server.py eth0         # Usar interfaz 'eth0'
  python3 server.py --list       # Listar interfaces con ID
  python3 server.py --help       # Mostrar ayuda
```

## Ejemplos

### TCP (Recomendado)

**Windows:**
```powershell
# Terminal 1 - Servidor
python3 server_tcp.py

# Terminal 2 (en otra máquina con Linux)
bash client_tcp.sh myfile.txt 192.168.1.151
```

**Linux:**
```bash
# Terminal 1 - Servidor
python3 server_tcp.py

# Terminal 2 (en otra máquina)
bash client_tcp.sh myfile.txt 192.168.1.100
```

Resultado: `received_file_*` contendrá los datos del archivo.

### ICMP/Ping (Legacy)

```bash
# Terminal 1 - Servidor
sudo python3 server.py lo

# Terminal 2 - Cliente (con scapy)
sudo python3 client.py photo.jpg 127.0.0.1

# O con shell script (solo Linux)
bash client.sh photo.jpg 127.0.0.1
```

## Notas de seguridad

- Este proyecto es educativo/experimental
- Requiere acceso a raw sockets (administrador)
- En redes reales, los firewalls pueden bloquear paquetes ICMP anómalos
- No usar para transferencias sensibles sin encriptación adicional

## Licencia

MIT

## Autor

Created as a proof-of-concept for data exfiltration via ICMP
