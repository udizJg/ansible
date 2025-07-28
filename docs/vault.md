# Ansible Vault

## 📚 ¿Qué es Ansible Vault?

**Ansible Vault** es una característica de Ansible que permite **encriptar información sensible** como contraseñas, claves API, certificados SSL y otros datos confidenciales. Es esencial para mantener la seguridad en proyectos de automatización.

### 🎯 **Características principales:**
- ✅ **Encriptación AES256**: Algoritmo de encriptación robusto
- ✅ **Integración transparente**: Funciona con playbooks existentes
- ✅ **Gestión de contraseñas**: Múltiples formas de manejar contraseñas
- ✅ **Archivos individuales**: Encripta archivos específicos, no todo el proyecto
- ✅ **Variables seguras**: Protege información sensible en variables

## 🔐 **Comandos principales de Ansible Vault**

### **Encriptar archivos**
```bash
# Encriptar un archivo (te pedirá contraseña)
ansible-vault encrypt archivo.yml

# Encriptar con archivo de contraseña
ansible-vault encrypt archivo.yml --vault-password-file .vault_pass

# Encriptar con contraseña desde variable de entorno
export ANSIBLE_VAULT_PASSWORD=mi_contraseña
ansible-vault encrypt archivo.yml --vault-password-file /dev/stdin
```

### **Desencriptar archivos**
```bash
# Desencriptar un archivo
ansible-vault decrypt archivo.yml

# Desencriptar con archivo de contraseña
ansible-vault decrypt archivo.yml --vault-password-file .vault_pass
```

### **Ver contenido encriptado**
```bash
# Ver contenido sin desencriptar
ansible-vault view archivo.yml

# Ver con archivo de contraseña
ansible-vault view archivo.yml --vault-password-file .vault_pass
```

### **Editar archivos encriptados**
```bash
# Editar directamente (se abre en editor)
ansible-vault edit archivo.yml

# Editar con archivo de contraseña
ansible-vault edit archivo.yml --vault-password-file .vault_pass
```

### **Crear archivos encriptados**
```bash
# Crear archivo nuevo ya encriptado
ansible-vault create archivo.yml

# Crear con archivo de contraseña
ansible-vault create archivo.yml --vault-password-file .vault_pass
```

### **Cambiar contraseña**
```bash
# Cambiar contraseña de un archivo
ansible-vault rekey archivo.yml

# Cambiar con archivo de contraseña
ansible-vault rekey archivo.yml --vault-password-file .vault_pass
```

## 📁 **Estructura recomendada para variables sensibles**

```
proyecto-ansible/
├── vars/
│   ├── secrets.yml          # Variables sensibles (encriptado)
│   ├── database.yml         # Configuración de BD (encriptado)
│   └── api_keys.yml         # Claves API (encriptado)
├── .vault_pass              # Archivo de contraseña (modo 600)
├── .gitignore               # Incluir archivos sensibles
└── playbooks/
    └── deploy.yml           # Playbook que usa variables encriptadas
```

## 🔧 **Configuración de seguridad**

### **Archivo de contraseña (.vault_pass)**
```bash
# Crear archivo de contraseña
echo "mi_contraseña_vault_segura_123" > .vault_pass

# Configurar permisos seguros
chmod 600 .vault_pass
```

### **Variables de entorno**
```bash
# Configurar contraseña como variable de entorno
export ANSIBLE_VAULT_PASSWORD="mi_contraseña_vault_segura_123"

# O usar un archivo
export ANSIBLE_VAULT_PASSWORD_FILE=".vault_pass"
```

## 📝 **Ejemplo de archivo de variables sensibles**

```yaml
---
# ===========================================
# ARCHIVO DE VARIABLES SENSIBLES
# ===========================================

# Credenciales de base de datos
database:
  root_password: 'SuperSecretRootPassword123!'
  app_password: 'AppUserPassword456!'
  backup_password: 'BackupPassword789!'

# Credenciales de API
api_credentials:
  github_token: 'ghp_1234567890abcdefghijklmnopqrstuvwxyz'
  aws_access_key: 'AKIA1234567890ABCDEF'
  aws_secret_key: 'abcdefghijklmnopqrstuvwxyz1234567890abcdefghijklmnop'

# Tokens de servicios
service_tokens:
  redis_password: 'RedisSecretPassword123!'
  nginx_basic_auth: 'admin:SuperSecretNginxPass456!'
  monitoring_api_key: 'monitoring_secret_key_789!'

# Variables de entorno sensibles
environment_vars:
  NODE_ENV: 'production'
  JWT_SECRET: 'super_secret_jwt_key_123456789'
  SESSION_SECRET: 'session_secret_key_987654321'
```

## 🎭 **Uso en playbooks**

### **Cargar variables encriptadas**
```yaml
---
- name: Playbook con variables encriptadas
  hosts: all
  gather_facts: yes
  
  # Cargar variables encriptadas
  vars_files:
    - vars/secrets.yml
  
  tasks:
    - name: Usar variables sensibles
      debug:
        msg: "Conectando a BD con usuario: {{ database.app_password }}"
      no_log: true  # Oculta la salida en logs
```

### **Crear archivos de configuración seguros**
```yaml
- name: Crear archivo de configuración seguro
  copy:
    content: |
      [database]
      password = {{ database.app_password }}
      host = {{ database.host }}
    dest: /etc/app/database.conf
    mode: '0600'  # Solo propietario puede leer
    owner: app_user
    group: app_group
  no_log: true  # Oculta contenido en logs
```

## 🛡️ **Mejores prácticas de seguridad**

### **1. Gestión de contraseñas**
- ✅ Usar contraseñas fuertes (mínimo 16 caracteres)
- ✅ No compartir contraseñas en código
- ✅ Rotar contraseñas regularmente
- ✅ Usar archivos de contraseña con permisos 600

### **2. Estructura de archivos**
- ✅ Separar variables sensibles de no sensibles
- ✅ Usar nombres descriptivos para archivos
- ✅ Mantener archivos encriptados en repositorio
- ✅ Documentar qué contiene cada archivo

### **3. Logs y debugging**
- ✅ Usar `no_log: true` para tareas sensibles
- ✅ Enmascarar variables en mensajes de debug
- ✅ No mostrar contraseñas completas en logs
- ✅ Usar filtros como `[:10]` para mostrar solo parte

### **4. Permisos de archivos**
- ✅ Archivos de configuración: 600 (solo propietario)
- ✅ Directorios de configuración: 700
- ✅ Archivos de contraseña: 600
- ✅ Scripts de aplicación: 755

## 🔍 **Troubleshooting común**

### **Error: "Unable to read source file"**
```bash
# Verificar que el archivo existe
ls -la vars/secrets.yml

# Verificar permisos
chmod 600 vars/secrets.yml
```

### **Error: "Decryption failed"**
```bash
# Verificar contraseña
ansible-vault view archivo.yml

# Recrear archivo de contraseña
echo "nueva_contraseña" > .vault_pass
chmod 600 .vault_pass
```

### **Error: "Variables undefined"**
```yaml
# Verificar ruta en vars_files
vars_files:
  - "{{ playbook_dir }}/../vars/secrets.yml"  # Ruta relativa correcta
```

## 📚 **Comandos útiles adicionales**

### **Verificar archivo encriptado**
```bash
# Ver encabezado de encriptación
head -1 archivo.yml
# Debe mostrar: $ANSIBLE_VAULT;1.1;AES256
```

### **Listar archivos encriptados**
```bash
# Buscar archivos encriptados en el proyecto
find . -name "*.yml" -exec head -1 {} \; | grep ANSIBLE_VAULT
```

### **Backup de archivos encriptados**
```bash
# Crear backup antes de cambios
cp vars/secrets.yml vars/secrets.yml.backup
```

## 🎯 **Resumen**

Ansible Vault es una herramienta esencial para:
- 🔐 **Proteger información sensible** en proyectos de automatización
- 🚀 **Integrar seguridad** de forma transparente en playbooks
- 📁 **Organizar variables** de manera segura y mantenible
- 🔄 **Facilitar el trabajo en equipo** sin comprometer seguridad

**Recuerda**: La seguridad es responsabilidad de todos. Siempre encripta información sensible y sigue las mejores prácticas de seguridad. 