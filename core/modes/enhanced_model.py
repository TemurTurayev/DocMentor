"""Enhanced model with TREAD optimization"""

from transformers import AutoTokenizer, AutoModel
from ..tread.optimization import TREADOptimizer

class EnhancedModel:
    def __init__(self, model_name: str = 'distilbert-base-uncased'):
        """Initialize enhanced model with TREAD optimization"""
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModel.from_pretrained(model_name)
        self.optimizer = TREADOptimizer(self.model)

    def process_text(self, text: str):
        """Process text using TREAD optimization"""
        inputs = self.tokenizer(
            text,
            return_tensors='pt',
            padding=True,
            truncation=True
        )

        optimized_output = self.optimizer.optimize_forward_pass(
            inputs['input_ids'],
            attention_mask=inputs['attention_mask']
        )

        return optimized_output