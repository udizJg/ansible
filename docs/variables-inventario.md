# Variables de Inventario en Ansible

## 📚 ¿Qué son las Variables de Inventario?

Las **variables de inventario** permiten definir valores específicos para cada host o grupo de hosts directamente en el archivo de inventario (`inventory.ini`) o en archivos separados. Son ideales para personalizar la configuración según el entorno, servidor o grupo.

### 🎯 **Características principales:**
- ✅ **Personalización por host**: Variables específicas para cada servidor
- ✅ **Personalización por grupo**: Variables comunes para grupos de servidores
- ✅ **Variables globales**: Configuración que aplica a todos los hosts
- ✅ **Sobrescritura**: Las variables más específicas tienen prioridad

## 🏗️ Estructura de Variables de Inventario

### **Niveles de variables:**
1. **Variables de host** - Solo para un host específico
2. **Variables de grupo** - Para todos los hosts de un grupo
3. **Variables globales** - Para todos los hosts

### **Orden de precedencia:**
1. Variables de línea de comando
2. Variables de host
3. Variables de grupo
4. Variables globales (`all:vars`)
5. Variables por defecto de roles

## 📝 Sintaxis de Variables de Inventario

### 1. **Variables a nivel de host**
```ini
[webservers]
192.168.1.10 ansible_user=admin app_env=produccion app_port=8080
192.168.1.11 ansible_user=ubuntu app_env=staging app_port=9090
```

### 2. **Variables a nivel de grupo**
```ini
[webservers]
192.168.1.10
192.168.1.11

[webservers:vars]
ansible_user=ubuntu
app_env=produccion
nginx_port=80
ssl_enabled=true
```

### 3. **Variables globales**
```ini
[all:vars]
timezone=America/Mexico_City
python_version=3.13
log_level=INFO
ansible_python_interpreter=/usr/bin/python3
```

### 4. **Variables en archivos separados**
```
group_vars/
  webservers.yml
  dbservers.yml
host_vars/
  192.168.1.10.yml
  192.168.1.11.yml
```

## 📖 Ejemplos Prácticos

### **Ejemplo 1: Configuración básica**
```ini
[webservers]
192.168.1.10 ansible_user=admin app_env=produccion
192.168.1.11 ansible_user=ubuntu app_env=staging

[dbservers]
192.168.1.20 ansible_user=dbadmin

[webservers:vars]
web_port=8080
web_server=nginx
ssl_enabled=true

[dbservers:vars]
db_port=3306
db_type=mysql
backup_enabled=true

[all:vars]
timezone=America/Mexico_City
python_version=3.13
```

### **Ejemplo 2: Configuración avanzada**
```ini
[production]
prod-web-01 ansible_host=192.168.1.10 app_env=produccion app_name=mi-app-prod
prod-web-02 ansible_host=192.168.1.11 app_env=produccion app_name=mi-app-prod
prod-db-01 ansible_host=192.168.1.20 app_env=produccion app_name=mi-app-prod

[staging]
stage-web-01 ansible_host=192.168.2.10 app_env=staging app_name=mi-app-stage
stage-db-01 ansible_host=192.168.2.20 app_env=staging app_name=mi-app-stage

[production:vars]
web_port=80
db_port=3306
ssl_enabled=true
monitoring_enabled=true

[staging:vars]
web_port=8080
db_port=3307
ssl_enabled=false
monitoring_enabled=false

[all:vars]
timezone=America/Mexico_City
python_version=3.13
log_level=INFO
```

## 🎯 Cómo usar Variables de Inventario en Playbooks

### **Acceso directo en tareas:**
```yaml
- name: Mostrar variables de inventario
  debug:
    msg: |
      Host: {{ inventory_hostname }}
      Entorno: {{ app_env }}
      Puerto: {{ web_port | default('No definido') }}
      Usuario: {{ ansible_user }}
```

### **En plantillas Jinja2:**
```jinja2
# nginx.conf.j2
user {{ ansible_user }};
server {
    listen {{ web_port }};
    server_name {{ inventory_hostname }};
    
    {% if ssl_enabled %}
    ssl_certificate /etc/ssl/certs/{{ inventory_hostname }}.crt;
    ssl_certificate_key /etc/ssl/private/{{ inventory_hostname }}.key;
    {% endif %}
}
```

### **En condiciones:**
```yaml
- name: Configurar SSL solo si está habilitado
  template:
    src: ssl.conf.j2
    dest: /etc/nginx/ssl.conf
  when: ssl_enabled | default(false)
```

## 🔧 Variables Especiales de Ansible

### **Variables de conexión:**
- `ansible_host`: IP o nombre DNS del host
- `ansible_port`: Puerto SSH (por defecto 22)
- `ansible_user`: Usuario para conexión SSH
- `ansible_connection`: Tipo de conexión (`ssh`, `local`, `docker`, etc.)
- `ansible_python_interpreter`: Ruta al intérprete de Python

### **Variables de inventario:**
- `inventory_hostname`: Nombre del host en el inventario
- `groups`: Diccionario con todos los grupos
- `group_names`: Lista de grupos a los que pertenece el host

### **Variables de facts:**
- `ansible_hostname`: Hostname del sistema
- `ansible_system`: Sistema operativo
- `ansible_architecture`: Arquitectura del sistema

## 📁 Archivos de Variables Separados

### **group_vars/webservers.yml:**
```yaml
---
# Variables para el grupo webservers
web_port: 8080
web_server: nginx
ssl_enabled: true
max_connections: 1000
```

### **host_vars/192.168.1.10.yml:**
```yaml
---
# Variables específicas para el host 192.168.1.10
app_env: produccion
app_name: mi-app-prod
ssl_cert_path: /etc/ssl/certs/prod.crt
```

## 🎯 Mejores Prácticas

### 1. **Nombres descriptivos**
```ini
# ✅ Bueno
app_env=produccion
web_port=8080
db_backup_enabled=true

# ❌ Malo
env=prod
port=8080
backup=true
```

### 2. **Organización por grupos**
```ini
[webservers:vars]
web_port=8080
web_server=nginx

[dbservers:vars]
db_port=3306
db_type=mysql
```

### 3. **Variables globales para configuración común**
```ini
[all:vars]
timezone=America/Mexico_City
python_version=3.13
log_level=INFO
```

### 4. **Uso de archivos separados para proyectos grandes**
```
inventory/
├── group_vars/
│   ├── webservers.yml
│   ├── dbservers.yml
│   └── all.yml
├── host_vars/
│   ├── prod-web-01.yml
│   └── prod-db-01.yml
└── inventory.ini
```

## 🔄 Comandos Útiles

### **Ver variables de un host específico:**
```bash
ansible-inventory --host 192.168.1.10
```

### **Ver variables de todos los hosts:**
```bash
ansible-inventory --list
```

### **Ver variables de un grupo:**
```bash
ansible-inventory --list | jq '.webservers.hosts'
```

### **Ejecutar playbook con variables específicas:**
```bash
ansible-playbook playbook.yml -e "app_env=produccion"
```

## 🎯 Casos de Uso Comunes

### 1. **Configuración por entorno**
```ini
[production:vars]
app_env=produccion
ssl_enabled=true
monitoring_enabled=true

[staging:vars]
app_env=staging
ssl_enabled=false
monitoring_enabled=false
```

### 2. **Configuración por tipo de servidor**
```ini
[webservers:vars]
web_port=8080
web_server=nginx

[dbservers:vars]
db_port=3306
db_type=mysql
```

### 3. **Configuración por región**
```ini
[us-east:vars]
timezone=America/New_York
region=us-east-1

[us-west:vars]
timezone=America/Los_Angeles
region=us-west-1
```

## 🔄 Próximos Pasos

1. ✅ Variables de inventario básicas
2. 🔄 Vault para información sensible
3. 🔄 Templates avanzadas
4. 🔄 Playbooks complejos
5. 🔄 Ansible Galaxy
6. 🔄 Integración con CI/CD 