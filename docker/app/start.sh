#!/bin/bash
# ===========================================
# SCRIPT DE INICIO PARA APLICACIÓN ANSIBLE
# ===========================================

set -e

echo "🚀 Iniciando aplicación Ansible CI/CD..."

# Verificar que Ansible esté disponible
if ! command -v ansible &> /dev/null; then
    echo "❌ Error: Ansible no está instalado"
    exit 1
fi

# Verificar configuración
echo "🔍 Verificando configuración..."
if [ ! -f "/app/ansible.cfg" ]; then
    echo "⚠️  Advertencia: ansible.cfg no encontrado, usando configuración por defecto"
fi

if [ ! -f "/app/inventory/inventory.ini" ]; then
    echo "⚠️  Advertencia: inventory.ini no encontrado"
fi

# Verificar playbooks
echo "📋 Verificando playbooks..."
if [ -d "/app/playbooks" ]; then
    echo "✅ Playbooks encontrados:"
    ls -la /app/playbooks/*.yml 2>/dev/null || echo "   No se encontraron playbooks .yml"
else
    echo "⚠️  Directorio playbooks no encontrado"
fi

# Verificar roles
echo "🎭 Verificando roles..."
if [ -d "/app/roles" ]; then
    echo "✅ Roles encontrados:"
    ls -la /app/roles/ 2>/dev/null || echo "   No se encontraron roles"
else
    echo "⚠️  Directorio roles no encontrado"
fi

# Mostrar versión de Ansible
echo "📊 Información del sistema:"
ansible --version | head -1

# Verificar conectividad si hay inventario
if [ -f "/app/inventory/inventory.ini" ]; then
    echo "🔗 Verificando conectividad..."
    ansible all -m ping -i /app/inventory/inventory.ini --connection=local || echo "⚠️  Algunos hosts no respondieron"
fi

# Iniciar aplicación Flask
echo "🌐 Iniciando servidor web..."
exec python3 /app/app.py 