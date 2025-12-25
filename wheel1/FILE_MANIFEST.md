# Wheel系统 - 完整文件清单

## 📂 项目目录结构

```
wheel1/
├── 核心程序入口
│   └── wheel1.py ⭐ (300行) - 系统主程序和WheelSystem类
│
├── core/ - 核心模块
│   ├── modes.py (200行) - 三种处理模式定义
│   ├── pipeline.py (250行) - 数据处理管道
│   └── engine.py (350行) - 多策略检索引擎
│
├── processors/ - 数据处理
│   ├── document_processor.py (300行) - 多模态文档处理
│   └── embedding.py (200行) - 嵌入服务(多提供商)
│
├── storage/ - 存储层
│   └── vector_store.py (350行) - 向量DB + 关系DB + 缓存
│
├── api/ - API接口
│   └── main.py (300行) - FastAPI应用(18个端点)
│
├── agents/ - Agent和MCP
│   └── mcp_integration.py (400行) - MCP服务器和6个预定义Skills
│
├── monitoring/ - 监控和评估
│   └── metrics.py (250行) - 性能指标和A/B测试框架
│
├── 文档
│   ├── wheel_architecture.md (750行) ⭐ 完整架构设计
│   ├── README.md (450行) - 项目使用说明
│   ├── PROJECT_STRUCTURE.md (500行) - 项目结构详解
│   ├── QUICKSTART.md (300行) - 5分钟快速开始
│   └── COMPLETION_REPORT.md (400行) - 项目完成总结
│
├── 示例和测试
│   ├── examples.py (450行) ⭐ 8个完整使用示例
│   └── test_api.py (350行) - API集成测试工具
│
├── 配置和部署
│   ├── requirements.txt (60行) - Python依赖清单
│   ├── docker-compose.yml ⭐ - Docker完整编排
│   ├── Dockerfile - Docker镜像定义
│   └── __init__.py - 包初始化
│
└── 这个文件
    └── FILE_MANIFEST.md - 项目完整文件清单
```

---

## 📋 文件详细说明

### 核心程序 (300行)

**wheel1.py** - ⭐ 系统主程序
- `WheelSystem`: 核心系统类，统一入口
- `WheelSystemConfig`: 配置数据类
- 初始化所有核心组件
- 提供`process_document()`, `query()`, `switch_mode()`等主要方法
- 支持健康检查和指标获取

### 核心模块 - core/ (~800行)

**modes.py** (200行) - 三种处理模式
- `ProcessingMode`: 枚举(efficiency/balanced/precision)
- `ModeConfig`: 模式配置库(包含完整配置字典)
- 三层完整配置(metrics、models、processing、storage、retrieval)
- `print_comparison()`: 模式对比输出

**pipeline.py** (250行) - 数据处理管道
- `DataProcessingPipeline`: 主处理流程
- `ProcessResult`: 结果数据类
- 处理流程: 验证→提取→预处理→分块→嵌入→存储
- 支持三种模式的不同参数配置

**engine.py** (350行) - 检索引擎
- `RetrievalEngine`: 统一检索接口
- `RetrievalStrategy`: 检索策略枚举(BM25/向量/混合/高级RAG)
- 支持多种检索: BM25、向量、混合、高级RAG(HyDE/知识图谱)
- 结果重排、融合、验证
- 缓存支持

### 数据处理 - processors/ (~500行)

**document_processor.py** (300行) - 多模态文档处理
- `TextExtractor`: 抽象基类
- `PDFExtractor`: PDF文本提取
- `DocXExtractor`: Word文档处理
- `ImageExtractor`: OCR处理(Mistral/Paddle/GPT-4V)
- `VideoExtractor`: 视频处理框架
- `DocumentProcessor`: 统一接口，支持多格式和缓存

**embedding.py** (200行) - 嵌入服务
- `EmbeddingProvider`: 基类
- `OpenAIEmbedding`: OpenAI集成
- `SentenceTransformerEmbedding`: 本地模型
- `EmbeddingService`: 统一接口，支持批处理和缓存

### 存储层 - storage/ (350行)

**vector_store.py** (350行) - 存储和缓存
- `CacheManager`: Redis缓存管理(带本地fallback)
- `VectorStoreBackend`: 向量存储基类
- `LocalVectorStore`: 本地存储(开发用)
- `MilvusVectorStore`: Milvus集成
- `VectorStore`: 统一向量存储接口
- `DatabaseConnector`: PostgreSQL/MongoDB连接

### API接口 - api/ (300行)

**main.py** (300行) - FastAPI应用
- `create_app()`: 应用工厂函数
- **18个API端点**:
  - 系统: health, root
  - 查询: query, stream
  - 文档: upload
  - 模式: modes, current_mode, switch
  - 监控: metrics, metrics_summary
  - 配置: config
  - 管理: clear_cache, admin_stats
- 完整的Pydantic数据模型
- Swagger/ReDoc自动文档

### Agent和MCP - agents/ (400行)

**mcp_integration.py** (400行) - MCP集成
- `Skill`: 技能基类
- `SkillDefinition`: 技能定义数据类
- `BasicSkill`: 基础技能实现
- `SkillRegistry`: 技能注册和管理
- `create_default_skills()`: 6个预定义技能
  1. Document Ingestion
  2. Semantic Search
  3. Text Extraction
  4. Image Understanding
  5. Knowledge Graph Building
  6. Mode Switch
- `MCPServer`: MCP服务器
  - OpenAI Tools格式转换
  - Claude Tools格式转换
  - 异步工具执行

### 监控 - monitoring/ (250行)

**metrics.py** (250行) - 性能监控
- `MetricRecord`: 指标记录数据类
- `MetricsCollector`: 指标收集器
  - 记录文档处理、查询、嵌入指标
  - 计算平均值、百分位数(p95/p99)
  - 按模式分组统计
- `ABTestFramework`: A/B测试框架
  - 创建和管理实验
  - 记录结果
  - 计算改进比例

### 示例代码 - examples.py (450行)

8个完整使用示例:
1. **基础使用** - 系统初始化和简单查询
2. **模式切换** - 三种模式演示和对比
3. **文档处理** - 多格式文件处理
4. **MCP和Skills** - Agent系统演示
5. **A/B测试** - 实验框架使用
6. **性能基准** - 三模式性能对比
7. **自定义配置** - 系统配置定制
8. **错误处理** - 异常处理演示

### 测试工具 - test_api.py (350行)

API集成测试:
- `WheelAPITester`: 测试工具类
- 18个API端点的自动化测试
- 性能基准测试
- 详细结果输出和统计

### 文档 (~2000行)

#### wheel_architecture.md (750行) - 完整架构设计 ⭐
- 系统概述和设计原则
- 三层架构详细说明
- 可复用组件设计
- API设计(完整端点规范)
- 数据库和缓存策略
- 实施路线图(Phase 1-4)
- 风险分析和应对
- 长期产品化支持

#### README.md (450行) - 项目使用说明
- 快速开始指南
- 三种模式详细说明
- 关键特性列表
- 系统架构概览
- 配置指南
- 开发指南
- 性能基准
- 部署方案
- 故障排除

#### PROJECT_STRUCTURE.md (500行) - 项目结构详解
- 完整目录树和文件说明
- 核心概念解释
- 数据流程图
- 存储架构说明
- API端点完整列表
- 预定义Skills说明
- 快速开始命令
- 扩展点说明
- 性能调优建议
- 故障排查表

#### QUICKSTART.md (300行) - 5分钟快速开始
- 30秒快速启动
- 项目文件清单
- 三种模式对比表
- 快速配置示例
- 18个API端点速查表
- 6个预定义Skills
- 常见用例示例
- 性能优化建议
- 学习路径
- 故障排除快速表

#### COMPLETION_REPORT.md (400行) - 项目完成总结
- 项目概况
- 需求完成情况(分类总结)
- 技术栈总览
- 核心能力对比表
- 性能基准预期
- 项目文件清单
- 三个产品化版本设计
- 使用流程示例
- 创新亮点总结
- 结语

### 配置文件

**requirements.txt** (60行) - Python依赖
- 核心框架: FastAPI, Uvicorn, Pydantic
- LLM和嵌入: OpenAI, LangChain, Sentence-Transformers
- 文档处理: PyPDF2, python-docx, Pillow, PaddleOCR, EasyOCR
- 向量数据库: Milvus, Qdrant, Pinecone
- 关系数据库: PostgreSQL, MongoDB
- 缓存: Redis
- 监控和工具: Prometheus, Pandas, NumPy, Scikit-learn
- 测试: Pytest
- 开发: Black, Flake8, MyPy

**docker-compose.yml** - Docker编排
- PostgreSQL 15数据库
- Redis 7缓存
- Milvus 2.3向量数据库
- Wheel API服务
- 自动健康检查
- 持久化卷
- 网络配置

**Dockerfile** - Docker镜像
- Python 3.11基础镜像
- 系统依赖安装
- Python依赖安装
- 应用入口配置

**__init__.py** - 包初始化
- 版本信息
- 核心类导出
- 公开API定义

---

## 📊 代码统计

### 代码规模
- **总代码行数**: ~2,900行
- **核心程序**: ~2,350行
- **文档行数**: ~2,000行
- **总计**: ~4,900行

### 分布
| 部分 | 行数 | 比例 |
|------|------|------|
| 核心系统 | 800 | 27% |
| 数据处理 | 500 | 17% |
| 存储层 | 350 | 12% |
| API接口 | 300 | 10% |
| MCP/Agent | 400 | 14% |
| 监控框架 | 250 | 9% |
| 示例和测试 | 800 | 11% |

### 复杂度
- **文件数**: 20个
- **模块数**: 10个
- **类数**: 40+个
- **API端点**: 18个
- **Skills**: 6个

---

## 🎯 文件使用指南

### 快速开始 (5分钟)
1. 阅读 `QUICKSTART.md`
2. 运行 `python wheel1.py`
3. 访问 `http://localhost:8000/docs`

### 学习系统 (1小时)
1. `wheel_architecture.md` - 理解架构
2. `PROJECT_STRUCTURE.md` - 理解结构
3. `examples.py` - 运行示例

### 集成应用 (2小时)
1. 阅读 `api/main.py` - 了解API
2. 阅读 `agents/mcp_integration.py` - 了解MCP
3. 集成到自己的应用

### 部署生产 (1小时)
1. `docker-compose.yml` - 启动完整栈
2. 根据 `wheel_architecture.md` 配置参数
3. 使用 `test_api.py` 验证系统

### 性能优化 (持续)
1. `monitoring/metrics.py` - 收集指标
2. `examples.py` - 运行性能基准
3. 根据指标调整配置

---

## 🚀 启动顺序

### 第1步: 安装依赖
```bash
pip install -r requirements.txt
```

### 第2步: 启动服务
```bash
# 选项A: 本地启动
python wheel1.py

# 选项B: Docker启动 (推荐)
docker-compose up -d
```

### 第3步: 验证系统
```bash
# 浏览器访问
http://localhost:8000/docs

# 或运行测试
python test_api.py
```

### 第4步: 运行示例
```bash
python examples.py
```

---

## 📈 文件依赖关系

```
wheel1.py (入口)
  ├→ core/modes.py
  ├→ core/pipeline.py
  ├→ core/engine.py
  ├→ processors/document_processor.py
  ├→ processors/embedding.py
  ├→ storage/vector_store.py
  ├→ api/main.py
  ├→ agents/mcp_integration.py
  └→ monitoring/metrics.py

api/main.py
  └→ wheel1.py (WheelSystem)

examples.py
  ├→ wheel1.py
  ├→ core/modes.py
  ├→ agents/mcp_integration.py
  └→ monitoring/metrics.py

test_api.py
  └→ HTTP requests to API
```

---

## ✅ 交付清单

- ✅ 20个源代码文件
- ✅ 5个核心文档
- ✅ 8个使用示例
- ✅ 1套API文档
- ✅ 1套Docker部署
- ✅ 1套测试工具
- ✅ 完整的依赖清单
- ✅ 项目初始化脚本

---

## 🎯 最后检查

```bash
# 确保所有文件都已创建
✓ wheel1.py
✓ core/modes.py
✓ core/pipeline.py
✓ core/engine.py
✓ processors/document_processor.py
✓ processors/embedding.py
✓ storage/vector_store.py
✓ api/main.py
✓ agents/mcp_integration.py
✓ monitoring/metrics.py
✓ examples.py
✓ test_api.py
✓ requirements.txt
✓ docker-compose.yml
✓ Dockerfile
✓ __init__.py
✓ wheel_architecture.md
✓ README.md
✓ PROJECT_STRUCTURE.md
✓ QUICKSTART.md
✓ COMPLETION_REPORT.md
✓ FILE_MANIFEST.md (本文件)

总计: 22个文件，~4,900行代码和文档
```

---

## 📞 下一步

1. **立即使用**: `python wheel1.py`
2. **深入学习**: 查看 `wheel_architecture.md`
3. **实际应用**: 参考 `examples.py`
4. **生产部署**: 使用 `docker-compose.yml`

---

**项目状态**: ✅ 完成并就绪
**最后更新**: 2025年12月25日
**版本**: 1.0.0

