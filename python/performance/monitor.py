import psutil
import time
import json
from prometheus_client import start_http_server, Gauge
from typing import Dict, Any
from datetime import datetime

class PerformanceMonitor:
    """Real-time performance monitoring system"""
    
    def __init__(self, port: int = 8000):
        self.port = port
        self.metrics = {}
        self.setup_prometheus_metrics()
    
    def setup_prometheus_metrics(self):
        """Setup Prometheus metrics"""
        self.cpu_usage = Gauge('cpu_usage_percent', 'CPU Usage Percentage')
        self.memory_usage = Gauge('memory_usage_percent', 'Memory Usage Percentage')
        self.disk_usage = Gauge('disk_usage_percent', 'Disk Usage Percentage')
        self.network_sent = Gauge('network_sent_bytes', 'Network Bytes Sent')
        self.network_recv = Gauge('network_recv_bytes', 'Network Bytes Received')
    
    def collect_system_metrics(self) -> Dict[str, Any]:
        """Collect system performance metrics"""
        try:
            # CPU metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            cpu_freq = psutil.cpu_freq()
            
            # Memory metrics
            memory = psutil.virtual_memory()
            swap = psutil.swap_memory()
            
            # Disk metrics
            disk = psutil.disk_usage('/')
            disk_io = psutil.disk_io_counters()
            
            # Network metrics
            network = psutil.net_io_counters()
            
            # Process metrics
            process = psutil.Process()
            process_cpu = process.cpu_percent()
            process_memory = process.memory_info()
            
            metrics = {
                'timestamp': datetime.now().isoformat(),
                'system': {
                    'cpu': {
                        'percent': cpu_percent,
                        'count': cpu_count,
                        'frequency': cpu_freq.current if cpu_freq else 0
                    },
                    'memory': {
                        'total': memory.total,
                        'available': memory.available,
                        'percent': memory.percent,
                        'used': memory.used,
                        'swap_percent': swap.percent,
                        'swap_used': swap.used
                    },
                    'disk': {
                        'total': disk.total,
                        'used': disk.used,
                        'free': disk.free,
                        'percent': disk.percent
                    },
                    'network': {
                        'bytes_sent': network.bytes_sent,
                        'bytes_recv': network.bytes_recv,
                        'packets_sent': network.packets_sent,
                        'packets_recv': network.packets_recv
                    }
                },
                'process': {
                    'cpu_percent': process_cpu,
                    'memory_rss': process_memory.rss,
                    'memory_vms': process_memory.vms
                }
            }
            
            if disk_io:
                metrics['system']['disk_io'] = {
                    'read_bytes': disk_io.read_bytes,
                    'write_bytes': disk_io.write_bytes,
                    'read_count': disk_io.read_count,
                    'write_count': disk_io.write_count
                }
            
            return metrics
            
        except Exception as e:
            print(f"Metrics collection failed: {e}")
            return {}
    
    def update_prometheus_metrics(self, metrics: Dict[str, Any]):
        """Update Prometheus metrics"""
        try:
            if 'system' in metrics:
                system = metrics['system']
                
                # Update CPU metrics
                if 'cpu' in system:
                    self.cpu_usage.set(system['cpu']['percent'])
                
                # Update memory metrics
                if 'memory' in system:
                    self.memory_usage.set(system['memory']['percent'])
                
                # Update disk metrics
                if 'disk' in system:
                    self.disk_usage.set(system['disk']['percent'])
                
                # Update network metrics
                if 'network' in system:
                    self.network_sent.set(system['network']['bytes_sent'])
                    self.network_recv.set(system['network']['bytes_recv'])
                    
        except Exception as e:
            print(f"Prometheus metrics update failed: {e}")
    
    def start_monitoring(self, interval: int = 30):
        """Start continuous monitoring"""
        print(f"Starting performance monitoring on port {self.port}")
        start_http_server(self.port)
        
        try:
            while True:
                metrics = self.collect_system_metrics()
                if metrics:
                    self.update_prometheus_metrics(metrics)
                    self.log_metrics(metrics)
                time.sleep(interval)
                
        except KeyboardInterrupt:
            print("Monitoring stopped by user")
        except Exception as e:
            print(f"Monitoring error: {e}")
    
    def log_metrics(self, metrics: Dict[str, Any]):
        """Log metrics to console"""
        try:
            timestamp = metrics.get('timestamp', 'N/A')
            cpu_percent = metrics.get('system', {}).get('cpu', {}).get('percent', 0)
            memory_percent = metrics.get('system', {}).get('memory', {}).get('percent', 0)
            disk_percent = metrics.get('system', {}).get('disk', {}).get('percent', 0)
            
            print(f"[{timestamp}] CPU: {cpu_percent:.1f}% | Memory: {memory_percent:.1f}% | Disk: {disk_percent:.1f}%")
            
        except Exception as e:
            print(f"Metrics logging failed: {e}")
    
    def get_current_metrics(self) -> Dict[str, Any]:
        """Get current metrics without starting monitoring"""
        return self.collect_system_metrics()
    
    def save_metrics_to_file(self, metrics: Dict[str, Any], filename: str):
        """Save metrics to JSON file"""
        try:
            with open(filename, 'w') as f:
                json.dump(metrics, f, indent=2)
            return True
        except Exception as e:
            print(f"Failed to save metrics: {e}")
            return False