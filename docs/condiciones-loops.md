# Condiciones y Loops en Ansible

## 📚 ¿Qué son las Condiciones y Loops?

### 🎯 **Condiciones (`when`)**
Las condiciones permiten **ejecutar tareas solo cuando se cumplen ciertos criterios**. Esto hace que tus playbooks sean más inteligentes y eficientes.

### 🔄 **Loops**
Los loops permiten **repetir tareas múltiples veces** con diferentes valores. Esto evita la duplicación de código y hace que tus playbooks sean más mantenibles.

## 🎯 Condiciones con `when`

### 1. **Condiciones Básicas**
```yaml
- name: Instalar paquete solo en Ubuntu
  apt:
    name: nginx
    state: present
  when: ansible_os_family == "Debian"

- name: Instalar paquete solo en CentOS
  yum:
    name: nginx
    state: present
  when: ansible_os_family == "RedHat"
```

### 2. **Condiciones con Variables**
```yaml
vars:
  entorno: "produccion"
  debug: true

tasks:
  - name: Crear archivo de configuración
    copy:
      content: "config"
      dest: "/etc/app.conf"
    when: entorno == "desarrollo"

  - name: Habilitar modo debug
    lineinfile:
      path: "/etc/app.conf"
      line: "debug = true"
    when: debug == true
```

### 3. **Condiciones Múltiples**
```yaml
- name: Crear archivo solo en desarrollo y Linux
  copy:
    content: "config"
    dest: "/tmp/config.txt"
  when: 
    - entorno == "desarrollo"
    - ansible_os_family == "RedHat"
```

### 4. **Operadores Lógicos**
```yaml
# OR (o)
- name: Crear archivo para ARM o x86
  copy:
    content: "config"
    dest: "/tmp/config.txt"
  when: ansible_architecture == "arm64" or ansible_architecture == "x86_64"

# AND (y)
- name: Crear archivo solo si es desarrollo Y Linux
  copy:
    content: "config"
    dest: "/tmp/config.txt"
  when: entorno == "desarrollo" and ansible_os_family == "RedHat"

# NOT (no)
- name: Crear archivo si NO es producción
  copy:
    content: "config"
    dest: "/tmp/config.txt"
  when: entorno != "produccion"
```

### 5. **Condiciones con Facts**
```yaml
- name: Verificar espacio en disco
  stat:
    path: "/"
  register: disk_info

- name: Limpiar logs si hay poco espacio
  file:
    path: "/var/log"
    state: absent
  when: disk_info.stat.size < 1000000000  # Menos de 1GB
```

## 🔄 Loops

### 1. **Loops Básicos con `loop`**
```yaml
vars:
  servicios:
    - nginx
    - mysql
    - redis

tasks:
  - name: Crear directorios para servicios
    file:
      path: "/opt/{{ item }}"
      state: directory
      mode: '0755'
    loop: "{{ servicios }}"

  - name: Instalar servicios
    package:
      name: "{{ item }}"
      state: present
    loop: "{{ servicios }}"
```

### 2. **Loops con Listas de Diccionarios**
```yaml
vars:
  usuarios:
    - nombre: "admin"
      email: "admin@example.com"
      rol: "administrador"
    - nombre: "usuario1"
      email: "user1@example.com"
      rol: "usuario"

tasks:
  - name: Crear usuarios
    user:
      name: "{{ item.nombre }}"
      email: "{{ item.email }}"
      groups: "{{ item.rol }}"
    loop: "{{ usuarios }}"
```

### 3. **Loops con `with_items` (Método Alternativo)**
```yaml
- name: Crear archivos
  copy:
    content: "contenido"
    dest: "/tmp/{{ item }}"
  with_items:
    - "archivo1.txt"
    - "archivo2.txt"
    - "archivo3.txt"
```

### 4. **Loops con `with_dict`**
```yaml
vars:
  configuracion:
    nginx: "servidor web"
    mysql: "base de datos"
    redis: "cache"

tasks:
  - name: Crear archivos de configuración
    copy:
      content: "{{ value }}"
      dest: "/etc/{{ key }}.conf"
    with_dict: "{{ configuracion }}"
```

### 5. **Loops Anidados**
```yaml
- name: Crear estructura de directorios
  file:
    path: "/opt/{{ item[0] }}/{{ item[1] }}"
    state: directory
  loop: "{{ ['app1', 'app2'] | product(['logs', 'config', 'data']) | list }}"
```

## 🎯 Combinando Condiciones y Loops

### 1. **Loops con Condiciones**
```yaml
vars:
  usuarios:
    - nombre: "admin"
      activo: true
    - nombre: "usuario1"
      activo: true
    - nombre: "usuario2"
      activo: false

tasks:
  - name: Crear solo usuarios activos
    user:
      name: "{{ item.nombre }}"
      state: present
    loop: "{{ usuarios }}"
    when: item.activo == true
```

### 2. **Condiciones en Loops**
```yaml
- name: Verificar servicios
  command: which {{ item }}
  register: servicio_check
  loop: "{{ servicios }}"
  ignore_errors: yes

- name: Mostrar servicios disponibles
  debug:
    msg: "{{ item.item }}: {{ 'Instalado' if item.rc == 0 else 'No instalado' }}"
  loop: "{{ servicio_check.results }}"

- name: Instalar solo servicios faltantes
  package:
    name: "{{ item.item }}"
    state: present
  loop: "{{ servicio_check.results }}"
  when: item.rc != 0
```

## 🔧 Operadores de Comparación

### **Comparaciones Básicas**
```yaml
when: variable == "valor"      # Igual
when: variable != "valor"      # Diferente
when: variable > 10           # Mayor que
when: variable < 10           # Menor que
when: variable >= 10          # Mayor o igual
when: variable <= 10          # Menor o igual
```

### **Operadores de Existencia**
```yaml
when: variable is defined     # Variable existe
when: variable is not defined # Variable no existe
when: variable is none        # Variable es None
when: variable is not none    # Variable no es None
```

### **Operadores de Lista**
```yaml
when: item in lista           # Elemento está en lista
when: item not in lista       # Elemento no está en lista
when: lista | length > 0      # Lista no está vacía
```

## 🎨 Filtros Útiles para Loops

### **Filtros de Lista**
```yaml
# Filtrar elementos
- name: Crear solo usuarios activos
  user:
    name: "{{ item.nombre }}"
  loop: "{{ usuarios | selectattr('activo', 'equalto', true) | list }}"

# Obtener elementos únicos
- name: Crear directorios únicos
  file:
    path: "/opt/{{ item }}"
    state: directory
  loop: "{{ directorios | unique | list }}"

# Combinar listas
- name: Crear estructura combinada
  file:
    path: "/opt/{{ item[0] }}/{{ item[1] }}"
    state: directory
  loop: "{{ lista1 | product(lista2) | list }}"
```

## 🎯 Mejores Prácticas

### 1. **Usar `loop` en lugar de `with_*`**
```yaml
# ✅ Recomendado (Ansible 2.5+)
- name: Crear archivos
  copy:
    content: "{{ item }}"
    dest: "/tmp/{{ item }}"
  loop: "{{ archivos }}"

# ❌ Deprecado
- name: Crear archivos
  copy:
    content: "{{ item }}"
    dest: "/tmp/{{ item }}"
  with_items: "{{ archivos }}"
```

### 2. **Usar condiciones específicas**
```yaml
# ✅ Específico
when: ansible_os_family == "RedHat"

# ❌ Genérico
when: ansible_system == "Linux"
```

### 3. **Agrupar condiciones relacionadas**
```yaml
# ✅ Agrupado
when: 
  - entorno == "desarrollo"
  - ansible_os_family == "RedHat"
  - debug == true

# ❌ Separado
when: entorno == "desarrollo"
when: ansible_os_family == "RedHat"
when: debug == true
```

### 4. **Usar variables para condiciones complejas**
```yaml
vars:
  es_desarrollo: "{{ entorno == 'desarrollo' }}"
  es_linux: "{{ ansible_os_family == 'RedHat' }}"

tasks:
  - name: Crear archivo
    copy:
      content: "config"
      dest: "/tmp/config.txt"
    when: es_desarrollo and es_linux
```

## 📖 Ejemplos Prácticos

### **Ejemplo 1: Configuración según el sistema**
```yaml
- name: Configurar nginx en Ubuntu
  template:
    src: nginx-ubuntu.conf.j2
    dest: /etc/nginx/nginx.conf
  when: ansible_os_family == "Debian"

- name: Configurar nginx en CentOS
  template:
    src: nginx-centos.conf.j2
    dest: /etc/nginx/nginx.conf
  when: ansible_os_family == "RedHat"
```

### **Ejemplo 2: Instalar paquetes según el sistema**
```yaml
- name: Instalar paquetes en Ubuntu
  apt:
    name: "{{ item }}"
    state: present
  loop:
    - nginx
    - mysql-server
    - redis-server
  when: ansible_os_family == "Debian"

- name: Instalar paquetes en CentOS
  yum:
    name: "{{ item }}"
    state: present
  loop:
    - nginx
    - mysql-server
    - redis
  when: ansible_os_family == "RedHat"
```

### **Ejemplo 3: Crear usuarios con diferentes configuraciones**
```yaml
vars:
  usuarios:
    - nombre: "admin"
      grupos: ["sudo", "docker"]
      shell: "/bin/bash"
    - nombre: "usuario1"
      grupos: ["users"]
      shell: "/bin/bash"
    - nombre: "servicio"
      grupos: ["service"]
      shell: "/bin/false"

tasks:
  - name: Crear usuarios
    user:
      name: "{{ item.nombre }}"
      groups: "{{ item.grupos }}"
      shell: "{{ item.shell }}"
    loop: "{{ usuarios }}"
```

## 🔄 Próximos Pasos

1. ✅ Condiciones básicas (`when`)
2. ✅ Loops básicos (`loop`)
3. 🔄 Handlers (ejecutar tareas solo cuando es necesario)
4. 🔄 Roles (organizar playbooks en componentes)
5. 🔄 Variables de inventario
6. 🔄 Vault para información sensible 