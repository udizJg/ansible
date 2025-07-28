# Handlers y Condiciones Avanzadas en Ansible

## 📚 ¿Qué son Handlers y Condiciones Avanzadas?

**Handlers y Condiciones Avanzadas** son características poderosas de Ansible que permiten crear playbooks más inteligentes, eficientes y mantenibles. Los handlers ejecutan tareas solo cuando es necesario, mientras que las condiciones avanzadas permiten lógica compleja y toma de decisiones.

### 🎯 **Características principales:**
- ✅ **Handlers inteligentes**: Ejecutan tareas solo cuando son notificados
- ✅ **Múltiples notificaciones**: Un handler puede ser notificado por varias tareas
- ✅ **Condiciones complejas**: Lógica AND, OR, NOT y expresiones anidadas
- ✅ **Bloques de manejo de errores**: `block`, `rescue`, `always`
- ✅ **Validación de variables**: Verificar configuración antes de ejecutar
- ✅ **Condiciones basadas en facts**: Tomar decisiones según el sistema

## 🔄 **Handlers Avanzados**

### **1. Múltiples notificaciones**
```yaml
- name: Crear archivo de configuración
  copy:
    content: "configuración"
    dest: /etc/app/config.conf
  notify: 
    - "reiniciar servicio"
    - "verificar estado"
    - "actualizar monitoreo"
```

### **2. Handlers con dependencias**
```yaml
- name: Reiniciar servicio
  debug:
    msg: "Reiniciando servicio"
  notify: "verificar estado"

- name: Verificar estado
  debug:
    msg: "Verificando estado del servicio"
  listen: "verificar estado"
```

### **3. Handlers condicionales**
```yaml
- name: Modificar configuración
  lineinfile:
    path: /etc/app/config.conf
    line: "nueva_configuración"
  notify: "reiniciar servicio"
  when: configuracion_cambiada | bool
```

### **4. Handlers con variables**
```yaml
- name: Crear configuración de servicio
  copy:
    content: |
      [{{ item.key }}]
      puerto = {{ item.value.puerto }}
      estado = {{ item.value.estado }}
    dest: "/etc/{{ item.key }}.conf"
  loop: "{{ servicios | dict2items }}"
  notify: "reiniciar {{ item.key }}"
```

## 🔍 **Condiciones Avanzadas**

### **1. Operadores lógicos básicos**

#### **AND (&&)**
```yaml
- name: Configurar SSL si está habilitado y certificado disponible
  copy:
    content: "configuración SSL"
    dest: /etc/ssl.conf
  when: 
    - ssl_enabled == true
    - ssl_cert_available == true
    - servicio_web == true
```

#### **OR (||)**
```yaml
- name: Crear backup si es producción o backup está habilitado
  copy:
    content: "configuración de backup"
    dest: /etc/backup.conf
  when: 
    - entorno == "produccion" or backup_enabled == true
```

#### **NOT (!)**
```yaml
- name: Crear configuración de desarrollo si NO es producción
  copy:
    content: "configuración de desarrollo"
    dest: /etc/dev.conf
  when: entorno != "produccion"
```

### **2. Condiciones con facts del sistema**
```yaml
- name: Configurar para macOS específicamente
  copy:
    content: "configuración macOS"
    dest: /etc/macos.conf
  when: ansible_system == "Darwin"

- name: Configurar para Linux específicamente
  copy:
    content: "configuración Linux"
    dest: /etc/linux.conf
  when: ansible_system == "Linux"
```

### **3. Condiciones con loops y filtros**
```yaml
- name: Crear configuraciones de servicios habilitados
  copy:
    content: "configuración de {{ item.key }}"
    dest: "/etc/{{ item.key }}.conf"
  loop: "{{ servicios | dict2items }}"
  when: item.value.habilitado == true
```

### **4. Condiciones con expresiones complejas**
```yaml
- name: Configurar monitoreo avanzado
  copy:
    content: "configuración de monitoreo"
    dest: /etc/monitoring.conf
  when: 
    - monitoring_enabled == true
    - (entorno == "produccion" or entorno == "staging")
    - umbral_cpu is defined and umbral_cpu > 0
```

## 🛡️ **Bloques de Manejo de Errores**

### **1. Estructura básica**
```yaml
- name: Configurar servicios críticos
  block:
    - name: Crear configuración de web server
      copy:
        content: "configuración web"
        dest: /etc/web.conf
      when: web_enabled == true

    - name: Crear configuración de base de datos
      copy:
        content: "configuración db"
        dest: /etc/db.conf
      when: db_enabled == true

  rescue:
    - name: Manejar error en configuración crítica
      debug:
        msg: "Error en configuración crítica"
      loop: "{{ ['web', 'db'] }}"

  always:
    - name: Limpiar archivos temporales
      debug:
        msg: "Limpieza completada"
```

### **2. Bloques anidados**
```yaml
- name: Despliegue completo
  block:
    - name: Preparar sistema
      block:
        - name: Crear directorios
          file:
            path: "{{ item }}"
            state: directory
          loop: ["/opt/app", "/var/log/app"]

    - name: Configurar aplicación
      block:
        - name: Copiar archivos
          copy:
            src: files/
            dest: /opt/app/

  rescue:
    - name: Rollback en caso de error
      debug:
        msg: "Ejecutando rollback"

  always:
    - name: Limpiar recursos
      debug:
        msg: "Limpieza final"
```

## ✅ **Validación de Variables**

### **1. Validación básica**
```yaml
- name: Validar configuración
  assert:
    that:
      - variable_requerida is defined
      - variable_requerida != ""
      - configuracion is defined
      - configuracion | length > 0
    fail_msg: "Configuración inválida: faltan variables requeridas"
    success_msg: "Configuración válida, procediendo con despliegue"
```

### **2. Validación con condiciones**
```yaml
- name: Validar entorno de producción
  assert:
    that:
      - entorno == "produccion"
      - backup_enabled == true
      - monitoring_enabled == true
      - ssl_enabled == true
    fail_msg: "Configuración de producción incompleta"
    success_msg: "Entorno de producción validado"
  when: entorno == "produccion"
```

## 🎭 **Ejemplos Prácticos**

### **1. Configuración de servicios con handlers**
```yaml
- name: Configurar servicios web
  hosts: webservers
  vars:
    servicios:
      nginx:
        puerto: 80
        config: nginx.conf
      apache:
        puerto: 8080
        config: apache.conf

  tasks:
    - name: Crear configuraciones de servicios
      copy:
        content: |
          [{{ item.key }}]
          puerto = {{ item.value.puerto }}
          config = {{ item.value.config }}
        dest: "/etc/{{ item.key }}.conf"
      loop: "{{ servicios | dict2items }}"
      notify: "reiniciar {{ item.key }}"

  handlers:
    - name: reiniciar nginx
      debug:
        msg: "Reiniciando nginx"

    - name: reiniciar apache
      debug:
        msg: "Reiniciando apache"
```

### **2. Despliegue condicional por entorno**
```yaml
- name: Despliegue inteligente
  hosts: all
  vars:
    entorno: "desarrollo"
    debug: true

  tasks:
    - name: Configurar para desarrollo
      copy:
        content: "configuración de desarrollo"
        dest: /etc/dev.conf
      when: entorno == "desarrollo"

    - name: Configurar para producción
      copy:
        content: "configuración de producción"
        dest: /etc/prod.conf
      when: entorno == "produccion"

    - name: Habilitar debug
      copy:
        content: "debug = true"
        dest: /etc/debug.conf
      when: debug == true

    - name: Configurar SSL
      copy:
        content: "configuración SSL"
        dest: /etc/ssl.conf
      when: 
        - entorno == "produccion"
        - ssl_enabled == true
```

### **3. Manejo de errores robusto**
```yaml
- name: Despliegue con manejo de errores
  hosts: all
  tasks:
    - name: Despliegue principal
      block:
        - name: Crear directorios
          file:
            path: "{{ item }}"
            state: directory
          loop: ["/opt/app", "/var/log/app", "/etc/app"]

        - name: Copiar archivos de aplicación
          copy:
            src: app/
            dest: /opt/app/

        - name: Configurar servicios
          copy:
            content: "configuración"
            dest: /etc/app/config.conf
          notify: "reiniciar servicios"

      rescue:
        - name: Notificar error
          debug:
            msg: "Error durante el despliegue"

        - name: Intentar rollback
          file:
            path: /opt/app
            state: absent

      always:
        - name: Limpiar archivos temporales
          file:
            path: /tmp/ansible-temp
            state: absent

  handlers:
    - name: reiniciar servicios
      debug:
        msg: "Reiniciando servicios"
```

## 🔧 **Mejores Prácticas**

### **1. Organización de handlers**
- ✅ Usar nombres descriptivos para handlers
- ✅ Agrupar handlers relacionados
- ✅ Documentar qué tareas notifican cada handler
- ✅ Usar handlers para acciones que deben ejecutarse una sola vez

### **2. Condiciones eficientes**
- ✅ Usar condiciones simples cuando sea posible
- ✅ Evitar condiciones muy complejas (dividir en múltiples tareas)
- ✅ Usar variables para simplificar condiciones
- ✅ Documentar la lógica de condiciones complejas

### **3. Manejo de errores**
- ✅ Usar bloques para tareas relacionadas
- ✅ Implementar rollback en caso de error
- ✅ Limpiar recursos en la sección `always`
- ✅ Proporcionar mensajes de error útiles

### **4. Validación**
- ✅ Validar variables al inicio del playbook
- ✅ Usar `assert` para verificar configuración
- ✅ Validar entorno antes de ejecutar tareas críticas
- ✅ Proporcionar mensajes de error claros

## 🚨 **Errores Comunes y Soluciones**

### **Error: "Handler not found"**
```yaml
# Problema: Handler no definido
notify: "handler_inexistente"

# Solución: Definir el handler
handlers:
  - name: handler_inexistente
    debug:
      msg: "Handler ejecutado"
```

### **Error: "Conditional check failed"**
```yaml
# Problema: Condición mal formada
when: variable == "valor" and otra_variable

# Solución: Usar comparación explícita
when: variable == "valor" and otra_variable == true
```

### **Error: "Variable undefined"**
```yaml
# Problema: Variable no definida
when: mi_variable == "valor"

# Solución: Verificar si existe
when: mi_variable is defined and mi_variable == "valor"
```

## 🎯 **Resumen**

Handlers y Condiciones Avanzadas permiten:
- 🔄 **Automatización inteligente** que ejecuta tareas solo cuando es necesario
- 🎭 **Lógica compleja** para tomar decisiones basadas en múltiples factores
- 🛡️ **Manejo robusto de errores** con bloques y rollback
- ✅ **Validación de configuración** antes de ejecutar tareas críticas
- 📊 **Playbooks mantenibles** y fáciles de entender

**Recuerda**: Los handlers y condiciones avanzadas hacen que tus playbooks sean más inteligentes y confiables. Úsalos para crear automatización que se adapte a diferentes entornos y situaciones. 