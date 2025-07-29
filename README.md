# Proyecto de Aprendizaje de Ansible

Este proyecto está diseñado para aprender Ansible paso a paso, desde lo más básico hasta conceptos avanzados.

## 🏠 Configuración Local

**Este proyecto está configurado para usar tu máquina local**, lo que significa:
- ✅ No necesitas servidores remotos
- ✅ No necesitas configurar SSH
- ✅ Puedes practicar inmediatamente
- ✅ Todo se ejecuta en tu MacBook

## 📁 Estructura del Proyecto Recomendada

```
ansible/
├── inventory/
│   └── inventory.ini          # Archivo de inventario (define qué servidores gestionar)
├── playbooks/
│   ├── 01-hello-world.yml     # Primer playbook (define qué tareas ejecutar)
│   ├── 02-local-test.yml      # Playbook para probar con IPs locales
│   └── 03-modulos-basicos.yml # Playbook para aprender módulos básicos
├── roles/                     # Roles (se crearán más adelante)
├── docs/                      # Documentación
│   └── modulos-basicos.md     # Guía de módulos básicos
├── templates/                 # Plantillas Jinja2 (se crearán más adelante)
├── files/                     # Archivos estáticos (se crearán más adelante)
├── vars/                      # Variables (se crearán más adelante)
├── ansible.cfg                # Configuración de Ansible (configuración global)
└── README.md                  # Este archivo
```

## 🎯 Mejores Prácticas de Ubicación de Archivos

### 📂 **Archivos en tu proyecto** (Recomendado para archivos importantes)
- **Configuraciones**: `files/config/`
- **Plantillas**: `templates/`
- **Documentación**: `docs/`
- **Variables**: `vars/`
- **Scripts**: `files/scripts/`

### 🗂️ **Archivos temporales** (Para pruebas y demostraciones)
- **Ubicación**: `/tmp/ansible-demo/`
- **Propósito**: Pruebas, demostraciones, experimentos
- **Ventaja**: Se limpia automáticamente

## Explicación de Archivos

### 📁 inventory/inventory.ini
- **¿Qué es?** Lista de servidores que Ansible puede gestionar
- **¿Qué hace?** Define grupos de hosts (webservers, dbservers, etc.)
- **¿Por qué es importante?** Sin inventario, Ansible no sabe en qué servidores trabajar
- **🔧 Configuración local:** Usa `localhost` y `127.0.0.1` para ejecutar en tu máquina

### 📁 playbooks/
- **¿Qué es?** Conjunto de playbooks (tareas automatizadas)
- **¿Qué hace?** Define qué tareas ejecutar y en qué orden
- **¿Por qué es importante?** Es donde defines la automatización

### 📁 docs/
- **¿Qué es?** Documentación del proyecto
- **¿Qué hace?** Guías, tutoriales, mejores prácticas
- **¿Por qué es importante?** Te ayuda a recordar y aprender

### 📁 ansible.cfg
- **¿Qué es?** Archivo de configuración global de Ansible
- **¿Qué hace?** Define configuraciones como inventario por defecto, SSH, etc.
- **¿Por qué es importante?** Asegura que todos los comandos usen la misma configuración

## Comandos Básicos Explicados

### 1. Verificar el inventario
```bash
ansible-inventory --list
```
**¿Qué hace?** Muestra todos los hosts y grupos en formato JSON
**¿Cuándo usarlo?** Para verificar que Ansible puede leer tu inventario

### 2. Ejecutar tu primer playbook
```bash
ansible-playbook playbooks/01-hello-world.yml
```
**¿Qué hace?** Ejecuta todas las tareas definidas en el playbook
**¿Cuándo usarlo?** Para automatizar tareas en tus servidores

### 3. Probar con IPs locales
```bash
ansible-playbook playbooks/02-local-test.yml
```
**¿Qué hace?** Muestra información detallada de tu sistema local
**¿Cuándo usarlo?** Para aprender qué información puede recopilar Ansible

### 4. Aprender módulos básicos
```bash
ansible-playbook playbooks/03-modulos-basicos.yml
```
**¿Qué hace?** Demuestra los módulos más importantes de Ansible
**¿Cuándo usarlo?** Para aprender cómo automatizar tareas comunes

### 5. Hacer ping a todos los hosts
```bash
ansible all -m ping
```
**¿Qué hace?** Verifica conectividad con todos los hosts del inventario
**¿Cuándo usarlo?** Para probar que puedes conectarte a tus servidores

### 6. Ejecutar un comando en todos los hosts
```bash
ansible all -m command -a "uptime"
```
**¿Qué hace?** Ejecuta el comando "uptime" en todos los hosts
**¿Cuándo usarlo?** Para ejecutar comandos rápidos sin crear un playbook

## Conceptos Clave

### 🔧 Módulos
- **¿Qué son?** Funciones predefinidas de Ansible (ping, command, debug, etc.)
- **Ejemplos:** `ping`, `command`, `file`, `copy`, `template`

### 🎯 Tasks (Tareas)
- **¿Qué son?** Acciones individuales que se ejecutan en los servidores
- **Ejemplo:** "Instalar nginx", "Copiar archivo", "Reiniciar servicio"

### 🎭 Plays
- **¿Qué son?** Conjuntos de tareas que se ejecutan en un grupo de hosts
- **Ejemplo:** Un play para configurar webservers, otro para dbservers

### 📦 Playbooks
- **¿Qué son?** Archivos YAML que contienen uno o más plays
- **Ejemplo:** Un playbook completo para desplegar una aplicación web

### 🏠 Conexión Local
- **¿Qué es?** `ansible_connection=local` ejecuta tareas en tu máquina
- **¿Cuándo usarlo?** Para desarrollo, pruebas y aprendizaje
- **Ventajas:** No requiere SSH, más rápido, ideal para principiantes

## Próximos Pasos

1. ✅ Configurar inventario básico
2. ✅ Crear primer playbook
3. ✅ Configurar para uso local
4. ✅ Aprender módulos básicos (file, copy, template)
5. ✅ Crear playbooks más complejos
6. ✅ Trabajar con variables y facts
7. ✅ Crear roles reutilizables
8. ✅ Manejar secrets y vault
9. ✅ Testing y debugging de playbooks
10. ✅ Handlers y condiciones avanzadas
11. ✅ CI/CD con Ansible

## Consejos de Uso

- **Siempre verifica tu sintaxis:** `ansible-playbook --syntax-check playbook.yml`
- **Ejecuta en modo dry-run:** `ansible-playbook --check playbook.yml`
- **Usa verbose para debug:** `ansible-playbook -v playbook.yml`
- **Lee los logs:** Ansible te dice exactamente qué está pasando
- **Para desarrollo local:** Usa `ansible_connection=local` en tu inventario
- **Archivos temporales:** Usa `/tmp` para pruebas y demostraciones
- **Archivos importantes:** Guárdalos en tu proyecto con estructura organizada

## 🧪 **Testing y Debugging**

### **Comandos esenciales:**
```bash
# Verificar sintaxis
ansible-playbook --syntax-check playbooks/10-testing-debugging.yml

# Simular ejecución (dry-run)
ansible-playbook --check playbooks/10-testing-debugging.yml

# Ejecutar con información detallada
ansible-playbook -v playbooks/10-testing-debugging.yml

# Verificar conectividad
ansible all -m ping
```

### **Archivos de ejemplo:**
- `playbooks/10-testing-debugging.yml` - Demostración de testing
- `playbooks/10-testing-errors.yml` - Ejemplos de errores (para debugging)
- `docs/testing-debugging.md` - Guía completa de testing

### **Beneficios:**
- ✅ Detecta errores antes de ejecutar
- ✅ Prueba cambios sin afectar sistemas
- ✅ Obtiene información detallada para debugging
- ✅ Valida configuración antes de producción

## 🔄 **Handlers y Condiciones Avanzadas**

### **Comandos esenciales:**
```bash
# Ejecutar playbook con handlers avanzados
ansible-playbook playbooks/11-handlers-avanzados.yml

# Ejecutar playbook con condiciones avanzadas
ansible-playbook playbooks/11-condiciones-avanzadas.yml
```

### **Archivos de ejemplo:**
- `playbooks/11-handlers-avanzados.yml` - Handlers con múltiples notificaciones
- `playbooks/11-condiciones-avanzadas.yml` - Condiciones complejas y bloques
- `docs/handlers-condiciones-avanzadas.md` - Guía completa

### **Características:**
- ✅ Handlers inteligentes que se ejecutan solo cuando es necesario
- ✅ Condiciones complejas (AND, OR, NOT) y expresiones anidadas
- ✅ Bloques de manejo de errores (block, rescue, always)
- ✅ Validación de variables antes de ejecutar tareas críticas

## 🚀 **CI/CD con Ansible**

### **Comandos esenciales:**
```bash
# Ejecutar pipeline completo (requiere GitHub Actions)
git push origin main

# Build de imágenes Docker
docker build -f docker/Dockerfile.base -t ansible-base .
docker build -f docker/Dockerfile.app -t ansible-app .

# Desplegar a staging
ansible-playbook ci-cd/deploy-staging.yml -e "image_tag=latest"

# Desplegar a producción
ansible-playbook ci-cd/deploy-production.yml -e "image_tag=latest"

# Ejecutar health checks
python monitoring/health_check.py

# Configurar alertas
python monitoring/setup_alerts.py

# Generar reporte
python monitoring/generate_report.py
```

### **Archivos de ejemplo:**
- `.github/workflows/ansible-ci-cd.yml` - Pipeline completo de GitHub Actions
- `docker/Dockerfile.base` - Imagen base con Ansible
- `docker/Dockerfile.app` - Imagen de aplicación
- `kubernetes/staging/` - Configuración de Kubernetes para staging
- `kubernetes/production/` - Configuración de Kubernetes para producción
- `ci-cd/deploy-staging.yml` - Playbook de despliegue a staging
- `ci-cd/deploy-production.yml` - Playbook de despliegue a producción
- `monitoring/health_check.py` - Script de health checks
- `monitoring/setup_alerts.py` - Configuración de alertas
- `monitoring/generate_report.py` - Generación de reportes
- `docs/ci-cd.md` - Guía completa de CI/CD

### **Características:**
- ✅ Pipeline completo de CI/CD con GitHub Actions
- ✅ Containerización con Docker y orquestación con Kubernetes
- ✅ Despliegue automático a staging y producción
- ✅ Monitoring y alertas con Prometheus y Slack
- ✅ Health checks automáticos y reportes detallados
- ✅ Rollback automático en caso de errores
- ✅ Aplicación web con dashboard para gestión

## 🔐 **Ansible Vault - Seguridad**

### **¿Qué es Vault?**
Ansible Vault permite encriptar información sensible como contraseñas, claves API y certificados.

### **Comandos básicos de Vault:**
```bash
# Encriptar archivo
ansible-vault encrypt vars/secrets.yml

# Ver contenido encriptado
ansible-vault view vars/secrets.yml

# Ejecutar playbook con archivo encriptado
ansible-playbook playbook.yml --vault-password-file .vault_pass
```

### **Archivos de ejemplo:**
- `vars/secrets.yml` - Variables sensibles (encriptado)
- `.vault_pass` - Archivo de contraseña (no subir al repositorio)
- `playbooks/09-vault-demo.yml` - Demostración de Vault

### **Seguridad:**
- ✅ Archivos encriptados con AES256
- ✅ Contraseñas separadas del código
- ✅ Permisos seguros en archivos
- ✅ Variables enmascaradas en logs 