# 🚀 FDE 快速上岗完整计划 (1-2 周救火式 Onboarding)

**欢迎来到奇绩创坛！** 这是你的 FDE 救火式上岗计划。

**核心理念**: 不是成为算法专家，而是在 **不确定的业务场景中，最快交付一个能跑通且有商业价值的 AI 系统**。

---

## 📋 完整学习路线 (1-2 周)

### 🟦 第一阶段：生存与基建（第 1-3 天，共 20 小时）

#### 目标
环境配好、Git 熟练、能接通 API、能快速写出第一个 Demo。

#### 学习清单

| 模块 | 核心任务 | 时间 | 达标标准 | 资源 |
|------|--------|------|--------|------|
| **工程协同** | 统一 Python 环境（Conda/Poetry），Git 操作流程 | 4h | 能 clone/pull/commit/push，不弄崩团队仓库 | [FDE_Engineering_Setup.md](FDE_Engineering_Setup.md) |
| **API 调用** | OpenAI / Anthropic / DeepSeek API | 6h | 掌握 System Prompt、长文本处理、JSON Mode | [FDE_API_Mastery.md](FDE_API_Mastery.md) |
| **快速 Demo** | Streamlit / Chainlit 前端 UI | 6h | 30 分钟内搭一个能演示的原型 | [FDE_Demo_Tools.md](FDE_Demo_Tools.md) |
| **第一个项目** | 完成"FAQ 对话"小项目 | 4h | 本地跑通 + 部署到 Streamlit Cloud | [Project_01_FAQ_Bot.md](Project_01_FAQ_Bot.md) |

#### 每天进度表
```
Day 1: 
  - 上午：环境配置 + Conda/Git 基础
  - 下午：第一次 API 调用成功
  - 晚上：读 System Prompt 最佳实践

Day 2:
  - 上午：Streamlit 快速上手
  - 下午：搭建"问答机器人"UI
  - 晚上：部署到云

Day 3:
  - 上午：完成第一个小项目
  - 下午：演讲稿准备
  - 晚上：复习+整理笔记
```

---

### 🟦 第二阶段：RAG 实战与 B2B 落地（第 4-7 天，共 24 小时）

#### 目标
解决企业私有数据"幻觉"问题。这是 FDE **最常见的工作**。

#### 学习清单

| 模块 | 核心任务 | 时间 | 达标标准 | 资源 |
|------|--------|------|--------|------|
| **RAG 链路** | 解析 → 切片 → 向量化 → 检索 | 8h | 理解 PDF、Excel、数据库不同处理策略 | [FDE_RAG_Deep_Dive.md](FDE_RAG_Deep_Dive.md) |
| **B2B 场景** | HR查制度、财务审合同、技术查文档 | 6h | 能根据场景选型（何时用 RAG、何时用 Text-to-SQL） | [FDE_B2B_Scenarios.md](FDE_B2B_Scenarios.md) |
| **本地部署** | Ollama + vLLM，GPU/CPU 判断 | 6h | 在任何机器上让模型跑起来 | [FDE_Local_Deployment.md](FDE_Local_Deployment.md) |
| **第二个项目** | "企业文档智能问答"完整系统 | 4h | 包含 RAG + 本地部署 + UI | [Project_02_Enterprise_RAG.md](Project_02_Enterprise_RAG.md) |

#### 每天进度表
```
Day 4:
  - 上午：RAG 链路讲解 + PyMuPDF
  - 下午：Chunking 策略讨论
  - 晚上：第一个 PDF 解析成功

Day 5:
  - 上午：向量化 + 向量库（Chroma/FAISS）
  - 下午：B2B 场景分析（3 个真实案例）
  - 晚上：选型练习

Day 6:
  - 上午：Ollama 本地部署
  - 下午：GPU/CPU 下的内存计算
  - 晚上：vLLM 高级用法

Day 7:
  - 上午：完整的 RAG 项目演示
  - 下午：优化 + 边界沟通
  - 晚上：项目复盘
```

---

### 🟦 第三阶段：Agent 工作流与沉淀（第 8-14 天，共 20 小时）

#### 目标
解决复杂逻辑，形成可复用的 Playbook。

#### 学习清单

| 模块 | 核心任务 | 时间 | 达标标准 | 资源 |
|------|--------|------|--------|------|
| **Agent 工作流** | LangGraph / Dify 多步任务编排 | 8h | 能处理"搜图 → 写文案 → 发邮件"这种循环任务 | [FDE_Agent_Workflow.md](FDE_Agent_Workflow.md) |
| **FDE 方法论** | 记录坑位、建立复盘模板 | 6h | 产出"项目交付复盘模板" | [FDE_Methodology.md](FDE_Methodology.md) |
| **第三个项目** | "多步工作流"实际项目 | 4h | 如：合同审查 → 提取信息 → 生成报告 | [Project_03_Multi_Step_Workflow.md](Project_03_Multi_Step_Workflow.md) |
| **上岗前准备** | 项目总结 + 思维导图 | 2h | 能给团队讲清楚你学到了什么 | [FDE_Readiness_Check.md](FDE_Readiness_Check.md) |

#### 每天进度表
```
Day 8-9:
  - LangGraph 基础 + 实例
  - Dify 工作流可视化
  - 第一个多步 Agent

Day 10-11:
  - 真实场景复盘（合同审查、HR 规则查询等）
  - 坑位整理 + 最佳实践
  - 项目交付模板完善

Day 12-13:
  - 完成第三个项目（多步工作流）
  - 代码复审 + 优化

Day 14:
  - 知识沉淀（写 Playbook）
  - 上岗前自测
  - 团队分享准备
```

---

## 📚 完整学习资源清单

### 核心文档（必读）
1. [FDE_Engineering_Setup.md](#) - 环境和协同
2. [FDE_API_Mastery.md](#) - API 调用和 Prompt
3. [FDE_Demo_Tools.md](#) - Streamlit/Chainlit
4. [FDE_RAG_Deep_Dive.md](#) - RAG 完整链路
5. [FDE_B2B_Scenarios.md](#) - 真实场景判断
6. [FDE_Local_Deployment.md](#) - 本地部署指南
7. [FDE_Agent_Workflow.md](#) - 多步工作流
8. [FDE_Methodology.md](#) - FDE 方法论

### 项目实践（动手）
1. [Project_01_FAQ_Bot.md](#) - Day 1-3 项目
2. [Project_02_Enterprise_RAG.md](#) - Day 4-7 项目
3. [Project_03_Multi_Step_Workflow.md](#) - Day 8-14 项目

### 参考资源（辅助）
1. [RAG_Day1_Core_Concepts.md](RAG_Day1_Core_Concepts.md) - RAG 基础概念（复用）
2. [RAG_Day2_Business_Adaptation.md](RAG_Day2_Business_Adaptation.md) - B2B 诊断框架（复用）
3. [QuickReference.md](QuickReference.md) - 快速查阅表（复用）

### 外部资源（推荐）
- **Streamlit 官方文档** [免费 | 2h]
- **Missing Semester (Git)** [免费 | 1h]
- **DeepLearning.AI: RAG** [免费/付费 | 5h]
- **LangChain Docs** [免费]
- **Dify.ai 开源 Repo** [免费]
- **Ollama 官网** [免费 | 30min]

---

## 🎯 合格标准：FDE Ready Checklist

当你能独立完成以下闭环时，你就是一个合格的 FDE 新人了：

### ✅ 第一阶段合格
- [ ] 能从零搭建 Python 环境（Conda/venv）
- [ ] Git 操作不会弄崩团队仓库
- [ ] 能独立调用 3 个不同的 LLM API（OpenAI/Claude/DeepSeek）
- [ ] 能用 Streamlit 在 30 分钟内搭个原型
- [ ] 完成项目 01（FAQ Bot）并部署上线

### ✅ 第二阶段合格
- [ ] 能解析 PDF、Excel、SQL 数据库
- [ ] 理解 Chunking 对 RAG 效果的影响
- [ ] 能判断"这个场景该用 RAG 还是 Text-to-SQL"
- [ ] 能在 CPU-only 和 GPU 环境下部署模型
- [ ] 完成项目 02（企业文档 RAG）并演示给客户

### ✅ 第三阶段合格（上岗前）
- [ ] 能用 LangGraph 或 Dify 编排多步任务
- [ ] 有一份"项目交付复盘模板"
- [ ] 能解释为什么某个项目失败了（并给出改进方案）
- [ ] 能给团队讲清楚你学到的 3 个最重要的事
- [ ] 完成项目 03（多步工作流）

---

## 🚀 每日学习节奏

### 推荐时间分配
```
每天 8 小时学习
├─ 30% (2.4h) 理论学习 + 看文档
├─ 40% (3.2h) 代码练习 + 跟进度
├─ 20% (1.6h) 项目实战
└─ 10% (0.8h) 总结 + 复盘

周末: 项目冲刺 + 知识沉淀
```

### 学习方法
```
不要只读文档！一定要：
1. 边读边敲代码
2. 遇到错误时自己 debug（不要一遇到问题就问）
3. 每个知识点都要有"自己的实例"
4. 每天晚上写 5-10 分钟的学习日记
```

---

## 💡 FDE 硬核建议

### 建议 1: 不要只做"对话"
```
❌ 错误: 搭一个"聊天框"，用户问什么答什么
✅ 正确: 左边放"原始文档"，右边放"AI 抽取的结构化表格"，中间放"引用来源"

有来源（Citations）的 RAG 才是客户敢用的 RAG！
```

### 建议 2: 处理多样化数据
```
PDF:      不要直接读，用 Marker / Unstructured 解析表格
Excel:    不要全喂给 RAG，用 Pandas Agent / Text-to-SQL
SQL DB:   用 SQL 查询，再把结果喂给 LLM
```

### 建议 3: 演示策略
```
永远准备一个"录屏备份"
原因: 客户现场网络差，API 可能超时，现场演示可能失败
方案: 事先录好演示视频，关键时刻播放
```

### 建议 4: 环境隔离很关键
```
❌ 错误: 把依赖包安装到全局系统
✅ 正确: 永远使用 venv 或 Conda

否则在客户服务器上部署时，会发生环境灾难！
```

### 建议 5: 本地部署必须掌握
```
CPU 环境:    llama.cpp / Ollama + GGUF 格式模型
GPU 环境:    检查 nvidia-smi + 用 vLLM

记住: 模型参数量 * 2 / 量化位数 = 最少需要的内存
      例如: 7B 模型 4-bit 量化 = 7GB 显存（留 2GB 给 Context）
```

---

## 📊 学习进度追踪

### 自我评估表

| 阶段 | 时间点 | 达标指标 | 你的进度 |
|------|--------|--------|--------|
| 第一阶段 | Day 3 结束 | 能独立部署 FAQ Bot | _____ |
| 第二阶段 | Day 7 结束 | 能独立部署 Enterprise RAG | _____ |
| 第三阶段 | Day 14 结束 | 能独立编排多步工作流 | _____ |

### 迷茫时的快速检查
```
如果你感到迷茫，问自己:

Q1: 我今天学的内容能用代码演示吗？
    是 → 继续深入
    否 → 重新看一遍文档，这次一定要跟代码

Q2: 我能给别人讲清楚这个概念吗？
    是 → 可以开始下一个主题
    否 → 写在笔记里，晚上准备讲稿

Q3: 我在实际项目中见过这个用法吗？
    是 → 记录下来，写进 Playbook
    否 → 找一个真实案例，改造一下演示

如果三个问题都是"是"，你就可以上岗了。
```

---

## 🎓 学习完成后

### 你将获得
- ✅ 3 个完整的项目（可以放进简历）
- ✅ 1 个"项目交付复盘模板"（FDE 的核心资产）
- ✅ 能独立处理 95% 的 B2B AI 需求
- ✅ 对"什么能做、什么做不了"有清晰的认知

### 你还不能做（但可以在实战中学）
- ❌ 从零训练/微调大模型
- ❌ 优化 Token 使用成本到极致
- ❌ 处理超大规模（百亿级）的数据
- ❌ 复杂的分布式系统架构

**没关系！** 因为 FDE 的工作就是用现成的工具快速交付。深度优化是 ML Engineer 的工作。

---

## 🆘 遇到问题怎么办？

### 第一步：自己 Debug 5 分钟
```
看报错信息 → 谷歌搜索 → Stack Overflow
90% 的问题都能自己解决
```

### 第二步：看文档和示例代码
```
找到类似的例子 → 改改参数 → 再试一遍
```

### 第三步：问导师或团队
```
只有在前两步都失败了，才问别人
但问之前，先给出：
1. 你试过什么
2. 报错信息是什么
3. 你觉得问题在哪
```

---

## ⏰ 时间表总览

```
Week 1:
  Day 1: 环境 + API
  Day 2: Streamlit
  Day 3: 项目 01 + 复盘
  Day 4: RAG 基础
  Day 5: B2B 场景
  Day 6: 本地部署
  Day 7: 项目 02 + 复盘

Week 2:
  Day 8-9:   Agent + Dify
  Day 10-11: 方法论 + Playbook
  Day 12-13: 项目 03
  Day 14:    最终准备 + 上岗前自测
```

---

## 📖 如何使用本学习系统

### 推荐阅读顺序

```
第 1-3 天：
  1. 本文档的第一阶段部分
  2. FDE_Engineering_Setup.md
  3. FDE_API_Mastery.md
  4. FDE_Demo_Tools.md
  5. Project_01_FAQ_Bot.md

第 4-7 天：
  6. FDE_RAG_Deep_Dive.md
  7. FDE_B2B_Scenarios.md
  8. FDE_Local_Deployment.md
  9. Project_02_Enterprise_RAG.md

第 8-14 天：
  10. FDE_Agent_Workflow.md
  11. FDE_Methodology.md
  12. Project_03_Multi_Step_Workflow.md
  13. FDE_Readiness_Check.md
```

### 每个文档的用法

- **理论文档** (FDE_*.md): 早上读 + 做笔记 + 下午实践
- **项目文档** (Project_*.md): 动手做 + 遇到问题再回头看理论
- **参考资源** (RAG_*.md): 需要时查阅

---

## 🎯 最后的话

> **FDE 不是要你成为专家，而是要你快速解决问题。**
> 
> 当你能在 24 小时内，从"听客户描述需求"到"演示一个能跑通的原型"，
> 你就成功了。
>
> 其他的（代码优雅度、算法创新、系统复杂度）都是次要的。
>
> 记住：**速度 > 完美**。

祝你上岗顺利！🚀

---

**文档版本**: 1.0  
**最后更新**: 2025-12-22  
**状态**: 完成并交付
