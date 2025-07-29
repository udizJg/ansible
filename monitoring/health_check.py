#!/usr/bin/env python3
# ===========================================
# SCRIPT DE HEALTH CHECK PARA MONITORING
# ===========================================

import os
import sys
import json
import requests
import subprocess
from datetime import datetime
import structlog

# Configurar logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer()
    ],
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

class HealthChecker:
    def __init__(self):
        self.health_status = {
            'timestamp': datetime.utcnow().isoformat(),
            'overall_status': 'healthy',
            'checks': {}
        }
        
    def check_ansible_version(self):
        """Verificar versión de Ansible"""
        try:
            result = subprocess.run(
                ['ansible', '--version'],
                capture_output=True, text=True
            )
            if result.returncode == 0:
                version = result.stdout.split('\n')[0]
                self.health_status['checks']['ansible_version'] = {
                    'status': 'healthy',
                    'version': version
                }
                logger.info("Ansible version check passed", version=version)
            else:
                self.health_status['checks']['ansible_version'] = {
                    'status': 'unhealthy',
                    'error': result.stderr
                }
                logger.error("Ansible version check failed", error=result.stderr)
        except Exception as e:
            self.health_status['checks']['ansible_version'] = {
                'status': 'unhealthy',
                'error': str(e)
            }
            logger.error("Ansible version check failed", error=str(e))
    
    def check_inventory(self):
        """Verificar inventario de Ansible"""
        try:
            inventory_file = os.path.join(os.getcwd(), 'inventory', 'inventory.ini')
            if os.path.exists(inventory_file):
                result = subprocess.run(
                    ['ansible-inventory', '-i', inventory_file, '--list'],
                    capture_output=True, text=True
                )
                if result.returncode == 0:
                    inventory = json.loads(result.stdout)
                    self.health_status['checks']['inventory'] = {
                        'status': 'healthy',
                        'hosts_count': len(inventory.get('_meta', {}).get('hostvars', {}))
                    }
                    logger.info("Inventory check passed", hosts_count=len(inventory.get('_meta', {}).get('hostvars', {})))
                else:
                    self.health_status['checks']['inventory'] = {
                        'status': 'unhealthy',
                        'error': result.stderr
                    }
                    logger.error("Inventory check failed", error=result.stderr)
            else:
                self.health_status['checks']['inventory'] = {
                    'status': 'unhealthy',
                    'error': 'Inventory file not found'
                }
                logger.error("Inventory file not found")
        except Exception as e:
            self.health_status['checks']['inventory'] = {
                'status': 'unhealthy',
                'error': str(e)
            }
            logger.error("Inventory check failed", error=str(e))
    
    def check_playbooks(self):
        """Verificar playbooks disponibles"""
        try:
            playbooks_dir = os.path.join(os.getcwd(), 'playbooks')
            if os.path.exists(playbooks_dir):
                playbooks = [f for f in os.listdir(playbooks_dir) if f.endswith('.yml')]
                self.health_status['checks']['playbooks'] = {
                    'status': 'healthy',
                    'count': len(playbooks),
                    'files': playbooks
                }
                logger.info("Playbooks check passed", count=len(playbooks))
            else:
                self.health_status['checks']['playbooks'] = {
                    'status': 'unhealthy',
                    'error': 'Playbooks directory not found'
                }
                logger.error("Playbooks directory not found")
        except Exception as e:
            self.health_status['checks']['playbooks'] = {
                'status': 'unhealthy',
                'error': str(e)
            }
            logger.error("Playbooks check failed", error=str(e))
    
    def check_roles(self):
        """Verificar roles disponibles"""
        try:
            roles_dir = os.path.join(os.getcwd(), 'roles')
            if os.path.exists(roles_dir):
                roles = [d for d in os.listdir(roles_dir) if os.path.isdir(os.path.join(roles_dir, d))]
                self.health_status['checks']['roles'] = {
                    'status': 'healthy',
                    'count': len(roles),
                    'roles': roles
                }
                logger.info("Roles check passed", count=len(roles))
            else:
                self.health_status['checks']['roles'] = {
                    'status': 'unhealthy',
                    'error': 'Roles directory not found'
                }
                logger.error("Roles directory not found")
        except Exception as e:
            self.health_status['checks']['roles'] = {
                'status': 'unhealthy',
                'error': str(e)
            }
            logger.error("Roles check failed", error=str(e))
    
    def check_connectivity(self):
        """Verificar conectividad con hosts"""
        try:
            inventory_file = os.path.join(os.getcwd(), 'inventory', 'inventory.ini')
            if os.path.exists(inventory_file):
                result = subprocess.run(
                    ['ansible', 'all', '-m', 'ping', '-i', inventory_file, '--connection=local'],
                    capture_output=True, text=True
                )
                if result.returncode == 0:
                    self.health_status['checks']['connectivity'] = {
                        'status': 'healthy',
                        'message': 'All hosts responding'
                    }
                    logger.info("Connectivity check passed")
                else:
                    self.health_status['checks']['connectivity'] = {
                        'status': 'unhealthy',
                        'error': result.stderr
                    }
                    logger.error("Connectivity check failed", error=result.stderr)
            else:
                self.health_status['checks']['connectivity'] = {
                    'status': 'unhealthy',
                    'error': 'Inventory file not found'
                }
                logger.error("Inventory file not found for connectivity check")
        except Exception as e:
            self.health_status['checks']['connectivity'] = {
                'status': 'unhealthy',
                'error': str(e)
            }
            logger.error("Connectivity check failed", error=str(e))
    
    def check_web_application(self):
        """Verificar aplicación web si está disponible"""
        try:
            # Intentar conectar a la aplicación web
            response = requests.get('http://localhost:5000/health', timeout=5)
            if response.status_code == 200:
                data = response.json()
                self.health_status['checks']['web_application'] = {
                    'status': 'healthy',
                    'response': data
                }
                logger.info("Web application check passed")
            else:
                self.health_status['checks']['web_application'] = {
                    'status': 'unhealthy',
                    'error': f'HTTP {response.status_code}'
                }
                logger.error("Web application check failed", status_code=response.status_code)
        except requests.exceptions.RequestException as e:
            self.health_status['checks']['web_application'] = {
                'status': 'unhealthy',
                'error': str(e)
            }
            logger.error("Web application check failed", error=str(e))
    
    def run_all_checks(self):
        """Ejecutar todos los health checks"""
        logger.info("Starting health checks")
        
        self.check_ansible_version()
        self.check_inventory()
        self.check_playbooks()
        self.check_roles()
        self.check_connectivity()
        self.check_web_application()
        
        # Determinar estado general
        unhealthy_checks = [check for check in self.health_status['checks'].values() 
                           if check['status'] == 'unhealthy']
        
        if unhealthy_checks:
            self.health_status['overall_status'] = 'unhealthy'
            logger.error("Health checks completed with failures", 
                        unhealthy_count=len(unhealthy_checks))
        else:
            logger.info("All health checks passed")
        
        return self.health_status

def main():
    """Función principal"""
    checker = HealthChecker()
    health_status = checker.run_all_checks()
    
    # Imprimir resultado
    print(json.dumps(health_status, indent=2))
    
    # Retornar código de salida
    if health_status['overall_status'] == 'healthy':
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == '__main__':
    main() 