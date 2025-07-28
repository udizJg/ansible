# Módulos Básicos de Ansible

## 📚 ¿Qué son los módulos?

Los módulos son **funciones predefinidas** de Ansible que realizan tareas específicas. Son como "herramientas" que Ansible tiene disponibles para automatizar diferentes aspectos de la gestión de sistemas.

## 🔧 Módulos Más Importantes

### 1. **FILE** - Gestión de archivos y directorios

**¿Qué hace?** Crea, modifica, elimina archivos y directorios.

**Parámetros principales:**
- `path`: Ruta del archivo/directorio
- `state`: `present` (crear), `absent` (eliminar), `directory`, `touch`
- `mode`: Permisos (ej: `0755`, `0644`)
- `owner`: Propietario del archivo
- `group`: Grupo del archivo

**Ejemplos:**
```yaml
# Crear directorio
- file:
    path: /tmp/mi-directorio
    state: directory
    mode: '0755'

# Crear archivo vacío
- file:
    path: /tmp/mi-archivo.txt
    state: touch
    mode: '0644'

# Eliminar archivo
- file:
    path: /tmp/archivo-viejo.txt
    state: absent
```

### 2. **COPY** - Copiar archivos y contenido

**¿Qué hace?** Copia archivos desde el controlador a los hosts, o crea archivos con contenido específico.

**Parámetros principales:**
- `src`: Archivo origen (desde controlador)
- `dest`: Archivo destino (en el host)
- `content`: Contenido directo del archivo
- `mode`: Permisos del archivo
- `owner`: Propietario
- `group`: Grupo

**Ejemplos:**
```yaml
# Copiar archivo desde controlador
- copy:
    src: /ruta/local/archivo.conf
    dest: /etc/archivo.conf
    mode: '0644'

# Crear archivo con contenido
- copy:
    content: |
      # Mi configuración
      nombre = "valor"
      activo = true
    dest: /tmp/config.txt
    mode: '0644'
```

### 3. **TEMPLATE** - Plantillas Jinja2

**¿Qué hace?** Procesa plantillas Jinja2 y las copia a los hosts. Permite usar variables y lógica.

**Parámetros principales:**
- `src`: Plantilla Jinja2 (desde controlador)
- `dest`: Archivo destino (en el host)
- `mode`: Permisos
- `owner`: Propietario
- `group`: Grupo

**Ejemplo de plantilla (`template.conf.j2`):**
```jinja2
# Configuración para {{ ansible_hostname }}
[servidor]
nombre = {{ ansible_hostname }}
ip = {{ ansible_default_ipv4.address }}
sistema = {{ ansible_system }}

{% if ansible_os_family == "RedHat" %}
# Configuración específica para RedHat
{% elif ansible_os_family == "Debian" %}
# Configuración específica para Debian
{% endif %}
```

**Uso en playbook:**
```yaml
- template:
    src: templates/config.conf.j2
    dest: /etc/mi-aplicacion.conf
    mode: '0644'
```

### 4. **LINEINFILE** - Modificar archivos línea por línea

**¿Qué hace?** Agrega, modifica o elimina líneas específicas en archivos.

**Parámetros principales:**
- `path`: Archivo a modificar
- `line`: Línea a agregar/modificar
- `regexp`: Expresión regular para buscar
- `state`: `present` (agregar), `absent` (eliminar)
- `insertafter`: Después de qué línea agregar
- `insertbefore`: Antes de qué línea agregar

**Ejemplos:**
```yaml
# Agregar línea al final
- lineinfile:
    path: /etc/hosts
    line: "192.168.1.100 mi-servidor"
    state: present

# Agregar línea después de un patrón
- lineinfile:
    path: /etc/ssh/sshd_config
    line: "PermitRootLogin no"
    insertafter: "^#PermitRootLogin"
    state: present

# Eliminar línea que coincida con patrón
- lineinfile:
    path: /etc/hosts
    regexp: "^192\.168\.1\.100"
    state: absent
```

### 5. **STAT** - Obtener información de archivos

**¿Qué hace?** Obtiene información detallada sobre archivos y directorios.

**Parámetros principales:**
- `path`: Ruta del archivo/directorio

**Información disponible:**
- `exists`: Si existe
- `isdir`: Si es directorio
- `isreg`: Si es archivo regular
- `size`: Tamaño en bytes
- `mode`: Permisos
- `pw_name`: Propietario
- `gr_name`: Grupo

**Ejemplo:**
```yaml
- stat:
    path: /etc/passwd
  register: info_archivo

- debug:
    msg: "El archivo existe: {{ info_archivo.stat.exists }}"
```

### 6. **FIND** - Buscar archivos

**¿Qué hace?** Busca archivos y directorios según criterios específicos.

**Parámetros principales:**
- `paths`: Directorios donde buscar
- `file_type`: `file`, `directory`, `any`
- `recurse`: Buscar recursivamente
- `patterns`: Patrones de archivo
- `age`: Edad del archivo
- `size`: Tamaño del archivo

**Ejemplo:**
```yaml
- find:
    paths: /tmp
    file_type: file
    patterns: "*.log"
    recurse: yes
  register: archivos_log

- debug:
    msg: "Archivos .log encontrados: {{ archivos_log.files | length }}"
```

### 7. **COMMAND** y **SHELL** - Ejecutar comandos

**¿Qué hace?** Ejecuta comandos del sistema operativo.

**Diferencias:**
- `command`: Ejecuta comandos simples (sin pipes, redirecciones)
- `shell`: Ejecuta comandos complejos (con pipes, redirecciones, etc.)

**Ejemplos:**
```yaml
# Comando simple
- command: whoami
  register: usuario

# Comando complejo con shell
- shell: ps aux | grep nginx | wc -l
  register: procesos_nginx

# Comando con argumentos
- command: 
    cmd: echo "Hola {{ ansible_hostname }}"
  register: saludo
```

## 🎯 Mejores Prácticas

### 1. **Usar módulos específicos en lugar de comandos**
```yaml
# ❌ Mal - Usar command para crear directorio
- command: mkdir -p /tmp/mi-dir

# ✅ Bien - Usar módulo file
- file:
    path: /tmp/mi-dir
    state: directory
```

### 2. **Siempre especificar permisos y propietarios**
```yaml
- copy:
    content: "mi contenido"
    dest: /etc/config.txt
    mode: '0644'
    owner: root
    group: root
```

### 3. **Usar variables para rutas y configuraciones**
```yaml
- copy:
    content: "{{ config_content }}"
    dest: "{{ config_path }}"
    mode: "{{ config_mode }}"
```

### 4. **Verificar antes de modificar**
```yaml
- stat:
    path: /etc/archivo.conf
  register: archivo_info

- copy:
    content: "nuevo contenido"
    dest: /etc/archivo.conf
  when: archivo_info.stat.exists
```

## 📖 Comandos Útiles para Aprender

```bash
# Ver todos los módulos disponibles
ansible-doc -l

# Ver documentación de un módulo específico
ansible-doc file
ansible-doc copy
ansible-doc template

# Ver ejemplos de un módulo
ansible-doc -s file
ansible-doc -s copy
```

## 🔄 Próximos Pasos

1. ✅ Módulos básicos (file, copy, template)
2. 🔄 Módulos de paquetes (package, yum, apt)
3. 🔄 Módulos de servicios (service, systemd)
4. 🔄 Módulos de usuarios (user, group)
5. 🔄 Módulos de red (uri, get_url) 