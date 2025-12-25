"""
数据处理管道 - 统一处理文档的各个阶段
支持多模态输入（文本、图像、视频）
"""

import logging
import time
from typing import Dict, Any, Optional, List
from pathlib import Path
from dataclasses import dataclass, field
from datetime import datetime
import hashlib

from core.modes import ProcessingMode, ModeConfig

logger = logging.getLogger(__name__)


@dataclass
class ProcessResult:
    """处理结果数据类"""
    document_id: str
    source_file: str
    mode: str
    status: str  # 'success', 'partial', 'failed'
    chunks: List[Dict[str, Any]] = field(default_factory=list)
    embeddings: List[List[float]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    duration: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)
    error: Optional[str] = None


class DataProcessingPipeline:
    """数据处理管道"""
    
    def __init__(
        self,
        mode: ProcessingMode,
        doc_processor: Any,
        embedding_service: Any,
        vector_store: Any,
        db: Any
    ):
        """
        初始化处理管道
        
        Args:
            mode: 处理模式
            doc_processor: 文档处理器
            embedding_service: 嵌入服务
            vector_store: 向量存储
            db: 数据库连接
        """
        self.mode = mode
        self.config = ModeConfig.get_config(mode)
        self.doc_processor = doc_processor
        self.embedding_service = embedding_service
        self.vector_store = vector_store
        self.db = db
        
        logger.info(f"初始化数据处理管道 - 模式: {mode.value}")
    
    def process(
        self,
        file_path: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        处理文档
        
        流程:
        1. 验证文件
        2. 提取文本（支持OCR）
        3. 预处理
        4. 分块
        5. 嵌入
        6. 存储
        
        Args:
            file_path: 文件路径
            metadata: 文档元数据
        
        Returns:
            处理结果
        """
        start_time = time.time()
        doc_id = self._generate_doc_id(file_path)
        
        try:
            logger.info(f"开始处理文档: {file_path}")
            
            # 步骤1: 验证文件
            self._validate_file(file_path)
            
            # 步骤2: 提取文本
            extracted_text = self.doc_processor.extract_text(
                file_path,
                mode=self.mode
            )
            
            # 步骤3: 预处理
            processed_text = self._preprocess_text(extracted_text)
            
            # 步骤4: 分块
            chunks = self._chunk_text(processed_text, file_path)
            
            # 步骤5: 嵌入
            embeddings = self._embed_chunks(chunks)
            
            # 步骤6: 存储
            self._store_results(doc_id, chunks, embeddings, file_path, metadata)
            
            duration = time.time() - start_time
            
            result = {
                "status": "success",
                "document_id": doc_id,
                "chunks_count": len(chunks),
                "duration": duration,
                "mode": self.mode.value
            }
            
            logger.info(f"文档处理完成: {file_path} ({duration:.2f}s, {len(chunks)} chunks)")
            return result
        
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"文档处理失败: {e}")
            
            return {
                "status": "failed",
                "document_id": doc_id,
                "error": str(e),
                "duration": duration,
                "mode": self.mode.value
            }
    
    def _generate_doc_id(self, file_path: str) -> str:
        """生成文档ID"""
        content = f"{file_path}:{datetime.now().isoformat()}"
        return hashlib.md5(content.encode()).hexdigest()[:16]
    
    def _validate_file(self, file_path: str):
        """验证文件存在且格式正确"""
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"文件不存在: {file_path}")
        
        allowed_extensions = {'.pdf', '.docx', '.txt', '.jpg', '.png', '.mp4'}
        if path.suffix.lower() not in allowed_extensions:
            raise ValueError(f"不支持的文件格式: {path.suffix}")
    
    def _preprocess_text(self, text: str) -> str:
        """
        预处理文本
        - 清理空白
        - 规范化符号
        - 移除特殊字符（可选）
        """
        # 移除多余空白
        text = ' '.join(text.split())
        
        # 规范化引号
        text = text.replace('"', '"').replace('"', '"')
        text = text.replace(''', "'").replace(''', "'")
        
        return text
    
    def _chunk_text(
        self,
        text: str,
        source: str
    ) -> List[Dict[str, Any]]:
        """
        按照模式配置分块文本
        
        根据mode选择不同的分块策略:
        - EFFICIENCY: 简单固定大小分块
        - BALANCED: 固定大小 + 语义边界
        - PRECISION: 分层分块 + 完整上下文
        """
        config = self.config['processing']
        chunk_size = config['chunk_size']
        chunk_overlap = config['chunk_overlap']
        
        chunks = []
        start = 0
        chunk_id = 0
        
        while start < len(text):
            end = start + chunk_size
            chunk_text = text[start:end].strip()
            
            if not chunk_text:
                break
            
            chunk = {
                'id': f"{source}_{chunk_id}",
                'text': chunk_text,
                'source': source,
                'start_pos': start,
                'end_pos': end,
                'chunk_index': chunk_id
            }
            chunks.append(chunk)
            
            # 移动窗口
            start = end - chunk_overlap
            chunk_id += 1
        
        logger.info(f"文本分块完成: {len(chunks)} chunks (大小: {chunk_size}, 重叠: {chunk_overlap})")
        return chunks
    
    def _embed_chunks(self, chunks: List[Dict[str, Any]]) -> List[List[float]]:
        """
        为分块文本生成嵌入向量
        """
        texts = [chunk['text'] for chunk in chunks]
        
        # 批处理嵌入
        embeddings = self.embedding_service.embed_batch(
            texts,
            batch_size=self.config.get('batch_size', 32)
        )
        
        logger.info(f"嵌入生成完成: {len(embeddings)} 向量")
        return embeddings
    
    def _store_results(
        self,
        doc_id: str,
        chunks: List[Dict[str, Any]],
        embeddings: List[List[float]],
        file_path: str,
        metadata: Optional[Dict[str, Any]]
    ):
        """
        存储处理结果
        - 向量存储: 存储向量
        - 关系数据库: 存储元数据和chunks
        """
        
        # 存储元数据到数据库
        doc_metadata = {
            'document_id': doc_id,
            'source_file': file_path,
            'mode': self.mode.value,
            'chunk_count': len(chunks),
            'processed_at': datetime.now().isoformat(),
            **(metadata or {})
        }
        
        self.db.insert_document(doc_metadata)
        
        # 存储chunks和向量到向量数据库
        for i, chunk in enumerate(chunks):
            self.vector_store.add_vector(
                vector_id=chunk['id'],
                vector=embeddings[i],
                metadata={
                    'document_id': doc_id,
                    'chunk_index': i,
                    'text': chunk['text'][:500],  # 预览文本
                    'source': file_path
                }
            )
        
        logger.info(f"结果存储完成: {len(chunks)} vectors")
    
    def switch_mode(self, new_mode: ProcessingMode):
        """切换处理模式"""
        self.mode = new_mode
        self.config = ModeConfig.get_config(new_mode)
        logger.info(f"处理管道切换模式: {new_mode.value}")
