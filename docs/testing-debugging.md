# Testing y Debugging en Ansible

## 📚 ¿Qué es Testing y Debugging?

**Testing y Debugging** en Ansible son técnicas esenciales para desarrollar playbooks robustos y confiables. Permiten detectar errores antes de la ejecución en producción y solucionar problemas de forma eficiente.

### 🎯 **Características principales:**
- ✅ **Detección temprana de errores**: Encuentra problemas antes de ejecutar
- ✅ **Simulación segura**: Prueba cambios sin afectar sistemas
- ✅ **Información detallada**: Obtiene logs completos para debugging
- ✅ **Validación de sintaxis**: Verifica que el YAML sea correcto
- ✅ **Análisis de cambios**: Ve qué se modificará antes de ejecutar

## 🔍 **Comandos principales de Testing**

### **1. Verificación de sintaxis**
```bash
# Verificar que el playbook tiene sintaxis correcta
ansible-playbook --syntax-check playbook.yml

# Verificar múltiples playbooks
ansible-playbook --syntax-check playbooks/*.yml

# Verificar con inventario específico
ansible-playbook --syntax-check -i inventory.ini playbook.yml
```

**¿Qué detecta?**
- ✅ Errores de sintaxis YAML
- ✅ Módulos inexistentes
- ✅ Variables indefinidas
- ✅ Estructura incorrecta de tareas

### **2. Modo Dry-Run (Simulación)**
```bash
# Simular ejecución sin hacer cambios
ansible-playbook --check playbook.yml

# Dry-run con verbose
ansible-playbook --check -v playbook.yml

# Dry-run con diff (muestra diferencias)
ansible-playbook --check --diff playbook.yml

# Dry-run con inventario específico
ansible-playbook --check -i inventory.ini playbook.yml
```

**¿Qué hace?**
- ✅ Simula todas las tareas
- ✅ Muestra qué se cambiaría
- ✅ No modifica archivos/sistemas
- ✅ Perfecto para pruebas

### **3. Modos Verbose (Debugging)**
```bash
# Verbose básico (-v)
ansible-playbook -v playbook.yml

# Verbose detallado (-vv)
ansible-playbook -vv playbook.yml

# Verbose muy detallado (-vvv)
ansible-playbook -vvv playbook.yml

# Verbose máximo (-vvvv)
ansible-playbook -vvvv playbook.yml
```

**Niveles de verbose:**
- **-v**: Información básica de tareas
- **-vv**: Información detallada + variables
- **-vvv**: Información muy detallada + conexiones
- **-vvvv**: Información máxima + debugging interno

### **4. Ejecutar tareas específicas**
```bash
# Ejecutar solo tareas con tags específicos
ansible-playbook --tags "config,deploy" playbook.yml

# Ejecutar desde una tarea específica
ansible-playbook --start-at-task "Crear directorio" playbook.yml

# Ejecutar hasta una tarea específica
ansible-playbook --step playbook.yml

# Ejecutar solo hosts específicos
ansible-playbook --limit "webservers" playbook.yml
```

### **5. Validación de inventario**
```bash
# Verificar inventario
ansible-inventory --list

# Verificar inventario con variables
ansible-inventory --list -i inventory.ini

# Verificar conectividad
ansible all -m ping

# Verificar conectividad con inventario específico
ansible all -m ping -i inventory.ini
```

## 🛠️ **Técnicas de Debugging**

### **1. Usar módulo debug**
```yaml
- name: Debug de variables
  debug:
    msg: "Variable: {{ mi_variable }}"

- name: Debug de facts
  debug:
    var: ansible_facts

- name: Debug de tarea específica
  debug:
    msg: "Valor de la variable: {{ item }}"
  loop: "{{ mi_lista }}"
```

### **2. Registrar resultados**
```yaml
- name: Crear archivo y registrar resultado
  file:
    path: /tmp/test.txt
    state: touch
  register: resultado_archivo

- name: Mostrar resultado
  debug:
    var: resultado_archivo
```

### **3. Condiciones de debugging**
```yaml
- name: Debug condicional
  debug:
    msg: "Esta tarea se ejecutó"
  when: variable_debug | bool

- name: Debug con información del sistema
  debug:
    msg: |
      Host: {{ ansible_hostname }}
      OS: {{ ansible_system }}
      Usuario: {{ ansible_user_id }}
  when: ansible_system == "Darwin"
```

## 📋 **Checklist de Testing**

### **Antes de ejecutar:**
- [ ] **Sintaxis correcta**: `ansible-playbook --syntax-check`
- [ ] **Inventario válido**: `ansible-inventory --list`
- [ ] **Conectividad**: `ansible all -m ping`
- [ ] **Variables definidas**: Verificar todas las variables
- [ ] **Permisos**: Verificar permisos de archivos

### **Durante desarrollo:**
- [ ] **Dry-run**: `ansible-playbook --check`
- [ ] **Verbose mode**: `ansible-playbook -v`
- [ ] **Tags específicos**: Probar tareas individuales
- [ ] **Hosts específicos**: Probar en hosts de prueba
- [ ] **Logs detallados**: Revisar salida completa

### **Antes de producción:**
- [ ] **Testing completo**: Ejecutar en entorno de pruebas
- [ ] **Backup**: Hacer backup de configuraciones
- [ ] **Rollback plan**: Tener plan de reversión
- [ ] **Documentación**: Actualizar documentación
- [ ] **Monitoreo**: Configurar alertas

## 🔧 **Mejores prácticas**

### **1. Estructura de testing**
```yaml
# Usar tags para organizar tareas
- name: Configurar aplicación
  tags: 
    - config
    - app
  tasks:
    - name: Crear directorio
      file:
        path: /opt/app
        state: directory
      tags: setup

    - name: Copiar archivos
      copy:
        src: files/
        dest: /opt/app/
      tags: deploy
```

### **2. Manejo de errores**
```yaml
- name: Tarea con manejo de errores
  block:
    - name: Crear archivo
      file:
        path: /tmp/test.txt
        state: touch
  rescue:
    - name: Manejar error
      debug:
        msg: "Error al crear archivo"
  always:
    - name: Limpiar
      debug:
        msg: "Limpieza completada"
```

### **3. Validación de variables**
```yaml
- name: Validar variables requeridas
  assert:
    that:
      - variable_requerida is defined
      - variable_requerida != ""
    fail_msg: "Variable requerida no está definida"
    success_msg: "Todas las variables están definidas"
```

### **4. Testing de roles**
```bash
# Probar rol específico
ansible-playbook --tags "web_server" playbook.yml

# Probar con variables específicas
ansible-playbook -e "web_port=8080" playbook.yml

# Probar en hosts específicos
ansible-playbook --limit "webservers" playbook.yml
```

## 🚨 **Errores comunes y soluciones**

### **Error: "syntax error"**
```bash
# Solución: Verificar sintaxis YAML
ansible-playbook --syntax-check playbook.yml

# Verificar indentación
# Usar editor con soporte YAML
```

### **Error: "module not found"**
```bash
# Solución: Verificar nombre del módulo
ansible-doc -l | grep nombre_modulo

# Instalar colecciones necesarias
ansible-galaxy collection install community.general
```

### **Error: "variable undefined"**
```yaml
# Solución: Definir variable o usar default
- name: Usar variable con default
  debug:
    msg: "{{ mi_variable | default('valor_por_defecto') }}"
```

### **Error: "permission denied"**
```bash
# Solución: Verificar permisos
ls -la archivo.yml
chmod 644 archivo.yml

# Verificar usuario SSH
ansible_user=usuario_correcto
```

### **Error: "connection failed"**
```bash
# Solución: Verificar conectividad
ansible all -m ping

# Verificar configuración SSH
ssh usuario@servidor
```

## 📊 **Herramientas adicionales**

### **1. Ansible Lint**
```bash
# Instalar ansible-lint
pip install ansible-lint

# Verificar playbook
ansible-lint playbook.yml

# Verificar con reglas específicas
ansible-lint --rules=all playbook.yml
```

### **2. Molecule (Testing de roles)**
```bash
# Instalar molecule
pip install molecule

# Crear tests para rol
molecule init scenario --driver-name docker

# Ejecutar tests
molecule test
```

### **3. Ansible Test**
```bash
# Ejecutar tests integrados
ansible-test sanity

# Ejecutar tests de integración
ansible-test integration
```

## 🎯 **Resumen**

Testing y Debugging en Ansible es esencial para:
- 🔍 **Detectar errores temprano** antes de afectar sistemas
- 🛡️ **Probar cambios de forma segura** con dry-run
- 📊 **Obtener información detallada** para debugging
- ✅ **Validar configuración** antes de producción
- 🚀 **Desarrollar playbooks confiables** y mantenibles

**Recuerda**: Siempre prueba tus playbooks antes de ejecutarlos en producción. Un minuto de testing puede ahorrar horas de debugging. 