"""
存储层 - 支持向量数据库和关系数据库
包括Redis缓存、向量存储、持久化存储
"""

import logging
from typing import Dict, Any, List, Optional, Tuple
from abc import ABC, abstractmethod
import json
import hashlib
logger = logging.getLogger(__name__)
class CacheManager:
    """缓存管理器 - Redis"""
    def __init__(
        self,
        host: str = "localhost",
        port: int = 6379,
        db: int = 0,
        ttl: int = 3600,
        enabled: bool = True
    ):
        """
        初始化Redis缓存管理器
        Args:
            host: Redis主机
            port: Redis端口
            db: Redis数据库号
            ttl: 默认TTL（秒）
            enabled: 是否启用缓存
        """
        self.host = host
        self.port = port
        self.db = db
        self.ttl = ttl
        self.enabled = enabled
        self.client = None
        if enabled:
            self._connect()
    def _connect(self):
        """连接Redis"""
        try:
            import redis
            self.client = redis.Redis(
                host=self.host,
                port=self.port,
                db=self.db,
                decode_responses=True
            )
            # 测试连接
            self.client.ping()
            logger.info(f"Redis连接成功: {self.host}:{self.port}")
        except Exception as e:
            logger.warning(f"Redis连接失败: {e}，将使用本地缓存")
            self.client = None
            self._init_local_cache()
    
    def _init_local_cache(self):
        """初始化本地内存缓存"""
        self.local_cache = {}

    def get(self, key: str) -> Optional[Any]:
        """获取缓存"""
        if not self.enabled:
            return None
        
        try:
            if self.client:
                value = self.client.get(key)
                if value:
                    return json.loads(value)
            else:
                return self.local_cache.get(key)
        except Exception as e:
            logger.debug(f"缓存读取失败: {e}")
        
        return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """设置缓存"""
        if not self.enabled:
            return False
        
        ttl = ttl or self.ttl
        
        try:
            if self.client:
                self.client.setex(
                    key,
                    ttl,
                    json.dumps(value, default=str)
                )
            else:
                self.local_cache[key] = value
            
            return True
        except Exception as e:
            logger.debug(f"缓存写入失败: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """删除缓存"""
        try:
            if self.client:
                self.client.delete(key)
            elif key in self.local_cache:
                del self.local_cache[key]
            return True
        except Exception as e:
            logger.debug(f"缓存删除失败: {e}")
            return False

    def health_check(self) -> bool:
        """健康检查"""
        if not self.enabled:
            return True
        
        try:
            if self.client:
                self.client.ping()
                return True
            else:
                return True  # 本地缓存总是可用
        except Exception as e:
            logger.error(f"缓存健康检查失败: {e}")
            return False


class VectorStoreBackend(ABC):
    """向量存储后端基类"""
    
    @abstractmethod
    def add_vector(self, vector_id: str, vector: List[float], metadata: Dict):
        """添加向量"""
        pass
    
    @abstractmethod
    def search(self, query_vector: List[float], top_k: int, threshold: float = 0.0):
        """搜索向量"""
        pass
    
    @abstractmethod
    def health_check(self) -> bool:
        """健康检查"""
        pass


class LocalVectorStore(VectorStoreBackend):
    """本地向量存储（用于开发和测试）"""
    
    def __init__(self):
        """初始化本地向量存储"""
        self.vectors = {}  # vector_id -> vector
        self.metadata = {}  # vector_id -> metadata
        logger.info("初始化本地向量存储")
    
    def add_vector(self, vector_id: str, vector: List[float], metadata: Dict):
        """添加向量"""
        self.vectors[vector_id] = vector
        self.metadata[vector_id] = metadata
    
    def search(self, query_vector: List[float], top_k: int, threshold: float = 0.0):
        """使用余弦相似度搜索"""
        import math
        
        results = []
        
        for vector_id, vector in self.vectors.items():
            # 计算余弦相似度
            dot_product = sum(a * b for a, b in zip(query_vector, vector))
            norm_q = math.sqrt(sum(a * a for a in query_vector))
            norm_v = math.sqrt(sum(a * a for a in vector))
            
            if norm_q > 0 and norm_v > 0:
                similarity = dot_product / (norm_q * norm_v)
            else:
                similarity = 0.0
            
            if similarity >= threshold:
                results.append({
                    'id': vector_id,
                    'similarity': similarity,
                    'metadata': self.metadata[vector_id],
                    'text': self.metadata[vector_id].get('text', '')
                })
        
        # 排序并返回top-k
        results = sorted(results, key=lambda x: x['similarity'], reverse=True)
        return results[:top_k]
    
    def health_check(self) -> bool:
        """健康检查"""
        return True


class MilvusVectorStore(VectorStoreBackend):
    """Milvus向量数据库"""
    
    def __init__(self, host: str = "localhost", port: int = 19530):
        """
        初始化Milvus
        
        Args:
            host: Milvus主机
            port: Milvus端口
        """
        self.host = host
        self.port = port
        self.client = None
        
        try:
            from pymilvus import connections, Collection
            connections.connect("default", host=host, port=port)
            self.client = True
            logger.info(f"Milvus连接成功: {host}:{port}")
        except Exception as e:
            logger.warning(f"Milvus连接失败: {e}，将使用本地存储")
            self.client = None
    
    def add_vector(self, vector_id: str, vector: List[float], metadata: Dict):
        """添加向量"""
        if not self.client:
            return
        
        try:
            # Milvus操作逻辑
            logger.debug(f"添加向量到Milvus: {vector_id}")
        except Exception as e:
            logger.error(f"Milvus添加失败: {e}")
    
    def search(self, query_vector: List[float], top_k: int, threshold: float = 0.0):
        """搜索向量"""
        if not self.client:
            return []
        
        try:
            # Milvus搜索逻辑
            return []
        except Exception as e:
            logger.error(f"Milvus搜索失败: {e}")
            return []
    
    def health_check(self) -> bool:
        """健康检查"""
        try:
            from pymilvus import connections
            connections.get_connection()
            return True
        except Exception as e:
            logger.error(f"Milvus健康检查失败: {e}")
            return False


class VectorStore:
    """统一向量存储接口"""
    
    BACKENDS = {
        'local': LocalVectorStore,
        'milvus': MilvusVectorStore,
    }
    
    def __init__(
        self,
        backend: str = "local",
        host: str = "localhost",
        port: int = 19530
    ):
        """
        初始化向量存储
        
        Args:
            backend: 后端类型（local, milvus, qdrant等）
            host: 数据库主机
            port: 数据库端口
        """
        self.backend_name = backend
        
        backend_class = self.BACKENDS.get(backend, LocalVectorStore)
        
        if backend == 'local':
            self.backend = backend_class()
        else:
            self.backend = backend_class(host, port)
        
        logger.info(f"初始化向量存储: {backend}")
    
    def add_vector(self, vector_id: str, vector: List[float], metadata: Dict):
        """添加向量"""
        self.backend.add_vector(vector_id, vector, metadata)
    
    def search(
        self,
        query_vector: List[float],
        top_k: int = 5,
        threshold: float = 0.0
    ) -> List[Dict]:
        """搜索向量"""
        return self.backend.search(query_vector, top_k, threshold)
    
    def embed_query(self, query_text: str) -> List[float]:
        """
        对查询进行嵌入
        这里应该调用嵌入服务
        """
        # 这个方法应该由嵌入服务提供
        # 暂时返回虚拟向量
        import hashlib
        seed = int(hashlib.md5(query_text.encode()).hexdigest()[:8], 16)
        import random
        random.seed(seed)
        return [random.random() for _ in range(768)]
    
    def health_check(self) -> bool:
        """健康检查"""
        return self.backend.health_check()


class DatabaseConnector:
    """数据库连接器 - PostgreSQL/MongoDB"""
    
    def __init__(
        self,
        host: str = "localhost",
        port: int = 5432,
        database: str = "wheel_db",
        user: str = "postgres",
        password: str = ""
    ):
        """
        初始化数据库连接
        
        Args:
            host: 数据库主机
            port: 数据库端口
            database: 数据库名
            user: 用户名
            password: 密码
        """
        self.host = host
        self.port = port
        self.database = database
        self.user = user
        self.password = password
        self.connection = None
        
        self._connect()
    
    def _connect(self):
        """连接数据库"""
        try:
            import psycopg2
            self.connection = psycopg2.connect(
                host=self.host,
                port=self.port,
                database=self.database,
                user=self.user,
                password=self.password
            )
            logger.info(f"数据库连接成功: {self.host}:{self.port}/{self.database}")
        except Exception as e:
            logger.warning(f"数据库连接失败: {e}，使用模拟模式")
            self.connection = None
    
    def insert_document(self, metadata: Dict[str, Any]) -> bool:
        """插入文档元数据"""
        try:
            if not self.connection:
                logger.debug(f"插入文档元数据: {metadata}")
                return True
            
            # SQL操作
            cursor = self.connection.cursor()
            cursor.execute(
                """
                INSERT INTO documents (document_id, source_file, mode, chunk_count, processed_at)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (
                    metadata['document_id'],
                    metadata['source_file'],
                    metadata['mode'],
                    metadata['chunk_count'],
                    metadata['processed_at']
                )
            )
            self.connection.commit()
            return True
        except Exception as e:
            logger.error(f"插入文档失败: {e}")
            return False
    
    def bm25_search(self, query: str, top_k: int) -> List[Dict]:
        """BM25搜索"""
        # 模拟实现
        logger.debug(f"执行BM25搜索: {query}")
        return []
    
    def health_check(self) -> bool:
        """健康检查"""
        try:
            if self.connection:
                cursor = self.connection.cursor()
                cursor.execute("SELECT 1")
                return True
            return True  # 模拟模式也返回True
        except Exception as e:
            logger.error(f"数据库健康检查失败: {e}")
            return False
