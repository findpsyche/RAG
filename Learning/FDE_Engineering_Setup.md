# 🛠️ FDE 工程协同与环境配置 (第 1 天)

**目标**: 环境配好、Git 熟练、能接通 API。

---

## 第一部分：Python 环境配置 (2h)

### 为什么要隔离环境？

```
❌ 错误做法:
  pip install package1 package2 package3  (装到全局系统)
  
结果:
  - 不同项目可能需要同一个包的不同版本 → 冲突
  - 在客户服务器部署时，环境不一样 → 代码跑不动
  - 卸载一个包时，可能破坏其他项目

✅ 正确做法:
  每个项目一个独立的虚拟环境
```

### 方案 1: Conda（推荐）

```bash
# 安装 Miniconda (轻量级 Conda)
# 从 https://docs.conda.io/projects/miniconda/en/latest/ 下载

# 创建环境
conda create -n fde-project python=3.11

# 激活环境
conda activate fde-project

# 安装依赖
pip install openai langchain streamlit

# 查看已安装包
pip list

# 保存依赖列表
pip freeze > requirements.txt

# 在别的机器上复现环境
pip install -r requirements.txt
```

### 方案 2: venv（轻量级，只需要 Python）

```bash
# 创建虚拟环境
python -m venv fde-env

# 激活环境
# Windows:
fde-env\Scripts\activate
# Mac/Linux:
source fde-env/bin/activate

# 剩下的操作和 Conda 一样
pip install -r requirements.txt
```

### 方案 3: Poetry（最现代，推荐用于公司项目）

```bash
# 安装 Poetry
pip install poetry

# 初始化项目
poetry init

# 添加依赖
poetry add openai langchain streamlit

# 安装所有依赖
poetry install

# 进入虚拟环境
poetry shell
```

### 第一天的检查清单
- [ ] 安装了 Miniconda 或 Conda
- [ ] 创建了一个虚拟环境 `fde-project`
- [ ] 能激活/关闭环境
- [ ] 能安装包和冻结依赖

---

## 第二部分：Git 与团队协同 (1.5h)

### Git 基础（必须掌握）

#### 配置 Git
```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

#### 标准工作流

```bash
# 1. 克隆仓库
git clone https://github.com/team/repo.git
cd repo

# 2. 创建自己的分支（永远不要在 main 上写代码）
git checkout -b feature/add-rag-module

# 3. 进行编辑和提交
# ... 编辑文件 ...
git add .
git commit -m "feat: add RAG module for HR docs"

# 4. 推送到远程
git push origin feature/add-rag-module

# 5. 在 GitHub/GitLab 上发起 Pull Request
# ... 等待 code review ...

# 6. 合并到 main
# ... 通过 review 后，点击 "Merge" ...

# 7. 拉取最新的 main
git checkout main
git pull origin main
```

### Commit Message 规范

```bash
# ❌ 不好的 commit message
git commit -m "fix bug"
git commit -m "update code"

# ✅ 好的 commit message
git commit -m "feat: add RAG module for HR document search"
git commit -m "fix: update prompt to improve JSON parsing accuracy"
git commit -m "refactor: simplify chunking logic with better error handling"
git commit -m "docs: add deployment guide for vLLM on GPU"

# 格式: type: brief description
# type 可以是:
#   feat:     新功能
#   fix:      修复
#   refactor: 代码重构
#   docs:     文档更新
#   test:     测试
#   perf:     性能优化
```

### 常见问题与解决

```bash
# 问题 1: 我不小心在 main 上提交了
# 解决:
git reset HEAD~1              # 撤销最后一个 commit
git checkout -b my-feature    # 创建新分支
git commit -m "..."           # 重新提交

# 问题 2: 我想看我的改动
# 解决:
git diff                      # 看未提交的改动
git log --oneline             # 看提交历史

# 问题 3: 我想回到某个旧版本
# 解决:
git log --oneline             # 找到目标 commit 的 hash
git checkout <hash>           # 切换到那个版本

# 问题 4: Merge conflict（两个人改同一行）
# 解决:
# VS Code 会自动显示冲突位置
# 手动选择要保留的代码 → git add . → git commit
```

### 第一天的检查清单
- [ ] 配置了 git user.name 和 user.email
- [ ] 能克隆一个仓库
- [ ] 能创建分支、提交、推送
- [ ] 写过至少 3 个规范的 commit message

---

## 第三部分：第一次 API 调用 (2.5h)

### 准备工作

```bash
# 激活虚拟环境
conda activate fde-project

# 安装必要的包
pip install openai requests python-dotenv

# 创建 .env 文件存储 API Key（不要放在代码里！）
echo "OPENAI_API_KEY=sk-..." > .env
echo ".env" >> .gitignore  # 确保 API Key 不被提交到 GitHub
```

### 第一个调用成功：Hello, API!

```python
# hello_api.py
from openai import OpenAI
import os
from dotenv import load_dotenv

# 从 .env 加载 API Key
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

# 初始化客户端
client = OpenAI(api_key=api_key)

# 第一次调用：简单问答
response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What is 2 + 2?"}
    ]
)

print(response.choices[0].message.content)
```

```bash
# 运行
python hello_api.py
# 输出: 2 + 2 equals 4.
```

### 深入理解：System Prompt

System Prompt 是 AI 的"人格指引"。不同的 System Prompt 会导致完全不同的回应：

```python
# 例子 1: 严肃的助手
response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "system", "content": "You are a professional business consultant. Provide concise, actionable advice."},
        {"role": "user", "content": "What's a good marketing strategy for a SaaS startup?"}
    ]
)

# 例子 2: 创意的助手
response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "system", "content": "You are a creative copywriter. Write engaging, witty responses."},
        {"role": "user", "content": "What's a good marketing strategy for a SaaS startup?"}
    ]
)

# 例子 3: 指定输出格式（JSON）
response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "system", "content": "You are a helpful assistant. Always respond in JSON format with 'answer' and 'confidence' fields."},
        {"role": "user", "content": "What is the capital of France?"}
    ]
)

# 输出: {"answer": "Paris", "confidence": 0.99}
```

### 处理长文本（关键！）

```python
# LLM 有 token 限制。太长的文本会被截断。

# ❌ 错误：直接发送 10000 行日志
def bad_approach(log_file):
    with open(log_file) as f:
        log_content = f.read()  # 可能是 100KB
    return client.chat.completions.create(
        messages=[{"role": "user", "content": f"分析这个日志: {log_content}"}]
    )

# ✅ 正确：只发送关键部分
def good_approach(log_file):
    with open(log_file) as f:
        lines = f.readlines()
    
    # 只取最后 500 行（这样通常能放进 context）
    relevant_lines = lines[-500:]
    log_content = "".join(relevant_lines)
    
    return client.chat.completions.create(
        messages=[{"role": "user", "content": f"分析这个日志: {log_content}"}]
    )

# 更好：使用分页
def better_approach(log_file):
    """分多次处理超长文本"""
    with open(log_file) as f:
        lines = f.readlines()
    
    # 每次处理 100 行
    results = []
    for i in range(0, len(lines), 100):
        chunk = "".join(lines[i:i+100])
        result = client.chat.completions.create(
            messages=[{"role": "user", "content": f"总结这部分日志: {chunk}"}]
        )
        results.append(result.choices[0].message.content)
    
    # 最后汇总所有结果
    summary = client.chat.completions.create(
        messages=[{"role": "user", "content": f"汇总这些分析: {results}"}]
    )
    return summary
```

### JSON Mode（输出结构化数据）

```python
# 有时我们需要 AI 返回的不是文本，而是结构化数据

# ❌ 不稳定的方式（让 AI 返回 JSON 字符串）
response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[{"role": "user", "content": "Extract name and age from: 'John is 30 years old'. Return JSON."}]
)
# 问题: AI 有时会返回 "The JSON is: {...}" 而不是纯 JSON

# ✅ 稳定的方式（使用 JSON Mode）
response = client.chat.completions.create(
    model="gpt-4-turbo",  # 或 gpt-3.5-turbo（某些版本支持）
    messages=[{"role": "user", "content": "Extract name and age from: 'John is 30 years old'"}],
    response_format={"type": "json_object"}
)

import json
result = json.loads(response.choices[0].message.content)
print(result)  # {"name": "John", "age": 30}
```

### 多个 LLM 提供商对比

```python
# OpenAI
from openai import OpenAI
client = OpenAI(api_key="sk-...")

# Claude (Anthropic)
from anthropic import Anthropic
client = Anthropic(api_key="sk-ant-...")

# DeepSeek（便宜！）
from openai import OpenAI
client = OpenAI(
    api_key="sk-...",
    base_url="https://api.deepseek.com"
)

# 通常的用法是一样的，只是 model 参数不同
```

### 第一天的检查清单
- [ ] 创建了虚拟环境
- [ ] 安装了 openai / anthropic 包
- [ ] 成功调用了 API（看到了回复）
- [ ] 修改了 System Prompt，看到不同的回应
- [ ] 处理过超过 1000 字的文本

---

## 常见问题

### Q: 我的 API Key 泄露了怎么办？
**A:** 立刻在 OpenAI 后台删除这个 key，生成新的。

### Q: 怎么降低 API 成本？
**A:**
```
- 用 gpt-3.5-turbo 而不是 gpt-4（便宜 10 倍）
- 用 DeepSeek（便宜 100 倍，但质量可能稍差）
- 用本地模型（Ollama），成本为 0
- 减少不必要的 API 调用（缓存、批量处理）
```

### Q: 为什么我的 commit 推不上去？
**A:** 
```bash
# 通常是分支冲突，试试：
git pull origin main  # 先拉最新的 main
git rebase main       # 或 merge
git push origin <你的分支>
```

---

**检查清单**：当天结束，你应该能：
- [ ] 独立配置 Python 环境
- [ ] 用 Git 完成一个完整的工作流（clone → create branch → commit → push）
- [ ] 调用 API 并解析返回值
- [ ] 处理长文本和结构化输出

🎉 恭喜！你完成了第 1 天。现在可以进入第 2 天：Streamlit 快速演示。
