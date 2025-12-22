# 🎯 FDE API 调用精通指南 (第 2 天)

**目标**: 掌握 System Prompt 调试，处理长文本截断与 JSON Mode 输出。

---

## 第一部分：System Prompt 调试艺术 (2h)

### 为什么 System Prompt 这么重要？

同一个 API，不同的 System Prompt，输出完全不同：

```python
question = "What should a startup do to grow?"

# ✅ 案例 1: 商业顾问风格
response1 = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
        {
            "role": "system",
            "content": "You are a seasoned venture capitalist with 20 years of experience. Provide strategic, data-driven advice for startup growth. Be concise."
        },
        {"role": "user", "content": question}
    ]
)
# 输出: Focus on product-market fit metrics. If CAC > LTV, revisit positioning...

# ✅ 案例 2: 励志教练风格
response2 = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
        {
            "role": "system",
            "content": "You are a motivational startup coach. Give encouraging, actionable advice focused on team morale and persistence."
        },
        {"role": "user", "content": question}
    ]
)
# 输出: Believe in your vision! Growth comes from consistency and..

# ✅ 案例 3: 律师/风险规避风格
response3 = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
        {
            "role": "system",
            "content": "You are a cautious legal advisor. Point out all potential risks and compliance issues. Be thorough."
        },
        {"role": "user", "content": question}
    ]
)
# 输出: Ensure regulatory compliance first. Verify IP rights, employment..
```

**关键洞察**: 不同的 System Prompt 激活了 LLM 不同的"知识"。选对了，质量提升 5 倍。

---

## System Prompt 最佳实践

### 原则 1: 角色定位要具体

```python
# ❌ 太宽泛
"You are a helpful assistant."

# ✅ 具体有力
"You are an expert product manager at a Series B SaaS company. You have shipped 5 products and understand the complete product-engineering-design workflow."
```

### 原则 2: 指定输出格式

```python
# ❌ 格式模糊
"Summarize this document."

# ✅ 格式清晰
"""Summarize this document in the following format:
- Key Points (3-5 bullet points)
- Risks (2-3)
- Recommended Actions (2-3)
Return as JSON."""
```

### 原则 3: 指定语气和风格

```python
# ❌ 风格不清楚
"Write an article about AI."

# ✅ 风格明确
"""Write a technical blog post for experienced ML engineers. 
- Target audience: 10+ years in ML
- Tone: Insightful, data-driven, sometimes humorous
- Length: 1500 words
- Structure: Intro -> Problem -> Solution -> Benchmark -> Lessons"""
```

### 原则 4: 给出反面例子

```python
system_prompt = """You are a data analyst summarizing research papers.

CORRECT approach:
"The paper demonstrates a 15% improvement in latency through..."

INCORRECT approach:
"The paper is really interesting and shows that..."

Always be specific with numbers and mechanisms."""
```

---

## 第二部分：处理超长上下文 (2h)

### 问题：Token 限制

```
GPT-3.5-turbo:   4K tokens (约 3000 字)
GPT-4:           8K / 32K / 128K tokens
Claude 3 Opus:   200K tokens
Llama 2:         4K tokens
```

### 场景 1: 文档总结

```python
def summarize_long_document(doc_path, chunk_size=2000):
    """
    分块总结超长文档
    """
    with open(doc_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 按字符数分块（不是完美的，但快速）
    chunks = [content[i:i+chunk_size] for i in range(0, len(content), chunk_size)]
    
    chunk_summaries = []
    for i, chunk in enumerate(chunks):
        print(f"处理块 {i+1}/{len(chunks)}")
        summary = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Summarize the following text in 3-5 bullet points."},
                {"role": "user", "content": chunk}
            ]
        ).choices[0].message.content
        chunk_summaries.append(summary)
    
    # 最终汇总
    final_summary = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Merge these summaries into a comprehensive overview."},
            {"role": "user", "content": "\n\n".join(chunk_summaries)}
        ]
    ).choices[0].message.content
    
    return final_summary
```

### 场景 2: 合同审查（只看关键部分）

```python
def extract_key_sections(contract_text):
    """
    不是读整个合同，而是让 AI 先识别关键部分
    """
    # 第一步：识别关键章节
    response1 = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": "Identify the most important sections in this contract (sections about payment, termination, liability, etc.). Return as a list of line numbers or section headers."
            },
            {"role": "user", "content": contract_text[:3000]}  # 只看前 3000 字识别结构
        ]
    ).choices[0].message.content
    
    print(f"关键部分:\n{response1}")
    
    # 第二步：只深入分析关键部分
    response2 = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": "Analyze these contract sections for risks. Focus on: payment terms, termination clauses, liability caps, and exclusions."
            },
            {"role": "user", "content": response1 + "\n\nNow analyze the full contract..."}
        ]
    ).choices[0].message.content
    
    return response2
```

### 场景 3: 日志分析（智能采样）

```python
import json
from datetime import datetime, timedelta

def analyze_logs_intelligently(log_file):
    """
    处理百万级日志，但只分析最相关的部分
    """
    with open(log_file) as f:
        lines = f.readlines()
    
    # 策略：采样最后 500 行 + 错误日志
    critical_lines = []
    
    # 加入最后 500 行
    critical_lines.extend(lines[-500:])
    
    # 加入所有 ERROR 和 CRITICAL 日志
    for line in lines:
        if 'ERROR' in line or 'CRITICAL' in line:
            critical_lines.append(line)
    
    # 去重并排序
    critical_lines = list(set(critical_lines))
    critical_text = "".join(critical_lines[:1000])  # 最多 1000 行
    
    analysis = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": "Analyze these application logs. Identify: 1) Root cause of issues 2) Severity 3) Recommended actions"
            },
            {"role": "user", "content": critical_text}
        ]
    ).choices[0].message.content
    
    return analysis
```

---

## 第三部分：JSON Mode 与结构化输出 (1h)

### 为什么需要 JSON Mode？

```python
# ❌ 问题：让 AI 返回 JSON，但结果不稳定
response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
        {
            "role": "user",
            "content": 'Extract name, age, email from "John Smith, 30, john@example.com". Return as JSON.'
        }
    ]
)

# 有时返回: {"name": "John Smith", "age": 30, "email": "john@example.com"}
# 有时返回: "Here is the JSON: {\"name\": \"John Smith\", ...}"
# 有时返回: "John Smith is 30 years old. Email: john@example.com"

# 结果混乱！

# ✅ 解决：用 JSON Mode（GPT-4 和某些 GPT-3.5 版本支持）
response = client.chat.completions.create(
    model="gpt-4-turbo",
    messages=[
        {
            "role": "system",
            "content": "You always respond with valid JSON."
        },
        {
            "role": "user",
            "content": 'Extract name, age, email from "John Smith, 30, john@example.com"'
        }
    ],
    response_format={"type": "json_object"}
)

# 现在一定返回 valid JSON
result = json.loads(response.choices[0].message.content)
print(result["name"])  # 安全！不会报错
```

### 场景 1: 数据提取

```python
import json
from typing import Any

def extract_data_from_text(text: str) -> dict:
    """
    从任意文本提取结构化数据
    """
    response = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=[
            {
                "role": "system",
                "content": """You are a data extraction expert. 
Extract the following fields and return valid JSON:
- person_name
- company
- job_title
- contact_email
- key_achievements (list of 3 items)

If a field is not found, use null."""
            },
            {
                "role": "user",
                "content": f"Extract data from: {text}"
            }
        ],
        response_format={"type": "json_object"}
    )
    
    return json.loads(response.choices[0].message.content)

# 使用
text = "Meet Jane Doe, VP of Product at Acme Corp. She led 3 successful launches. Contact: jane@acme.com"
data = extract_data_from_text(text)
print(data["person_name"])  # Jane Doe
```

### 场景 2: 分类任务

```python
def classify_support_ticket(ticket_text: str) -> dict:
    """
    对客服工单进行分类和优先级评定
    """
    response = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=[
            {
                "role": "system",
                "content": """Classify the support ticket. Return JSON:
{
    "category": "billing|technical|feature_request|other",
    "priority": "low|medium|high|critical",
    "sentiment": "positive|neutral|negative",
    "suggested_response_type": "automated|escalate|follow_up",
    "summary": "Brief summary"
}"""
            },
            {
                "role": "user",
                "content": ticket_text
            }
        ],
        response_format={"type": "json_object"}
    )
    
    return json.loads(response.choices[0].message.content)

# 使用
ticket = "My invoice shows $500 but I only used API 10 times. This is a billing error!"
result = classify_support_ticket(ticket)
print(f"优先级: {result['priority']}")  # high
print(f"分类: {result['category']}")     # billing
```

### 场景 3: 多步骤工作流

```python
def process_job_application(resume_text: str, job_description: str) -> dict:
    """
    评估求职者和职位的匹配度（多步骤）
    """
    
    # 步骤 1: 提取求职者信息
    step1_response = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=[
            {
                "role": "system",
                "content": """Extract from resume:
{
    "name": "",
    "experience_years": 0,
    "key_skills": [],
    "past_companies": [],
    "education": ""
}"""
            },
            {"role": "user", "content": resume_text}
        ],
        response_format={"type": "json_object"}
    ).choices[0].message.content
    
    candidate = json.loads(step1_response)
    
    # 步骤 2: 提取职位要求
    step2_response = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=[
            {
                "role": "system",
                "content": """Extract from job description:
{
    "position_title": "",
    "required_experience_years": 0,
    "required_skills": [],
    "preferred_skills": [],
    "education_requirement": ""
}"""
            },
            {"role": "user", "content": job_description}
        ],
        response_format={"type": "json_object"}
    ).choices[0].message.content
    
    job = json.loads(step2_response)
    
    # 步骤 3: 匹配和评分
    step3_response = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=[
            {
                "role": "system",
                "content": """Rate the match between candidate and job:
{
    "overall_match_score": 0-100,
    "matching_skills": [],
    "missing_skills": [],
    "recommendation": "strong_yes|yes|maybe|no"
}"""
            },
            {
                "role": "user",
                "content": f"Candidate: {json.dumps(candidate)}\n\nJob: {json.dumps(job)}"
            }
        ],
        response_format={"type": "json_object"}
    ).choices[0].message.content
    
    match = json.loads(step3_response)
    
    return {
        "candidate": candidate,
        "job": job,
        "match": match
    }
```

---

## 第四部分：多 LLM 提供商对比 (0.5h)

| 提供商 | 最强模型 | 成本 | 上下文 | 最佳用途 |
|--------|--------|------|--------|--------|
| OpenAI | GPT-4 | $$ | 128K | 复杂推理、高精度 |
| Anthropic | Claude 3 Opus | $$ | 200K | 长文本分析、法律 |
| DeepSeek | DeepSeek-67B | $ | 4K | 成本敏感的任务 |
| Meta | Llama 3 | 免费 (本地) | 8K | 隐私敏感、离线 |

### 成本对比（处理 100 万字）

```python
# 假设 1 百万字，价格对比：

# OpenAI GPT-3.5-turbo
# 费用: $0.0015 * 100 万 / 1000 = $150

# Claude 3 Haiku（便宜版本）
# 费用: $0.00025 * 100 万 / 1000 = $25

# DeepSeek API
# 费用: $0.00003 * 100 万 / 1000 = $3

# Llama 3 (本地 GPU)
# 费用: $0（你已经有 GPU）

# FDE 实践: 便宜的任务用 DeepSeek，复杂的用 GPT-4
```

---

## 实战案例：构建"智能文档助手"

```python
class SmartDocumentAssistant:
    def __init__(self, api_key):
        self.client = OpenAI(api_key=api_key)
    
    def process_document(self, doc_path):
        """完整的文档处理流程"""
        
        # 1. 加载文档
        with open(doc_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 2. 如果太长，采样关键部分
        if len(content) > 5000:
            content = self._smart_sample(content)
        
        # 3. 结构化提取
        extraction = self._extract_structure(content)
        
        # 4. 分类和标签
        classification = self._classify(content, extraction)
        
        # 5. 返回结果
        return {
            "extraction": extraction,
            "classification": classification,
            "summary": extraction.get("summary", "")
        }
    
    def _smart_sample(self, text):
        """智能采样"""
        lines = text.split('\n')
        # 取开头、中间、结尾
        sampled = lines[:100] + lines[len(lines)//2-50:len(lines)//2+50] + lines[-100:]
        return '\n'.join(sampled)
    
    def _extract_structure(self, text):
        """提取结构化数据"""
        response = self.client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[
                {
                    "role": "system",
                    "content": """Extract document structure as JSON:
{
    "title": "",
    "main_sections": [],
    "key_concepts": [],
    "summary": "",
    "metadata": {"author": "", "date": ""}
}"""
                },
                {"role": "user", "content": f"Document:\n{text}"}
            ],
            response_format={"type": "json_object"}
        )
        return json.loads(response.choices[0].message.content)
    
    def _classify(self, text, extraction):
        """分类"""
        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "Classify the document type and importance"
                },
                {"role": "user", "content": f"Structure: {extraction}"}
            ]
        )
        return response.choices[0].message.content
```

---

## 第二天的检查清单
- [ ] 写过 5 个不同的 System Prompt，看到了不同的回应
- [ ] 成功处理过超 5000 字的文本
- [ ] 使用了 JSON Mode 并解析了返回值
- [ ] 对比过 2+ 个 LLM 提供商
- [ ] 能解释为什么某个 System Prompt 比另一个更好

🎉 第 2 天完成！现在你是 API 调用高手。下一步：Streamlit 快速搭 UI。
