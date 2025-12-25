# Wheel系统架构设计文档

## 1. 系统概述

**Wheel System** 是一个企业级、模块化的多模态数据处理和知识检索系统，支持三种可插拔的处理架构，满足从快速MVP验证到高精度生产部署的全流程需求。

### 核心设计原则
- **模块化与Wheel化**：可复用组件，支持动态组装和扩展
- **软件定义**：自动化工作流，最小化人工干预
- **数据驱动**：所有决策由指标和A/B测试指导
- **长期主义**：支持数据库长期存储、高并发查询、缓存优化

---

## 2. 三层架构模型

### 2.1 高效模式 (Efficiency Mode) - 快速MVP
**目标**：快速证明价值，低成本启动
- **召回率**：40-60%
- **延迟**：100-300ms
- **成本**：极低（OCR API调用最小化）
- **适用场景**：客服、快速分类、初期验证

**技术选型**：
- OCR：Mistral AI OCR 3 (轻量级) / EasyOCR
- 嵌入模型：快速轻量级模型 (e.g., `sentence-transformers/all-MiniLM-L6-v2`)
- 向量存储：本地或简单Redis
- LLM：OpenAI GPT-4 Turbo / Mistral 7B

**关键模块**：
- 快速文本提取（无复杂处理）
- 简单向量化和相似度检索
- 单轮对话处理
- 基础缓存层

---

### 2.2 中效模式 (Balanced Mode) - 一般企业场景
**目标**：平衡效率和质量
- **召回率**：70-80%
- **延迟**：500ms-2s
- **成本**：中等
- **适用场景**：财务分析、HR问询、通用企业知识库

**技术选型**：
- OCR：Paddle OCR + GPU优化
- 嵌入模型：中等规模 (e.g., `sentence-transformers/all-mpnet-base-v2`)
- 向量存储：Milvus / Weaviate
- LLM：GPT-4 / Claude 3 Sonnet

**关键模块**：
- 多阶段文本处理（预处理、分块、重排）
- 混合检索（向量+BM25）
- 多轮对话和上下文管理
- Redis热数据缓存

---

### 2.3 低效模式 (Precision Mode) - 高精度要求
**目标**：最大化准确性，不容出错
- **召回率**：90-95%+
- **延迟**：2-10s（可接受）
- **成本**：高（优先质量）
- **适用场景**：法律合规、医疗、工业生产、金融风控

**技术选型**：
- OCR：GPT-4V + 专业医疗/法律OCR
- 嵌入模型：高性能模型 (e.g., `Alibaba-NLP/gte-large`, `OpenAI text-embedding-3-large`)
- 向量存储：Pinecone / Qdrant + 多副本
- LLM：GPT-5 / Claude 3 Opus + 微调
- RAG优化：Graph RAG、多步推理、知识图谱

**关键模块**：
- 深度多模态理解（文本+图像+表格）
- 高级RAG（Graph RAG、HyDE、Re-Rank）
- 复杂推理链（Chain-of-Thought、Self-Consistency）
- 知识图谱检索
- 结果验证和高置信度保证

---

## 3. 核心可复用组件

### 3.1 数据处理管道 (Data Pipeline)
```
原始数据 → 预处理器 → 分块器 → 嵌入器 → 存储器 → 查询引擎
```

**组件**：
- `DocumentProcessor`: 支持PDF、Word、图像、视频
- `ChunkingStrategy`: 不同分块策略（固定大小、语义、层级）
- `EmbeddingService`: 多模型支持的嵌入层
- `VectorStore`: 统一向量存储接口（支持多个后端）

### 3.2 检索引擎 (Retrieval Engine)
- `BM25Retriever`: 精准关键词匹配
- `VectorRetriever`: 向量相似度检索
- `HybridRetriever`: 混合检索（向量+BM25）
- `RerankingModule`: 结果重排和精化

### 3.3 LLM推理层 (LLM Inference Layer)
- `LLMAgent`: 通用LLM调用接口
- `ReasoningEngine`: 多步推理、CoT
- `FunctionCalling`: 工具调用和函数执行
- `PromptTemplates`: 可复用的提示模板库

### 3.4 缓存和存储层 (Cache & Storage Layer)
- `RedisCache`: 热数据缓存
- `DatabaseConnector`: 多数据库支持（PostgreSQL、MongoDB）
- `VectorDatabase`: 向量数据库集成

### 3.5 监控和评估 (Monitoring & Evaluation)
- `MetricsCollector`: 性能指标收集
- `ABTestFramework`: A/B测试框架
- `EvaluationMetrics`: 召回率、精确度、延迟等

---

## 4. API设计

### 4.1 核心API端点

```
POST /api/v1/process
- 输入：多模态文档、处理模式选择（efficiency/balanced/precision）
- 输出：处理结果、嵌入向量、元数据

POST /api/v1/query
- 输入：查询文本、模式、模型参数
- 输出：排序结果、相关文档、推理过程

POST /api/v1/train
- 输入：标注数据、模型配置
- 输出：训练结果、性能指标

GET /api/v1/metrics
- 输出：系统性能指标、缓存命中率、成本统计

POST /api/v1/agent/execute
- 输入：Agent配置、任务描述
- 输出：执行结果、执行日志
```

### 4.2 Skills系统设计
每个可复用功能作为一个Skill：
- `DocumentIngestionSkill`：文档摄入
- `SemanticSearchSkill`：语义搜索
- `TextExtractionSkill`：文本提取
- `ImageUnderstandingSkill`：图像理解
- `KnowledgeGraphBuildingSkill`：知识图谱构建

### 4.3 MCP集成 (Model Context Protocol)
- 支持OpenAI native tools和Claude tools
- 动态工具注册和版本管理
- 工具执行环境隔离

---

## 5. 数据库和缓存策略

### 5.1 多层存储架构

```
┌─────────────────────┐
│   Redis缓存层       │ (热数据，1小时TTL)
└──────────┬──────────┘
           │
┌──────────▼──────────┐
│  向量数据库          │ (Milvus/Qdrant/Pinecone)
│  - 文档向量         │
│  - 查询向量         │
└──────────┬──────────┘
           │
┌──────────▼──────────┐
│  PostgreSQL/MongoDB │ (永久存储)
│  - 原始文档         │
│  - 处理元数据       │
│  - 用户交互历史     │
│  - 性能指标         │
└─────────────────────┘
```

### 5.2 Redis缓存策略
- **查询缓存**：Top-K热查询缓存（击中率优化）
- **计算缓存**：向量计算结果缓存
- **会话缓存**：用户对话上下文

### 5.3 数据库设计
关键表：
- `documents`：文档及处理元数据
- `chunks`：文档分块及向量ID
- `embeddings`：预计算的向量（同步至向量数据库）
- `interactions`：用户查询和结果记录
- `metrics`：性能指标和成本数据

---

## 6. 实施路线图

### Phase 1: MVP (2-4周)
1. 实现高效模式基础版本
2. 构建简单的API和Web界面
3. 快速验证业务价值

### Phase 2: 中效模式 (4-6周)
1. 集成中等规模模型和更好的嵌入器
2. 实现混合检索
3. 部署Redis缓存层
4. 建立基础性能监控

### Phase 3: 生产化 (6-8周)
1. 实现低效（高精度）模式
2. 部署向量数据库和PostgreSQL
3. 实现完整的监控、告警、日志系统
4. 执行性能基准测试

### Phase 4: 优化和微调 (持续)
1. LLM微调管道
2. RAG优化（Graph RAG、多步推理）
3. 数据驱动的A/B测试
4. 成本优化和性能调优

---

## 7. 潜在风险与应对

| 风险 | 影响 | 应对措施 |
|------|------|---------|
| **向量漂移** | 检索精度下降 | 定期重新计算关键向量，监控相似度分布 |
| **成本爆炸** | 超预算 | 实施速率限制、查询缓存、批处理 |
| **延迟抖动** | 用户体验差 | 使用流式响应、异步处理、CDN缓存 |
| **召回率不稳定** | 服务质量不一致 | A/B测试框架、自动阈值调整 |
| **模型幻觉** | 错误信息输出 | 置信度评分、结果验证、知识检索引用 |
| **数据隐私泄露** | 安全风险 | 数据加密、访问控制、审计日志 |

---

## 8. 长期产品化支持

### 8.1 可扩展性
- 水平扩展：支持多节点向量数据库和LLM推理集群
- 垂直扩展：更大模型、更高精度组件

### 8.2 持续改进
- **数据收集**：自动记录用户反馈、模型评分
- **模型升级**：定期评估新模型和架构
- **成本控制**：按模式选择最优成本/性能比

### 8.3 行业适配
预留接口支持不同行业的定制化需求：
- **法律**：合规检查、条款分析
- **医疗**：医学知识库、临床推荐
- **金融**：风险评估、合规监查

---

## 9. 项目结构

```
wheel1/
├── wheel1.py                      # 主程序入口
├── config/
│   ├── __init__.py
│   ├── config.yaml               # 配置文件
│   └── models.py                 # 模型配置
├── core/
│   ├── __init__.py
│   ├── modes.py                  # 三种模式定义
│   ├── pipeline.py               # 数据处理管道
│   └── engine.py                 # 检索引擎
├── processors/
│   ├── __init__.py
│   ├── document_processor.py      # 文档处理
│   ├── embedding.py              # 嵌入层
│   └── chunking.py               # 分块策略
├── storage/
│   ├── __init__.py
│   ├── vector_store.py           # 向量存储
│   ├── database.py               # 数据库连接
│   └── cache.py                  # 缓存层
├── agents/
│   ├── __init__.py
│   ├── base_agent.py             # 基础Agent
│   ├── mcp_integration.py        # MCP集成
│   └── skills.py                 # Skills定义
├── api/
│   ├── __init__.py
│   ├── main.py                   # FastAPI应用
│   ├── routes.py                 # API路由
│   └── schemas.py                # 数据模型
├── monitoring/
│   ├── __init__.py
│   ├── metrics.py                # 指标收集
│   ├── evaluation.py             # 评估框架
│   └── ab_test.py                # A/B测试
├── utils/
│   ├── __init__.py
│   ├── logging_config.py         # 日志配置
│   └── helpers.py                # 辅助函数
├── tests/
│   ├── __init__.py
│   ├── test_modes.py             # 模式测试
│   ├── test_api.py               # API测试
│   └── test_pipeline.py          # 管道测试
├── requirements.txt              # 依赖
├── README.md                     # 项目文档
└── docker-compose.yml            # Docker配置
```

---

## 10. 关键指标定义

### 性能指标
- **延迟 (Latency)**：查询到结果的平均时间
- **吞吐 (Throughput)**：每秒处理查询数
- **召回率 (Recall)**：返回相关结果的比例
- **精确度 (Precision)**：返回结果中有效的比例

### 业务指标
- **成本 (Cost)**：每次查询平均成本
- **缓存命中率 (Cache Hit Rate)**：缓存命中占比
- **用户满意度 (Satisfaction)**：人工评分

### 系统健康
- **可用性 (Availability)**：服务正常运行时间比例
- **错误率 (Error Rate)**：处理失败比例

