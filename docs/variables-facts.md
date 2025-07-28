# Variables y Facts en Ansible

## 📚 ¿Qué son las Variables y Facts?

### 🔧 **Variables**
Las variables son **contenedores de datos** que puedes definir y usar en tus playbooks. Permiten hacer tu código más dinámico y reutilizable.

### 📊 **Facts**
Los facts son **información automática** que Ansible recopila sobre los hosts. Incluyen datos como hostname, sistema operativo, IP, memoria, etc.

## 🎯 Tipos de Variables

### 1. **Variables Simples**
```yaml
vars:
  nombre: "Mi Aplicación"
  version: "1.0"
  puerto: 8080
```

### 2. **Variables con Listas**
```yaml
vars:
  servicios:
    - nginx
    - mysql
    - redis
  
  usuarios:
    - admin
    - user1
    - user2
```

### 3. **Variables con Diccionarios**
```yaml
vars:
  configuracion:
    puerto_web: 8080
    puerto_db: 3306
    entorno: "desarrollo"
    debug: true
  
  usuario:
    nombre: "admin"
    email: "admin@example.com"
    rol: "administrador"
```

### 4. **Variables con Expresiones**
```yaml
vars:
  fecha_actual: "{{ ansible_date_time.iso8601 }}"
  usuario_sistema: "{{ ansible_user_id }}"
  hostname: "{{ ansible_hostname }}"
```

## 📍 Dónde Definir Variables

### 1. **En el Playbook (vars)**
```yaml
- name: Mi Playbook
  hosts: local
  vars:
    mi_variable: "valor"
  tasks:
    - debug:
        msg: "{{ mi_variable }}"
```

### 2. **En Tareas (vars)**
```yaml
- name: Tarea con variables locales
  debug:
    msg: "{{ mi_variable }}"
  vars:
    mi_variable: "valor local"
```

### 3. **Con set_fact (dinámicas)**
```yaml
- name: Crear variable dinámica
  set_fact:
    timestamp: "{{ ansible_date_time.epoch }}"
    ruta_completa: "/tmp/{{ timestamp }}"
```

### 4. **Con register (resultados de tareas)**
```yaml
- name: Ejecutar comando
  command: whoami
  register: resultado_comando

- name: Mostrar resultado
  debug:
    msg: "Usuario: {{ resultado_comando.stdout }}"
```

## 🔍 Facts Importantes de Ansible

### **Información del Sistema**
- `ansible_hostname`: Nombre del host
- `ansible_system`: Sistema operativo (Linux, Darwin, etc.)
- `ansible_architecture`: Arquitectura (x86_64, arm64, etc.)
- `ansible_os_family`: Familia del SO (RedHat, Debian, etc.)

### **Información de Red**
- `ansible_default_ipv4.address`: IP principal
- `ansible_default_ipv4.interface`: Interfaz principal
- `ansible_all_ipv4_addresses`: Todas las IPs IPv4

### **Información de Usuario**
- `ansible_user_id`: Usuario actual
- `ansible_user_gid`: Grupo del usuario
- `ansible_user_gecos`: Información completa del usuario

### **Información de Fecha/Hora**
- `ansible_date_time.iso8601`: Fecha en formato ISO
- `ansible_date_time.epoch`: Timestamp Unix
- `ansible_date_time.year`: Año actual

### **Información de Hardware**
- `ansible_memtotal_mb`: Memoria total en MB
- `ansible_processor_cores`: Número de núcleos
- `ansible_processor_count`: Número de procesadores

## 🎨 Uso de Variables en Plantillas Jinja2

### **Sintaxis Básica**
```jinja2
# Variable simple
{{ mi_variable }}

# Variable de diccionario
{{ configuracion.puerto_web }}

# Variable de lista
{{ servicios[0] }}
```

### **Condiciones**
```jinja2
{% if configuracion.debug %}
# Modo debug activado
{% endif %}

{% if ansible_os_family == "RedHat" %}
# Configuración para RedHat
{% elif ansible_os_family == "Debian" %}
# Configuración para Debian
{% endif %}
```

### **Bucles**
```jinja2
{% for servicio in servicios %}
- {{ servicio }}
{% endfor %}

{% for key, value in configuracion.items() %}
{{ key }} = {{ value }}
{% endfor %}
```

### **Filtros**
```jinja2
{{ mi_variable | upper }}          # Mayúsculas
{{ mi_variable | lower }}          # Minúsculas
{{ lista | length }}               # Longitud de lista
{{ mi_variable | default("valor") }} # Valor por defecto
```

## 🎯 Mejores Prácticas

### 1. **Usar nombres descriptivos**
```yaml
# ❌ Mal
vars:
  var1: "valor"

# ✅ Bien
vars:
  nombre_aplicacion: "Mi Aplicación"
```

### 2. **Agrupar variables relacionadas**
```yaml
vars:
  aplicacion:
    nombre: "Mi App"
    version: "1.0"
    puerto: 8080
  
  base_datos:
    host: "localhost"
    puerto: 3306
    nombre: "mydb"
```

### 3. **Usar variables para rutas**
```yaml
vars:
  directorio_base: "/opt/mi-aplicacion"
  directorio_logs: "{{ directorio_base }}/logs"
  directorio_config: "{{ directorio_base }}/config"
```

### 4. **Validar variables**
```yaml
- name: Verificar que la variable existe
  fail:
    msg: "La variable 'mi_variable' no está definida"
  when: mi_variable is not defined
```

### 5. **Usar variables por defecto**
```yaml
- name: Usar variable con valor por defecto
  debug:
    msg: "Puerto: {{ puerto | default(8080) }}"
```

## 🔧 Comandos Útiles

### **Ver todos los facts de un host**
```bash
ansible localhost -m setup
```

### **Ver facts específicos**
```bash
ansible localhost -m setup -a "filter=ansible_hostname"
ansible localhost -m setup -a "filter=ansible_os*"
```

### **Ver variables en un playbook**
```bash
ansible-playbook --list-vars playbook.yml
```

## 📖 Ejemplos Prácticos

### **Ejemplo 1: Configuración de aplicación**
```yaml
vars:
  app_config:
    nombre: "Mi Aplicación Web"
    puerto: 8080
    entorno: "desarrollo"
    debug: true
    directorio: "/opt/mi-app"

tasks:
  - name: Crear directorio de la aplicación
    file:
      path: "{{ app_config.directorio }}"
      state: directory
      mode: '0755'
```

### **Ejemplo 2: Configuración condicional**
```yaml
vars:
  entorno: "desarrollo"

tasks:
  - name: Configurar según el entorno
    set_fact:
      es_desarrollo: "{{ entorno == 'desarrollo' }}"
      es_produccion: "{{ entorno == 'produccion' }}"
  
  - name: Crear configuración de desarrollo
    copy:
      content: |
        [app]
        debug = true
        log_level = DEBUG
      dest: "/tmp/config.ini"
    when: es_desarrollo
```

### **Ejemplo 3: Usar facts del sistema**
```yaml
tasks:
  - name: Mostrar información del sistema
    debug:
      msg: |
        Hostname: {{ ansible_hostname }}
        Sistema: {{ ansible_system }}
        Arquitectura: {{ ansible_architecture }}
        Memoria: {{ ansible_memtotal_mb }} MB
        IP: {{ ansible_default_ipv4.address }}
```

## 🔄 Próximos Pasos

1. ✅ Variables y Facts básicos
2. 🔄 Variables de inventario
3. 🔄 Variables de grupo
4. 🔄 Variables de host
5. 🔄 Archivos de variables externos
6. 🔄 Vault para variables sensibles 