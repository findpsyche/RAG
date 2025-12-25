## 本地化 AI 部署与多 Agent 数据分析方案（0→1 指南）

> 适用场景：数据敏感企业（金融/医疗/政企）；全程本地，无云 API；模型与数据均在内网/本地磁盘。

### 一、环境与依赖（简述）
- Python 建议 3.10/3.11；使用 pyenv/conda 创建隔离环境。
- 配置 pip 国内镜像（示例，Linux/macOS：`~/.config/pip/pip.conf`；Windows：`%APPDATA%/pip/pip.ini`）：
  ```ini
  [global]
  index-url = https://pypi.tuna.tsinghua.edu.cn/simple
  extra-index-url = https://mirrors.aliyun.com/pypi/simple/
  timeout = 30
  ```
- 安装关键依赖（CPU 示例；GPU 可安装对应 CUDA 版 torch）：
  ```bash
  python -m pip install -U pip
  pip install "torch==2.3.1" transformers==4.41.1 \
              langchain==0.2.14 langchain-community==0.2.12 \
              langgraph==0.0.60 chromadb==0.5.3 \
              "llama-cpp-python[server]==0.2.86" sentence-transformers
  ```

### 二、本地模型部署
- 模型选择（合规、可商用版本）：Qwen2/1.5、Mistral、Llama-3 中文量化、Baichuan2；确认许可证。
- 部署方式（三选一示例，均离线权重）：
  1) **Ollama**：易用  
     ```bash
     # 导入本地 gguf
     ollama create qwen2-7b -f ./Modelfile
     ollama run qwen2-7b "你好"
     ```
  2) **llama-cpp-python**：纯本地推理  
     ```bash
     python -m llama_cpp.server --model /models/qwen2-7b-instruct-q4_0.gguf --port 8000 --n-gpu-layers 35
     ```
  3) **Transformers（GPU）**：  
     ```bash
     python - <<'PY'
     from transformers import AutoModelForCausalLM, AutoTokenizer
     mdir="/models/qwen2-7b"
     tok=AutoTokenizer.from_pretrained(mdir, local_files_only=True)
     m=AutoModelForCausalLM.from_pretrained(mdir, device_map="auto", local_files_only=True)
     out=m.generate(**tok("你好", return_tensors="pt").to(m.device), max_new_tokens=64)
     print(tok.decode(out[0], skip_special_tokens=True))
     PY
     ```
- 隐私与网络：防火墙阻断出站；推理端口仅内网；模型/数据磁盘加密；开启审计日志。

### 三、可复用的数据分析 Agent 设计（多模态入库 + 多 Agent 编排）
- 需求假设：处理文本/CSV/PDF/图片（提取文本后入库），接入向量库，支持高级任务编排与高质量 RAG。
- 技术选型：LangChain + LangGraph（编排）+ Chroma（本地向量库）+ llama-cpp 本地 LLM + 本地 embedding（如 bge-base-zh-v1.5）。
- 关键能力：
  1) 数据管道：文件解析 → 文本规范化 → 切分 → 向量化 → 入库。
  2) 高 RAG：可配置 Top-k、相似度阈值、引用返回、无依据拒答。
  3) 多 Agent 编排：规划/执行/验证三角色（Planner/Executor/Verifier），均使用本地模型。
  4) 工具层：文件读写、数据库查询（可扩展）、向量检索。
  5) 记忆与审计：对话/任务历史存本地；日志记录输入、检索得分、输出摘要（脱敏）。

### 四、代码结构（已提供）
```
docs/
  onprem_agent_guide.md      # 本指南
agent/
  data_agent.py              # 数据入库与 RAG 查询
  graph_workflow.py          # 多 Agent 编排（LangGraph）
```

### 五、快速运行示例
1) 准备本地模型与 embedding：
   - `LOCAL_LLM_PATH=/models/qwen2-7b-instruct-q4_0.gguf`
   - `LOCAL_EMBED_PATH=/models/bge-base-zh-v1.5`
   - 可选：`CHROMA_DIR=./storage/chroma_store`
2) 数据入库与查询（单 Agent RAG）：
   ```bash
   python agent/data_agent.py --ingest ./data --query "列出三条安全合规要点"
   ```
3) 多 Agent 编排示例（LangGraph）：
   ```bash
   python agent/graph_workflow.py --query "为内部知识库写一个上线前检查清单"
   ```

### 六、提升“强回复、低幻觉”的措施
- 检索：精细 chunk（重叠切分）、Top-k/阈值调优；无命中拒答。
- 约束：提示词要求“只基于引用”且输出引用；限制生成长度。
- 评测：本地小模型 LLM-as-judge 或基于 BERTScore 的离线集；缓存热点问答。

### 七、后续扩展
- 更多模态：表格结构化写入、OCR 文本化后再入库。
- 安全：JWT/MTLS 保护接口；依赖/模型哈希校验；只读模型卷。
- 微调/RAG 增强：在内网进行 LoRA/QLoRA；定期重建向量索引；多 Agent 通过队列/总线协同。

