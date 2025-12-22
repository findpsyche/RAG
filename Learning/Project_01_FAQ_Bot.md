# 🎯 Project 01: FAQ Bot - 第一个完整项目
## 从代码零行到能演示的系统 (3 小时)

**目标**：构建一个可以在客户面前演示的 FAQ 机器人

**成果**：一个 Streamlit 应用，用户可以：
- 提问任何问题
- 实时获得 AI 回答
- 查看对话历史
- 导出对话记录

**时间分配**：
- 项目规划 (15 min)
- 环境搭建 (15 min)
- 核心功能 (90 min)
- 测试和优化 (30 min)
- 演示准备 (30 min)

---

## 📋 第一步：项目规划

### 明确需求
```
功能需求：
✅ 用户可以输入问题
✅ AI 可以实时回答
✅ 显示之前的对话
✅ 可以清空对话
✅ 可以导出对话

非功能需求：
⚡ 启动 < 5 秒
⚡ 回答 < 10 秒
⚡ 支持 5 个并发用户
🎨 界面清洁专业

超出本项目范围：
❌ 用户登录和权限
❌ 数据库存储
❌ 高可用部署
```

### 技术选型
```
后端：OpenAI API (gpt-3.5-turbo)
前端：Streamlit
数据存储：内存 (session_state)
部署：本地开发 + 可选上传到 Streamlit Cloud
```

### 文件结构
```
project_01_faq_bot/
├── app.py                 # 主程序
├── config.py              # 配置文件
├── .env                   # API Key（不提交到 Git）
├── .env.example           # 示例（提交到 Git）
├── requirements.txt       # 依赖列表
└── README.md             # 项目说明
```

---

## 🛠️ 第二步：环境搭建

### 2.1 创建虚拟环境

```bash
# 进入项目目录
cd project_01_faq_bot

# 创建虚拟环境
conda create -n faq-bot python=3.11 -y
conda activate faq-bot

# 或用 venv
python -m venv venv
.\venv\Scripts\activate  # Windows
source venv/bin/activate  # macOS/Linux
```

### 2.2 安装依赖

**创建 `requirements.txt`**：
```
streamlit==1.28.0
openai==1.3.0
python-dotenv==1.0.0
```

**安装**：
```bash
pip install -r requirements.txt
```

### 2.3 配置 API Key

**创建 `.env`**：
```
OPENAI_API_KEY=sk-xxxxxxxxxxxx
```

**创建 `.env.example`**（给别人参考）：
```
OPENAI_API_KEY=your-api-key-here
```

**更新 `.gitignore`**：
```
.env
__pycache__/
*.pyc
venv/
.DS_Store
```

---

## 💻 第三步：核心功能开发

### 3.1 创建配置文件 - `config.py`

```python
"""
FAQ Bot 配置文件
"""

import os
from dotenv import load_dotenv

load_dotenv()

# API 配置
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("❌ 未找到 OPENAI_API_KEY，请检查 .env 文件")

# 模型配置
DEFAULT_MODEL = "gpt-3.5-turbo"
DEFAULT_TEMPERATURE = 0.7
DEFAULT_MAX_TOKENS = 1000

# UI 配置
APP_TITLE = "💼 企业 FAQ 问答系统"
APP_DESCRIPTION = "智能回答任何问题，支持对话记录导出"

# 系统提示词
SYSTEM_PROMPT = """你是一个专业的企业 FAQ 助手。
特点：
- 用简洁、清晰的语言回答
- 优先给出直接答案，然后补充细节
- 如果不确定，说'我不太确定，建议咨询相关部门'
- 保持专业和友好的语气
"""

# 演示模式（没有 API Key 时用）
DEMO_MODE = not OPENAI_API_KEY or OPENAI_API_KEY.startswith("your-")
```

### 3.2 创建主程序 - `app.py`

```python
"""
FAQ Bot 主程序
一个简单但专业的问答机器人
"""

import streamlit as st
from openai import OpenAI
import os
from config import (
    OPENAI_API_KEY, 
    DEFAULT_MODEL, 
    DEFAULT_TEMPERATURE,
    APP_TITLE,
    APP_DESCRIPTION,
    SYSTEM_PROMPT,
    DEMO_MODE
)

# ============================================================
# 页面配置
# ============================================================

st.set_page_config(
    page_title="FAQ Bot",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 隐藏 Streamlit 默认菜单（可选，使界面更清洁）
hide_streamlit_style = """
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
</style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# ============================================================
# 初始化
# ============================================================

# 初始化 API 客户端
if not DEMO_MODE:
    client = OpenAI(api_key=OPENAI_API_KEY)
else:
    client = None

# 初始化 session state
if "messages" not in st.session_state:
    st.session_state.messages = []

if "total_questions" not in st.session_state:
    st.session_state.total_questions = 0

if "current_model" not in st.session_state:
    st.session_state.current_model = DEFAULT_MODEL

if "current_temperature" not in st.session_state:
    st.session_state.current_temperature = DEFAULT_TEMPERATURE

# ============================================================
# 侧边栏 - 配置和统计
# ============================================================

with st.sidebar:
    st.header("⚙️ 设置")
    
    # 模型选择
    st.session_state.current_model = st.selectbox(
        "选择 AI 模型",
        ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo"],
        index=0 if st.session_state.current_model == "gpt-3.5-turbo" else 1
    )
    
    # 温度调整（影响回答的创意程度）
    st.session_state.current_temperature = st.slider(
        "创意程度",
        min_value=0.0,
        max_value=2.0,
        value=st.session_state.current_temperature,
        step=0.1,
        help="0.0 = 严格准确，1.0 = 平衡，2.0 = 非常有创意"
    )
    
    # 系统提示词编辑
    with st.expander("📝 编辑系统提示词"):
        edited_prompt = st.text_area(
            "系统提示词",
            value=SYSTEM_PROMPT,
            height=150,
            key="system_prompt"
        )
    
    st.markdown("---")
    
    # 统计信息
    st.subheader("📊 使用统计")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("总对话轮次", st.session_state.total_questions)
    with col2:
        msg_count = len(st.session_state.messages)
        st.metric("当前消息数", msg_count)
    
    # 模式提示
    if DEMO_MODE:
        st.warning("⚠️ 演示模式（无 API Key）")
    else:
        st.success("✅ API 已连接")

# ============================================================
# 主界面 - 标题和说明
# ============================================================

st.title(APP_TITLE)
st.markdown(APP_DESCRIPTION)

if DEMO_MODE:
    st.error("❌ 当前在演示模式。要使用真实 AI，请在 .env 中配置 OPENAI_API_KEY")

# ============================================================
# 聊天区域 - 显示历史消息
# ============================================================

st.subheader("💬 对话历史")

# 显示所有历史消息
for i, message in enumerate(st.session_state.messages):
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ============================================================
# 输入区域 - 用户提问
# ============================================================

st.subheader("📝 输入您的问题")

# 使用 chat_input 获得更好的用户体验
user_input = st.chat_input(
    "提出你的问题...",
    key="user_input"
)

# 处理用户输入
if user_input:
    # 显示用户消息
    with st.chat_message("user"):
        st.markdown(user_input)
    
    # 保存到历史
    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })
    
    # 调用 API 获取回答
    if DEMO_MODE:
        # 演示模式：返回虚拟回答
        assistant_message = f"【演示回答】关于'{user_input}'的问题很好！在实际应用中，这里会调用 OpenAI API 获取真实回答。"
    else:
        # 真实模式：调用 OpenAI API
        with st.spinner("🔄 AI 正在思考..."):
            try:
                response = client.chat.completions.create(
                    model=st.session_state.current_model,
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT},
                        *st.session_state.messages
                    ],
                    temperature=st.session_state.current_temperature,
                    max_tokens=DEFAULT_MAX_TOKENS
                )
                
                assistant_message = response.choices[0].message.content
                
            except Exception as e:
                st.error(f"❌ 调用 API 失败：{str(e)}")
                st.info("💡 常见原因：API Key 错误、余额不足、网络问题")
                assistant_message = None
    
    # 显示和保存助手回复
    if assistant_message:
        with st.chat_message("assistant"):
            st.markdown(assistant_message)
        
        st.session_state.messages.append({
            "role": "assistant",
            "content": assistant_message
        })
        
        st.session_state.total_questions += 1
        st.rerun()  # 重新运行，刷新界面

# ============================================================
# 底部功能区 - 清空、导出、分享
# ============================================================

st.markdown("---")
st.subheader("🛠️ 工具")

col1, col2, col3, col4 = st.columns(4)

# 清空对话
with col1:
    if st.button("🗑️ 清空对话", use_container_width=True):
        st.session_state.messages = []
        st.session_state.total_questions = 0
        st.success("✅ 已清空所有对话")
        st.rerun()

# 导出为 Markdown
with col2:
    if st.session_state.messages:
        conversation_md = "\n\n".join([
            f"**{msg['role'].upper()}**: {msg['content']}"
            for msg in st.session_state.messages
        ])
        st.download_button(
            label="📋 导出 Markdown",
            data=conversation_md,
            file_name="conversation.md",
            mime="text/markdown",
            use_container_width=True
        )

# 导出为 JSON（对于程序处理）
with col3:
    if st.session_state.messages:
        import json
        conversation_json = json.dumps(
            st.session_state.messages,
            ensure_ascii=False,
            indent=2
        )
        st.download_button(
            label="📄 导出 JSON",
            data=conversation_json,
            file_name="conversation.json",
            mime="application/json",
            use_container_width=True
        )

# 复制到剪贴板的说明
with col4:
    st.info("💡 使用导出功能保存对话记录")

# ============================================================
# 页脚和说明
# ============================================================

st.markdown("---")

col_left, col_mid, col_right = st.columns(3)

with col_left:
    st.markdown("**🚀 快速开始**")
    st.markdown("""
    1. 在右上角输入你的问题
    2. 按 Enter 提交
    3. 等待 AI 回答
    4. 使用导出功能保存
    """)

with col_mid:
    st.markdown("**⚡ 提示**")
    st.markdown("""
    - 问题越具体，回答越准确
    - 创意程度 = 0.7 最平衡
    - 长对话在导出时包含全部内容
    """)

with col_right:
    st.markdown("**📚 学习资源**")
    st.markdown("""
    - [OpenAI API 文档](https://platform.openai.com/docs)
    - [Streamlit 文档](https://docs.streamlit.io)
    - [项目代码](https://github.com/your-repo)
    """)

# 应用信息
st.caption("🤖 FDE Project 01 - FAQ Bot | Made with Streamlit")
```

### 3.3 创建 README.md

```markdown
# FAQ Bot - 企业问答系统

一个简单但专业的 AI 问答机器人，展示 FDE 核心能力。

## 快速开始

### 1. 环境搭建

\`\`\`bash
# 创建虚拟环境
conda create -n faq-bot python=3.11 -y
conda activate faq-bot

# 安装依赖
pip install -r requirements.txt
\`\`\`

### 2. 配置 API

复制 `.env.example` 为 `.env`：
\`\`\`bash
OPENAI_API_KEY=sk-xxxxxxxxxxxxx
\`\`\`

### 3. 运行应用

\`\`\`bash
streamlit run app.py
\`\`\`

应用会在 http://localhost:8501 打开

## 功能特性

✅ 实时问答  
✅ 对话历史  
✅ 模型和参数可配置  
✅ 对话导出（Markdown / JSON）  
✅ 使用统计  
✅ 演示模式（无 API Key 也能运行）  

## 项目结构

\`\`\`
project_01_faq_bot/
├── app.py              # 主程序
├── config.py           # 配置
├── requirements.txt    # 依赖
├── .env               # API Key（不要提交）
├── .env.example       # 示例
├── .gitignore         # Git 忽略文件
└── README.md          # 说明（本文件）
\`\`\`

## 技术栈

- **前端**：Streamlit 1.28
- **后端**：OpenAI API
- **语言**：Python 3.11
- **依赖管理**：pip

## 部署

### 本地开发
\`\`\`bash
streamlit run app.py
\`\`\`

### 免费云部署（Streamlit Cloud）

1. 将代码推送到 GitHub
2. 访问 https://share.streamlit.io
3. 连接你的 GitHub repo
4. Streamlit 自动部署

### 自己的服务器

\`\`\`bash
streamlit run app.py --server.port 80 --server.address 0.0.0.0 --logger.level=warning
\`\`\`

## 常见问题

### Q: API Key 在哪里获取？
A: https://platform.openai.com/account/api-keys

### Q: 为什么没有回答？
A: 检查：
1. API Key 是否正确
2. 账户余额是否充足
3. 网络连接是否正常

### Q: 如何修改默认提示词？
A: 在侧边栏的"编辑系统提示词"中修改

### Q: 可以保存用户对话吗？
A: 当前版本存储在内存中。如需持久化，可以：
- 使用导出功能手动保存
- 添加数据库（PostgreSQL / MongoDB）
- 使用 Streamlit Cloud 的数据持久化

## 下一步改进

- [ ] 添加用户登录
- [ ] 集成向量数据库（Pinecone / Weaviate）
- [ ] 支持文档上传和 RAG
- [ ] 添加对话搜索功能
- [ ] 支持多语言
- [ ] 接入其他 LLM（Claude、LLaMA 等）

## License

MIT

## 作者

FDE Learning Project

## 反馈和支持

如有问题或建议，欢迎提交 Issue 或 Pull Request！
```

---

## ✅ 第四步：测试

### 4.1 功能测试清单

```
【基础功能】
- [ ] 应用正常启动
- [ ] 可以输入问题
- [ ] AI 能回答问题
- [ ] 对话历史显示正确

【高级功能】
- [ ] 可以切换模型
- [ ] 可以调整温度参数
- [ ] 可以编辑系统提示词
- [ ] 导出 Markdown 格式正确
- [ ] 导出 JSON 格式正确
- [ ] 清空对话功能正常

【性能】
- [ ] 启动时间 < 5 秒
- [ ] 回答时间 < 15 秒
- [ ] 切换标签页不卡顿

【错误处理】
- [ ] API Key 缺失时有提示
- [ ] API 错误时有提示
- [ ] 网络错误时有提示
```

### 4.2 测试问题集

```
【基础】
- "你好，你是谁？"
- "今天几号？"
- "2+2=？"

【实用】
- "怎样写好一份产品方案？"
- "如何管理远程团队？"
- "什么是 RAG？"

【边界情况】
- [输入超长问题]
- [快速输入多个问题]
- [切换模型后提问]
```

---

## 🎨 第五步：优化和演示准备

### 5.1 性能优化

```python
# 在 config.py 中添加缓存
@st.cache_resource
def get_api_client():
    """缓存 API 客户端，避免重复初始化"""
    return OpenAI(api_key=OPENAI_API_KEY)
```

### 5.2 演示准备

```markdown
## 演示脚本（对客户展示时）

1. **开场** (10 秒)
   "这是一个企业级 AI 问答系统，可以回答任何问题。"

2. **演示** (2 分钟)
   问题 1: "什么是数字化转型？"
   问题 2: "怎样评估 AI 项目的 ROI？"
   问题 3: "推荐一个 AI 团队的组织结构"

3. **功能展示** (1 分钟)
   - 导出对话
   - 调整参数
   - 修改提示词

4. **总结** (30 秒)
   "这只是基础演示。我们可以：
   - 集成你的内部文档（RAG）
   - 添加行业特定的知识库
   - 部署到你的私有服务器"
```

### 5.3 演示视频录制

```bash
# 使用 OBS 或 ScreenFlow 录制一个 2-3 分钟的演示
# 包含：
# 1. 正常提问和回答
# 2. 参数调整效果
# 3. 导出功能

# 这样即使 API 超时，你也有备用方案！
```

---

## 📊 成果检查

完成后，你应该有：

```
project_01_faq_bot/
├── app.py              ✅ 完整的应用代码
├── config.py           ✅ 配置管理
├── requirements.txt    ✅ 依赖列表
├── .env               ✅ API Key（本地）
├── .env.example       ✅ 示例模板
├── .gitignore         ✅ Git 忽略
├── README.md          ✅ 项目说明
└── demo_recording.mp4 ✅ 演示视频（可选）
```

## 🎯 学到的 FDE 核心技能

通过完成本项目，你学会了：

1. **速度** ⚡
   - 3 小时从零到能演示
   - Streamlit 的快速迭代
   - Python 的高效开发

2. **系统设计** 🏗️
   - 配置管理（config.py）
   - 状态管理（session_state）
   - 错误处理

3. **用户体验** 👥
   - 直观的界面设计
   - 清晰的说明文档
   - 错误时的友好提示

4. **部署能力** 🚀
   - 本地开发
   - 云部署（Streamlit Cloud）
   - 依赖管理

5. **文档和演示** 📚
   - README 编写
   - 代码注释
   - 演示脚本准备

---

## 💡 常见坑和解决方案

| 问题 | 原因 | 解决 |
|------|------|------|
| 无法导入 openai | 未安装依赖 | `pip install openai` |
| API Key 识别不了 | .env 文件位置错误 | 确保在项目根目录 |
| Streamlit 很慢 | 没有缓存 | 使用 `@st.cache_data` |
| 部署到云后 API 报错 | 环境变量未设置 | 在云平台设置 Secrets |
| 对话消失了 | 刷新页面丢失数据 | 使用 session_state 或数据库 |

---

**恭喜！你已经完成了第一个 FDE 项目。** 🎉

现在你可以：
- ✅ 在客户面前演示
- ✅ 修改代码满足定制需求
- ✅ 部署到云端
- ✅ 作为下一个项目的基础

**下一步**：进入第二个项目（Project_02_Enterprise_RAG），为系统添加文档理解能力！

最后更新: 2025-12-22
