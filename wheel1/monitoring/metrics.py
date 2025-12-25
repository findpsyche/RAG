"""
监控和评估模块
收集性能指标、执行A/B测试、评估系统效果
"""

import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import defaultdict
import statistics

logger = logging.getLogger(__name__)


@dataclass
class MetricRecord:
    """指标记录"""
    timestamp: datetime
    mode: str
    metric_type: str  # 'document_processing', 'query', 'embedding'
    duration: float = 0.0
    success: bool = True
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class MetricsCollector:
    """性能指标收集器"""
    
    def __init__(self, window_size: int = 1000):
        """
        初始化指标收集器
        
        Args:
            window_size: 保留的最大记录数
        """
        self.window_size = window_size
        self.records: List[MetricRecord] = []
        self.counters = defaultdict(int)
        
        logger.info("初始化性能指标收集器")
    
    def record_document_processing(
        self,
        mode: str,
        duration: float = 0.0,
        success: bool = True,
        error: Optional[str] = None,
        **metadata
    ):
        """记录文档处理指标"""
        record = MetricRecord(
            timestamp=datetime.now(),
            mode=mode,
            metric_type='document_processing',
            duration=duration,
            success=success,
            error=error,
            metadata=metadata
        )
        
        self._add_record(record)
        self.counters[f"{mode}:doc_processed"] += 1 if success else 0
        self.counters[f"{mode}:doc_failed"] += 1 if not success else 0
    
    def record_query(
        self,
        mode: str,
        latency: float = 0.0,
        result_count: int = 0,
        success: bool = True,
        error: Optional[str] = None,
        **metadata
    ):
        """记录查询指标"""
        record = MetricRecord(
            timestamp=datetime.now(),
            mode=mode,
            metric_type='query',
            duration=latency,
            success=success,
            error=error,
            metadata={
                'result_count': result_count,
                **metadata
            }
        )
        
        self._add_record(record)
        self.counters[f"{mode}:queries"] += 1
        self.counters[f"{mode}:query_errors"] += 1 if not success else 0
    
    def record_embedding(
        self,
        mode: str,
        vector_count: int,
        duration: float = 0.0,
        success: bool = True
    ):
        """记录嵌入指标"""
        record = MetricRecord(
            timestamp=datetime.now(),
            mode=mode,
            metric_type='embedding',
            duration=duration,
            success=success,
            metadata={'vector_count': vector_count}
        )
        
        self._add_record(record)
        self.counters[f"{mode}:embeddings"] += vector_count if success else 0
    
    def _add_record(self, record: MetricRecord):
        """添加记录"""
        self.records.append(record)
        
        # 限制记录数量
        if len(self.records) > self.window_size:
            self.records = self.records[-self.window_size:]
    
    def get_summary(self) -> Dict[str, Any]:
        """获取性能指标摘要"""
        if not self.records:
            return {}
        
        summary = {}
        
        # 按模式分组统计
        records_by_mode = defaultdict(list)
        for record in self.records:
            records_by_mode[record.mode].append(record)
        
        for mode, mode_records in records_by_mode.items():
            summary[mode] = self._compute_mode_metrics(mode_records)
        
        # 全局统计
        summary['overall'] = self._compute_global_metrics(self.records)
        
        return summary
    
    def _compute_mode_metrics(self, records: List[MetricRecord]) -> Dict[str, Any]:
        """计算模式的指标"""
        
        # 分离不同类型的记录
        doc_records = [r for r in records if r.metric_type == 'document_processing']
        query_records = [r for r in records if r.metric_type == 'query']
        embed_records = [r for r in records if r.metric_type == 'embedding']
        
        metrics = {
            'timestamp': datetime.now().isoformat(),
            'total_records': len(records),
        }
        
        # 文档处理指标
        if doc_records:
            success_count = sum(1 for r in doc_records if r.success)
            durations = [r.duration for r in doc_records if r.duration > 0]
            
            metrics['document_processing'] = {
                'total': len(doc_records),
                'successful': success_count,
                'error_rate': 1 - (success_count / len(doc_records)) if doc_records else 0,
                'avg_duration_ms': statistics.mean(durations) * 1000 if durations else 0,
                'min_duration_ms': min(durations) * 1000 if durations else 0,
                'max_duration_ms': max(durations) * 1000 if durations else 0,
            }
        
        # 查询指标
        if query_records:
            success_count = sum(1 for r in query_records if r.success)
            latencies = [r.duration for r in query_records if r.duration > 0]
            result_counts = [r.metadata.get('result_count', 0) for r in query_records]
            
            metrics['query'] = {
                'total': len(query_records),
                'successful': success_count,
                'error_rate': 1 - (success_count / len(query_records)) if query_records else 0,
                'avg_latency_ms': statistics.mean(latencies) * 1000 if latencies else 0,
                'p95_latency_ms': self._percentile(latencies, 95) * 1000 if latencies else 0,
                'p99_latency_ms': self._percentile(latencies, 99) * 1000 if latencies else 0,
                'avg_result_count': statistics.mean(result_counts) if result_counts else 0,
            }
        
        # 嵌入指标
        if embed_records:
            success_count = sum(1 for r in embed_records if r.success)
            total_vectors = sum(r.metadata.get('vector_count', 0) for r in embed_records)
            durations = [r.duration for r in embed_records if r.duration > 0]
            
            metrics['embedding'] = {
                'total_vectors': total_vectors,
                'successful_vectors': sum(
                    r.metadata.get('vector_count', 0) for r in embed_records if r.success
                ),
                'avg_duration_ms': statistics.mean(durations) * 1000 if durations else 0,
            }
        
        return metrics
    
    def _compute_global_metrics(self, records: List[MetricRecord]) -> Dict[str, Any]:
        """计算全局指标"""
        
        success_count = sum(1 for r in records if r.success)
        durations = [r.duration for r in records if r.duration > 0]
        
        return {
            'total_operations': len(records),
            'successful': success_count,
            'failed': len(records) - success_count,
            'overall_success_rate': success_count / len(records) if records else 0,
            'avg_duration_ms': statistics.mean(durations) * 1000 if durations else 0,
        }
    
    def _percentile(self, data: List[float], percentile: int) -> float:
        """计算百分位"""
        if not data:
            return 0.0
        
        sorted_data = sorted(data)
        index = int((percentile / 100) * len(sorted_data))
        return sorted_data[min(index, len(sorted_data) - 1)]
    
    def get_mode_comparison(self) -> Dict[str, Any]:
        """获取不同模式的对比"""
        summary = self.get_summary()
        
        comparison = {}
        for mode in ['efficiency', 'balanced', 'precision']:
            if mode in summary:
                comparison[mode] = summary[mode]
        
        return comparison


class ABTestFramework:
    """A/B测试框架"""
    
    def __init__(self):
        """初始化A/B测试框架"""
        self.experiments = {}
        logger.info("初始化A/B测试框架")
    
    def create_experiment(
        self,
        name: str,
        control_config: Dict[str, Any],
        treatment_config: Dict[str, Any],
        duration: timedelta = timedelta(days=7)
    ) -> str:
        """
        创建A/B测试实验
        
        Args:
            name: 实验名称
            control_config: 对照组配置
            treatment_config: 处理组配置
            duration: 实验持续时间
        
        Returns:
            实验ID
        """
        experiment_id = f"exp_{datetime.now().timestamp()}"
        
        self.experiments[experiment_id] = {
            'name': name,
            'created_at': datetime.now(),
            'end_at': datetime.now() + duration,
            'control': control_config,
            'treatment': treatment_config,
            'results': {
                'control': [],
                'treatment': []
            }
        }
        
        logger.info(f"创建A/B实验: {name} ({experiment_id})")
        return experiment_id
    
    def record_result(
        self,
        experiment_id: str,
        group: str,  # 'control' or 'treatment'
        metrics: Dict[str, float]
    ):
        """记录实验结果"""
        if experiment_id not in self.experiments:
            logger.warning(f"实验不存在: {experiment_id}")
            return
        
        self.experiments[experiment_id]['results'][group].append({
            'timestamp': datetime.now(),
            'metrics': metrics
        })
    
    def get_results(self, experiment_id: str) -> Dict[str, Any]:
        """获取实验结果"""
        if experiment_id not in self.experiments:
            return {}
        
        exp = self.experiments[experiment_id]
        control_results = exp['results']['control']
        treatment_results = exp['results']['treatment']
        
        # 计算统计量
        control_metrics = self._aggregate_metrics(control_results)
        treatment_metrics = self._aggregate_metrics(treatment_results)
        
        # 计算差异
        diff = {}
        for key in control_metrics:
            if key in treatment_metrics:
                diff[key] = {
                    'control': control_metrics[key],
                    'treatment': treatment_metrics[key],
                    'improvement': (treatment_metrics[key] - control_metrics[key]) / control_metrics[key] * 100
                }
        
        return {
            'experiment': exp['name'],
            'duration': f"{(exp['end_at'] - exp['created_at']).days}d",
            'control_samples': len(control_results),
            'treatment_samples': len(treatment_results),
            'metrics_comparison': diff
        }
    
    def _aggregate_metrics(self, results: List[Dict]) -> Dict[str, float]:
        """聚合指标"""
        if not results:
            return {}
        
        aggregated = defaultdict(list)
        for result in results:
            for metric, value in result['metrics'].items():
                aggregated[metric].append(value)
        
        return {
            metric: statistics.mean(values)
            for metric, values in aggregated.items()
        }
