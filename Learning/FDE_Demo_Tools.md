# 🎨 FDE Demo Tools 速查指南
## Streamlit / Chainlit 快速上手 (Day 2-3)

**目标**：用 Streamlit 在 2 小时内写出能展示给客户的原型

**为什么重要**：
- FDE 的最高境界 = 用最少的代码生成最多的价值
- 一个好的 UI 比 100 行优雅的代码更能打动投资人
- 客户不关心后端实现，只关心能否用、能否演示

---

## 📦 快速安装

```bash
# 推荐方式：用独立虚拟环境
conda create -n streamlit-env python=3.11 -y
conda activate streamlit-env

# 安装依赖（根据你的项目选择）
pip install streamlit         # 基础版
pip install streamlit chainlit    # 两个都要
pip install streamlit pandas numpy requests python-dotenv
```

**检查安装**：
```bash
streamlit --version
# 应该输出类似：Streamlit, version 1.28.0
```

---

## 🚀 一个 5 分钟的 Streamlit Demo

### 最小化示例（10 行代码）

**文件**: `hello_streamlit.py`
```python
import streamlit as st

st.set_page_config(page_title="FAQ Bot", layout="wide")

st.title("🤖 简单问答机器人")

# 用户输入
user_question = st.text_input("问我一个问题：")

if user_question:
    st.success(f"你问：{user_question}")
    st.info("我是一个简单的回复机器人。实际应用中，这里会调用 LLM API")
```

**运行**：
```bash
streamlit run hello_streamlit.py
```

**现象**：
- 自动打开浏览器 `http://localhost:8501`
- 可以实时交互
- 修改代码会自动刷新（超级快！）

---

## 🎯 完整的 FAQ Bot Demo（实战级）

**文件**: `faq_bot.py`

```python
import streamlit as st
import os
from dotenv import load_dotenv
from openai import OpenAI

# ============ 配置部分 ============
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

st.set_page_config(page_title="企业 FAQ Bot", layout="wide", initial_sidebar_state="expanded")

# ============ 侧边栏配置 ============
with st.sidebar:
    st.title("⚙️ 配置")
    
    model = st.selectbox(
        "选择 LLM 模型",
        ["gpt-4-turbo", "gpt-3.5-turbo"]
    )
    
    temperature = st.slider(
        "回答创意程度",
        min_value=0.0,
        max_value=2.0,
        value=0.7,
        step=0.1
    )
    
    system_prompt = st.text_area(
        "系统提示词",
        value="你是一个企业 FAQ 助手。用简洁、专业的语言回答问题。",
        height=100
    )
    
    st.markdown("---")
    st.write("📊 使用统计")
    st.write(f"✅ 已回答问题：{st.session_state.get('question_count', 0)}")

# ============ 主界面 ============
st.title("💼 企业 FAQ 问答系统")
st.markdown("输入任何问题，我会为你提供答案。")

# ============ 聊天历史（使用 Session State）============
if "messages" not in st.session_state:
    st.session_state.messages = []
if "question_count" not in st.session_state:
    st.session_state.question_count = 0

# ============ 显示历史消息 ============
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ============ 用户输入 ============
if prompt := st.chat_input("问我什么吧..."):
    # 显示用户消息
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # 加入历史
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # 调用 API
    with st.spinner("🔄 思考中..."):
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    *st.session_state.messages
                ],
                temperature=temperature,
                max_tokens=1000
            )
            
            assistant_message = response.choices[0].message.content
            
            # 显示助手回复
            with st.chat_message("assistant"):
                st.markdown(assistant_message)
            
            # 保存到历史
            st.session_state.messages.append({
                "role": "assistant",
                "content": assistant_message
            })
            
            # 更新计数
            st.session_state.question_count += 1
            
        except Exception as e:
            st.error(f"❌ 出错了：{str(e)}")
            st.warning("💡 提示：检查 .env 文件中的 API Key 是否正确")

# ============ 页脚 ============
st.markdown("---")
col1, col2, col3 = st.columns(3)
with col1:
    if st.button("🗑️ 清空对话"):
        st.session_state.messages = []
        st.session_state.question_count = 0
        st.rerun()

with col2:
    if st.button("📋 导出对话"):
        conversation_text = "\n\n".join([
            f"**{msg['role'].upper()}**: {msg['content']}"
            for msg in st.session_state.messages
        ])
        st.download_button(
            label="下载 Markdown",
            data=conversation_text,
            file_name="conversation.md",
            mime="text/markdown"
        )

st.caption("🚀 FDE Demo - 展示企业级 AI 能力")
```

**运行**：
```bash
# 确保 .env 有 OPENAI_API_KEY
streamlit run faq_bot.py
```

**关键特性**：
- ✅ 聊天历史保留（用 `st.session_state`）
- ✅ 侧边栏配置（温度、Model 选择）
- ✅ 错误处理（API 失败时有友好提示）
- ✅ 导出功能（客户可以下载对话）
- ✅ 计数统计（展示"已回答 10 个问题"之类）

---

## 🔧 Streamlit 核心组件速查表

### 输入组件
```python
# 文本输入（单行）
name = st.text_input("你的名字")

# 文本输入（多行）
description = st.text_area("描述")

# 选择框
option = st.selectbox("选择一个", ["选项 1", "选项 2"])

# 多选
choices = st.multiselect("多选", ["A", "B", "C"])

# 滑块
value = st.slider("数值", 0, 100, 50)

# 文件上传
uploaded_file = st.file_uploader("上传文件")
if uploaded_file:
    content = uploaded_file.read()  # 读取文件内容
```

### 显示组件
```python
# 标题和文本
st.title("大标题")
st.header("中标题")
st.subheader("小标题")
st.write("普通文本")
st.markdown("# 用 Markdown 格式")

# 提示框
st.success("✅ 成功")
st.error("❌ 错误")
st.warning("⚠️ 警告")
st.info("ℹ️ 信息")

# 代码显示
st.code("""
def hello():
    print("world")
""", language="python")

# 表格
st.dataframe(dataframe_object)

# 图表（如果装了 plotly）
import plotly.express as px
fig = px.bar(data, x='name', y='value')
st.plotly_chart(fig)
```

### 布局组件
```python
# 多列布局
col1, col2, col3 = st.columns(3)
with col1:
    st.write("第一列")
with col2:
    st.write("第二列")

# 侧边栏
with st.sidebar:
    st.write("这是侧边栏")

# 标签页（Streamlit 1.26+）
tab1, tab2 = st.tabs(["标签 1", "标签 2"])
with tab1:
    st.write("内容 1")
with tab2:
    st.write("内容 2")

# 容器（组织内容）
with st.container():
    st.write("这些内容会组织在一起")
```

### 交互组件
```python
# 按钮
if st.button("点击我"):
    st.write("你点击了！")

# 复选框
if st.checkbox("同意条款"):
    st.write("谢谢同意！")

# 单选
choice = st.radio("选择一个", ["A", "B", "C"])

# 加载状态（进度条）
with st.spinner("加载中..."):
    time.sleep(3)

# 进度条
progress_bar = st.progress(0)
for i in range(100):
    progress_bar.progress(i + 1)

# 下载按钮
st.download_button(
    label="下载数据",
    data="file content",
    file_name="data.txt"
)
```

### Session State（记住状态）
```python
# 初始化
if "counter" not in st.session_state:
    st.session_state.counter = 0

# 使用
if st.button("增加"):
    st.session_state.counter += 1

st.write(f"计数：{st.session_state.counter}")

# 这样即使用户交互，数据也不会丢失！
```

---

## 💡 实战模式：RAG + Streamlit

**场景**：用户上传文档，提问文档内容

**文件**: `rag_demo.py`

```python
import streamlit as st
import os
from dotenv import load_dotenv
from openai import OpenAI
import json

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

st.set_page_config(page_title="文档 RAG Demo", layout="wide")

st.title("📄 文档问答系统")

# ============ 侧边栏：管理文档 ============
with st.sidebar:
    st.header("📚 文档管理")
    
    # 初始化存储
    if "documents" not in st.session_state:
        st.session_state.documents = {}
    
    # 上传新文档
    uploaded_file = st.file_uploader("上传 .txt 或 .md 文档")
    if uploaded_file:
        content = uploaded_file.read().decode('utf-8')
        doc_name = uploaded_file.name
        st.session_state.documents[doc_name] = content
        st.success(f"✅ 已添加：{doc_name}")
    
    st.markdown("---")
    st.subheader("已加载的文档")
    for doc_name in st.session_state.documents:
        st.write(f"📄 {doc_name}")

# ============ 主界面：提问 ============
if st.session_state.documents:
    
    # 选择要查询的文档
    selected_doc = st.selectbox(
        "选择要查询的文档",
        list(st.session_state.documents.keys())
    )
    
    # 用户问题
    question = st.text_input("问你的问题：")
    
    if question:
        # 构造 RAG 提示词
        doc_content = st.session_state.documents[selected_doc]
        
        rag_prompt = f"""根据下面的文档内容回答问题。如果文档中没有相关信息，说"文档中找不到相关信息"。

【文档内容】
{doc_content}

【用户问题】
{question}

【你的回答】
"""
        
        with st.spinner("🔄 分析中..."):
            try:
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "你是一个文档分析助手。基于提供的文档准确回答问题。"},
                        {"role": "user", "content": rag_prompt}
                    ],
                    temperature=0.3  # 降低温度，更稳定
                )
                
                answer = response.choices[0].message.content
                
                st.success("✅ 回答完成")
                st.markdown("### 答案")
                st.write(answer)
                
            except Exception as e:
                st.error(f"错误：{str(e)}")
else:
    st.warning("⚠️ 请先在左侧上传文档")

st.caption("这是一个简化的 RAG demo，生产环境应使用向量数据库")
```

**运行**：
```bash
streamlit run rag_demo.py
```

**上传测试文件**：
创建 `test_doc.txt`：
```
我们公司是一个 AI 创业公司。
CEO 是 Alice，成立于 2024 年。
主要产品是文档分析平台。
```

然后上传，提问："CEO 叫什么名字？" → 应该回答 "Alice"

---

## 🎨 更高级的 Streamlit 技巧

### 1. 自定义主题
```python
# streamlit_config.yaml (在项目根目录的 .streamlit/ 文件夹中创建)
[theme]
primaryColor = "#FF6B6B"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"
font = "sans serif"
```

### 2. 隐藏 Streamlit 菜单（生产级）
```python
st.set_page_config(initial_sidebar_state="collapsed")

hide_streamlit_style = """
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
</style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)
```

### 3. 使用 Columns 做高级布局
```python
# 响应式布局
st.title("销售仪表板")

col1, col2, col3 = st.columns([2, 1, 1])  # 2:1:1 的宽度比例

with col1:
    st.metric("总收入", "$100K", "+5%")
with col2:
    st.metric("新客户", "23", "+3")
with col3:
    st.metric("满意度", "92%", "-1%")
```

### 4. 缓存优化（加快速度）
```python
# 如果数据加载慢，用 cache 装饰器
@st.cache_data  # 缓存数据（不会变的数据）
def load_large_dataset():
    import pandas as pd
    return pd.read_csv("big_file.csv")

@st.cache_resource  # 缓存资源（如 LLM 客户端）
def get_client():
    from openai import OpenAI
    return OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# 第一次调用会很慢，之后就快了
df = load_large_dataset()
client = get_client()
```

---

## 🚀 Chainlit vs Streamlit：选择指南

| 特性 | Streamlit | Chainlit |
|------|-----------|---------|
| 学习曲线 | 超级简单 ✅ | 中等 |
| 聊天 UI | 需要自己写 | 内置 ✅ |
| 部署速度 | 快 | 快 |
| 生产就绪 | 可以 | 更专业 ✅ |
| 自定义程度 | 高 | 中等 |

**建议**：
- 快速 Demo → **Streamlit**（2 小时内）
- 正式聊天产品 → **Chainlit**（额外 1 小时学习）
- 复杂界面 → **Streamlit**（自由度更高）

---

## 📦 Chainlit 快速示例

**安装**：
```bash
pip install chainlit
```

**最小示例** - `app.py`：
```python
from chainlit.input_widgets import Select
import chainlit as cl
from openai import AsyncOpenAI

client = AsyncOpenAI()

@cl.on_message
async def main(message: cl.Message):
    response = await client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": message.content}],
        stream=True,
    )
    
    msg = cl.Message(content="")
    async for chunk in response:
        if chunk.choices[0].delta.content:
            await msg.stream_token(chunk.choices[0].delta.content)
    
    await msg.send()
```

**运行**：
```bash
chainlit run app.py
```

**特点**：
- 自动处理聊天历史 ✅
- 更优雅的流式输出 ✅
- 更专业的外观 ✅

---

## 🎯 常见问题

### Q1: Streamlit 如何保存用户数据？
A: 使用 `st.session_state` 保存当前会话数据。如果需要持久化（用户刷新后还有），需要：
```python
import json

# 保存到文件
def save_data(data):
    with open("data.json", "w") as f:
        json.dump(data, f)

# 加载
def load_data():
    if os.path.exists("data.json"):
        with open("data.json") as f:
            return json.load(f)
    return {}
```

### Q2: 如何处理大文件上传？
A:
```python
uploaded_file = st.file_uploader("上传 CSV")
if uploaded_file is not None:
    # 处理大文件，分块读取
    for chunk in pd.read_csv(uploaded_file, chunksize=1000):
        # 处理每个 chunk
        pass
```

### Q3: 如何在 Streamlit 中显示长文本而不卡顿？
A:
```python
# 不好的方式（会卡）
st.write(very_long_text)

# 好的方式
st.text_area("内容", value=very_long_text, disabled=True)

# 或者用 markdown 的代码块
st.markdown(f"```\n{very_long_text}\n```")
```

### Q4: 如何部署 Streamlit 应用？
A:
1. **最快方式**（免费）：Streamlit Cloud
   ```bash
   # 推送到 GitHub
   git push origin main
   
   # 在 https://share.streamlit.io 连接你的 GitHub repo
   # Streamlit 会自动部署！
   ```

2. **专业方式**：自己的服务器
   ```bash
   # 在服务器上
   streamlit run app.py --server.port 80 --server.address 0.0.0.0
   ```

---

## ✅ Day 2-3 任务清单

- [ ] 安装 Streamlit（`pip install streamlit`）
- [ ] 运行 `hello_streamlit.py` 示例
- [ ] 理解 `st.session_state` 的工作原理
- [ ] 修改 `faq_bot.py` 中的 System Prompt
- [ ] 成功部署一个简单的 Streamlit 应用
- [ ] （可选）尝试 Chainlit 示例

**目标**：到 Day 3 结束，你能在 30 分钟内用 Streamlit 写出一个能演示的 Demo。

---

## 📚 推荐资源

- **Streamlit 官方文档**：https://docs.streamlit.io
- **Chainlit 官方文档**：https://docs.chainlit.io
- **Streamlit Gallery**：https://streamlit.io/gallery（看别人怎么写的）

---

**完成本章后，你已经掌握了 FDE 最常用的工具！** 🎉

下一步：用 Streamlit + API 完成 Project_01_FAQ_Bot

最后更新: 2025-12-22
