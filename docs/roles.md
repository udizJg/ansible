# Roles en Ansible

## 📚 ¿Qué son los Roles?

Los **roles** son una forma de organizar playbooks en **componentes reutilizables y modulares**. Permiten estructurar tu automatización de manera más organizada y mantenible.

### 🎯 **Características principales:**
- ✅ **Modularidad**: Cada rol tiene una responsabilidad específica
- ✅ **Reutilización**: Los roles se pueden usar en múltiples playbooks
- ✅ **Organización**: Estructura clara y predecible
- ✅ **Mantenibilidad**: Fácil de mantener y actualizar

## 🏗️ Estructura de un Rol

### **Estructura estándar:**
```
roles/
├── mi_rol/
│   ├── tasks/           # Tareas principales
│   │   └── main.yml
│   ├── handlers/        # Handlers del rol
│   │   └── main.yml
│   ├── templates/       # Plantillas Jinja2
│   │   └── config.j2
│   ├── files/          # Archivos estáticos
│   │   └── script.sh
│   ├── vars/           # Variables específicas del rol
│   │   └── main.yml
│   ├── defaults/       # Variables por defecto
│   │   └── main.yml
│   └── meta/           # Metadatos del rol
│       └── main.yml
```

## 📁 Componentes de un Rol

### 1. **tasks/main.yml** - Tareas principales
```yaml
---
- name: Instalar paquetes
  package:
    name: "{{ item }}"
    state: present
  loop: "{{ packages }}"

- name: Configurar servicio
  template:
    src: config.j2
    dest: /etc/mi-servicio/config.conf
  notify: restart servicio
```

### 2. **handlers/main.yml** - Handlers del rol
```yaml
---
- name: restart servicio
  service:
    name: mi-servicio
    state: restarted

- name: reload configuracion
  service:
    name: mi-servicio
    state: reloaded
```

### 3. **templates/** - Plantillas Jinja2
```jinja2
# config.j2
[servicio]
nombre = {{ servicio_nombre }}
puerto = {{ servicio_puerto }}
debug = {{ debug_mode }}
```

### 4. **files/** - Archivos estáticos
```bash
#!/bin/bash
# script.sh
echo "Script del rol"
```

### 5. **defaults/main.yml** - Variables por defecto
```yaml
---
# Variables que pueden ser sobrescritas
servicio_nombre: "mi-servicio"
servicio_puerto: 8080
debug_mode: false
```

### 6. **vars/main.yml** - Variables específicas
```yaml
---
# Variables específicas del rol (no se sobrescriben)
packages:
  - nginx
  - mysql
  - redis
```

## 🎯 Cómo usar Roles

### **En un playbook:**
```yaml
---
- name: Configurar servidor web
  hosts: webservers
  roles:
    - web_server
    - database
    - application
```

### **Con variables:**
```yaml
---
- name: Configurar servidor web
  hosts: webservers
  roles:
    - role: web_server
      vars:
        web_port: 8080
        web_site_title: "Mi Sitio"
    - role: database
      vars:
        db_name: "mi_app"
        db_user: "app_user"
```

### **Con condiciones:**
```yaml
---
- name: Configurar servidor
  hosts: all
  roles:
    - role: web_server
      when: inventory_hostname in groups['webservers']
    - role: database
      when: inventory_hostname in groups['dbservers']
```

## 📖 Ejemplos Prácticos

### **Ejemplo 1: Rol de Servidor Web**
```yaml
# roles/web_server/tasks/main.yml
---
- name: Instalar nginx
  package:
    name: nginx
    state: present

- name: Configurar nginx
  template:
    src: nginx.conf.j2
    dest: /etc/nginx/nginx.conf
  notify: reload nginx

- name: Habilitar sitio web
  copy:
    src: sitio.conf
    dest: /etc/nginx/sites-available/default
  notify: reload nginx
```

### **Ejemplo 2: Rol de Base de Datos**
```yaml
# roles/database/tasks/main.yml
---
- name: Instalar MySQL
  package:
    name: mysql-server
    state: present

- name: Configurar MySQL
  template:
    src: mysql.conf.j2
    dest: /etc/mysql/mysql.conf.d/mysqld.cnf
  notify: restart mysql

- name: Crear base de datos
  mysql_db:
    name: "{{ db_name }}"
    state: present
```

### **Ejemplo 3: Rol de Aplicación**
```yaml
# roles/application/tasks/main.yml
---
- name: Crear directorio de la aplicación
  file:
    path: "{{ app_dir }}"
    state: directory
    mode: '0755'

- name: Copiar código de la aplicación
  copy:
    src: "{{ app_src }}"
    dest: "{{ app_dir }}"
    mode: '0644'

- name: Instalar dependencias
  pip:
    requirements: "{{ app_dir }}/requirements.txt"
```

## 🔧 Roles Avanzados

### 1. **Roles con Dependencias**
```yaml
# roles/mi_rol/meta/main.yml
---
dependencies:
  - role: common
  - role: nginx
    vars:
      nginx_port: 8080
```

### 2. **Roles con Tags**
```yaml
---
- name: Configurar servidor
  hosts: all
  roles:
    - role: web_server
      tags: web
    - role: database
      tags: database
    - role: monitoring
      tags: monitoring
```

### 3. **Roles con Condiciones**
```yaml
---
- name: Configurar servidor
  hosts: all
  roles:
    - role: web_server
      when: ansible_os_family == "RedHat"
    - role: database
      when: inventory_hostname in groups['dbservers']
```

## 🎯 Mejores Prácticas

### 1. **Nombres descriptivos**
```yaml
# ✅ Bueno
roles:
  - web_server
  - database_mysql
  - monitoring_prometheus

# ❌ Malo
roles:
  - web
  - db
  - mon
```

### 2. **Variables por defecto**
```yaml
# roles/mi_rol/defaults/main.yml
---
# Variables que pueden ser sobrescritas
servicio_puerto: 8080
servicio_nombre: "mi-servicio"
debug_mode: false
```

### 3. **Documentación**
```yaml
# roles/mi_rol/README.md
# Rol: Mi Servicio
# Descripción: Configura un servicio básico
# Variables:
#   - servicio_puerto: Puerto del servicio
#   - servicio_nombre: Nombre del servicio
```

### 4. **Estructura consistente**
```
roles/
├── common/          # Configuración común
├── web_server/      # Servidor web
├── database/        # Base de datos
├── application/     # Aplicación
└── monitoring/      # Monitoreo
```

## 🔄 Comandos Útiles

### **Crear estructura de rol**
```bash
ansible-galaxy init mi_rol
```

### **Instalar rol desde Galaxy**
```bash
ansible-galaxy install username.rol_name
```

### **Listar roles instalados**
```bash
ansible-galaxy list
```

### **Ejecutar playbook con roles**
```bash
ansible-playbook playbook.yml
```

## 🎯 Casos de Uso Comunes

### 1. **Configuración de Servidor Web**
```yaml
roles:
  - common
  - nginx
  - php
  - mysql
  - application
```

### 2. **Configuración de Base de Datos**
```yaml
roles:
  - common
  - mysql
  - backup
  - monitoring
```

### 3. **Configuración de Aplicación**
```yaml
roles:
  - common
  - python
  - application
  - nginx_proxy
  - monitoring
```

## 🔄 Próximos Pasos

1. ✅ Roles básicos
2. 🔄 Variables de inventario
3. 🔄 Vault para información sensible
4. 🔄 Templates avanzadas
5. 🔄 Playbooks complejos
6. 🔄 Ansible Galaxy 