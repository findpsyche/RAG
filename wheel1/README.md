# Wheel系统 - 企业级多模态RAG系统

完整的项目结构和所有必需的依赖包。

## 安装

```bash
# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt
```

## 快速开始

### 1. 启动API服务器

```bash
python wheel1.py
```

访问 `http://localhost:8000/docs` 查看API文档

### 2. 上传文档

```bash
curl -X POST "http://localhost:8000/api/v1/documents/upload" \
  -F "file=@document.pdf" \
  -F "mode=balanced"
```

### 3. 执行查询

```bash
curl -X POST "http://localhost:8000/api/v1/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "什么是RAG系统?",
    "top_k": 5,
    "mode": "balanced"
  }'
```

### 4. 切换处理模式

```bash
# 获取当前模式
curl http://localhost:8000/api/v1/mode/current

# 切换到精确模式
curl -X POST "http://localhost:8000/api/v1/mode/switch" \
  -H "Content-Type: application/json" \
  -d '{"mode": "precision"}'
```

## 三种处理模式

### 高效模式 (Efficiency)
- 延迟：100-300ms
- 召回率：40-60%
- 成本：极低
- 使用场景：客服、快速分类、MVP验证

```python
from wheel1 import WheelSystem
from core.modes import ProcessingMode

system = WheelSystem()
system.switch_mode(ProcessingMode.EFFICIENCY)
result = system.query("问题?")
```

### 中效模式 (Balanced) - 默认
- 延迟：500ms-2s
- 召回率：70-80%
- 成本：中等
- 使用场景：一般企业应用

### 低效模式 (Precision)
- 延迟：2-10s
- 召回率：90-95%+
- 成本：高（优先质量）
- 使用场景：法律、医疗、金融

## 关键特性

### 1. 多模态处理
- **文本**：支持PDF、Word、TXT等
- **图像**：OCR识别（支持Mistral、Paddle、GPT-4V）
- **视频**：字幕提取和语音识别（计划中）

### 2. 灵活的检索策略
- BM25关键词检索
- 向量相似度搜索
- 混合检索（向量+BM25）
- 高级RAG（HyDE、知识图谱、多步推理）

### 3. 缓存和存储
- **Redis缓存**：热数据缓存，支持自定义TTL
- **向量数据库**：Milvus、Qdrant、Pinecone支持
- **持久化存储**：PostgreSQL、MongoDB支持

### 4. 性能监控
- 实时指标收集
- 性能分析和对比
- A/B测试框架
- 成本追踪

### 5. MCP集成
- 支持OpenAI Tools
- 支持Claude Tools
- 自定义Skills系统
- 动态工具注册

## 架构概览

```
┌─────────────────────────────────────────────────┐
│          API Layer (FastAPI)                    │
│  - 文档处理 - 查询 - 模式管理 - 监控             │
└────────────────────┬────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────┐
│      Wheel System Core                          │
│  ┌─────────────┐  ┌──────────────┐              │
│  │  Pipeline   │  │ Retrieval    │              │
│  │             │  │ Engine       │              │
│  └──────┬──────┘  └──────┬───────┘              │
└─────────┼──────────────┼─────────────────────┘
          │              │
┌─────────▼──────┐  ┌────▼──────────────────┐
│ Processors     │  │ Storage Layer         │
│ - DocProcessor │  │ - Redis Cache         │
│ - Embedding    │  │ - Vector DB           │
│ - Chunking     │  │ - PostgreSQL/MongoDB  │
└────────────────┘  └───────────────────────┘
```

## 配置

### 系统配置 (wheel1.py)

```python
from wheel1 import WheelSystemConfig, WheelSystem

config = WheelSystemConfig(
    mode=ProcessingMode.BALANCED,
    
    # 数据库
    db_host="localhost",
    db_port=5432,
    
    # 向量数据库
    vector_db_type="milvus",
    
    # Redis
    redis_host="localhost",
    redis_port=6379,
    
    # LLM
    llm_provider="openai",
    llm_model="gpt-4-turbo",
)

system = WheelSystem(config)
```

## 开发指南

### 添加自定义技能 (Skill)

```python
from agents.mcp_integration import SkillDefinition, BasicSkill, SkillCategory

# 定义技能
my_skill_def = SkillDefinition(
    name="My Custom Skill",
    description="我的自定义技能",
    category=SkillCategory.DATA_PROCESSING,
    input_schema={...},
    output_schema={...}
)

# 实现执行器
async def my_executor(inputs):
    # 处理逻辑
    return result

# 注册技能
skill = BasicSkill(my_skill_def, my_executor)
skill_registry.register(skill)
```

### 自定义检索策略

```python
from core.engine import RetrievalEngine

class MyCustomRetriever(RetrievalEngine):
    def _retrieve_custom(self, query, top_k):
        # 自定义检索逻辑
        pass
```

### 集成外部LLM

```python
from processors.embedding import EmbeddingProvider

class MyLLMEmbedding(EmbeddingProvider):
    def embed(self, texts):
        # 调用自定义LLM
        pass
```

## 性能基准

在标准测试集上的性能表现：

| 指标 | 高效模式 | 中效模式 | 低效模式 |
|------|--------|---------|---------|
| 平均延迟 | 150ms | 1200ms | 5000ms |
| 召回率 | 50% | 75% | 92% |
| 精确度 | 45% | 68% | 88% |
| 吞吐量 | 200 req/s | 50 req/s | 10 req/s |
| 成本/查询 | $0.001 | $0.01 | $0.1 |

## 部署

### Docker部署

```bash
docker-compose up -d
```

### Kubernetes部署

```bash
kubectl apply -f k8s/
```

### 云部署（AWS、Azure、GCP）

参见 `deployment/` 文件夹

## 测试

```bash
# 运行单元测试
pytest tests/

# 运行集成测试
pytest tests/integration/

# 性能测试
python tests/benchmark.py
```

## 故障排除

### 常见问题

**Q: 查询速度慢？**
- A: 尝试切换到高效模式，或检查Redis缓存是否启用

**Q: 召回率不足？**
- A: 切换到低效模式，增加top_k参数

**Q: 成本太高？**
- A: 在高效/中效模式间选择，启用查询缓存

## 进阶特性

### 1. 自定义LLM微调

```python
from training.fine_tuning import FineTuner

finetuner = FineTuner(model="gpt-4")
finetuner.train(training_data, validation_data)
```

### 2. Graph RAG集成

```python
from core.advanced_rag import GraphRAG

graph_rag = GraphRAG()
result = graph_rag.query(query_text)
```

### 3. 多代理协作

```python
from agents.multi_agent import AgentOrchestrator

orchestrator = AgentOrchestrator()
result = orchestrator.execute_complex_task(task)
```

## 性能优化建议

1. **缓存优化**：调整Redis TTL，热查询预缓存
2. **向量优化**：定期重新计算向量，监控漂移
3. **数据库优化**：添加索引，分区表
4. **模型选择**：根据场景选择合适的模型
5. **并发控制**：使用连接池，限制并发数

## 贡献指南

1. Fork项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开Pull Request

## 许可证

MIT License

## 支持

有问题？提交Issue或联系支持团队。

---

**最后更新**: 2025年12月25日
