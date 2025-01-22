"""TREAD optimization implementation"""

import torch
from typing import Dict, List, Union
from .token_router import TREADRouter
from .config import TREAD_CONFIG

class TREADOptimizer:
    def __init__(self, model):
        """Initialize TREAD optimizer with model"""
        self.model = model
        self.router = TREADRouter(TREAD_CONFIG)
        self.layer_mapping = self._create_layer_mapping()

    def _create_layer_mapping(self) -> Dict[str, int]:
        """Create mapping between layer names and indices"""
        mapping = {}
        for idx, (name, _) in enumerate(self.model.named_modules()):
            if 'layer' in name and 'attention' in name:
                mapping[name] = idx
        return mapping

    def optimize_forward_pass(
        self, 
        input_ids: torch.Tensor,
        attention_mask: torch.Tensor = None,
    ) -> torch.Tensor:
        """Optimize forward pass through the model using token routing"""
        if not TREAD_CONFIG['optimize_layers']:
            return self.model(input_ids, attention_mask=attention_mask)

        batch_size = input_ids.size(0)
        hidden_states = self.model.embeddings(input_ids)

        for layer_name, layer_idx in self.layer_mapping.items():
            layer = self._get_layer(layer_name)
            routed_tokens = self.router.route_tokens(
                hidden_states.mean(dim=-1),
                [layer_idx]
            )

            # Create routing mask
            routing_mask = torch.zeros_like(attention_mask)
            routing_mask[:, routed_tokens[layer_idx]] = 1

            # Apply attention only to routed tokens
            hidden_states = self._optimized_layer_forward(
                layer,
                hidden_states,
                routing_mask
            )

        return self.model.head(hidden_states)

    def _optimized_layer_forward(
        self,
        layer,
        hidden_states: torch.Tensor,
        routing_mask: torch.Tensor
    ) -> torch.Tensor:
        """Optimized forward pass for a single layer"""
        # Apply attention only where routing_mask is 1
        attention_mask = routing_mask.unsqueeze(1).unsqueeze(2)
        attention_output = layer.attention(
            hidden_states,
            attention_mask=attention_mask
        )[0]

        # Only process necessary tokens
        active_tokens = routing_mask.bool()
        hidden_states[active_tokens] = layer.output(
            attention_output[active_tokens],
            hidden_states[active_tokens]
        )

        return hidden_states

    def _get_layer(self, layer_name: str):
        """Get layer by name from model"""
        for name, module in self.model.named_modules():
            if name == layer_name:
                return module
        raise ValueError(f"Layer {layer_name} not found")