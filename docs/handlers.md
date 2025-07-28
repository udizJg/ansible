# Handlers en Ansible

## 📚 ¿Qué son los Handlers?

Los **handlers** son tareas especiales en Ansible que se ejecutan **solo cuando son notificados** por otras tareas. Son perfectos para acciones como reiniciar servicios, recargar configuraciones, o realizar mantenimiento después de cambios.

### 🎯 **Características principales:**
- ✅ Se ejecutan solo cuando son notificados
- ✅ Se ejecutan una sola vez por notificación
- ✅ Se ejecutan al final de todas las tareas
- ✅ Perfectos para reiniciar servicios

## 🔄 Cómo funcionan los Handlers

### **Flujo básico:**
1. **Tarea principal** ejecuta y hace cambios
2. **Tarea notifica** al handler usando `notify`
3. **Handler se marca** para ejecución
4. **Al final del playbook**, todos los handlers marcados se ejecutan

### **Ejemplo básico:**
```yaml
tasks:
  - name: Modificar configuración de nginx
    template:
      src: nginx.conf.j2
      dest: /etc/nginx/nginx.conf
    notify: reload nginx  # Notifica al handler

handlers:
  - name: reload nginx
    service:
      name: nginx
      state: reloaded
```

## 🎯 Sintaxis de Handlers

### 1. **Definir un Handler**
```yaml
handlers:
  - name: reiniciar servicio
    service:
      name: mi-servicio
      state: restarted
```

### 2. **Notificar un Handler**
```yaml
tasks:
  - name: Modificar archivo de configuración
    copy:
      content: "nueva configuración"
      dest: /etc/mi-app/config.conf
    notify: reiniciar servicio  # Notifica al handler
```

### 3. **Múltiples Notificaciones**
```yaml
tasks:
  - name: Modificar configuración principal
    template:
      src: config.j2
      dest: /etc/app/config.conf
    notify: reiniciar aplicacion
  
  - name: Modificar configuración de base de datos
    template:
      src: db.j2
      dest: /etc/app/database.conf
    notify: reiniciar base de datos
    notify: reiniciar aplicacion  # Múltiples notificaciones
```

## 📖 Ejemplos Prácticos

### **Ejemplo 1: Servicio Web**
```yaml
tasks:
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
      dest: /etc/nginx/sites-available/mi-sitio
    notify: reload nginx

handlers:
  - name: reload nginx
    service:
      name: nginx
      state: reloaded
```

### **Ejemplo 2: Aplicación con Base de Datos**
```yaml
tasks:
  - name: Modificar configuración de la aplicación
    lineinfile:
      path: /etc/mi-app/config.conf
      line: "puerto = 8080"
      regexp: "^puerto ="
    notify: reiniciar aplicacion
  
  - name: Modificar configuración de base de datos
    lineinfile:
      path: /etc/mi-app/database.conf
      line: "host = nuevo-servidor"
      regexp: "^host ="
    notify: reiniciar base de datos
    notify: reiniciar aplicacion

handlers:
  - name: reiniciar aplicacion
    service:
      name: mi-aplicacion
      state: restarted
  
  - name: reiniciar base de datos
    service:
      name: mysql
      state: restarted
```

### **Ejemplo 3: Múltiples Servicios**
```yaml
tasks:
  - name: Actualizar configuración de firewall
    template:
      src: firewall.conf.j2
      dest: /etc/ufw/user.rules
    notify: reload firewall
  
  - name: Actualizar configuración de SSH
    template:
      src: sshd.conf.j2
      dest: /etc/ssh/sshd_config
    notify: reload ssh
  
  - name: Actualizar configuración de sistema
    copy:
      src: sysctl.conf
      dest: /etc/sysctl.conf
    notify: reload system

handlers:
  - name: reload firewall
    service:
      name: ufw
      state: reloaded
  
  - name: reload ssh
    service:
      name: ssh
      state: reloaded
  
  - name: reload system
    command: sysctl -p
```

## 🔧 Handlers Avanzados

### 1. **Handlers con Condiciones**
```yaml
tasks:
  - name: Modificar configuración
    template:
      src: config.j2
      dest: /etc/app/config.conf
    notify: reiniciar servicio

handlers:
  - name: reiniciar servicio
    service:
      name: mi-servicio
      state: restarted
    when: ansible_os_family == "RedHat"
```

### 2. **Handlers con Variables**
```yaml
vars:
  servicio_nombre: "mi-aplicacion"
  servicio_puerto: 8080

tasks:
  - name: Modificar configuración
    template:
      src: config.j2
      dest: /etc/{{ servicio_nombre }}/config.conf
    notify: reiniciar {{ servicio_nombre }}

handlers:
  - name: reiniciar mi-aplicacion
    service:
      name: "{{ servicio_nombre }}"
      state: restarted
```

### 3. **Handlers con Múltiples Acciones**
```yaml
handlers:
  - name: reiniciar aplicacion completa
    block:
      - name: Detener aplicación
        service:
          name: mi-app
          state: stopped
      
      - name: Limpiar archivos temporales
        file:
          path: /tmp/mi-app
          state: absent
      
      - name: Iniciar aplicación
        service:
          name: mi-app
          state: started
      
      - name: Verificar estado
        command: curl -f http://localhost:8080/health
```

## 🎯 Mejores Prácticas

### 1. **Usar nombres descriptivos**
```yaml
# ✅ Bueno
notify: reiniciar nginx
notify: reload configuracion

# ❌ Malo
notify: restart
notify: reload
```

### 2. **Agrupar handlers relacionados**
```yaml
handlers:
  # Handlers de servicios web
  - name: reload nginx
    service:
      name: nginx
      state: reloaded
  
  - name: restart apache
    service:
      name: apache2
      state: restarted
  
  # Handlers de base de datos
  - name: restart mysql
    service:
      name: mysql
      state: restarted
  
  - name: restart postgresql
    service:
      name: postgresql
      state: restarted
```

### 3. **Usar handlers para mantenimiento**
```yaml
handlers:
  - name: limpiar cache
    file:
      path: /var/cache/mi-app
      state: absent
  
  - name: rotar logs
    command: logrotate /etc/logrotate.d/mi-app
  
  - name: actualizar permisos
    file:
      path: /var/www/mi-app
      recurse: yes
      mode: '0755'
```

### 4. **Evitar handlers innecesarios**
```yaml
# ✅ Solo cuando es necesario
- name: Modificar configuración crítica
  template:
    src: config.j2
    dest: /etc/app/config.conf
  notify: reiniciar servicio

# ❌ No para cambios menores
- name: Crear archivo de log
  copy:
    content: "log"
    dest: /var/log/app.log
  # No necesita handler
```

## 🔄 Comportamiento de Handlers

### **Ejecución Única**
```yaml
tasks:
  - name: Cambio 1
    copy:
      content: "config1"
      dest: /etc/app/config1.conf
    notify: reiniciar servicio
  
  - name: Cambio 2
    copy:
      content: "config2"
      dest: /etc/app/config2.conf
    notify: reiniciar servicio
  
  # El handler se ejecuta SOLO UNA VEZ al final
```

### **Orden de Ejecución**
```yaml
tasks:
  - name: Tarea 1
    copy:
      content: "data1"
      dest: /tmp/file1
    notify: handler1
  
  - name: Tarea 2
    copy:
      content: "data2"
      dest: /tmp/file2
    notify: handler2
  
  - name: Tarea 3
    copy:
      content: "data3"
      dest: /tmp/file3
    notify: handler1  # Se ejecuta solo una vez

# Orden de ejecución:
# 1. Todas las tareas
# 2. handler1 (una vez)
# 3. handler2 (una vez)
```

## 🎯 Casos de Uso Comunes

### 1. **Reiniciar Servicios**
```yaml
- name: Actualizar configuración
  template:
    src: service.conf.j2
    dest: /etc/service/config.conf
  notify: restart service

handlers:
  - name: restart service
    service:
      name: "{{ service_name }}"
      state: restarted
```

### 2. **Recargar Configuraciones**
```yaml
- name: Actualizar configuración
  copy:
    src: config.conf
    dest: /etc/app/config.conf
  notify: reload config

handlers:
  - name: reload config
    service:
      name: app
      state: reloaded
```

### 3. **Limpiar Cache**
```yaml
- name: Actualizar archivos
  copy:
    src: "{{ item }}"
    dest: /var/www/
  loop: "{{ archivos }}"
  notify: clear cache

handlers:
  - name: clear cache
    file:
      path: /var/cache/app
      state: absent
```

### 4. **Rotar Logs**
```yaml
- name: Escribir en log
  lineinfile:
    path: /var/log/app.log
    line: "{{ ansible_date_time.iso8601 }} - Evento"
  notify: rotate logs

handlers:
  - name: rotate logs
    command: logrotate /etc/logrotate.d/app
```

## 🔧 Comandos Útiles

### **Ver handlers en un playbook**
```bash
ansible-playbook --list-tasks playbook.yml
```

### **Ejecutar solo handlers**
```bash
ansible-playbook --tags handlers playbook.yml
```

### **Forzar ejecución de handlers**
```bash
ansible-playbook --force-handlers playbook.yml
```

## 🔄 Próximos Pasos

1. ✅ Handlers básicos
2. 🔄 Roles (organizar playbooks en componentes)
3. 🔄 Variables de inventario
4. 🔄 Vault para información sensible
5. 🔄 Templates avanzadas
6. 🔄 Playbooks complejos 