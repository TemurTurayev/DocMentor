"""Token routing implementation for TREAD"""

import torch
from typing import Dict, List, Union
from .config import TREAD_CONFIG

class TREADRouter:
    def __init__(self, model_config: Dict = None):
        """Initialize TREAD router with optional model configuration"""
        self.config = model_config or TREAD_CONFIG
        self.routing_cache = {}
        self.medical_terms = self._load_medical_terms()

    def _load_medical_terms(self) -> set:
        """Load medical terms for specialized weighting"""
        # TODO: Load from medical terminology database
        return set(['diagnosis', 'treatment', 'patient', 'symptoms'])
    
    def route_tokens(
        self, 
        tokens: Union[List[str], torch.Tensor],
        layer_ids: List[int]
    ) -> Dict[int, List[int]]:
        """Route tokens to appropriate layers based on importance"""
        cache_key = self._get_cache_key(tokens)
        if cache_key in self.routing_cache:
            return self.routing_cache[cache_key]

        token_importance = self._calculate_token_importance(tokens)
        routed_tokens = {}

        for layer_id in layer_ids:
            threshold = self._get_layer_threshold(layer_id)
            important_indices = self._select_important_tokens(
                token_importance, 
                threshold
            )
            routed_tokens[layer_id] = important_indices

        if self.config['cache_routing']:
            self.routing_cache[cache_key] = routed_tokens

        return routed_tokens

    def _calculate_token_importance(
        self, 
        tokens: Union[List[str], torch.Tensor]
    ) -> torch.Tensor:
        """Calculate importance scores for tokens"""
        if isinstance(tokens, list):
            importance = torch.zeros(len(tokens))
            for i, token in enumerate(tokens):
                # Apply medical domain weighting
                if token.lower() in self.medical_terms:
                    importance[i] = self.config['medical_terms_weight']
                else:
                    importance[i] = 1.0
            return importance
        return tokens.float().mean(dim=-1)  # For tensor inputs

    def _select_important_tokens(
        self, 
        importance: torch.Tensor,
        threshold: float
    ) -> List[int]:
        """Select tokens above importance threshold"""
        min_tokens = int(len(importance) * self.config['min_tokens_per_layer'])
        indices = torch.where(importance >= threshold)[0].tolist()
        
        if len(indices) < min_tokens:
            # Ensure minimum token count
            _, top_indices = torch.topk(importance, min_tokens)
            indices = top_indices.tolist()
        
        return indices

    def _get_layer_threshold(self, layer_id: int) -> float:
        """Get threshold for specific layer"""
        # Lower layers need more tokens for basic understanding
        return self.config['routing_threshold'] * (1 + 0.1 * layer_id)

    def _get_cache_key(self, tokens) -> str:
        """Generate cache key for token sequence"""
        if isinstance(tokens, list):
            return ','.join(tokens)
        return tokens.sum().item()  # Simple hash for tensor