"""
ANE (Apple Neural Engine) 加速的向量化编码器。

该模块利用 Apple Silicon 的神经引擎进行高效的文本向量化，
以满足 Mac mini M4 的低内存和高性能要求。
"""

import logging
from typing import List, Union, Dict, Any
import numpy as np

# Try to import Core ML for ANE acceleration
try:
    import coremltools as ct
    from transformers import AutoTokenizer, AutoModel
    ANE_AVAILABLE = True
except ImportError:
    ANE_AVAILABLE = False
    logging.warning("Core ML or Transformers not available, falling back to CPU")

# Fallback to sentence-transformers if ANE is not available
if not ANE_AVAILABLE:
    try:
        from sentence_transformers import SentenceTransformer
    except ImportError:
        raise ImportError("Either Core ML + Transformers OR sentence-transformers must be installed")


class ANEEncoder:
    """ANE 加速的文本向量化编码器。"""

    def __init__(self, config: Dict[str, Any]):
        """初始化 ANE 编码器。
        
        Args:
            config: 配置字典，包含 embedding_model 等参数。
        """
        self.logger = logging.getLogger("ANEEncoder")
        self.config = config
        self.model_name = config.get("embedding_model", "all-MiniLM-L6-v2")
        self.use_ane = config.get("use_ane", True) and ANE_AVAILABLE
        
        if self.use_ane:
            self.logger.info(f"Initializing ANE-accelerated encoder with model: {self.model_name}")
            self._init_ane_model()
        else:
            self.logger.info(f"Initializing CPU-based encoder with model: {self.model_name}")
            self._init_cpu_model()

    def _init_ane_model(self):
        """初始化 ANE 模型（使用 Core ML）。"""
        try:
            # Load the Hugging Face model
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            hf_model = AutoModel.from_pretrained(self.model_name)
            
            # Convert to Core ML format
            # This is a simplified version - in practice, you'd need to handle the specific model architecture
            self.coreml_model = ct.convert(
                hf_model,
                inputs=[ct.TensorType(name="input_ids", shape=(1, 128))],
                convert_to="mlprogram"
            )
            
            self.logger.info("Successfully initialized ANE model")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize ANE model: {e}")
            self.logger.info("Falling back to CPU model")
            self.use_ane = False
            self._init_cpu_model()

    def _init_cpu_model(self):
        """初始化 CPU 模型（使用 sentence-transformers）。"""
        try:
            self.cpu_model = SentenceTransformer(self.model_name)
            self.logger.info("Successfully initialized CPU model")
        except Exception as e:
            raise RuntimeError(f"Failed to initialize CPU model: {e}")

    def encode(self, text: Union[str, List[str]]) -> List[float]:
        """对文本进行向量化编码。
        
        Args:
            text: 要编码的文本或文本列表。
            
        Returns:
            文本的向量表示。
        """
        if isinstance(text, list):
            if len(text) == 0:
                return []
            # For simplicity, we'll just encode the first item
            text = text[0]
            
        if not isinstance(text, str):
            text = str(text)
            
        if len(text.strip()) == 0:
            # Return zero vector for empty text
            return [0.0] * self._get_embedding_dim()
            
        try:
            if self.use_ane:
                return self._encode_with_ane(text)
            else:
                return self._encode_with_cpu(text)
                
        except Exception as e:
            self.logger.error(f"Error encoding text: {e}")
            # Return zero vector as fallback
            return [0.0] * self._get_embedding_dim()

    def _encode_with_ane(self, text: str) -> List[float]:
        """使用 ANE 对文本进行编码。
        
        Args:
            text: 要编码的文本。
            
        Returns:
            文本的向量表示。
        """
        # Tokenize the input
        inputs = self.tokenizer(
            text,
            return_tensors="np",
            padding="max_length",
            truncation=True,
            max_length=128
        )
        
        # Run inference on Core ML model
        outputs = self.coreml_model.predict({
            "input_ids": inputs["input_ids"],
            "attention_mask": inputs["attention_mask"]
        })
        
        # Extract the embedding (this depends on the specific model architecture)
        # For sentence-transformers models, we typically take the mean of the last hidden state
        if "last_hidden_state" in outputs:
            embedding = np.mean(outputs["last_hidden_state"], axis=1)
        else:
            # Fallback to the first output
            embedding = list(outputs.values())[0]
            if len(embedding.shape) > 1:
                embedding = np.mean(embedding, axis=0)
                
        return embedding.flatten().tolist()

    def _encode_with_cpu(self, text: str) -> List[float]:
        """使用 CPU 对文本进行编码。
        
        Args:
            text: 要编码的文本。
            
        Returns:
            文本的向量表示。
        """
        embedding = self.cpu_model.encode(text)
        return embedding.tolist()

    def _get_embedding_dim(self) -> int:
        """获取嵌入维度。
        
        Returns:
            嵌入向量的维度。
        """
        if self.use_ane:
            # For all-MiniLM-L6-v2, the dimension is 384
            return 384
        else:
            return self.cpu_model.get_sentence_embedding_dimension()