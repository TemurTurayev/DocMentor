"""Configuration for TREAD (Token Routing for Efficient Architecture-agnostic Diffusion)"""

TREAD_CONFIG = {
    # Routing configuration
    'routing_threshold': 0.5,      # Threshold for token importance
    'cache_size': 1000,           # Size of routing cache
    'min_tokens_per_layer': 0.3,  # Minimum fraction of tokens to keep per layer
    
    # Optimization settings
    'optimize_layers': True,      # Enable layer optimization
    'dynamic_routing': True,      # Enable dynamic token routing
    'cache_routing': True,        # Enable routing cache
    
    # Performance settings
    'batch_size': 32,            # Batch size for token processing
    'num_workers': 4,            # Number of workers for parallel processing
    
    # Medical domain specific settings
    'medical_terms_weight': 1.5,  # Weight multiplier for medical terms
    'preserve_medical_context': True,  # Ensure medical context is preserved
}