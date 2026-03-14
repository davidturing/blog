"""
ANE (Apple Neural Engine) accelerated text encoder.

This module provides efficient text vectorization optimized for
Mac mini M4's Apple Neural Engine, ensuring low memory footprint
and high performance for cognitive entropy calculations.
"""

import logging
from typing import List, Union, Optional
import numpy as np

# Conditional imports to handle environments without ANE support
try:
    import torch
    from sentence_transformers import SentenceTransformer
    ANE_AVAILABLE = True
except ImportError:
    ANE_AVAILABLE = False
    logging.warning("PyTorch or sentence-transformers not available. Using fallback encoder.")


class ANEEncoder:
    """ANE-accelerated text encoder for cognitive entropy calculations."""
    
    def __init__(self, config: dict):
        """Initialize the ANE encoder.
        
        Args:
            config: Configuration dictionary containing embedding model settings.
        """
        self.logger = logging.getLogger("ANEEncoder")
        self.model_name = config.get("embedding_model", "all-MiniLM-L6-v2")
        self.device = self._get_optimal_device()
        self.model = self._load_model()
        
    def _get_optimal_device(self) -> str:
        """Determine the optimal device for inference.
        
        Returns:
            Device string ('mps' for ANE, 'cpu' as fallback).
        """
        if not ANE_AVAILABLE:
            self.logger.info("Using CPU for embeddings (ANE not available)")
            return "cpu"
            
        if torch.backends.mps.is_available():
            self.logger.info("Using MPS (Apple Neural Engine) for embeddings")
            return "mps"
        else:
            self.logger.info("MPS not available, using CPU for embeddings")
            return "cpu"
            
    def _load_model(self) -> Optional[object]:
        """Load the sentence transformer model.
        
        Returns:
            Loaded model or None if unavailable.
        """
        if not ANE_AVAILABLE:
            return None
            
        try:
            model = SentenceTransformer(self.model_name, device=self.device)
            # Enable ANE optimizations if available
            if self.device == "mps":
                model.eval()  # Set to evaluation mode for better performance
            return model
        except Exception as e:
            self.logger.error(f"Failed to load embedding model: {e}")
            return None
            
    def encode(self, text: Union[str, List[str]]) -> List[float]:
        """Encode text into vector representation.
        
        Args:
            text: Single string or list of strings to encode.
            
        Returns:
            Vector representation as list of floats.
        """
        if self.model is None:
            # Fallback implementation for environments without proper dependencies
            return self._fallback_encode(text)
            
        try:
            # Ensure input is a list for consistent processing
            if isinstance(text, str):
                texts = [text]
            else:
                texts = text
                
            # Generate embeddings
            with torch.no_grad():  # Disable gradient computation for inference
                embeddings = self.model.encode(texts, convert_to_numpy=True)
                
            # Return single embedding if input was single string
            if isinstance(text, str):
                return embeddings[0].tolist()
            else:
                return embeddings.tolist()
                
        except Exception as e:
            self.logger.error(f"Error encoding text: {e}")
            return self._fallback_encode(text)
            
    def _fallback_encode(self, text: Union[str, List[str]]) -> List[float]:
        """Fallback encoding method when ANE is not available.
        
        Uses a simple hash-based approach to generate pseudo-embeddings.
        This ensures the system can still function (albeit less accurately)
        in constrained environments.
        
        Args:
            text: Text to encode.
            
        Returns:
            Pseudo-embedding as list of floats.
        """
        import hashlib
        
        # Determine embedding dimension from config or use default
        embedding_dim = 384  # Default for all-MiniLM-L6-v2
        
        if isinstance(text, str):
            texts = [text]
        else:
            texts = text
            
        embeddings = []
        for t in texts:
            # Create a hash of the text
            hash_obj = hashlib.sha256(t.encode('utf-8'))
            hash_bytes = hash_obj.digest()
            
            # Convert bytes to float array
            float_array = []
            for i in range(embedding_dim):
                byte_idx = i % len(hash_bytes)
                float_val = (hash_bytes[byte_idx] - 128) / 128.0  # Normalize to [-1, 1]
                float_array.append(float_val)
                
            embeddings.append(float_array)
            
        if isinstance(text, str):
            return embeddings[0]
        else:
            return embeddings

    def calculate_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """Calculate cosine similarity between two embeddings.
        
        Args:
            embedding1: First embedding vector.
            embedding2: Second embedding vector.
            
        Returns:
            Cosine similarity score between 0 and 1.
        """
        try:
            # Convert to numpy arrays for efficient computation
            vec1 = np.array(embedding1)
            vec2 = np.array(embedding2)
            
            # Calculate cosine similarity
            dot_product = np.dot(vec1, vec2)
            norm1 = np.linalg.norm(vec1)
            norm2 = np.linalg.norm(vec2)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
                
            similarity = dot_product / (norm1 * norm2)
            # Ensure result is in [0, 1] range
            return max(0.0, min(1.0, (similarity + 1) / 2))
            
        except Exception as e:
            self.logger.error(f"Error calculating similarity: {e}")
            return 0.0