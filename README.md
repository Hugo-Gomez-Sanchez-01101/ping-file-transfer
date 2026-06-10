# TCP File Transfer Tool

Herramienta simple y confiable para transferir archivos entre máquinas Windows y Linux usando TCP.

## Características

- **Cliente bash puro** - Sin dependencias Python
- **Servidor Python** - Compatible con Windows y Linux
- **Envío de nombre de archivo** - Los archivos se reciben con su nombre original
- **Múltiples métodos** - /dev/tcp, netcat, telnet, socat
- **Bidireccional** - Funciona de Windows a Linux y Linux a Linux

## Requisitos

### Servidor
- Python 3.6+
- Permisos de administrador/root

### Cliente
- bash (no sh)
- Una de estas herramientas:
  - `/dev/tcp` (bash built-in - Linux/macOS)
  - `nc` (netcat)
  - `telnet`
  - `socat`

## Instalación rápida

```bash
# Instalar netcat si no tienes /dev/tcp
sudo apt-get install netcat-openbsd   # Debian/Ubuntu
sudo yum install nmap-ncat             # RHEL/CentOS
brew install netcat                    # macOS
```

## Uso

### 1. Iniciar servidor

**Windows (PowerShell como Administrador):**
```powershell
python3 .\server_tcp.py
```

**Linux/macOS:**
```bash
sudo python3 server_tcp.py
```

### 2. Enviar archivo

**Desde otra máquina:**
```bash
bash client_tcp.sh archivo.txt 192.168.1.151 9999
```

**Parámetros:**
- `archivo.txt` - Archivo a enviar
- `192.168.1.151` - IP del servidor
- `9999` - Puerto (opcional, por defecto 9999)

### 3. Verificar archivo

El servidor guardará el archivo con su **nombre original** automáticamente.

## Ejemplos

### Windows → Linux
```bash
# En Linux (servidor)
sudo python3 server_tcp.py

# En Windows (cliente) - WSL o Git Bash
bash client_tcp.sh documento.pdf 192.168.1.100 9999
```

### Linux → Linux
```bash
# Servidor
sudo python3 server_tcp.py

# Cliente
bash client_tcp.sh photo.jpg 192.168.1.50 9999
```

### Windows → Windows
```powershell
# Servidor (PowerShell Admin)
python3 .\server_tcp.py
```

```bash
# Cliente (otro Windows - WSL/Git Bash)
bash client_tcp.sh archivo.exe 192.168.1.151 9999
```

## Cómo funciona

1. **Cliente** se conecta al servidor TCP
2. **Cliente** envía:
   - Longitud del nombre de archivo (1 byte)
   - Nombre del archivo
   - Contenido del archivo
3. **Servidor** recibe y guarda con nombre original

## Métodos de conexión (automáticos)

El cliente intenta en orden:
1. `/dev/tcp` (bash built-in, rápido, Linux/macOS)
2. `nc` (netcat, multiplataforma)
3. `telnet` (disponible en la mayoría de sistemas)
4. `socat` (robusto, si está instalado)

## Troubleshooting

**"Error: El puerto está en uso"**
```bash
# Linux: cambiar puerto
sudo python3 server_tcp.py 9999  # usar otro puerto

# Windows: ejecutar como Administrador
```

**"No se pudo usar ningún método"**
```bash
# Instalar netcat (más compatible)
sudo apt-get install netcat-openbsd
```

**"Archivo no aparece en servidor"**
- Verificar que el servidor está ejecutándose
- Verificar firewall permite puerto 9999
- En Windows: desactivar Windows Defender Firewall (para tests)

## Licencia

MIT

## Notas

- Usa TCP, no ICMP/ping - mucho más confiable
- Funciona a través de redes e internet
- No tiene límite de tamaño de archivo
- Comparte conexión: múltiples archivos sequencialmente
