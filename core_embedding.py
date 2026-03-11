"""
DavidAgent 核心 Embedding 引擎 (Real Vectors, No Fake)
基于 sentence-transformers 提取高维真实语义空间。
"""

import os
import numpy as np

# Lazy load to avoid slowing down imports if not actively embedding
_model = None

def _get_model():
    global _model
    if _model is None:
        try:
            from sentence_transformers import SentenceTransformer
            print("🚀 [Embedding Engine] Loading real dense embedding model (all-MiniLM-L6-v2)...")
            # Using a lightweight, widely standard embedding model for semantic spaces
            _model = SentenceTransformer('all-MiniLM-L6-v2')
        except ImportError:
            raise ImportError("sentence-transformers not installed. Cannot use real vectors.")
    return _model

def get_embedding(text: str) -> np.ndarray:
    """
    将文本转换为真实的稠密向量 (默认 384 维)。
    :param text: 输入文本 (状态、前置条件、效果)
    :return: numpy.ndarray
    """
    if not text or not isinstance(text, str):
        text = str(text) if text else "empty"
    
    model = _get_model()
    # encode() returns a numpy array
    return model.encode(text, convert_to_numpy=True)
