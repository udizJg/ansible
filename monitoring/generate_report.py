#!/usr/bin/env python3
# ===========================================
# SCRIPT PARA GENERAR REPORTES DE DESPLIEGUE
# ===========================================

import os
import json
import subprocess
import requests
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

class DeploymentReporter:
    def __init__(self):
        self.report = {
            'timestamp': datetime.utcnow().isoformat(),
            'deployment_info': {},
            'system_status': {},
            'playbooks_executed': [],
            'health_checks': {},
            'recommendations': []
        }
        
    def collect_deployment_info(self):
        """Recopilar información del despliegue"""
        deployment_info = {
            'environment': os.getenv('ENVIRONMENT', 'unknown'),
            'image_tag': os.getenv('IMAGE_TAG', 'latest'),
            'commit_sha': os.getenv('GITHUB_SHA', 'unknown'),
            'branch': os.getenv('GITHUB_REF', 'unknown'),
            'deployed_by': os.getenv('GITHUB_ACTOR', 'unknown'),
            'deployment_time': datetime.utcnow().isoformat()
        }
        
        self.report['deployment_info'] = deployment_info
        logger.info("Deployment info collected", info=deployment_info)
    
    def collect_system_status(self):
        """Recopilar estado del sistema"""
        try:
            # Verificar Ansible
            ansible_result = subprocess.run(
                ['ansible', '--version'],
                capture_output=True, text=True
            )
            ansible_version = ansible_result.stdout.split('\n')[0] if ansible_result.returncode == 0 else 'Unknown'
            
            # Verificar inventario
            inventory_file = os.path.join(os.getcwd(), 'inventory', 'inventory.ini')
            inventory_exists = os.path.exists(inventory_file)
            
            # Verificar playbooks
            playbooks_dir = os.path.join(os.getcwd(), 'playbooks')
            playbooks_count = len([f for f in os.listdir(playbooks_dir) if f.endswith('.yml')]) if os.path.exists(playbooks_dir) else 0
            
            # Verificar roles
            roles_dir = os.path.join(os.getcwd(), 'roles')
            roles_count = len([d for d in os.listdir(roles_dir) if os.path.isdir(os.path.join(roles_dir, d))]) if os.path.exists(roles_dir) else 0
            
            system_status = {
                'ansible_version': ansible_version,
                'inventory_exists': inventory_exists,
                'playbooks_count': playbooks_count,
                'roles_count': roles_count,
                'python_version': f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
                'working_directory': os.getcwd()
            }
            
            self.report['system_status'] = system_status
            logger.info("System status collected", status=system_status)
            
        except Exception as e:
            logger.error("Error collecting system status", error=str(e))
            self.report['system_status'] = {'error': str(e)}
    
    def collect_playbooks_info(self):
        """Recopilar información de playbooks"""
        try:
            playbooks_dir = os.path.join(os.getcwd(), 'playbooks')
            if os.path.exists(playbooks_dir):
                playbooks = []
                for file in os.listdir(playbooks_dir):
                    if file.endswith('.yml'):
                        playbook_info = {
                            'name': file,
                            'path': os.path.join(playbooks_dir, file),
                            'size': os.path.getsize(os.path.join(playbooks_dir, file)),
                            'modified': datetime.fromtimestamp(
                                os.path.getmtime(os.path.join(playbooks_dir, file))
                            ).isoformat()
                        }
                        playbooks.append(playbook_info)
                
                self.report['playbooks_executed'] = playbooks
                logger.info("Playbooks info collected", count=len(playbooks))
            else:
                logger.warning("Playbooks directory not found")
                
        except Exception as e:
            logger.error("Error collecting playbooks info", error=str(e))
    
    def run_health_checks(self):
        """Ejecutar health checks"""
        try:
            # Health check básico
            health_checks = {}
            
            # Verificar conectividad
            inventory_file = os.path.join(os.getcwd(), 'inventory', 'inventory.ini')
            if os.path.exists(inventory_file):
                ping_result = subprocess.run(
                    ['ansible', 'all', '-m', 'ping', '-i', inventory_file, '--connection=local'],
                    capture_output=True, text=True
                )
                health_checks['connectivity'] = {
                    'status': 'healthy' if ping_result.returncode == 0 else 'unhealthy',
                    'details': ping_result.stdout if ping_result.returncode == 0 else ping_result.stderr
                }
            
            # Verificar aplicación web
            try:
                response = requests.get('http://localhost:5000/health', timeout=5)
                health_checks['web_application'] = {
                    'status': 'healthy' if response.status_code == 200 else 'unhealthy',
                    'response_code': response.status_code
                }
            except requests.exceptions.RequestException:
                health_checks['web_application'] = {
                    'status': 'unhealthy',
                    'error': 'Application not responding'
                }
            
            # Verificar sintaxis de playbooks
            playbooks_dir = os.path.join(os.getcwd(), 'playbooks')
            if os.path.exists(playbooks_dir):
                syntax_errors = []
                for file in os.listdir(playbooks_dir):
                    if file.endswith('.yml'):
                        syntax_result = subprocess.run(
                            ['ansible-playbook', '--syntax-check', os.path.join(playbooks_dir, file)],
                            capture_output=True, text=True
                        )
                        if syntax_result.returncode != 0:
                            syntax_errors.append({
                                'file': file,
                                'error': syntax_result.stderr
                            })
                
                health_checks['playbook_syntax'] = {
                    'status': 'healthy' if not syntax_errors else 'unhealthy',
                    'errors': syntax_errors
                }
            
            self.report['health_checks'] = health_checks
            logger.info("Health checks completed", checks=len(health_checks))
            
        except Exception as e:
            logger.error("Error running health checks", error=str(e))
            self.report['health_checks'] = {'error': str(e)}
    
    def generate_recommendations(self):
        """Generar recomendaciones basadas en el estado del sistema"""
        recommendations = []
        
        # Verificar health checks
        if 'health_checks' in self.report:
            health_checks = self.report['health_checks']
            
            if health_checks.get('connectivity', {}).get('status') == 'unhealthy':
                recommendations.append({
                    'type': 'critical',
                    'message': 'Problemas de conectividad detectados. Verificar configuración de inventario.',
                    'action': 'Revisar inventory.ini y configuración de red'
                })
            
            if health_checks.get('web_application', {}).get('status') == 'unhealthy':
                recommendations.append({
                    'type': 'warning',
                    'message': 'Aplicación web no responde. Verificar estado del servicio.',
                    'action': 'Revisar logs de la aplicación y reiniciar si es necesario'
                })
            
            if health_checks.get('playbook_syntax', {}).get('status') == 'unhealthy':
                recommendations.append({
                    'type': 'critical',
                    'message': 'Errores de sintaxis en playbooks detectados.',
                    'action': 'Corregir errores de sintaxis antes del próximo despliegue'
                })
        
        # Verificar sistema
        if 'system_status' in self.report:
            system_status = self.report['system_status']
            
            if not system_status.get('inventory_exists'):
                recommendations.append({
                    'type': 'warning',
                    'message': 'Archivo de inventario no encontrado.',
                    'action': 'Crear inventory.ini con configuración apropiada'
                })
            
            if system_status.get('playbooks_count', 0) == 0:
                recommendations.append({
                    'type': 'info',
                    'message': 'No se encontraron playbooks.',
                    'action': 'Crear playbooks para automatización'
                })
        
        # Recomendaciones generales
        recommendations.append({
            'type': 'info',
            'message': 'Considerar implementar monitoreo continuo.',
            'action': 'Configurar Prometheus y Grafana para métricas'
        })
        
        recommendations.append({
            'type': 'info',
            'message': 'Implementar backup automático de configuración.',
            'action': 'Configurar backup de playbooks y roles'
        })
        
        self.report['recommendations'] = recommendations
        logger.info("Recommendations generated", count=len(recommendations))
    
    def create_report_file(self):
        """Crear archivo de reporte"""
        reports_dir = os.path.join(os.getcwd(), 'monitoring', 'reports')
        os.makedirs(reports_dir, exist_ok=True)
        
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        report_file = os.path.join(reports_dir, f'deployment_report_{timestamp}.json')
        
        with open(report_file, 'w') as f:
            json.dump(self.report, f, indent=2)
        
        logger.info("Deployment report file created", file=report_file)
        return report_file
    
    def generate_summary(self):
        """Generar resumen del reporte"""
        summary = {
            'deployment_status': 'success' if not self.report.get('health_checks', {}).get('error') else 'error',
            'total_playbooks': len(self.report.get('playbooks_executed', [])),
            'health_checks_passed': sum(1 for check in self.report.get('health_checks', {}).values() 
                                      if isinstance(check, dict) and check.get('status') == 'healthy'),
            'total_recommendations': len(self.report.get('recommendations', [])),
            'critical_recommendations': sum(1 for rec in self.report.get('recommendations', []) 
                                          if rec.get('type') == 'critical')
        }
        
        return summary
    
    def generate_full_report(self):
        """Generar reporte completo"""
        logger.info("Generating deployment report")
        
        self.collect_deployment_info()
        self.collect_system_status()
        self.collect_playbooks_info()
        self.run_health_checks()
        self.generate_recommendations()
        
        report_file = self.create_report_file()
        summary = self.generate_summary()
        
        logger.info("Deployment report generated successfully", 
                   file=report_file, summary=summary)
        
        return self.report, report_file, summary

def main():
    """Función principal"""
    import sys
    
    reporter = DeploymentReporter()
    report, report_file, summary = reporter.generate_full_report()
    
    print("📊 REPORTE DE DESPLIEGUE GENERADO")
    print("=" * 50)
    print(f"📁 Archivo: {report_file}")
    print(f"✅ Estado: {summary['deployment_status']}")
    print(f"🎭 Playbooks: {summary['total_playbooks']}")
    print(f"🏥 Health Checks: {summary['health_checks_passed']} pasaron")
    print(f"💡 Recomendaciones: {summary['total_recommendations']} (críticas: {summary['critical_recommendations']})")
    print("\n📋 Resumen completo:")
    print(json.dumps(summary, indent=2))

if __name__ == '__main__':
    main() 