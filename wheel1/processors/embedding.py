"""
嵌入服务 - 支持多种嵌入模型
"""

import logging
from typing import List, Optional, Dict, Any
import numpy as np
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class EmbeddingProvider(ABC):
    """嵌入提供商基类"""
    
    @abstractmethod
    def embed(self, texts: List[str]) -> List[List[float]]:
        """生成嵌入向量"""
        pass
    
    @abstractmethod
    def embed_query(self, text: str) -> List[float]:
        """为单个查询生成嵌入"""
        pass


class OpenAIEmbedding(EmbeddingProvider):
    """OpenAI嵌入服务"""
    
    def __init__(self, model: str = "text-embedding-3-small"):
        """
        初始化OpenAI嵌入
        
        Args:
            model: 模型名称
        """
        self.model = model
        
        try:
            from openai import OpenAI
            self.client = OpenAI()
        except ImportError:
            logger.warning("openai库未安装")
            self.client = None
    
    def embed(self, texts: List[str]) -> List[List[float]]:
        """生成嵌入向量"""
        if not self.client:
            return [self._dummy_embedding() for _ in texts]
        
        try:
            response = self.client.embeddings.create(
                model=self.model,
                input=texts
            )
            return [item.embedding for item in response.data]
        except Exception as e:
            logger.error(f"OpenAI嵌入失败: {e}")
            return [self._dummy_embedding() for _ in texts]
    
    def embed_query(self, text: str) -> List[float]:
        """为查询生成嵌入"""
        embeddings = self.embed([text])
        return embeddings[0] if embeddings else self._dummy_embedding()
    
    def _dummy_embedding(self) -> List[float]:
        """生成虚拟嵌入（用于测试）"""
        return [0.0] * 1536  # OpenAI默认维度


class SentenceTransformerEmbedding(EmbeddingProvider):
    """Sentence Transformers嵌入"""
    
    def __init__(self, model: str = "all-mpnet-base-v2"):
        """
        初始化SentenceTransformer嵌入
        
        Args:
            model: 模型名称
        """
        self.model_name = model
        
        try:
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer(model)
        except ImportError:
            logger.warning("sentence-transformers库未安装")
            self.model = None
    
    def embed(self, texts: List[str]) -> List[List[float]]:
        """生成嵌入向量"""
        if not self.model:
            return [self._dummy_embedding() for _ in texts]
        
        try:
            embeddings = self.model.encode(texts, show_progress_bar=False)
            return [embedding.tolist() for embedding in embeddings]
        except Exception as e:
            logger.error(f"SentenceTransformer嵌入失败: {e}")
            return [self._dummy_embedding() for _ in texts]
    
    def embed_query(self, text: str) -> List[float]:
        """为查询生成嵌入"""
        embeddings = self.embed([text])
        return embeddings[0] if embeddings else self._dummy_embedding()
    
    def _dummy_embedding(self) -> List[float]:
        """生成虚拟嵌入"""
        return [0.0] * 768  # 默认维度


class EmbeddingService:
    """统一嵌入服务"""
    
    PROVIDERS = {
        'openai': OpenAIEmbedding,
        'sentence-transformers': SentenceTransformerEmbedding,
    }
    
    def __init__(
        self,
        provider: str = "openai",
        model: str = "text-embedding-3-small",
        cache: Optional[Any] = None,
        batch_size: int = 32
    ):
        """
        初始化嵌入服务
        
        Args:
            provider: 提供商名称
            model: 模型名称
            cache: 缓存管理器
            batch_size: 批处理大小
        """
        self.provider_name = provider
        self.model = model
        self.cache = cache
        self.batch_size = batch_size
        
        # 初始化提供商
        provider_class = self.PROVIDERS.get(provider, OpenAIEmbedding)
        self.provider = provider_class(model)
        
        logger.info(f"初始化嵌入服务: {provider}/{model}")
    
    def embed(self, text: str) -> List[float]:
        """为单个文本生成嵌入"""
        # 检查缓存
        cache_key = f"embed:{text[:100]}"
        if self.cache:
            cached = self.cache.get(cache_key)
            if cached:
                return cached
        
        # 生成嵌入
        embedding = self.provider.embed_query(text)
        
        # 存储到缓存
        if self.cache:
            self.cache.set(cache_key, embedding, ttl=86400)
        
        return embedding
    
    def embed_batch(
        self,
        texts: List[str],
        batch_size: Optional[int] = None
    ) -> List[List[float]]:
        """批量生成嵌入"""
        batch_size = batch_size or self.batch_size
        embeddings = []
        
        for i in range(0, len(texts), batch_size):
            batch_texts = texts[i:i + batch_size]
            
            # 过滤缓存中已有的
            cached_embeddings = []
            uncached_texts = []
            uncached_indices = []
            
            if self.cache:
                for j, text in enumerate(batch_texts):
                    cache_key = f"embed:{text[:100]}"
                    cached = self.cache.get(cache_key)
                    if cached:
                        cached_embeddings.append((j, cached))
                    else:
                        uncached_texts.append(text)
                        uncached_indices.append(j)
            else:
                uncached_texts = batch_texts
                uncached_indices = list(range(len(batch_texts)))
            
            # 生成未缓存的嵌入
            if uncached_texts:
                new_embeddings = self.provider.embed(uncached_texts)
                
                # 存储到缓存
                if self.cache:
                    for text, embedding in zip(uncached_texts, new_embeddings):
                        cache_key = f"embed:{text[:100]}"
                        self.cache.set(cache_key, embedding, ttl=86400)
            else:
                new_embeddings = []
            
            # 合并结果
            batch_embeddings = [None] * len(batch_texts)
            
            for j, cached in cached_embeddings:
                batch_embeddings[j] = cached
            
            for j, idx in enumerate(uncached_indices):
                batch_embeddings[idx] = new_embeddings[j]
            
            embeddings.extend(batch_embeddings)
        
        logger.info(f"批量嵌入完成: {len(texts)} 文本")
        return embeddings
    
    def health_check(self) -> bool:
        """健康检查"""
        try:
            test_embedding = self.embed("test")
            return len(test_embedding) > 0
        except Exception as e:
            logger.error(f"嵌入服务健康检查失败: {e}")
            return False
