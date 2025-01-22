import psutil
import time
from dataclasses import dataclass
from typing import Dict, List
import logging

@dataclass
class PerformanceMetrics:
    memory_usage: float
    cpu_usage: float
    tokens_per_second: float
    batch_processing_time: float
    optimization_ratio: float

class TREADMonitor:
    def __init__(self):
        self.logger = logging.getLogger('tread_monitor')
        self.start_time = time.time()
        self.metrics = []
        self._setup_logging()

    def _setup_logging(self):
        handler = logging.FileHandler('logs/tread_performance.log')
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)

    def start_tracking(self):
        """Start tracking performance metrics"""
        self.start_time = time.time()
        self.initial_memory = psutil.Process().memory_info().rss / 1024 / 1024
        self.logger.info(f"Started tracking at {self.start_time}")

    def log_metrics(self, processed_tokens: int, batch_size: int):
        """Log current performance metrics"""
        current_time = time.time()
        elapsed_time = current_time - self.start_time
        
        current_memory = psutil.Process().memory_info().rss / 1024 / 1024
        memory_diff = current_memory - self.initial_memory
        
        metrics = PerformanceMetrics(
            memory_usage=current_memory,
            cpu_usage=psutil.cpu_percent(),
            tokens_per_second=processed_tokens / elapsed_time,
            batch_processing_time=elapsed_time / (processed_tokens / batch_size),
            optimization_ratio=processed_tokens / (memory_diff + 1)
        )
        
        self.metrics.append(metrics)
        self._log_metrics(metrics)

    def _log_metrics(self, metrics: PerformanceMetrics):
        """Log metrics to file"""
        self.logger.info(
            f"Memory: {metrics.memory_usage:.2f}MB | "
            f"CPU: {metrics.cpu_usage:.1f}% | "
            f"Speed: {metrics.tokens_per_second:.1f} tokens/s | "
            f"Batch time: {metrics.batch_processing_time:.3f}s | "
            f"Optimization: {metrics.optimization_ratio:.2f}"
        )

    def get_performance_stats(self) -> Dict:
        """Get current performance statistics"""
        if not self.metrics:
            return {}

        latest = self.metrics[-1]
        return {
            'memory_usage': latest.memory_usage,
            'cpu_usage': latest.cpu_usage,
            'tokens_per_second': latest.tokens_per_second,
            'batch_processing_time': latest.batch_processing_time,
            'optimization_ratio': latest.optimization_ratio
        }

    def generate_report(self) -> str:
        """Generate a detailed performance report"""
        stats = self.get_performance_stats()
        if not stats:
            return "No metrics available"

        report = [
            "TREAD Performance Report",
            "=======================",
            f"Memory Usage: {stats['memory_usage']:.2f}MB",
            f"CPU Usage: {stats['cpu_usage']:.1f}%",
            f"Processing Speed: {stats['tokens_per_second']:.1f} tokens/s",
            f"Batch Processing Time: {stats['batch_processing_time']:.3f}s",
            f"Optimization Ratio: {stats['optimization_ratio']:.2f}",
            "",
            "Performance Analysis:",
            "-------------------"
        ]

        # Add analysis
        if stats['memory_usage'] > 1000:
            report.append("⚠️ High memory usage detected")
        if stats['tokens_per_second'] < 100:
            report.append("⚠️ Processing speed below optimal")

        return '\n'.join(report)
