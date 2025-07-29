# CI/CD con Ansible

## 📚 ¿Qué es CI/CD con Ansible?

**CI/CD (Continuous Integration/Continuous Deployment)** con Ansible es una estrategia de automatización que integra Ansible en el pipeline de desarrollo, permitiendo automatizar el testing, building, deployment y monitoring de aplicaciones de manera continua y confiable.

### 🎯 **Características principales:**
- ✅ **Integración continua**: Testing automático en cada commit
- ✅ **Despliegue continuo**: Automatización de despliegues a múltiples entornos
- ✅ **Containerización**: Integración con Docker y Kubernetes
- ✅ **Monitoring**: Supervisión continua y alertas automáticas
- ✅ **Rollback**: Capacidad de revertir cambios automáticamente
- ✅ **Multi-entorno**: Staging, producción y otros entornos

## 🔄 **Arquitectura del Pipeline**

### **1. Flujo del Pipeline**
```
Código → Testing → Build → Deploy Staging → Testing → Deploy Production → Monitoring
```

### **2. Componentes del Sistema**
- **GitHub Actions**: Pipeline de CI/CD
- **Docker**: Containerización de aplicaciones
- **Kubernetes**: Orquestación de contenedores
- **Ansible**: Automatización de configuración
- **Prometheus**: Monitoring y métricas
- **Slack/Email**: Notificaciones y alertas

## 🚀 **GitHub Actions Workflow**

### **1. Estructura del Workflow**
```yaml
name: Ansible CI/CD Pipeline

on:
  push:
    branches: [ main, development ]
  pull_request:
    branches: [ main ]

jobs:
  - lint-and-validate    # Validación de sintaxis
  - test-playbooks       # Testing de playbooks
  - build-docker         # Build de imágenes Docker
  - deploy-staging       # Despliegue a staging
  - deploy-production    # Despliegue a producción
  - monitoring           # Monitoring y alertas
```

### **2. Jobs del Pipeline**

#### **Linting y Validación**
```yaml
lint-and-validate:
  name: Linting y Validación
  runs-on: ubuntu-latest
  steps:
    - name: Validar sintaxis de playbooks
      run: |
        for playbook in playbooks/*.yml; do
          ansible-playbook --syntax-check "$playbook"
        done
    
    - name: Linting con ansible-lint
      run: ansible-lint playbooks/
```

#### **Testing de Playbooks**
```yaml
test-playbooks:
  name: Testing de Playbooks
  needs: lint-and-validate
  steps:
    - name: Ejecutar tests de playbooks
      run: |
        ansible-playbook --check playbooks/01-hello-world.yml
        ansible-playbook --check playbooks/02-local-test.yml
```

#### **Build de Docker**
```yaml
build-docker:
  name: Build Docker Images
  needs: test-playbooks
  steps:
    - name: Build y push imagen base
      uses: docker/build-push-action@v5
      with:
        context: ./docker
        file: ./docker/Dockerfile.base
        push: true
        tags: |
          ${{ secrets.DOCKER_USERNAME }}/ansible-base:latest
          ${{ secrets.DOCKER_USERNAME }}/ansible-base:${{ github.sha }}
```

## 🐳 **Docker Integration**

### **1. Dockerfile Base**
```dockerfile
FROM ubuntu:22.04

# Instalar Ansible y herramientas
RUN apt-get update && apt-get install -y \
    python3 python3-pip git curl wget \
    openssh-client sudo rsync

# Instalar Ansible
RUN pip3 install ansible==8.5.0 ansible-lint yamllint

# Configurar directorio de trabajo
WORKDIR /ansible

# Copiar archivos de Ansible
COPY ansible.cfg /etc/ansible/ansible.cfg
COPY inventory/ /ansible/inventory/
COPY playbooks/ /ansible/playbooks/
COPY roles/ /ansible/roles/
```

### **2. Dockerfile de Aplicación**
```dockerfile
FROM python:3.11-slim

# Variables de entorno
ENV FLASK_APP=app.py
ENV FLASK_ENV=production
ENV ANSIBLE_FORCE_COLOR=true

# Instalar dependencias
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copiar aplicación
COPY docker/app/ .

# Exponer puerto
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1
```

## ☸️ **Kubernetes Integration**

### **1. Configuración de Staging**
```yaml
# Namespace
apiVersion: v1
kind: Namespace
metadata:
  name: staging
  labels:
    environment: staging

# ConfigMap
apiVersion: v1
kind: ConfigMap
metadata:
  name: ansible-config
  namespace: staging
data:
  ansible.cfg: |
    [defaults]
    inventory = /app/inventory/inventory.ini
    roles_path = /app/roles
    host_key_checking = False

# Deployment
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ansible-cicd
  namespace: staging
spec:
  replicas: 2
  selector:
    matchLabels:
      app: ansible-cicd
  template:
    spec:
      containers:
      - name: ansible-app
        image: ansible-app:latest
        ports:
        - containerPort: 5000
        env:
        - name: FLASK_ENV
          value: "production"
```

### **2. Configuración de Producción**
```yaml
# Deployment con más recursos
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ansible-cicd
  namespace: production
spec:
  replicas: 3
  template:
    spec:
      containers:
      - name: ansible-app
        image: ansible-app:latest
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "1Gi"
            cpu: "1000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 5000
          initialDelaySeconds: 30
          periodSeconds: 10
```

## 📊 **Monitoring y Alerting**

### **1. Health Checks**
```python
class HealthChecker:
    def check_ansible_version(self):
        """Verificar versión de Ansible"""
        result = subprocess.run(['ansible', '--version'], 
                              capture_output=True, text=True)
        return result.returncode == 0
    
    def check_inventory(self):
        """Verificar inventario de Ansible"""
        result = subprocess.run(
            ['ansible-inventory', '-i', 'inventory/inventory.ini', '--list'],
            capture_output=True, text=True
        )
        return result.returncode == 0
    
    def check_connectivity(self):
        """Verificar conectividad con hosts"""
        result = subprocess.run(
            ['ansible', 'all', '-m', 'ping', '-i', 'inventory/inventory.ini'],
            capture_output=True, text=True
        )
        return result.returncode == 0
```

### **2. Alertas de Prometheus**
```yaml
groups:
- name: ansible_alerts
  rules:
  - alert: AnsiblePlaybookFailure
    expr: increase(ansible_playbook_failures_total[5m]) > 0
    for: 1m
    labels:
      severity: critical
    annotations:
      summary: "Ansible playbook failure detected"
      description: "Ansible playbook has failed in the last 5 minutes"
  
  - alert: HighCPUUsage
    expr: cpu_usage_percent > 80
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "High CPU usage detected"
      description: "CPU usage is above 80% for more than 5 minutes"
```

### **3. Alertas de Slack**
```python
def send_slack_alert(message, color="good"):
    """Enviar alerta a Slack"""
    webhook_url = os.getenv('SLACK_WEBHOOK_URL')
    if webhook_url:
        payload = {
            "text": message,
            "attachments": [{
                "color": color,
                "fields": [{
                    "title": "Environment",
                    "value": os.getenv('ENVIRONMENT', 'unknown'),
                    "short": True
                }]
            }]
        }
        requests.post(webhook_url, json=payload)
```

## 🎭 **Playbooks de CI/CD**

### **1. Playbook de Despliegue a Staging**
```yaml
---
- name: Desplegar aplicación a Staging
  hosts: localhost
  gather_facts: yes
  
  vars:
    environment: "staging"
    image_tag: "{{ image_tag | default('latest') }}"
    namespace: "staging"
    app_name: "ansible-cicd"
  
  tasks:
    - name: Verificar configuración de staging
      assert:
        that:
          - environment == "staging"
          - image_tag is defined
        fail_msg: "Configuración de staging inválida"
    
    - name: Crear namespace staging
      kubernetes.core.k8s:
        state: present
        definition:
          apiVersion: v1
          kind: Namespace
          metadata:
            name: "{{ namespace }}"
            labels:
              environment: "{{ environment }}"
    
    - name: Aplicar Deployment para staging
      kubernetes.core.k8s:
        state: present
        definition:
          apiVersion: apps/v1
          kind: Deployment
          metadata:
            name: "{{ app_name }}"
            namespace: "{{ namespace }}"
          spec:
            replicas: 2
            selector:
              matchLabels:
                app: "{{ app_name }}"
            template:
              spec:
                containers:
                - name: ansible-app
                  image: "ansible-app:{{ image_tag }}"
                  ports:
                  - containerPort: 5000
```

### **2. Playbook de Despliegue a Producción**
```yaml
---
- name: Desplegar aplicación a Producción
  hosts: localhost
  gather_facts: yes
  
  vars:
    environment: "production"
    image_tag: "{{ image_tag | default('latest') }}"
    namespace: "production"
    app_name: "ansible-cicd"
  
  tasks:
    - name: Verificar configuración de producción
      assert:
        that:
          - environment == "production"
          - image_tag is defined
        fail_msg: "Configuración de producción inválida"
    
    - name: Crear namespace production
      kubernetes.core.k8s:
        state: present
        definition:
          apiVersion: v1
          kind: Namespace
          metadata:
            name: "{{ namespace }}"
            labels:
              environment: "{{ environment }}"
    
    - name: Aplicar Deployment para producción
      kubernetes.core.k8s:
        state: present
        definition:
          apiVersion: apps/v1
          kind: Deployment
          metadata:
            name: "{{ app_name }}"
            namespace: "{{ namespace }}"
          spec:
            replicas: 3
            selector:
              matchLabels:
                app: "{{ app_name }}"
            template:
              spec:
                containers:
                - name: ansible-app
                  image: "ansible-app:{{ image_tag }}"
                  ports:
                  - containerPort: 5000
                  resources:
                    requests:
                      memory: "512Mi"
                      cpu: "500m"
                    limits:
                      memory: "1Gi"
                      cpu: "1000m"
```

## 🔧 **Configuración de Secrets**

### **1. GitHub Secrets**
```bash
# Configurar secrets en GitHub
DOCKER_USERNAME=tu_usuario_docker
DOCKER_PASSWORD=tu_password_docker
KUBECONFIG_STAGING=configuracion_k8s_staging
KUBECONFIG_PRODUCTION=configuracion_k8s_produccion
SLACK_WEBHOOK_URL=url_webhook_slack
SMTP_SERVER=smtp.gmail.com
SMTP_USER=tu_email@gmail.com
SMTP_PASSWORD=tu_password_email
```

### **2. Variables de Entorno**
```bash
# Variables para la aplicación
export ANSIBLE_FORCE_COLOR=true
export PYTHONUNBUFFERED=1
export FLASK_ENV=production
export ANSIBLE_DIR=/app
```

## 📈 **Métricas y Reportes**

### **1. Métricas de Prometheus**
```python
from prometheus_client import Counter, Histogram, generate_latest

# Métricas
REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests', 
                       ['method', 'endpoint', 'status'])
REQUEST_LATENCY = Histogram('http_request_duration_seconds', 'HTTP request latency')
ANSIBLE_EXECUTIONS = Counter('ansible_executions_total', 'Total Ansible executions')
ANSIBLE_FAILURES = Counter('ansible_failures_total', 'Total Ansible failures')

@app.route('/metrics')
def metrics():
    """Endpoint para métricas de Prometheus"""
    return generate_latest(), 200, {'Content-Type': CONTENT_TYPE_LATEST}
```

### **2. Generación de Reportes**
```python
class DeploymentReporter:
    def generate_full_report(self):
        """Generar reporte completo"""
        self.collect_deployment_info()
        self.collect_system_status()
        self.collect_playbooks_info()
        self.run_health_checks()
        self.generate_recommendations()
        
        report_file = self.create_report_file()
        summary = self.generate_summary()
        
        return self.report, report_file, summary
```

## 🚨 **Manejo de Errores y Rollback**

### **1. Rollback Automático**
```yaml
---
- name: Rollback en caso de error
  hosts: localhost
  gather_facts: yes
  
  vars:
    environment: "{{ environment | default('staging') }}"
    app_name: "ansible-cicd"
  
  tasks:
    - name: Verificar estado del deployment
      kubernetes.core.k8s_info:
        api_version: apps/v1
        kind: Deployment
        name: "{{ app_name }}"
        namespace: "{{ environment }}"
      register: deployment_info
    
    - name: Rollback a versión anterior
      kubernetes.core.k8s:
        state: present
        definition:
          apiVersion: apps/v1
          kind: Deployment
          metadata:
            name: "{{ app_name }}"
            namespace: "{{ environment }}"
          spec:
            replicas: 1  # Reducir réplicas
            selector:
              matchLabels:
                app: "{{ app_name }}"
            template:
              spec:
                containers:
                - name: ansible-app
                  image: "ansible-app:previous"  # Imagen anterior
                  ports:
                  - containerPort: 5000
      when: deployment_info.resources[0].status.readyReplicas < 1
```

### **2. Notificaciones de Error**
```python
def notify_deployment_failure(error_message):
    """Notificar fallo de despliegue"""
    # Slack
    send_slack_alert(f"❌ Error en despliegue: {error_message}", "danger")
    
    # Email
    send_email_alert(
        subject="❌ Error en Despliegue - Ansible CI/CD",
        body=f"Se detectó un error durante el despliegue: {error_message}"
    )
    
    # Log
    logger.error("Deployment failed", error=error_message)
```

## 🎯 **Mejores Prácticas**

### **1. Seguridad**
- ✅ Usar secrets para credenciales sensibles
- ✅ Implementar RBAC en Kubernetes
- ✅ Escanear imágenes Docker por vulnerabilidades
- ✅ Usar Ansible Vault para variables sensibles

### **2. Testing**
- ✅ Ejecutar tests en cada commit
- ✅ Usar `--check` mode para validar playbooks
- ✅ Implementar health checks automáticos
- ✅ Testing de rollback

### **3. Monitoring**
- ✅ Configurar alertas proactivas
- ✅ Monitorear métricas de rendimiento
- ✅ Logging estructurado
- ✅ Dashboards de visualización

### **4. Automatización**
- ✅ Pipeline completamente automatizado
- ✅ Despliegue sin intervención manual
- ✅ Rollback automático en caso de error
- ✅ Notificaciones automáticas

## 🎯 **Resumen**

CI/CD con Ansible proporciona:
- 🔄 **Automatización completa** del pipeline de desarrollo
- 🐳 **Containerización** con Docker
- ☸️ **Orquestación** con Kubernetes
- 📊 **Monitoring** y alertas en tiempo real
- 🚨 **Manejo robusto de errores** con rollback automático
- 📈 **Métricas** y reportes detallados

**Recuerda**: Un pipeline de CI/CD bien configurado reduce errores humanos, acelera el tiempo de entrega y mejora la calidad del software. 