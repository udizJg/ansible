# ===========================================
# DOCKERFILE PARA APLICACIÓN CON ANSIBLE
# ===========================================
# Aplicación web que usa Ansible para automatización

FROM python:3.11-slim

# Variables de entorno
ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=app.py
ENV FLASK_ENV=production
ENV ANSIBLE_FORCE_COLOR=true

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    git \
    curl \
    wget \
    openssh-client \
    sudo \
    && rm -rf /var/lib/apt/lists/*

# Crear directorio de trabajo
WORKDIR /app

# Copiar requirements
COPY docker/requirements.txt .

# Instalar dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Instalar Ansible
RUN pip install ansible==8.5.0

# Copiar código de la aplicación
COPY docker/app/ .

# Copiar playbooks y roles
COPY playbooks/ /app/playbooks/
COPY roles/ /app/roles/
COPY inventory/ /app/inventory/
COPY ansible.cfg /app/ansible.cfg

# Crear directorios necesarios
RUN mkdir -p /app/logs /app/data /app/config

# Configurar permisos
RUN chmod +x /app/start.sh

# Exponer puerto
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# Comando de inicio
CMD ["/app/start.sh"] 