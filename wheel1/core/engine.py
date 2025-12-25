"""
检索引擎 - 支持多种检索策略
包括向量检索、BM25、混合检索、重排等
"""

import logging
import time
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
from core.modes import ProcessingMode, ModeConfig
logger = logging.getLogger(__name__)


@dataclass
class RetrievalResult:
    """检索结果"""
    rank: int
    doc_id: str
    text: str
    score: float
    source: str
    metadata: Dict[str, Any]
class RetrievalStrategy(str, Enum):
    """检索策略"""
    BM25_ONLY = "bm25_only"
    VECTOR_ONLY = "vector_only"
    HYBRID = "hybrid"
    ADVANCED_RAG = "advanced_rag"
class RetrievalEngine:
    """检索引擎"""

    def __init__(
        self,
        mode: ProcessingMode,
        vector_store: Any,
        cache: Any,
        db: Any
    ):
        """
        初始化检索引擎
        
        Args:
            mode: 处理模式
            vector_store: 向量存储
            cache: 缓存管理器
            db: 数据库连接
        """
        self.mode = mode
        self.config = ModeConfig.get_config(mode)
        self.vector_store = vector_store
        self.cache = cache
        self.db = db
        
        # 根据配置初始化检索策略
        retrieval_config = self.config['retrieval']
        self.strategy = RetrievalStrategy(retrieval_config['strategy'])
        
        logger.info(f"初始化检索引擎 - 模式: {mode.value}, 策略: {self.strategy.value}")
    
    def retrieve(
        self,
        query_text: str,
        top_k: int = 5,
        use_reranking: Optional[bool] = None,
        explain: bool = False
    ) -> Dict[str, Any]:
        """
        执行检索
        
        Args:
            query_text: 查询文本
            top_k: 返回结果数
            use_reranking: 是否使用重排（None为按配置）
            explain: 是否返回推理过程
        
        Returns:
            检索结果
        """
        start_time = time.time()
        
        # 检查缓存
        cache_key = self._get_cache_key(query_text, top_k)
        cached_result = self.cache.get(cache_key)
        if cached_result:
            logger.info(f"命中缓存: {query_text[:30]}...")
            cached_result['from_cache'] = True
            return cached_result
        
        try:
            # 使用缓存设置的重排选项
            if use_reranking is None:
                use_reranking = self.config['processing'].get('use_reranking', False)
            
            # 根据策略执行检索
            if self.strategy == RetrievalStrategy.BM25_ONLY:
                results = self._retrieve_bm25(query_text, top_k)
            
            elif self.strategy == RetrievalStrategy.VECTOR_ONLY:
                results = self._retrieve_vector(query_text, top_k)
            
            elif self.strategy == RetrievalStrategy.HYBRID:
                results = self._retrieve_hybrid(query_text, top_k)
            
            elif self.strategy == RetrievalStrategy.ADVANCED_RAG:
                results = self._retrieve_advanced_rag(query_text, top_k)
            
            else:
                results = self._retrieve_hybrid(query_text, top_k)
            
            # 重排（如配置）
            if use_reranking and len(results) > 0:
                results = self._rerank_results(query_text, results)
            
            # 构建返回结果
            latency = time.time() - start_time
            
            response = {
                'query': query_text,
                'results': results,
                'count': len(results),
                'latency_ms': latency * 1000,
                'strategy': self.strategy.value,
                'mode': self.mode.value,
                'from_cache': False
            }
            
            if explain:
                response['explanation'] = self._generate_explanation(
                    query_text, results, latency
                )
            
            # 存储到缓存
            self.cache.set(cache_key, response, ttl=3600)
            
            logger.info(
                f"检索完成: {len(results)} 结果 (延迟: {latency*1000:.1f}ms)"
            )
            
            return response
        
        except Exception as e:
            logger.error(f"检索失败: {e}")
            return {
                'query': query_text,
                'results': [],
                'error': str(e),
                'mode': self.mode.value
            }
    
    def _retrieve_bm25(
        self,
        query_text: str,
        top_k: int
    ) -> List[Dict[str, Any]]:
        """BM25 关键词检索"""
        logger.debug(f"执行BM25检索: {query_text[:50]}...")
        
        # 分词和BM25评分
        results = self.db.bm25_search(query_text, top_k)
        
        return [
            {
                'rank': i + 1,
                'text': r['text'],
                'score': r['score'],
                'source': r['source'],
                'metadata': r.get('metadata', {})
            }
            for i, r in enumerate(results)
        ]
    
    def _retrieve_vector(
        self,
        query_text: str,
        top_k: int
    ) -> List[Dict[str, Any]]:
        """向量相似度检索"""
        logger.debug(f"执行向量检索: {query_text[:50]}...")
        
        # 对查询进行嵌入
        query_embedding = self.vector_store.embed_query(query_text)
        
        # 向量相似度搜索
        similarity_threshold = self.config['retrieval'].get('similarity_threshold', 0.5)
        results = self.vector_store.search(
            query_embedding,
            top_k=top_k,
            threshold=similarity_threshold
        )
        
        return [
            {
                'rank': i + 1,
                'text': r['text'],
                'score': r['similarity'],
                'source': r['source'],
                'metadata': r.get('metadata', {})
            }
            for i, r in enumerate(results)
        ]
    
    def _retrieve_hybrid(
        self,
        query_text: str,
        top_k: int
    ) -> List[Dict[str, Any]]:
        """混合检索（向量 + BM25）"""
        logger.debug(f"执行混合检索: {query_text[:50]}...")
        
        # 并行执行两种检索
        bm25_results = self._retrieve_bm25(query_text, top_k * 2)  # 获取更多候选
        vector_results = self._retrieve_vector(query_text, top_k * 2)
        
        # 融合结果（权重默认各50%）
        merged = self._merge_results(
            bm25_results,
            vector_results,
            weights=[0.5, 0.5]
        )
        
        # 按融合分数排序并取top-k
        merged = sorted(merged, key=lambda x: x['score'], reverse=True)[:top_k]
        
        # 重新排名
        for i, result in enumerate(merged):
            result['rank'] = i + 1
        
        return merged
    
    def _retrieve_advanced_rag(
        self,
        query_text: str,
        top_k: int
    ) -> List[Dict[str, Any]]:
        """
        高级RAG检索
        - HyDE（假设型提问）
        - 知识图谱检索
        - 多步推理
        - 自洽性检查
        """
        logger.debug(f"执行高级RAG检索: {query_text[:50]}...")
        
        # 1. 混合检索基础结果
        results = self._retrieve_hybrid(query_text, top_k)
        
        # 2. HyDE增强：生成假设答案进行检索
        if self.config['retrieval'].get('hyde', False):
            hypothetical_results = self._hyde_retrieval(query_text, top_k)
            results = self._merge_results(results, hypothetical_results, [0.7, 0.3])
        
        # 3. 知识图谱检索（如可用）
        if self.config['retrieval'].get('knowledge_graph', False):
            kg_results = self._knowledge_graph_retrieval(query_text, top_k)
            results = self._merge_results(results, kg_results, [0.8, 0.2])
        
        # 4. 重排确保高质量
        results = self._rerank_results(query_text, results)
        
        # 5. 自洽性检查（多步验证）
        if self.config['retrieval'].get('self_consistency', False):
            results = self._verify_consistency(results)
        
        return results[:top_k]
    
    def _merge_results(
        self,
        results1: List[Dict[str, Any]],
        results2: List[Dict[str, Any]],
        weights: List[float] = [0.5, 0.5]
    ) -> List[Dict[str, Any]]:
        """
        融合两组检索结果
        根据文本ID和权重计算融合分数
        """
        # 创建结果映射
        merged = {}
        
        for result in results1:
            key = result['text'][:100]  # 使用文本前100字符作为key
            merged[key] = {
                'text': result['text'],
                'source': result['source'],
                'metadata': result['metadata'],
                'score': result['score'] * weights[0]
            }
        
        for result in results2:
            key = result['text'][:100]
            if key in merged:
                merged[key]['score'] += result['score'] * weights[1]
            else:
                merged[key] = {
                    'text': result['text'],
                    'source': result['source'],
                    'metadata': result['metadata'],
                    'score': result['score'] * weights[1]
                }
        
        return list(merged.values())
    
    def _rerank_results(
        self,
        query_text: str,
        results: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        使用重排模型重新评分和排序
        """
        if not results:
            return results
        
        # 使用cross-encoder重排
        # 这里使用mock实现，实际应调用cross-encoder模型
        
        reranked = []
        for i, result in enumerate(results):
            # 计算相关性分数
            relevance_score = self._compute_relevance(query_text, result['text'])
            result['rerank_score'] = relevance_score
            reranked.append(result)
        
        # 按重排分数排序
        reranked = sorted(reranked, key=lambda x: x['rerank_score'], reverse=True)
        
        # 更新rank
        for i, result in enumerate(reranked):
            result['rank'] = i + 1
        
        return reranked
    
    def _compute_relevance(self, query: str, text: str) -> float:
        """计算查询和文本的相关性（简单实现）"""
        # 实际应使用cross-encoder模型
        query_tokens = set(query.lower().split())
        text_tokens = set(text.lower().split())
        
        if not query_tokens or not text_tokens:
            return 0.0
        
        intersection = len(query_tokens & text_tokens)
        union = len(query_tokens | text_tokens)
        
        return intersection / union if union > 0 else 0.0
    
    def _hyde_retrieval(
        self,
        query_text: str,
        top_k: int
    ) -> List[Dict[str, Any]]:
        """
        HyDE (Hypothetical Document Embeddings) 检索
        生成假设答案，以该答案的嵌入进行检索
        """
        logger.debug("执行HyDE检索...")
        
        # 这里应调用LLM生成假设答案
        # 本示例中使用mock实现
        
        hypothetical_answer = f"关于'{query_text}'的详细解答..."
        
        # 对假设答案进行检索
        return self._retrieve_vector(hypothetical_answer, top_k)
    
    def _knowledge_graph_retrieval(
        self,
        query_text: str,
        top_k: int
    ) -> List[Dict[str, Any]]:
        """知识图谱检索"""
        logger.debug("执行知识图谱检索...")
        
        # 从知识图谱中检索相关实体和关系
        # 本示例为mock实现
        
        return []  # 实际应返回从KG检索的结果
    
    def _verify_consistency(
        self,
        results: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        验证结果的一致性
        多步验证确保高置信度
        """
        logger.debug("验证结果一致性...")
        
        # 在这里可以添加自洽性检查的逻辑
        # 例如：多轮提问验证、概念一致性检查等
        
        return results
    
    def _generate_explanation(
        self,
        query: str,
        results: List[Dict[str, Any]],
        latency: float
    ) -> str:
        """生成检索过程的说明"""
        explanation = f"""
        查询: {query}
        检索策略: {self.strategy.value}
        处理模式: {self.mode.value}
        返回结果数: {len(results)}
        检索延迟: {latency*1000:.1f}ms
        
        检索过程:
        1. 查询预处理和嵌入
        2. {self.strategy.value.upper()} 检索
        3. 结果重排和过滤
        4. 最终排序和返回
        """
        return explanation
    
    def _get_cache_key(self, query: str, top_k: int) -> str:
        """生成缓存键"""
        import hashlib
        key_str = f"{self.mode.value}:{query}:{top_k}"
        return hashlib.md5(key_str.encode()).hexdigest()
