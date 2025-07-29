#!/usr/bin/env python3
# ===========================================
# SCRIPT PARA CONFIGURAR ALERTAS
# ===========================================

import os
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

class AlertManager:
    def __init__(self):
        self.alerts_config = {
            'timestamp': datetime.utcnow().isoformat(),
            'alerts': []
        }
        
    def setup_prometheus_alerts(self):
        """Configurar alertas de Prometheus"""
        prometheus_alerts = {
            'name': 'prometheus_alerts',
            'type': 'prometheus',
            'rules': [
                {
                    'alert': 'AnsiblePlaybookFailure',
                    'expr': 'increase(ansible_playbook_failures_total[5m]) > 0',
                    'for': '1m',
                    'labels': {
                        'severity': 'critical'
                    },
                    'annotations': {
                        'summary': 'Ansible playbook failure detected',
                        'description': 'Ansible playbook has failed in the last 5 minutes'
                    }
                },
                {
                    'alert': 'HighCPUUsage',
                    'expr': 'cpu_usage_percent > 80',
                    'for': '5m',
                    'labels': {
                        'severity': 'warning'
                    },
                    'annotations': {
                        'summary': 'High CPU usage detected',
                        'description': 'CPU usage is above 80% for more than 5 minutes'
                    }
                },
                {
                    'alert': 'HighMemoryUsage',
                    'expr': 'memory_usage_percent > 85',
                    'for': '5m',
                    'labels': {
                        'severity': 'warning'
                    },
                    'annotations': {
                        'summary': 'High memory usage detected',
                        'description': 'Memory usage is above 85% for more than 5 minutes'
                    }
                }
            ]
        }
        
        self.alerts_config['alerts'].append(prometheus_alerts)
        logger.info("Prometheus alerts configured")
    
    def setup_slack_alerts(self):
        """Configurar alertas de Slack"""
        slack_webhook = os.getenv('SLACK_WEBHOOK_URL')
        if slack_webhook:
            slack_alerts = {
                'name': 'slack_alerts',
                'type': 'slack',
                'webhook_url': slack_webhook,
                'channels': ['#ansible-alerts', '#devops'],
                'templates': {
                    'deployment_success': {
                        'text': '✅ Despliegue exitoso',
                        'color': 'good'
                    },
                    'deployment_failure': {
                        'text': '❌ Error en despliegue',
                        'color': 'danger'
                    },
                    'health_check_failure': {
                        'text': '⚠️ Health check falló',
                        'color': 'warning'
                    }
                }
            }
            
            self.alerts_config['alerts'].append(slack_alerts)
            logger.info("Slack alerts configured")
        else:
            logger.warning("SLACK_WEBHOOK_URL not configured, skipping Slack alerts")
    
    def setup_email_alerts(self):
        """Configurar alertas por email"""
        email_config = {
            'name': 'email_alerts',
            'type': 'email',
            'smtp_server': os.getenv('SMTP_SERVER', 'smtp.gmail.com'),
            'smtp_port': int(os.getenv('SMTP_PORT', '587')),
            'smtp_user': os.getenv('SMTP_USER'),
            'smtp_password': os.getenv('SMTP_PASSWORD'),
            'recipients': os.getenv('ALERT_EMAILS', '').split(','),
            'templates': {
                'deployment_success': {
                    'subject': '✅ Despliegue Exitoso - Ansible CI/CD',
                    'body': 'El despliegue se completó exitosamente.'
                },
                'deployment_failure': {
                    'subject': '❌ Error en Despliegue - Ansible CI/CD',
                    'body': 'Se detectó un error durante el despliegue.'
                }
            }
        }
        
        self.alerts_config['alerts'].append(email_config)
        logger.info("Email alerts configured")
    
    def setup_health_check_alerts(self):
        """Configurar alertas de health check"""
        health_alerts = {
            'name': 'health_check_alerts',
            'type': 'health_check',
            'checks': [
                {
                    'name': 'ansible_version',
                    'interval': '5m',
                    'threshold': 1,
                    'action': 'restart_service'
                },
                {
                    'name': 'inventory_access',
                    'interval': '2m',
                    'threshold': 3,
                    'action': 'send_alert'
                },
                {
                    'name': 'playbook_execution',
                    'interval': '10m',
                    'threshold': 2,
                    'action': 'rollback'
                }
            ]
        }
        
        self.alerts_config['alerts'].append(health_alerts)
        logger.info("Health check alerts configured")
    
    def setup_kubernetes_alerts(self):
        """Configurar alertas de Kubernetes"""
        k8s_alerts = {
            'name': 'kubernetes_alerts',
            'type': 'kubernetes',
            'rules': [
                {
                    'alert': 'PodCrashLooping',
                    'expr': 'rate(kube_pod_container_status_restarts_total[15m]) > 0',
                    'for': '5m',
                    'labels': {
                        'severity': 'critical'
                    },
                    'annotations': {
                        'summary': 'Pod is crash looping',
                        'description': 'Pod {{ $labels.pod }} is restarting frequently'
                    }
                },
                {
                    'alert': 'HighPodMemoryUsage',
                    'expr': 'container_memory_usage_bytes / container_spec_memory_limit_bytes > 0.85',
                    'for': '5m',
                    'labels': {
                        'severity': 'warning'
                    },
                    'annotations': {
                        'summary': 'High memory usage in pod',
                        'description': 'Pod {{ $labels.pod }} is using more than 85% of memory'
                    }
                }
            ]
        }
        
        self.alerts_config['alerts'].append(k8s_alerts)
        logger.info("Kubernetes alerts configured")
    
    def create_alert_config_file(self):
        """Crear archivo de configuración de alertas"""
        config_dir = os.path.join(os.getcwd(), 'monitoring', 'config')
        os.makedirs(config_dir, exist_ok=True)
        
        config_file = os.path.join(config_dir, 'alerts.json')
        with open(config_file, 'w') as f:
            json.dump(self.alerts_config, f, indent=2)
        
        logger.info("Alert configuration file created", file=config_file)
        return config_file
    
    def setup_all_alerts(self):
        """Configurar todas las alertas"""
        logger.info("Setting up all alerts")
        
        self.setup_prometheus_alerts()
        self.setup_slack_alerts()
        self.setup_email_alerts()
        self.setup_health_check_alerts()
        self.setup_kubernetes_alerts()
        
        config_file = self.create_alert_config_file()
        
        logger.info("All alerts configured successfully", 
                   total_alerts=len(self.alerts_config['alerts']))
        
        return self.alerts_config

def main():
    """Función principal"""
    alert_manager = AlertManager()
    alerts_config = alert_manager.setup_all_alerts()
    
    print(json.dumps(alerts_config, indent=2))
    print(f"\n✅ Alertas configuradas: {len(alerts_config['alerts'])} tipos")
    print("📁 Archivo de configuración creado en: monitoring/config/alerts.json")

if __name__ == '__main__':
    main() 