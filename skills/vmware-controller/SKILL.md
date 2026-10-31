---
name: vmware-controller
description: Control y automatización de VMware Workstation Player mediante la CLI vmrun y vmplayer ubicada en C:\Program Files (x86)\VMware\VMware Player. Úsalo para encender, apagar, suspender, listar y ejecutar programas o pruebas dentro de máquinas virtuales de forma desatendida.
---

# VMware Controller (Workstation Player CLI)

Permite controlar máquinas virtuales VMware locales de forma desatendida utilizando la suite VIX / `vmrun.exe`.

## 1. Rutas del Sistema
- **Directorio Base:** `C:\Program Files (x86)\VMware\VMware Player`
- **CLI Principal (`vmrun`):** `C:\Program Files (x86)\VMware\VMware Player\vmrun.exe`
- **Ejecutable GUI (`vmplayer`):** `C:\Program Files (x86)\VMware\VMware Player\vmplayer.exe`
- **Servicio REST (`vmrest`):** `C:\Program Files (x86)\VMware\VMware Player\vmrest.exe`

---

## 2. Comandos Esenciales de `vmrun`

Para VMware Player, siempre utiliza el flag de tipo de producto `-T player`:

```powershell
# Variable de conveniencia
$VMRUN = "C:\Program Files (x86)\VMware\VMware Player\vmrun.exe"

# 1. Listar máquinas virtuales activas en ejecución
& $VMRUN -T player list

# 2. Iniciar máquina virtual en segundo plano (headless / sin ventana)
& $VMRUN -T player start "C:\Ruta\A\TuMaquina.vmx" nogui

# 3. Iniciar máquina virtual con interfaz gráfica
& $VMRUN -T player start "C:\Ruta\A\TuMaquina.vmx" gui

# 4. Apagar máquina virtual de forma segura (Graceful Shutdown)
& $VMRUN -T player stop "C:\Ruta\A\TuMaquina.vmx" soft

# 5. Apagar inmediatamente (Hard Power Off)
& $VMRUN -T player stop "C:\Ruta\A\TuMaquina.vmx" hard

# 6. Suspender máquina virtual
& $VMRUN -T player suspend "C:\Ruta\A\TuMaquina.vmx"

# 7. Reiniciar
& $VMRUN -T player reset "C:\Ruta\A\TuMaquina.vmx" soft
```

---

## 3. Ejecución de Comandos dentro de la Máquina Virtual (Guest)

Si la máquina tiene instaladas las **VMware Tools**, puedes ejecutar comandos directamente dentro del sistema operativo invitado sin abrir la interfaz:

```powershell
# Ejecutar un script o binario dentro del Guest:
& $VMRUN -T player -gu <UsuarioGuest> -gp <PasswordGuest> runProgramInGuest "C:\Ruta\A\TuMaquina.vmx" "C:\Windows\System32\cmd.exe" "/c dir C:\"

# Copiar archivo del Host al Guest:
& $VMRUN -T player -gu <UsuarioGuest> -gp <PasswordGuest> copyFileFromHostToGuest "C:\Ruta\A\TuMaquina.vmx" "C:\Host\archivo.zip" "C:\Guest\archivo.zip"

# Copiar archivo del Guest al Host:
& $VMRUN -T player -gu <UsuarioGuest> -gp <PasswordGuest> copyFileFromGuestToHost "C:\Ruta\A\TuMaquina.vmx" "C:\Guest\resultado.log" "C:\Host\resultado.log"
```
