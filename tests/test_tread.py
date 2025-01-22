"""Tests for TREAD functionality"""

import pytest
import torch
from core.tread.token_router import TREADRouter
from core.tread.optimization import TREADOptimizer
from core.modes.enhanced_model import EnhancedModel

def test_token_router_initialization():
    router = TREADRouter()
    assert router is not None
    assert router.config is not None

def test_token_routing():
    router = TREADRouter()
    tokens = ['test', 'medical', 'diagnosis', 'text']
    layer_ids = [0, 1, 2]
    
    routed_tokens = router.route_tokens(tokens, layer_ids)
    
    assert isinstance(routed_tokens, dict)
    assert all(layer_id in routed_tokens for layer_id in layer_ids)
    assert all(isinstance(indices, list) for indices in routed_tokens.values())

def test_medical_term_weighting():
    router = TREADRouter()
    tokens = ['test', 'diagnosis', 'treatment', 'normal']
    importance = router._calculate_token_importance(tokens)
    
    assert importance[1] > importance[0]  # Medical term should have higher importance
    assert importance[2] > importance[3]  # Medical term should have higher importance

@pytest.mark.skipif(not torch.cuda.is_available(), reason="CUDA not available")
def test_enhanced_model():
    model = EnhancedModel()
    text = "Patient shows symptoms of diagnosis"
    
    output = model.process_text(text)
    assert output is not None
    assert isinstance(output, torch.Tensor)

def test_optimization():
    model = EnhancedModel()
    optimizer = TREADOptimizer(model.model)
    
    # Create dummy input
    input_ids = torch.randint(0, 1000, (1, 10))
    attention_mask = torch.ones_like(input_ids)
    
    output = optimizer.optimize_forward_pass(input_ids, attention_mask)
    assert output is not None