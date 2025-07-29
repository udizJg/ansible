#!/usr/bin/env python3
# ===========================================
# APLICACIÓN FLASK CON INTEGRACIÓN ANSIBLE
# ===========================================

import os
import json
import subprocess
import logging
from datetime import datetime
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
import structlog

# Configurar logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

# Configurar Flask
app = Flask(__name__)
CORS(app)

# Métricas de Prometheus
REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'status'])
REQUEST_LATENCY = Histogram('http_request_duration_seconds', 'HTTP request latency')

# Configuración
ANSIBLE_DIR = os.getenv('ANSIBLE_DIR', '/app')
INVENTORY_FILE = os.path.join(ANSIBLE_DIR, 'inventory/inventory.ini')

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'ansible_version': get_ansible_version()
    })

@app.route('/metrics')
def metrics():
    """Endpoint para métricas de Prometheus"""
    return generate_latest(), 200, {'Content-Type': CONTENT_TYPE_LATEST}

@app.route('/api/ansible/version')
def ansible_version():
    """Obtener versión de Ansible"""
    try:
        version = get_ansible_version()
        return jsonify({'ansible_version': version})
    except Exception as e:
        logger.error("Error obteniendo versión de Ansible", error=str(e))
        return jsonify({'error': str(e)}), 500

@app.route('/api/ansible/inventory')
def get_inventory():
    """Obtener inventario de Ansible"""
    try:
        result = subprocess.run(
            ['ansible-inventory', '-i', INVENTORY_FILE, '--list'],
            capture_output=True, text=True, cwd=ANSIBLE_DIR
        )
        
        if result.returncode == 0:
            inventory = json.loads(result.stdout)
            return jsonify(inventory)
        else:
            logger.error("Error obteniendo inventario", error=result.stderr)
            return jsonify({'error': result.stderr}), 500
            
    except Exception as e:
        logger.error("Error obteniendo inventario", error=str(e))
        return jsonify({'error': str(e)}), 500

@app.route('/api/ansible/playbooks')
def list_playbooks():
    """Listar playbooks disponibles"""
    try:
        playbooks_dir = os.path.join(ANSIBLE_DIR, 'playbooks')
        playbooks = []
        
        for file in os.listdir(playbooks_dir):
            if file.endswith('.yml'):
                playbooks.append({
                    'name': file,
                    'path': os.path.join(playbooks_dir, file)
                })
        
        return jsonify({'playbooks': playbooks})
        
    except Exception as e:
        logger.error("Error listando playbooks", error=str(e))
        return jsonify({'error': str(e)}), 500

@app.route('/api/ansible/execute', methods=['POST'])
def execute_playbook():
    """Ejecutar un playbook"""
    try:
        data = request.get_json()
        playbook = data.get('playbook')
        extra_vars = data.get('extra_vars', {})
        
        if not playbook:
            return jsonify({'error': 'Playbook no especificado'}), 400
        
        playbook_path = os.path.join(ANSIBLE_DIR, 'playbooks', playbook)
        
        if not os.path.exists(playbook_path):
            return jsonify({'error': f'Playbook {playbook} no encontrado'}), 404
        
        # Construir comando
        cmd = ['ansible-playbook', '-i', INVENTORY_FILE, playbook_path]
        
        # Agregar variables extra
        if extra_vars:
            cmd.extend(['-e', json.dumps(extra_vars)])
        
        # Ejecutar playbook
        result = subprocess.run(
            cmd,
            capture_output=True, text=True, cwd=ANSIBLE_DIR
        )
        
        response = {
            'playbook': playbook,
            'return_code': result.returncode,
            'stdout': result.stdout,
            'stderr': result.stderr,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        if result.returncode == 0:
            logger.info("Playbook ejecutado exitosamente", playbook=playbook)
            return jsonify(response)
        else:
            logger.error("Error ejecutando playbook", playbook=playbook, error=result.stderr)
            return jsonify(response), 500
            
    except Exception as e:
        logger.error("Error ejecutando playbook", error=str(e))
        return jsonify({'error': str(e)}), 500

@app.route('/api/ansible/ping')
def ping_hosts():
    """Hacer ping a todos los hosts del inventario"""
    try:
        result = subprocess.run(
            ['ansible', 'all', '-m', 'ping', '-i', INVENTORY_FILE],
            capture_output=True, text=True, cwd=ANSIBLE_DIR
        )
        
        response = {
            'return_code': result.returncode,
            'stdout': result.stdout,
            'stderr': result.stderr,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        if result.returncode == 0:
            return jsonify(response)
        else:
            return jsonify(response), 500
            
    except Exception as e:
        logger.error("Error haciendo ping", error=str(e))
        return jsonify({'error': str(e)}), 500

@app.route('/api/ansible/facts')
def get_facts():
    """Obtener facts de todos los hosts"""
    try:
        result = subprocess.run(
            ['ansible', 'all', '-m', 'setup', '-i', INVENTORY_FILE],
            capture_output=True, text=True, cwd=ANSIBLE_DIR
        )
        
        response = {
            'return_code': result.returncode,
            'stdout': result.stdout,
            'stderr': result.stderr,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        if result.returncode == 0:
            return jsonify(response)
        else:
            return jsonify(response), 500
            
    except Exception as e:
        logger.error("Error obteniendo facts", error=str(e))
        return jsonify({'error': str(e)}), 500

@app.route('/')
def index():
    """Página principal con dashboard"""
    html_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Ansible CI/CD Dashboard</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            .container { max-width: 1200px; margin: 0 auto; }
            .header { background: #2c3e50; color: white; padding: 20px; border-radius: 5px; }
            .section { margin: 20px 0; padding: 20px; border: 1px solid #ddd; border-radius: 5px; }
            .button { background: #3498db; color: white; padding: 10px 20px; border: none; border-radius: 3px; cursor: pointer; }
            .button:hover { background: #2980b9; }
            .status { padding: 10px; margin: 10px 0; border-radius: 3px; }
            .status.success { background: #d4edda; color: #155724; }
            .status.error { background: #f8d7da; color: #721c24; }
            pre { background: #f8f9fa; padding: 10px; border-radius: 3px; overflow-x: auto; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🚀 Ansible CI/CD Dashboard</h1>
                <p>Panel de control para automatización con Ansible</p>
            </div>
            
            <div class="section">
                <h2>📊 Estado del Sistema</h2>
                <div id="health-status">Cargando...</div>
                <button class="button" onclick="checkHealth()">Verificar Estado</button>
            </div>
            
            <div class="section">
                <h2>📋 Inventario</h2>
                <div id="inventory">Cargando...</div>
                <button class="button" onclick="getInventory()">Actualizar Inventario</button>
            </div>
            
            <div class="section">
                <h2>🎭 Playbooks</h2>
                <div id="playbooks">Cargando...</div>
                <button class="button" onclick="listPlaybooks()">Listar Playbooks</button>
            </div>
            
            <div class="section">
                <h2>🔧 Ejecutar Playbook</h2>
                <select id="playbook-select">
                    <option value="">Seleccionar playbook...</option>
                </select>
                <button class="button" onclick="executePlaybook()">Ejecutar</button>
                <div id="execution-result"></div>
            </div>
            
            <div class="section">
                <h2>📈 Métricas</h2>
                <a href="/metrics" class="button" target="_blank">Ver Métricas Prometheus</a>
            </div>
        </div>
        
        <script>
            // Funciones JavaScript para interactuar con la API
            async function checkHealth() {
                try {
                    const response = await fetch('/health');
                    const data = await response.json();
                    document.getElementById('health-status').innerHTML = 
                        `<div class="status success">✅ ${JSON.stringify(data, null, 2)}</div>`;
                } catch (error) {
                    document.getElementById('health-status').innerHTML = 
                        `<div class="status error">❌ Error: ${error.message}</div>`;
                }
            }
            
            async function getInventory() {
                try {
                    const response = await fetch('/api/ansible/inventory');
                    const data = await response.json();
                    document.getElementById('inventory').innerHTML = 
                        `<pre>${JSON.stringify(data, null, 2)}</pre>`;
                } catch (error) {
                    document.getElementById('inventory').innerHTML = 
                        `<div class="status error">❌ Error: ${error.message}</div>`;
                }
            }
            
            async function listPlaybooks() {
                try {
                    const response = await fetch('/api/ansible/playbooks');
                    const data = await response.json();
                    const select = document.getElementById('playbook-select');
                    select.innerHTML = '<option value="">Seleccionar playbook...</option>';
                    
                    data.playbooks.forEach(playbook => {
                        const option = document.createElement('option');
                        option.value = playbook.name;
                        option.textContent = playbook.name;
                        select.appendChild(option);
                    });
                    
                    document.getElementById('playbooks').innerHTML = 
                        `<pre>${JSON.stringify(data, null, 2)}</pre>`;
                } catch (error) {
                    document.getElementById('playbooks').innerHTML = 
                        `<div class="status error">❌ Error: ${error.message}</div>`;
                }
            }
            
            async function executePlaybook() {
                const playbook = document.getElementById('playbook-select').value;
                if (!playbook) {
                    alert('Por favor selecciona un playbook');
                    return;
                }
                
                try {
                    const response = await fetch('/api/ansible/execute', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({playbook: playbook})
                    });
                    const data = await response.json();
                    document.getElementById('execution-result').innerHTML = 
                        `<pre>${JSON.stringify(data, null, 2)}</pre>`;
                } catch (error) {
                    document.getElementById('execution-result').innerHTML = 
                        `<div class="status error">❌ Error: ${error.message}</div>`;
                }
            }
            
            // Cargar datos al iniciar
            window.onload = function() {
                checkHealth();
                getInventory();
                listPlaybooks();
            };
        </script>
    </body>
    </html>
    """
    return render_template_string(html_template)

def get_ansible_version():
    """Obtener versión de Ansible"""
    try:
        result = subprocess.run(
            ['ansible', '--version'],
            capture_output=True, text=True, cwd=ANSIBLE_DIR
        )
        if result.returncode == 0:
            return result.stdout.split('\n')[0]
        return "Versión no disponible"
    except Exception:
        return "Versión no disponible"

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False) 