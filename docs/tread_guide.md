# TREAD Integration Guide for DocMentor

## Overview
This guide explains how to effectively use and configure TREAD optimization in DocMentor.

## Configuration

### Basic Setup
```yaml
# config/tread_config.yaml
general:
  enabled: true
  cache_size: 1000
```

### Advanced Configuration
```python
from core.tread.config import TREADConfig

config = TREADConfig(
    medical_term_weight=1.5,
    cache_size=2000,
    batch_size=64
)
```

## Usage Examples

### Basic Usage
```python
from core.modes.enhanced_model import EnhancedModel

# Initialize model with TREAD optimization
model = EnhancedModel()

# Process medical text
result = model.process_text("""
Patient presents with acute myocardial infarction.
Vital signs: BP 140/90, HR 95, RR 18
""")
```

### Custom Processing
```python
from core.tread.medical_processor import MedicalTermProcessor

processor = MedicalTermProcessor()

# Process with custom settings
result = processor.optimize_medical_content(
    text,
    enhance_terminology=True,
    preserve_context=True
)
```

## Performance Monitoring

### Memory Usage
```python
from core.tread.monitoring import TREADMonitor

monitor = TREADMonitor()
stats = monitor.get_performance_stats()
print(f"Memory usage: {stats['memory_usage']}MB")
print(f"Processing speed: {stats['tokens_per_second']} tokens/s")
```

### Optimization Statistics
```python
from core.tread.analytics import TREADAnalytics

analytics = TREADAnalytics()
report = analytics.generate_optimization_report()
```

## Best Practices

1. Memory Management
   - Keep batch sizes reasonable (32-64)
   - Enable caching for repeated operations
   - Monitor memory usage with TREADMonitor

2. Medical Term Processing
   - Use predefined medical term lists
   - Enable context preservation
   - Configure term weights appropriately

3. Performance Optimization
   - Enable GPU acceleration when available
   - Use fp16 for larger batches
   - Adjust routing threshold based on needs

## Troubleshooting

### Common Issues

1. High Memory Usage
```python
# Reduce memory usage
config.performance.optimize_memory = True
config.performance.batch_size = 16
```

2. Slow Processing
```python
# Enable performance optimizations
config.performance.use_fp16 = True
config.performance.gpu_acceleration = True
```

3. Poor Recognition
```python
# Improve medical term recognition
config.medical.enhance_terminology = True
config.routing.medical_term_weight = 2.0
```

## Advanced Features

### Custom Token Routing
```python
from core.tread.router import CustomTokenRouter

router = CustomTokenRouter()
router.add_custom_pattern(
    name="lab_values",
    pattern=r"\d+(?:\.\d+)?\s*(?:mg/dL|mmol/L)"
)
```

### Extended Monitoring
```python
from core.tread.monitoring import ExtendedMonitor

monitor = ExtendedMonitor()
monitor.start_tracking()

# Your processing code here

results = monitor.get_detailed_stats()
```

## Integration Examples

### With PDF Processor
```python
from core.tread.pdf import TREADPDFProcessor

pdf_processor = TREADPDFProcessor()
result = pdf_processor.process_medical_pdf(
    "document.pdf",
    enhance_tables=True,
    preserve_layout=True
)
```

### With Vector Store
```python
from core.tread.vector_store import TREADVectorStore

vector_store = TREADVectorStore()
vector_store.add_document(
    document,
    optimize_embeddings=True
)
```

## Feedback and Optimization

### Performance Logging
```python
from core.tread.logging import TREADLogger

logger = TREADLogger()
logger.start_session()

# Your code here

logger.end_session()
metrics = logger.get_session_metrics()
```

### Optimization Suggestions
```python
from core.tread.optimizer import TREADOptimizer

optimizer = TREADOptimizer()
suggestions = optimizer.analyze_performance()
for suggestion in suggestions:
    print(f"Suggestion: {suggestion.description}")
    print(f"Expected improvement: {suggestion.impact}%")
```