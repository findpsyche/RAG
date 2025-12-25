"""
Wheel系统 - 企业级多模态RAG系统主程序
支持三种处理模式：高效(Efficiency)、中效(Balanced)、低效(Precision)
"""

import sys
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime

# 项目结构初始化
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

from core.modes import ProcessingMode, ModeConfig
from core.pipeline import DataProcessingPipeline
from core.engine import RetrievalEngine
from processors.document_processor import DocumentProcessor
from processors.embedding import EmbeddingService
from storage.vector_store import VectorStore
from storage.database import DatabaseConnector
from storage.cache import CacheManager
from api.main import create_app
from monitoring.metrics import MetricsCollector

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class WheelSystemConfig:
    """Wheel系统配置"""
    mode: ProcessingMode = ProcessingMode.BALANCED
    
    # 数据库配置
    db_host: str = "localhost"
    db_port: int = 5432
    db_name: str = "wheel_db"
    db_user: str = "postgres"
    
    # 向量数据库配置
    vector_db_type: str = "milvus"  # milvus, qdrant, pinecone, weaviate
    vector_db_host: str = "localhost"
    vector_db_port: int = 19530
    
    # Redis缓存配置
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_ttl: int = 3600  # 1小时
    
    # LLM配置
    llm_provider: str = "openai"  # openai, anthropic, mistral
    llm_model: str = "gpt-4-turbo"
    embedding_model: str = "text-embedding-3-small"
    
    # 系统配置
    batch_size: int = 32
    max_workers: int = 4
    enable_monitoring: bool = True
    enable_cache: bool = True
    
    # 每种模式的特定配置
    mode_configs: Dict[ProcessingMode, Dict[str, Any]] = field(default_factory=dict)


class WheelSystem:
    """Wheel系统主类 - 统一入口"""
    
    def __init__(self, config: Optional[WheelSystemConfig] = None):
        """
        初始化Wheel系统
        
        Args:
            config: 系统配置，若为None使用默认配置
        """
        self.config = config or WheelSystemConfig()
        self.mode = self.config.mode
        
        logger.info(f"初始化Wheel系统 - 模式: {self.mode.value}")
        
        # 初始化核心组件
        self._initialize_components()
        
        logger.info("Wheel系统初始化完成")
    
    def _initialize_components(self):
        """初始化系统核心组件"""
        
        # 1. 初始化缓存管理器
        self.cache = CacheManager(
            host=self.config.redis_host,
            port=self.config.redis_port,
            ttl=self.config.redis_ttl,
            enabled=self.config.enable_cache
        )
        
        # 2. 初始化数据库连接
        self.db = DatabaseConnector(
            host=self.config.db_host,
            port=self.config.db_port,
            database=self.config.db_name,
            user=self.config.db_user
        )
        
        # 3. 初始化向量存储
        self.vector_store = VectorStore(
            backend=self.config.vector_db_type,
            host=self.config.vector_db_host,
            port=self.config.vector_db_port
        )
        
        # 4. 初始化嵌入服务
        self.embedding_service = EmbeddingService(
            provider=self.config.llm_provider,
            model=self.config.embedding_model,
            cache=self.cache
        )
        
        # 5. 初始化文档处理器
        self.doc_processor = DocumentProcessor(
            mode=self.mode,
            cache=self.cache
        )
        
        # 6. 初始化处理管道
        self.pipeline = DataProcessingPipeline(
            mode=self.mode,
            doc_processor=self.doc_processor,
            embedding_service=self.embedding_service,
            vector_store=self.vector_store,
            db=self.db
        )
        
        # 7. 初始化检索引擎
        self.retrieval_engine = RetrievalEngine(
            mode=self.mode,
            vector_store=self.vector_store,
            cache=self.cache,
            db=self.db
        )
        
        # 8. 初始化监控系统（可选）
        if self.config.enable_monitoring:
            self.metrics = MetricsCollector()
        else:
            self.metrics = None
    
    def process_document(
        self,
        file_path: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        处理文档
        
        Args:
            file_path: 文档文件路径
            metadata: 文档元数据
        
        Returns:
            处理结果
        """
        logger.info(f"处理文档: {file_path} (模式: {self.mode.value})")
        
        try:
            result = self.pipeline.process(file_path, metadata)
            
            if self.metrics:
                self.metrics.record_document_processing(
                    mode=self.mode.value,
                    duration=result.get('duration', 0),
                    success=True
                )
            
            logger.info(f"文档处理成功: {file_path}")
            return result
        
        except Exception as e:
            logger.error(f"文档处理失败: {e}")
            if self.metrics:
                self.metrics.record_document_processing(
                    mode=self.mode.value,
                    success=False,
                    error=str(e)
                )
            raise
    
    def query(
        self,
        query_text: str,
        top_k: int = 5,
        use_reranking: bool = None,
        explain: bool = False
    ) -> Dict[str, Any]:
        """
        执行查询
        
        Args:
            query_text: 查询文本
            top_k: 返回结果数
            use_reranking: 是否使用重排（None为按模式默认）
            explain: 是否返回推理过程
        
        Returns:
            查询结果
        """
        logger.info(f"执行查询: {query_text[:50]}... (模式: {self.mode.value})")
        
        try:
            result = self.retrieval_engine.retrieve(
                query_text,
                top_k=top_k,
                use_reranking=use_reranking,
                explain=explain
            )
            
            if self.metrics:
                self.metrics.record_query(
                    mode=self.mode.value,
                    latency=result.get('latency', 0),
                    result_count=len(result.get('results', [])),
                    success=True
                )
            
            return result
        
        except Exception as e:
            logger.error(f"查询失败: {e}")
            if self.metrics:
                self.metrics.record_query(
                    mode=self.mode.value,
                    success=False,
                    error=str(e)
                )
            raise
    
    def switch_mode(self, new_mode: ProcessingMode) -> None:
        """
        切换处理模式（运行时动态切换）
        
        Args:
            new_mode: 新的处理模式
        """
        logger.info(f"切换模式: {self.mode.value} -> {new_mode.value}")
        
        self.mode = new_mode
        self.config.mode = new_mode
        
        # 重新初始化关键组件以适应新模式
        self.pipeline.mode = new_mode
        self.retrieval_engine.mode = new_mode
        self.doc_processor.mode = new_mode
    
    def get_metrics(self) -> Dict[str, Any]:
        """获取系统性能指标"""
        if self.metrics:
            return self.metrics.get_summary()
        return {}
    
    def health_check(self) -> Dict[str, bool]:
        """系统健康检查"""
        health = {
            'database': self.db.health_check(),
            'vector_store': self.vector_store.health_check(),
            'cache': self.cache.health_check(),
            'embedding_service': self.embedding_service.health_check()
        }
        return all(health.values()), health
    
    def create_api_app(self):
        """创建FastAPI应用"""
        return create_app(self)


def main():
    """主程序示例"""
    
    # 创建系统实例（使用默认配置）
    system = WheelSystem()
    
    # 验证系统健康状态
    is_healthy, health_details = system.health_check()
    if not is_healthy:
        logger.warning(f"系统部分组件不健康: {health_details}")
    
    # 示例：创建并启动API服务
    app = system.create_api_app()
    
    import uvicorn
    logger.info("启动API服务器: http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()
