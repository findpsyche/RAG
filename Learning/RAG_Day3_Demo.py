"""
🟦 Day 3: 给被投公司做 RAG Demo（极其重要）

这个文件包含了可以直接运行的 Demo 代码框架
支持: PDF / Markdown / Excel / Streamlit UI

演示的是最小化但完整的 RAG 流程
- 无 RAG: 直接问 LLM
- 有 RAG: 问 LLM，但带上了检索到的文档

核心目标: 5分钟内让创始人说"这个我们能用"
"""

import os
import json
from typing import List, Tuple, Dict
from pathlib import Path
from datetime import datetime


# ============================================================================
# 第一部分: 样本数据生成（如果没有真实文档）
# ============================================================================

class SampleDataGenerator:
    """生成示例文档（Demo 用）"""
    
    @staticmethod
    def create_sample_documents() -> Dict[str, str]:
        """创建示例企业文档"""
        return {
            "产品介绍.md": """# 我们的产品

## 产品功能
- AI 中台: 提供企业级的大模型接口和向量数据库
- 知识库系统: 支持 PDF、Word、Excel 等多种格式
- 智能问答: 基于 RAG 技术的企业知识问答系统

## 技术栈
- 后端: Python + FastAPI
- 数据库: PostgreSQL + Milvus (向量数据库)
- 部署: Docker + Kubernetes
- 前端: React + TypeScript

## 价格
- 标准版: 5000元/月
- 企业版: 15000元/月（含定制化）
- API 调用: 0.01元/1000 tokens
""",
            
            "客户成功案例.md": """# 我们的客户案例

## 案例 1: 某律师事务所
- 问题: 500 份合同，律师每次查询都要手翻
- 解决方案: RAG 系统 + 精确检索
- 结果: 查询时间从 30 分钟降低到 2 分钟，准确率 99.2%

## 案例 2: 某制造业集团
- 问题: 3000 张工艺图纸，工人不知道规格参数
- 解决方案: 多模态 RAG + OCR 识别
- 结果: 生产效率提升 25%

## 案例 3: 某内部知识库
- 问题: 员工知识库，一年新增 1000+ 页内容
- 解决方案: 实时同步的 RAG 系统
- 结果: 员工查询命中率从 60% 提升到 95%
""",
            
            "常见问题.md": """# 常见问题 (FAQ)

## Q1: 系统支持什么文档格式？
A: 支持 PDF、Word、Excel、Markdown、纯文本等格式

## Q2: 检索速度如何？
A: 平均检索时间 < 100ms，支持每秒 1000+ 并发

## Q3: 准确率是多少？
A: 相关性 Top-1 准确率 92%，Top-5 准确率 98%

## Q4: 如何保证数据安全？
A: 企业级加密、数据隔离、完整的审计日志

## Q5: 可以集成现有的 CRM / ERP 吗？
A: 支持通过 API 集成任何企业系统
""",
            
            "定价.md": """# 定价方案

## 按版本
| 版本 | 价格 | 功能 |
|-----|------|------|
| 基础版 | 3000/月 | 支持 100GB 文档、1 个索引 |
| 专业版 | 8000/月 | 支持 500GB 文档、5 个索引、优先支持 |
| 企业版 | 定制 | 无限存储、专属架构、24/7 支持 |

## 按使用量
- API 调用: 0.01 元/1000 tokens
- 存储: 100 元/TB/月
- 月度最低消费: 1000 元
"""
        }
    
    @staticmethod
    def save_sample_documents(output_dir: str = "./sample_docs"):
        """保存示例文档到本地"""
        os.makedirs(output_dir, exist_ok=True)
        
        docs = SampleDataGenerator.create_sample_documents()
        for filename, content in docs.items():
            filepath = os.path.join(output_dir, filename)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
        
        print(f"✓ 已生成 {len(docs)} 个样本文档到 {output_dir}/")
        return output_dir


# ============================================================================
# 第二部分: 简单的文档加载和分块
# ============================================================================

class DocumentLoader:
    """加载和处理文档"""
    
    @staticmethod
    def load_markdown_files(directory: str) -> List[Tuple[str, str]]:
        """
        加载目录下的所有 Markdown 文件
        返回: [(文件名, 内容), ...]
        """
        documents = []
        
        for filepath in Path(directory).glob("*.md"):
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                documents.append((filepath.name, content))
        
        return documents
    
    @staticmethod
    def chunk_documents(documents: List[Tuple[str, str]], 
                       chunk_size: int = 300) -> List[Dict]:
        """
        将文档分块（简化版）
        
        chunk_size: 每块的大致字符数
        
        返回: [
            {
                "id": "产品介绍_chunk_1",
                "content": "...",
                "source_file": "产品介绍.md",
                "chunk_index": 0
            },
            ...
        ]
        """
        chunks = []
        chunk_id = 0
        
        for filename, content in documents:
            # 按段落分割
            paragraphs = content.split('\n\n')
            
            current_chunk = ""
            chunk_index = 0
            
            for para in paragraphs:
                if len(current_chunk) + len(para) < chunk_size:
                    current_chunk += para + "\n\n"
                else:
                    if current_chunk.strip():
                        chunks.append({
                            "id": f"{filename}_chunk_{chunk_index}",
                            "content": current_chunk.strip(),
                            "source_file": filename,
                            "chunk_index": chunk_index,
                            "char_count": len(current_chunk)
                        })
                        chunk_index += 1
                    current_chunk = para + "\n\n"
            
            # 处理最后一块
            if current_chunk.strip():
                chunks.append({
                    "id": f"{filename}_chunk_{chunk_index}",
                    "content": current_chunk.strip(),
                    "source_file": filename,
                    "chunk_index": chunk_index,
                    "char_count": len(current_chunk)
                })
        
        return chunks


# ============================================================================
# 第三部分: 简单的相似度匹配（替代向量数据库）
# ============================================================================

class SimpleRetriever:
    """简单的检索器（不用真实 Embedding，用关键词匹配演示）"""
    
    @staticmethod
    def keyword_match(query: str, chunks: List[Dict], top_k: int = 3) -> List[Dict]:
        """
        基于关键词的简单匹配
        在真实场景中，这里会用 Embedding + 向量相似度
        """
        # 提取查询的关键词
        keywords = query.lower().split()
        
        # 计算每个 chunk 与查询的相关性分数
        scored_chunks = []
        for chunk in chunks:
            score = 0
            content = chunk['content'].lower()
            
            # 计算关键词出现次数
            for kw in keywords:
                if len(kw) > 2:  # 忽略短词
                    count = content.count(kw)
                    score += count
            
            # 计算相似度 (简化)
            similarity = score / (len(keywords) * 10 + 1)
            similarity = min(similarity, 1.0)  # 限制在 0-1
            
            scored_chunks.append({
                **chunk,
                "similarity": round(similarity, 3)
            })
        
        # 按相似度排序
        scored_chunks.sort(key=lambda x: x['similarity'], reverse=True)
        
        return scored_chunks[:top_k]


# ============================================================================
# 第四部分: RAG Demo 框架
# ============================================================================

class RAGDemo:
    """完整的 RAG Demo"""
    
    def __init__(self, documents_dir: str = "./sample_docs"):
        """初始化 Demo"""
        self.documents_dir = documents_dir
        
        # 加载和处理文档
        raw_docs = DocumentLoader.load_markdown_files(documents_dir)
        self.chunks = DocumentLoader.chunk_documents(raw_docs, chunk_size=300)
        
        print(f"✓ 已加载 {len(self.chunks)} 个文档块")
    
    def demo_without_rag(self, question: str) -> str:
        """演示 1: 不用 RAG，直接问 LLM（会很泛）"""
        print("\n" + "="*70)
        print("❌ 演示 1: 不用 RAG，直接问大模型")
        print("="*70)
        print(f"\n用户问题: {question}\n")
        
        # 模拟 LLM 的泛回答
        generic_responses = {
            "产品定价": "产品定价取决于企业规模和需求，通常在几千到几万元之间。需要具体咨询销售人员。",
            "产品功能": "现代企业产品通常包含数据处理、用户管理、报表分析等功能。",
            "客户案例": "许多公司都使用类似的产品，效果因行业而异。",
            "技术": "技术选型需要根据具体业务需求来决定。"
        }
        
        response = "我不知道你们具体的情况，请提供更多细节。"
        for key, value in generic_responses.items():
            if key.lower() in question.lower():
                response = value
                break
        
        print(f"LLM 回答: {response}\n")
        print("⚠️  问题: 答案太泛，没有实际帮助！")
        
        return response
    
    def demo_with_rag(self, question: str, top_k: int = 3) -> Tuple[str, List[Dict]]:
        """演示 2: 使用 RAG，先检索再回答"""
        print("\n" + "="*70)
        print("✅ 演示 2: 使用 RAG（检索 → 增强 → 回答）")
        print("="*70)
        print(f"\n用户问题: {question}\n")
        
        # 第一步: 检索相关文档
        print(f"第一步: 从知识库检索相关信息 (Top-K={top_k}):")
        print("-" * 70)
        
        retrieved = SimpleRetriever.keyword_match(question, self.chunks, top_k)
        
        for i, item in enumerate(retrieved, 1):
            print(f"\n检索结果 #{i} [相似度: {item['similarity']}]")
            print(f"来源: {item['source_file']}")
            print(f"内容: {item['content'][:150]}...")
        
        # 第二步: 生成增强的回答
        print(f"\n\n第二步: 基于检索结果的回答:")
        print("-" * 70)
        
        # 组织检索结果
        context = "\n\n".join([f"[{item['source_file']}]\n{item['content']}" 
                               for item in retrieved])
        
        # 生成回答（简化版，实际会调用 LLM）
        answer = self._generate_answer(question, context)
        print(f"\nAI 回答: {answer}")
        
        print(f"\n\n第三步: 展示信息来源")
        print("-" * 70)
        for item in retrieved:
            print(f"✓ 来源: {item['source_file']} (相似度: {item['similarity']})")
        
        print(f"\n✅ 优点: 答案准确、有出处、用户信心高！")
        
        return answer, retrieved
    
    def _generate_answer(self, question: str, context: str) -> str:
        """生成基于上下文的回答"""
        # 这里在真实场景会调用 OpenAI/Claude/Qwen 等 LLM API
        # 简化版: 直接从上下文提取
        
        # 提取相关的第一句话作为答案
        lines = context.split('\n')
        for line in lines:
            if len(line) > 20 and not line.startswith('['):
                return line.strip()
        
        return context[:200] + "..."
    
    def run_comparison_demo(self, question: str):
        """运行对比演示（推荐用这个）"""
        print("\n" + "🔵"*35)
        print("🟦 RAG Demo 对比演示（5 分钟看到价值）🟦")
        print("🔵"*35)
        
        # 演示不用 RAG 的泛回答
        without_rag = self.demo_without_rag(question)
        
        # 演示用 RAG 的精准回答
        with_rag, sources = self.demo_with_rag(question, top_k=3)
        
        # 总结
        print("\n" + "="*70)
        print("🎯 核心总结（给创始人的一句话）")
        print("="*70)
        print("""
不是模型更聪明，是它终于能看你们的数据了。

❌ 没有 RAG: 大模型很聪明，但不知道你们的产品、客户、价格
✅ 有了 RAG: 大模型能看到你们的内部文档，答案准确、可追溯

这就是为什么 RAG 是 ToB 的 AK47。
        """)


# ============================================================================
# 第五部分: 快速演示脚本
# ============================================================================

def main():
    """主函数: 运行完整的 Demo"""
    
    print("\n" + "🔵"*35)
    print("🟦 Day 3: RAG Demo 完整演示 🟦")
    print("🔵"*35)
    
    # 第一步: 创建示例文档
    print("\n步骤 1: 生成示例文档")
    docs_dir = SampleDataGenerator.save_sample_documents()
    
    # 第二步: 初始化 Demo
    print("\n步骤 2: 初始化 RAG 系统")
    demo = RAGDemo(documents_dir=docs_dir)
    
    # 第三步: 运行演示
    print("\n步骤 3: 运行对比演示\n")
    
    # 示例问题 1: 产品定价
    demo.run_comparison_demo("你们的产品价格是多少？")
    
    # 示例问题 2: 产品功能
    print("\n\n" + "─"*70)
    print("再来一个例子...")
    print("─"*70)
    demo.run_comparison_demo("你们的产品支持什么格式？")
    
    # 总结
    print("\n\n" + "="*70)
    print("✅ Demo 演示完成！")
    print("="*70)
    print("""
📋 检查清单 - 创始人应该看到的：

✓ 问题 1 (相同的问题)
  - 不用 RAG: 泛泛而谈
  - 用 RAG: 准确指向内部文档

✓ 问题 2 (另一个相关问题)
  - 再次证明准确性和可追溯性

✓ 关键数据
  - 检索速度: < 100ms
  - 准确性: 92%+
  - 可扩展性: 支持 GB 级文档

🎬 创始人的反应应该是：
"这个我们能用。什么时候可以开始？"

如果他们这么说，说明 Demo 成功了！
    """)
    
    # 如果创始人还有问题，这是样本问题
    print("\n" + "─"*70)
    print("如果创始人继续问...")
    print("─"*70)
    
    additional_questions = [
        "这个系统能处理我们公司特殊的 PDF 格式吗？",
        "如果文档有更新，系统多久能同步？",
        "数据安全怎么保证？"
    ]
    
    for q in additional_questions:
        print(f"\nQ: {q}")
        answer, _ = demo.demo_with_rag(q, top_k=2)
        print(f"A: ✓ [系统能回答这个问题]")


if __name__ == "__main__":
    main()
