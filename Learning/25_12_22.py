"""
🟦 Day 1: RAG 核心概念实现
日期: 2025-12-22
主题: RAG 最小结构 + 5个关键调参实战

RAG 工作流:
    文档 → Chunk → Embedding → Vector DB
                        ↓
           用户问题 → 检索 → LLM → 回答
"""

import json
from typing import List, Dict, Tuple
import math


# ============================================================================
# 第一部分: 理解 Chunk Size 的影响
# ============================================================================

class ChunkDemo:
    """演示 Chunk Size 对效果的影响"""
    
    def __init__(self):
        # 模拟法律文档（完整的条款）
        self.legal_document = """
        第一章 总则
        第一条 本公司根据《中华人民共和国公司法》和其他相关法律、法规组织、运营。
        第二条 本公司的法定代表人为董事长，对公司负责。
        第三条 本公司实行董事长负责制，董事长主持董事会工作。
        
        第二章 股东权利
        第四条 股东享有以下权利：
        （一）参加或委托代理人参加股东会；
        （二）行使表决权，对公司重大事项进行表决；
        （三）查阅公司文件和记录；
        （四）分取红利或分配剩余财产；
        （五）依法转让出资或股权；
        （六）提议召开临时股东会。
        """
    
    def chunk_strategy_1_small(self) -> List[str]:
        """策略1: 小块 (256 tokens) - 约 30-50 词"""
        chunks = []
        sentences = self.legal_document.split('。')
        
        current_chunk = ""
        for sentence in sentences:
            if len(current_chunk) < 50:  # 简化: 按字符长度
                current_chunk += sentence + "。"
            else:
                if current_chunk.strip():
                    chunks.append(current_chunk)
                current_chunk = sentence + "。"
        
        if current_chunk.strip():
            chunks.append(current_chunk)
        
        return chunks
    
    def chunk_strategy_2_medium(self) -> List[str]:
        """策略2: 中块 (512 tokens) - 段落级别"""
        chunks = []
        paragraphs = self.legal_document.split('\n\n')
        
        for para in paragraphs:
            if para.strip():
                chunks.append(para.strip())
        
        return chunks
    
    def chunk_strategy_3_large(self) -> List[str]:
        """策略3: 大块 (1024+ tokens) - 完整章节"""
        return [self.legal_document.strip()]
    
    def demonstrate(self):
        """演示三种策略的区别"""
        print("\n" + "="*70)
        print("演示: Chunk Size 对检索效果的影响")
        print("="*70)
        
        small = self.chunk_strategy_1_small()
        medium = self.chunk_strategy_2_medium()
        large = self.chunk_strategy_3_large()
        
        print(f"\n✓ 小块策略 (256 tokens):")
        print(f"  - 块数: {len(small)}")
        print(f"  - 优点: 精准度高 ✓")
        print(f"  - 缺点: 可能碎片化、丢失逻辑连贯性 ✗")
        print(f"  - 示例块:\n    '{small[0][:60]}...'")
        
        print(f"\n✓ 中块策略 (512 tokens):")
        print(f"  - 块数: {len(medium)}")
        print(f"  - 优点: 平衡精准度与上下文 ✓")
        print(f"  - 缺点: 需要仔细调优")
        print(f"  - 示例块:\n    '{medium[0][:60]}...'")
        
        print(f"\n✓ 大块策略 (1024+ tokens):")
        print(f"  - 块数: {len(large)}")
        print(f"  - 优点: 保留完整逻辑 ✓✓")
        print(f"  - 缺点: 噪音多、成本高 ✗")
        print(f"  - 用途: 法律/医疗等需要逻辑连贯的文档")


# ============================================================================
# 第二部分: 模拟 Embedding 和相似度计算
# ============================================================================

class SimpleEmbedding:
    """简单的 Embedding 模拟（实际会用 OpenAI/Qwen）"""
    
    @staticmethod
    def simple_hash_embed(text: str, dim: int = 8) -> List[float]:
        """
        简化版 embedding: 用文本特征生成向量
        实际应用会用：
        - OpenAI Embedding API (1536 dim)
        - 开源模型: bge-base-zh (768 dim)
        - 轻量级: m3e-small (384 dim)
        """
        # 计算文本的几个特征
        features = []
        
        # 特征1: 文本长度
        features.append(len(text) % 10 / 10.0)
        
        # 特征2: 元音比例
        vowels = sum(1 for c in text if c in 'aeiouAEIOU')
        features.append(vowels / max(len(text), 1) / 10.0)
        
        # 特征3: 数字比例
        digits = sum(1 for c in text if c.isdigit())
        features.append(digits / max(len(text), 1) / 10.0)
        
        # 特征4-8: 词频特征
        for char in ['a', 'e', 'i']:
            count = text.lower().count(char)
            features.append(count % 5 / 5.0)
        
        # 补齐维度
        while len(features) < dim:
            features.append(0.5)
        
        return features[:dim]
    
    @staticmethod
    def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
        """计算余弦相似度 (0-1)"""
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        norm1 = math.sqrt(sum(a ** 2 for a in vec1))
        norm2 = math.sqrt(sum(b ** 2 for b in vec2))
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return dot_product / (norm1 * norm2)
    
    def demonstrate(self):
        """演示 Embedding 和相似度"""
        print("\n" + "="*70)
        print("演示: Embedding 和相似度计算")
        print("="*70)
        
        # 三个样本文本
        texts = [
            "公司 2024 年营收增长 30%",
            "今年的销售额相比去年提升三成",
            "我最近去旅游了很开心"
        ]
        
        print("\n文本 1 和 2 应该相似 (都是说营收增长)")
        print("文本 1 和 3 应该不相似 (不同主题)\n")
        
        embeddings = [self.simple_hash_embed(text) for text in texts]
        
        sim_1_2 = self.cosine_similarity(embeddings[0], embeddings[1])
        sim_1_3 = self.cosine_similarity(embeddings[0], embeddings[2])
        
        print(f"相似度 (文本1 vs 文本2): {sim_1_2:.3f} ✓ 应该较高")
        print(f"相似度 (文本1 vs 文本3): {sim_1_3:.3f} ✓ 应该较低")
        
        print(f"\n💡 关键认知:")
        print(f"   小模型 (384 dim) vs 大模型 (1536 dim)")
        print(f"   - 对大多数场景: 差异 < 10%")
        print(f"   - 成本差异: 10 倍以上")
        print(f"   - 推荐: 先用中等模型 (768 dim) 调试")


# ============================================================================
# 第三部分: Top-K 检索和幻觉分析
# ============================================================================

class TopKRetrieval:
    """演示 Top-K 对检索结果和幻觉的影响"""
    
    def __init__(self):
        # 模拟向量数据库: (文档块, 相似度)
        self.documents = [
            ("公司成立于 2018 年，总部在北京", 0.95),
            ("2024 年员工总数 500 人", 0.92),
            ("公司主要产品是 AI 中台", 0.88),
            ("月营收约 500 万人民币", 0.75),
            ("CEO 毕业于清华大学", 0.60),
            ("办公室在中关村创业大街", 0.45),
            ("食堂每周一提供免费早餐", 0.20),  # 明显不相关
        ]
    
    def retrieve_top_k(self, k: int) -> Tuple[List[Tuple[str, float]], float]:
        """
        检索相似度最高的 K 个文档
        返回: (检索结果, 平均相似度)
        """
        sorted_docs = sorted(self.documents, key=lambda x: x[1], reverse=True)
        top_k = sorted_docs[:k]
        
        avg_similarity = sum(sim for _, sim in top_k) / len(top_k) if top_k else 0
        
        return top_k, avg_similarity
    
    def analyze_hallucination(self, top_k: List[Tuple[str, float]]) -> Dict:
        """分析幻觉风险"""
        if not top_k:
            return {"risk": "HIGH", "reason": "没有检索结果"}
        
        avg_sim = sum(sim for _, sim in top_k) / len(top_k)
        min_sim = min(sim for _, sim in top_k)
        
        if min_sim < 0.5:
            risk = "HIGH"
            reason = "包含不相关文档，LLM 容易混淆"
        elif avg_sim > 0.8:
            risk = "LOW"
            reason = "结果相关性高，LLM 可信度高"
        else:
            risk = "MEDIUM"
            reason = "有一定相关性，但需要谨慎"
        
        return {
            "risk": risk,
            "avg_similarity": round(avg_sim, 3),
            "min_similarity": round(min_sim, 3),
            "reason": reason
        }
    
    def demonstrate(self):
        """演示不同 K 值的影响"""
        print("\n" + "="*70)
        print("演示: Top-K 对检索和幻觉的影响")
        print("="*70)
        
        for k in [1, 3, 5, 10]:
            results, avg_sim = self.retrieve_top_k(k)
            hallucination = self.analyze_hallucination(results)
            
            print(f"\n{'─'*70}")
            print(f"K = {k} 时的检索结果:")
            print(f"{'─'*70}")
            
            for i, (doc, sim) in enumerate(results, 1):
                print(f"  {i}. [{sim:.2f}] {doc}")
            
            print(f"\n幻觉分析:")
            print(f"  - 风险等级: {hallucination['risk']}")
            print(f"  - 平均相似度: {hallucination['avg_similarity']}")
            print(f"  - 最低相似度: {hallucination['min_similarity']}")
            print(f"  - 分析: {hallucination['reason']}")


# ============================================================================
# 第四部分: RAG 适用性判断
# ============================================================================

class RAGSuitability:
    """判断问题是否适合用 RAG"""
    
    SUITABLE_CASES = {
        "基于文档的事实查询": {
            "示例": "公司 2024 年营收是多少？",
            "why": "答案在文档里，RAG 可以精确检索",
            "适合": True
        },
        "跨文档综合": {
            "示例": "对比 A 和 B 产品的功能差异",
            "why": "需要从多份文档中提取信息",
            "适合": True
        },
        "需要溯源/引用": {
            "示例": "这条政策在哪一份文件的第几条？",
            "why": "必须指出来源，RAG 天然支持",
            "适合": True
        }
    }
    
    UNSUITABLE_CASES = {
        "复杂多步推理": {
            "示例": "帮我设计一个营销策略",
            "why": "需要 Agent（多步推理）",
            "适合": False
        },
        "实时交互": {
            "示例": "查一下现在的股票价格",
            "why": "需要 Tool Calling + API",
            "适合": False
        },
        "创意生成": {
            "示例": "帮我写一个产品广告文案",
            "why": "需要微调或更强的 prompt",
            "适合": False
        }
    }
    
    @staticmethod
    def judge(question: str) -> Dict:
        """判断一个问题是否适合 RAG"""
        keywords_rag = ["查询", "文档", "是什么", "哪里", "多少", "列出", "总结"]
        keywords_no = ["设计", "创作", "写", "实时", "现在", "最新", "代码执行"]
        
        rag_score = sum(1 for kw in keywords_rag if kw in question)
        no_score = sum(1 for kw in keywords_no if kw in question)
        
        if rag_score > no_score:
            return {"suitable": True, "confidence": min(rag_score / 3, 1.0)}
        else:
            return {"suitable": False, "confidence": min(no_score / 3, 1.0)}
    
    def demonstrate(self):
        """演示 RAG 适用性判断"""
        print("\n" + "="*70)
        print("演示: RAG 适用性判断 (FDE 的救命技能)")
        print("="*70)
        
        print("\n✅ RAG 适合的场景:")
        print("─"*70)
        for case, info in self.SUITABLE_CASES.items():
            print(f"\n📌 {case}")
            print(f"   例子: {info['示例']}")
            print(f"   原因: {info['why']}")
        
        print("\n\n❌ RAG 不适合的场景:")
        print("─"*70)
        for case, info in self.UNSUITABLE_CASES.items():
            print(f"\n📌 {case}")
            print(f"   例子: {info['示例']}")
            print(f"   原因: {info['why']}")
        
        # 测试几个问题
        print("\n\n🧪 示例问题判断:")
        print("─"*70)
        test_questions = [
            "我们公司的产品都有哪些功能？",
            "帮我写一个产品推介词",
            "查一下合同条款里的退款政策"
        ]
        
        for q in test_questions:
            result = self.judge(q)
            suitable = "✓ 适合 RAG" if result['suitable'] else "✗ 不适合 RAG"
            print(f"\nQ: {q}")
            print(f"A: {suitable} (置信度: {result['confidence']:.1%})")


# ============================================================================
# 主函数: 运行全部演示
# ============================================================================

def main():
    print("\n" + "🔵"*35)
    print("🟦 RAG Day 1: 核心概念完全演示 🟦")
    print("🔵"*35)
    
    # 演示 1: Chunk Size
    chunk_demo = ChunkDemo()
    chunk_demo.demonstrate()
    
    # 演示 2: Embedding
    embedding_demo = SimpleEmbedding()
    embedding_demo.demonstrate()
    
    # 演示 3: Top-K 和幻觉
    topk_demo = TopKRetrieval()
    topk_demo.demonstrate()
    
    # 演示 4: RAG 适用性
    suitability_demo = RAGSuitability()
    suitability_demo.demonstrate()
    
    print("\n" + "="*70)
    print("✅ Day 1 学习完成!")
    print("="*70)
    print("""
📋 Day 1 关键检查清单:
  ☐ 能解释 RAG 的 6 步工作流
  ☐ 知道 Chunk Size 的 3 种策略
  ☐ 理解 Embedding 的作用
  ☐ 能判断最优的 Top-K 值
  ☐ 知道 RAG 的适用和不适用场景

🎬 下一步: 进入 Day 2 - ToB 场景下的 RAG 差异化设计
    """)


if __name__ == "__main__":
    main()
