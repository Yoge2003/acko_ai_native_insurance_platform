"""
System resource telemetry collector utilizing psutil metrics.
"""

import os
import psutil
from typing import Dict, Any


class ResourceMonitor:
    """
    Utility module to read CPU, Memory, and Disk usage metrics.
    """
    
    @staticmethod
    def get_cpu_metrics() -> Dict[str, Any]:
        """Returns CPU usage details, load, log/physics core counts."""
        try:
            percent = psutil.cpu_percent(interval=0.1)
            cores_physical = psutil.cpu_count(logical=False)
            cores_logical = psutil.cpu_count(logical=True)
            freq = psutil.cpu_freq()
            freq_val = freq.current if freq else 0.0
        except Exception:
            percent = 0.0
            cores_physical = 1
            cores_logical = 1
            freq_val = 0.0
            
        return {
            "percent": percent,
            "cores_physical": cores_physical,
            "cores_logical": cores_logical,
            "frequency_mhz": freq_val
        }

    @staticmethod
    def get_memory_metrics() -> Dict[str, Any]:
        """Returns memory usage in Gigabytes and percentage."""
        try:
            mem = psutil.virtual_memory()
            total = round(mem.total / (1024 ** 3), 2)
            available = round(mem.available / (1024 ** 3), 2)
            used = round(mem.used / (1024 ** 3), 2)
            percent = mem.percent
        except Exception:
            total = 0.0
            available = 0.0
            used = 0.0
            percent = 0.0
            
        return {
            "total_gb": total,
            "available_gb": available,
            "used_gb": used,
            "percent": percent
        }

    @staticmethod
    def get_disk_metrics() -> Dict[str, Any]:
        """Returns disk space usage statistics for the current workspace path."""
        try:
            path = os.getcwd()
            usage = psutil.disk_usage(path)
            total = round(usage.total / (1024 ** 3), 2)
            used = round(usage.used / (1024 ** 3), 2)
            free = round(usage.free / (1024 ** 3), 2)
            percent = usage.percent
        except Exception:
            total = 0.0
            used = 0.0
            free = 0.0
            percent = 0.0
            
        return {
            "total_gb": total,
            "used_gb": used,
            "free_gb": free,
            "percent": percent
        }

    @staticmethod
    def get_all_resources() -> Dict[str, Any]:
        """Consolidates all resource usage statistics."""
        return {
            "cpu": ResourceMonitor.get_cpu_metrics(),
            "memory": ResourceMonitor.get_memory_metrics(),
            "disk": ResourceMonitor.get_disk_metrics()
        }
