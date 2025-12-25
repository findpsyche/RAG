# Wheel系统 - 完整项目结构说明

```
wheel1/
│
├── wheel1.py                           ★ 主程序入口
│   └── WheelSystem: 系统核心类
│   └── WheelSystemConfig: 配置类
│
├── __init__.py                         项目包初始化
│
├── wheel_architecture.md               系统架构文档（完整设计）
│
├── core/                               核心模块
│   ├── __init__.py
│   ├── modes.py                        ★ 三种处理模式定义
│   │   ├── ProcessingMode: 枚举(efficiency/balanced/precision)
│   │   └── ModeConfig: 模式配置库
│   ├── pipeline.py                     ★ 数据处理管道
│   │   ├── DataProcessingPipeline: 主处理流程
│   │   └── ProcessResult: 结果数据类
│   └── engine.py                       ★ 检索引擎
│       ├── RetrievalEngine: 统一检索接口
│       ├── RetrievalStrategy: 检索策略枚举
│       └── 支持: BM25/向量/混合/高级RAG
│
├── processors/                         处理模块
│   ├── __init__.py
│   ├── document_processor.py           ★ 文档处理器
│   │   ├── TextExtractor: 文本提取基类
│   │   ├── PDFExtractor: PDF提取
│   │   ├── DocXExtractor: Word提取
│   │   ├── ImageExtractor: OCR提取(支持3种OCR引擎)
│   │   └── DocumentProcessor: 统一接口
│   ├── embedding.py                    ★ 嵌入服务
│   │   ├── EmbeddingProvider: 基类
│   │   ├── OpenAIEmbedding: OpenAI集成
│   │   ├── SentenceTransformerEmbedding: 本地模型
│   │   └── EmbeddingService: 统一接口(支持缓存)
│   └── chunking.py                     分块策略(计划)
│
├── storage/                            存储层
│   ├── __init__.py
│   ├── vector_store.py                 ★ 向量+数据库存储
│   │   ├── CacheManager: Redis缓存管理
│   │   ├── VectorStoreBackend: 向量存储基类
│   │   ├── LocalVectorStore: 本地存储(开发)
│   │   ├── MilvusVectorStore: Milvus集成
│   │   ├── VectorStore: 统一接口
│   │   └── DatabaseConnector: PostgreSQL/MongoDB
│   ├── database.py                     数据库操作(计划)
│   └── cache.py                        缓存操作(计划)
│
├── agents/                             Agent系统
│   ├── __init__.py
│   ├── mcp_integration.py              ★ MCP/Skills集成
│   │   ├── Skill: 技能基类
│   │   ├── SkillDefinition: 技能定义
│   │   ├── SkillRegistry: 技能注册表
│   │   ├── create_default_skills(): 6个预定义技能
│   │   ├── MCPServer: MCP服务器
│   │   └── 支持: OpenAI Tools / Claude Tools
│   ├── base_agent.py                   Agent基类(计划)
│   └── skills.py                       技能库(计划)
│
├── api/                                API层
│   ├── __init__.py
│   ├── main.py                         ★ FastAPI应用
│   │   ├── create_app(): 应用工厂
│   │   ├── 18个API端点(详见下文)
│   │   └── 支持: 文档/查询/模式/监控/管理
│   ├── routes.py                       路由定义(计划)
│   └── schemas.py                      数据模型(计划)
│
├── monitoring/                         监控和评估
│   ├── __init__.py
│   ├── metrics.py                      ★ 性能指标和A/B测试
│   │   ├── MetricsCollector: 指标收集
│   │   ├── MetricRecord: 指标记录
│   │   └── ABTestFramework: A/B测试框架
│   ├── evaluation.py                   评估指标(计划)
│   └── ab_test.py                      A/B测试(计划)
│
├── utils/                              工具函数
│   ├── __init__.py
│   ├── logging_config.py               日志配置
│   └── helpers.py                      辅助函数
│
├── tests/                              测试
│   ├── __init__.py
│   ├── test_modes.py                   模式测试
│   ├── test_pipeline.py                管道测试
│   ├── test_api.py                     API测试
│   └── test_integration.py             集成测试
│
├── examples.py                         ★ 8个完整使用示例
│
├── requirements.txt                    ★ 依赖清单
│
├── docker-compose.yml                  ★ Docker编排
│   └── 包含: PostgreSQL + Redis + Milvus + API服务
│
├── Dockerfile                          Docker镜像
│
├── README.md                           ★ 项目文档
│
└── .env.example                        环境变量示例
```

---

## 核心概念理解

### 1. 三种处理模式

| 维度 | 高效(Efficiency) | 中效(Balanced) | 低效(Precision) |
|------|----------------|--------------|-----------------|
| **延迟** | 100-300ms | 500ms-2s | 2-10s |
| **召回率** | 40-60% | 70-80% | 90-95%+ |
| **成本** | 极低 | 中等 | 高 |
| **OCR** | Mistral 3 | Paddle | GPT-4V |
| **嵌入** | MiniLM | MPNet | text-embedding-3-large |
| **检索** | BM25 | 混合 | 高级RAG |
| **场景** | 客服、MVP | 一般企业 | 法律、医疗、金融 |

### 2. 数据流转流程

```
用户输入
  ↓
[API接收] → 参数验证
  ↓
[模式选择] → 切换处理配置
  ↓
[处理管道]
  ├→ 文档处理器 (多模态提取)
  ├→ 分块器 (语义分块)
  ├→ 嵌入器 (向量化)
  └→ 存储器 (向量DB + 关系DB)
  ↓
[检索引擎]
  ├→ BM25检索
  ├→ 向量检索
  ├→ 混合检索
  ├→ 高级RAG (HyDE/知识图谱)
  └→ 重排 (Cross-encoder)
  ↓
[结果处理]
  ├→ 缓存存储
  ├→ 指标记录
  └→ 响应返回
```

### 3. 存储架构

```
热数据层 (Redis) → 1小时TTL
  ↓缓存未命中
向量层 (Milvus) → 向量相似度查询
  ↓
冷数据层 (PostgreSQL) → 完整数据存储
  └→ documents表 (文档元数据)
  └→ chunks表 (文本块)
  └→ embeddings表 (向量ID映射)
  └→ interactions表 (用户查询历史)
  └→ metrics表 (性能数据)
```

---

## API端点完整列表

### 健康检查
- `GET /health` - 系统健康检查

### 文档管理
- `POST /api/v1/documents/upload` - 上传文档
- `GET /api/v1/documents/{doc_id}` - 获取文档详情(计划)

### 查询
- `POST /api/v1/query` - 执行同步查询
- `POST /api/v1/query/stream` - 流式查询

### 模式管理
- `GET /api/v1/modes` - 列出所有模式
- `POST /api/v1/mode/switch` - 切换模式
- `GET /api/v1/mode/current` - 获取当前模式

### 监控
- `GET /api/v1/metrics` - 获取详细指标
- `GET /api/v1/metrics/summary` - 指标摘要

### 配置
- `GET /api/v1/config` - 获取系统配置

### 管理
- `POST /api/v1/admin/clear-cache` - 清除缓存
- `GET /api/v1/admin/stats` - 获取统计信息

### 根路径
- `GET /` - API信息

---

## 预定义Skills (MCP)

1. **Document Ingestion** - 文档摄入 (DATA_PROCESSING)
2. **Semantic Search** - 语义搜索 (RETRIEVAL)
3. **Text Extraction** - 文本提取 (DATA_PROCESSING)
4. **Image Understanding** - 图像理解 (DATA_PROCESSING)
5. **Knowledge Graph Building** - 知识图谱 (KNOWLEDGE_MANAGEMENT)
6. **Mode Switch** - 模式切换 (INTEGRATION)

每个Skill都支持:
- OpenAI Tools格式导出
- Claude Tools格式导出
- 异步执行
- 输入/输出Schema验证

---

## 快速开始命令

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 启动完整系统(Docker)
docker-compose up -d

# 3. 启动API服务(本地)
python wheel1.py

# 4. 运行示例
python examples.py

# 5. 运行测试
pytest tests/ -v

# 6. 访问API文档
# http://localhost:8000/docs
```

---

## 扩展点

### 添加新的OCR引擎
编辑 `processors/document_processor.py`:
```python
class MyOCRExtractor(TextExtractor):
    def extract(self, file_path: str) -> str:
        # 实现
        pass
```

### 添加新的向量数据库
编辑 `storage/vector_store.py`:
```python
class MyVectorDB(VectorStoreBackend):
    def add_vector(self, ...): ...
    def search(self, ...): ...
```

### 添加新的LLM提供商
编辑 `processors/embedding.py`:
```python
class MyLLMEmbedding(EmbeddingProvider):
    def embed(self, texts: List[str]): ...
```

### 添加新的检索策略
编辑 `core/engine.py`:
```python
class MyRetrievalEngine(RetrievalEngine):
    def _retrieve_custom(self, query, top_k): ...
```

---

## 性能调优建议

1. **缓存优化**
   - 调整Redis TTL (默认3600s)
   - 监控缓存命中率
   - 预热热查询

2. **向量优化**
   - 定期重计算向量
   - 监控向量漂移
   - 使用向量压缩

3. **模型选择**
   - 根据场景选择合适的模型大小
   - 评估成本vs性能trade-off
   - 考虑模型微调

4. **并发控制**
   - 调整max_workers
   - 使用连接池
   - 限制batch_size

5. **监控告警**
   - 监控p95/p99延迟
   - 跟踪错误率
   - 追踪成本趋势

---

## 故障排查

| 问题 | 原因 | 解决方案 |
|------|------|--------|
| 查询慢 | 缓存未命中、向量搜索低效 | 启用缓存、优化top_k |
| 召回率低 | 模式选择不当 | 切换到precision模式 |
| 成本高 | 频繁调用API | 启用缓存、批处理 |
| OOM错误 | 向量维度过高、数据过大 | 降低batch_size、压缩向量 |
| 数据库满 | 持久化数据过多 | 实施数据过期策略 |

---

## 文件修改历史

| 文件 | 大小 | 功能 | 优先级 |
|------|------|------|--------|
| wheel1.py | ~300行 | 系统核心 | ⭐⭐⭐⭐⭐ |
| core/modes.py | ~200行 | 模式定义 | ⭐⭐⭐⭐⭐ |
| core/pipeline.py | ~250行 | 处理管道 | ⭐⭐⭐⭐⭐ |
| core/engine.py | ~350行 | 检索引擎 | ⭐⭐⭐⭐⭐ |
| processors/document_processor.py | ~300行 | 文档处理 | ⭐⭐⭐⭐ |
| processors/embedding.py | ~200行 | 嵌入服务 | ⭐⭐⭐⭐ |
| storage/vector_store.py | ~350行 | 存储层 | ⭐⭐⭐⭐ |
| api/main.py | ~300行 | API层 | ⭐⭐⭐⭐ |
| agents/mcp_integration.py | ~400行 | MCP/Skills | ⭐⭐⭐⭐ |
| monitoring/metrics.py | ~250行 | 监控 | ⭐⭐⭐ |

**总代码量**: ~2,900行核心代码 + 文档

---

## 下一步

1. ✅ 完成核心架构和三种模式
2. ✅ 实现完整的API和web界面
3. ✅ 集成MCP和Skills系统
4. ✅ 添加性能监控和A/B测试
5. 🔄 **待完成**:
   - LLM微调管道
   - Graph RAG高级实现
   - 多代理协调系统
   - Kubernetes部署配置
   - 完整的测试套件

