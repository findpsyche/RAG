"""
处理模式定义和配置
支持三种不同的处理架构：高效、中效、低效
"""

from enum import Enum
from dataclasses import dataclass
from typing import Dict, Any, Optional


class ProcessingMode(str, Enum):
    """处理模式枚举"""
    EFFICIENCY = "efficiency"      # 高效模式 - 快速MVP
    BALANCED = "balanced"          # 中效模式 - 通用企业场景
    PRECISION = "precision"        # 低效模式 - 高精度要求


@dataclass
class ModeConfig:
    """每种模式的详细配置"""
    
    # 高效模式配置
    EFFICIENCY_CONFIG = {
        "name": "高效模式(Efficiency Mode)",
        "description": "强调速度和快速成果，低召回率",
        "target_use_cases": ["客服", "快速分类", "初期验证"],
        
        # 性能指标目标
        "metrics": {
            "recall": (0.4, 0.6),           # 目标召回率范围
            "precision": (0.3, 0.5),        # 目标精确度范围
            "latency_ms": (100, 300),       # 目标延迟
            "cost_per_query": "minimal"     # 成本
        },
        
        # 模型选择
        "models": {
            "ocr": "mistral-ocr-3",         # 轻量级OCR
            "embedding": "sentence-transformers/all-MiniLM-L6-v2",  # 轻量级嵌入
            "llm": "gpt-4-turbo",           # 标准LLM
            "reranker": None                # 无重排
        },
        
        # 处理参数
        "processing": {
            "chunk_size": 512,              # 分块大小
            "chunk_overlap": 50,            # 分块重叠
            "use_reranking": False,         # 不使用重排
            "num_retrieval": 3,             # 检索结果数
            "reasoning_steps": 1            # 推理步骤数
        },
        
        # 存储策略
        "storage": {
            "vector_db": "local_cache",     # 本地缓存
            "enable_persistence": False,     # 无持久化
            "enable_cache": True
        },
        
        # 检索策略
        "retrieval": {
            "strategy": "bm25_only",        # 仅BM25
            "hybrid": False,                 # 无混合检索
            "similarity_threshold": 0.3
        }
    }
    
    # 中效模式配置
    BALANCED_CONFIG = {
        "name": "中效模式(Balanced Mode)",
        "description": "平衡召回率和速度，适用于一般企业场景",
        "target_use_cases": ["财务分析", "HR问询", "通用知识库"],
        
        # 性能指标目标
        "metrics": {
            "recall": (0.70, 0.80),         # 目标召回率范围
            "precision": (0.60, 0.75),      # 目标精确度范围
            "latency_ms": (500, 2000),      # 目标延迟
            "cost_per_query": "moderate"    # 成本
        },
        
        # 模型选择
        "models": {
            "ocr": "paddle-ocr",            # Paddle OCR
            "embedding": "sentence-transformers/all-mpnet-base-v2",  # 中等规模
            "llm": "gpt-4-turbo",           # 高性能LLM
            "reranker": "cross-encoder/ms-marco-MiniLM-L-6-v2"  # 轻量级重排
        },
        
        # 处理参数
        "processing": {
            "chunk_size": 1024,             # 更大的分块
            "chunk_overlap": 100,           # 更多重叠
            "use_reranking": True,          # 使用重排
            "num_retrieval": 5,             # 更多检索结果
            "reasoning_steps": 2            # 多步推理
        },
        
        # 存储策略
        "storage": {
            "vector_db": "milvus",          # Milvus向量数据库
            "enable_persistence": True,     # 持久化存储
            "enable_cache": True            # Redis缓存
        },
        
        # 检索策略
        "retrieval": {
            "strategy": "hybrid",           # 混合检索
            "hybrid": True,                 # 向量+BM25
            "similarity_threshold": 0.5
        }
    }
    
    # 低效（高精度）模式配置
    PRECISION_CONFIG = {
        "name": "低效模式(Precision Mode)",
        "description": "最大化准确性，不容出错",
        "target_use_cases": ["法律合规", "医疗", "工业", "金融风控"],
        
        # 性能指标目标
        "metrics": {
            "recall": (0.90, 0.98),         # 目标召回率范围（极高）
            "precision": (0.85, 0.95),      # 目标精确度范围（极高）
            "latency_ms": (2000, 10000),    # 目标延迟（可接受）
            "cost_per_query": "high"        # 成本优先级低
        },
        
        # 模型选择
        "models": {
            "ocr": "gpt-4v",                # 最强OCR
            "embedding": "text-embedding-3-large",  # 高性能嵌入
            "llm": "gpt-5",                 # 最强推理模型
            "reranker": "cross-encoder/qnli-distilroberta-base"  # 高质量重排
        },
        
        # 处理参数
        "processing": {
            "chunk_size": 2048,             # 更大分块保留上下文
            "chunk_overlap": 256,           # 大量重叠确保覆盖
            "use_reranking": True,          # 必使用重排
            "num_retrieval": 10,            # 检索更多结果
            "reasoning_steps": 3            # 复杂推理链
        },
        
        # 存储策略
        "storage": {
            "vector_db": "pinecone",        # Pinecone多副本
            "enable_persistence": True,     # 完整持久化
            "enable_cache": True,           # 积极缓存
            "replication_factor": 3         # 三副本冗余
        },
        
        # 检索策略
        "retrieval": {
            "strategy": "advanced_rag",     # 高级RAG（Graph RAG、HyDE等）
            "hybrid": True,                 # 混合检索
            "similarity_threshold": 0.7,    # 高置信度阈值
            "knowledge_graph": True,        # 使用知识图谱
            "hyde": True,                   # 假设型提问
            "self_consistency": True        # 一致性检查
        }
    }
    
    @classmethod
    def get_config(cls, mode: ProcessingMode) -> Dict[str, Any]:
        """获取指定模式的配置"""
        config_map = {
            ProcessingMode.EFFICIENCY: cls.EFFICIENCY_CONFIG,
            ProcessingMode.BALANCED: cls.BALANCED_CONFIG,
            ProcessingMode.PRECISION: cls.PRECISION_CONFIG
        }
        return config_map.get(mode, cls.BALANCED_CONFIG)
    
    @classmethod
    def print_comparison(cls):
        """打印三种模式的对比表"""
        configs = {
            ProcessingMode.EFFICIENCY: cls.EFFICIENCY_CONFIG,
            ProcessingMode.BALANCED: cls.BALANCED_CONFIG,
            ProcessingMode.PRECISION: cls.PRECISION_CONFIG
        }
        
        print("\n" + "="*100)
        print("Wheel系统 - 三种处理模式对比".center(100))
        print("="*100)
        
        for mode, config in configs.items():
            print(f"\n【{config['name']}】")
            print(f"说明: {config['description']}")
            print(f"使用场景: {', '.join(config['target_use_cases'])}")
            
            print("\n性能指标:")
            for metric, value in config['metrics'].items():
                print(f"  • {metric}: {value}")
            
            print("\n模型选择:")
            for model_type, model_name in config['models'].items():
                print(f"  • {model_type}: {model_name}")
            
            print("\n处理参数:")
            for param, value in config['processing'].items():
                print(f"  • {param}: {value}")
            
            print("\n存储策略:")
            for storage_type, value in config['storage'].items():
                print(f"  • {storage_type}: {value}")
            
            print("\n检索策略:")
            for strategy_type, value in config['retrieval'].items():
                print(f"  • {strategy_type}: {value}")


# 使用示例
if __name__ == "__main__":
    ModeConfig.print_comparison()
