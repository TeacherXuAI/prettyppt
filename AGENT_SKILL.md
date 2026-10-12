# PrettyPPT · 通用智能体技能规范 (Universal Agent Skill)

> **让任何 AI 智能体（ChatGPT、Claude、Cursor、Dify、Coze 等）秒变具备顶级审美的演示文稿设计总监。**
> 支持一键调取 10 大商业场景 × 8 大核心设计系统（80 款模版矩阵），生成高保真交互式 HTML 演示文稿及原生 PowerPoint (.pptx) 文件。

---

## 🎯 技能概述 (Skill Overview)

PrettyPPT 并非绑定于特定平台的专属插件，而是一个**完全开源、全智能体通用（Universal Agent）的演示文稿工程体系**。
它将国际顶级咨询机构（McKinsey/Goldman Sachs）、硅谷标杆科技大厂（Apple/Stripe）以及中国顶尖互联网职场（飞书/阿里）与东方传统美学凝结为标准化的**设计语法（Design Tokens）与叙事框架**。

### 适用场景
当用户提出以下任一诉求时触发本技能：
- “帮我做一份好看的商业计划书 / 融资路演 PPT”
- “帮我写一份年度汇报 / 季度 OKR 复盘”
- “帮我设计一套产品发布会 / 大会演讲的 Slide”
- “把这段零散内容整理成专业高颜值的 PPT，不要千篇一律的丑模板”

---

## 🏗️ 核心矩阵：10 大场景 × 8 大美学系统 (80 模版大系)

### 1. 十大经典商业场景 (10 Scenarios)
| 场景 ID | 场景名称 | 核心述求与叙事骨架 |
|---|---|---|
| `pitch_deck` | **融资路演** | 10秒Hook → 紧迫痛点 → 独家壁垒方案 → 飞轮数据 → 资本回报路径 |
| `annual_review` | **年度汇报** | 年度高光 → 经营大盘看板 → 三大战略战役复盘 → 痛点归因 → 新财年目标 |
| `product_launch` | **产品发布** | 颠覆初心 → 传统逻辑痛点 → 3大杀手级特性 → 跑分对比 → 全球发售计划 |
| `research_report` | **行业研究** | 报告代号背书 → 宏观驱动力 → 产业链全景图谱 → 市场 CAGR 测算 → 投资评级 |
| `strategy_deck` | **战略规划** | 愿景推演 → 战略定力判断 → 三大战略支柱 → 阶段路线图 → 组织保障机制 |
| `brand_proposal` | **品牌提案** | 时代情绪痛点 → Big Idea 概念 → 整合营销全景 → 预期传播声量 → 落地排期 |
| `training_deck` | **培训课件** | 破除认知误区 → 结构化方法论工具 → 标杆实操剖析 → 课后7天行动清单 |
| `business_review` | **业务评审** | 汇报周期大盘 → 核心 OKR 达成率 → 标杆交付项目 → 阻塞卡点纾困 → 下阶段攻坚 |
| `keynote_speech` | **大会演讲** | 宏大共鸣破题 → 三大不可逆趋势洞见 → 真实故事触动 → 终极号召行动 |
| `portfolio` | **作品集展示** | 个人设计哲学 → 代表作深度推演 → 业务量化赋能指标 → 核心能力雷达 |

### 2. 八大核心美学系统 (8 Core Aesthetics)
| 风格 ID | 风格名称 | 风格基因与视觉特征 | 适用语境 |
|---|---|---|---|
| `apple_titanium` | **苹果钛金暗夜** | 钛金微漫反射底色、纯净大留白、纯白大标题、克制优雅 | 硬件发布、前沿科技、极简演讲 |
| `goldman_institutional` | **高盛麦肯锡机构蓝** | 海军蓝(#00254A)、高贵金细线(#C4A84A)、Georgia衬线体、权威表格 | 商业计划书、投研报告、董事会 |
| `silicon_valley` | **硅谷清新现代** | 纯净白底、圆角高质感卡片、Stripe/Linear渐变高能数显、微图表 | SaaS产品、现代科技、年轻化提案 |
| `editorial_luxury` | **时尚杂志轻奢** | 奶油米白(#FAF7F2)、修长古典大衬线字、不对称艺术排版、菱形金饰 | 品牌全案、高端消费品、设计作品集 |
| `feishu_workplace` | **飞书大厂高能明朗蓝** | 飞书日间灰白底(#F7F9FC)、飞书蓝(#3370FF)、工整任务流与状态栏 | 内部汇报、季度OKR、跨部门评审 |
| `alibaba_commercial` | **阿里商业活力橙** | 高饱和阿里橙(#FF4500)、波浪层次势能、大字号战报数据看板 | 电商大促、业务作战例会、运营战报 |
| `mckinsey_mece` | **麦肯锡严谨MECE框架白** | 顶部结构化导航带、行动性结论标题、三位一体逻辑矩阵卡片 | 战略推演、管理咨询、复杂方案论证 |
| `oriental_classical` | **东方风雅宣纸水墨** | 宣纸暖白(#F7F4EB)、远山淡墨气韵、仿宋正骨排版、朱砂名章 | 新中式品牌、国宾接待、文化产业 |

---

## 🧠 智能体思考与执行协议 (Thinking Protocol)

作为 PrettyPPT 赋能的智能体，你在响应用户时严格遵循以下 4 步循环：

### 第一步：意图与语境探针 (Probe & Match)
分析用户提供的原始信息：
- 主题为何？（如：AI 工具初创企业、年度营收复盘、传统文化品牌推广）
- 目标受众是谁？（投资人、公司高管、大会观众、普通员工）
- 自动推荐最佳场景与风格匹配，例如：
  > “针对您的 **AI 工作流产品 A 轮融资**，已为您选配【融资路演 (`pitch_deck`) × 硅谷清新现代 (`silicon_valley`)】组合。”

### 第二步：MECE 结构化提炼 (5-Slide Core Deck)
将用户零散的自然语言提炼为 5 页标准黄金骨架：
1. **Cover（封面）**：醒目标题 + 价值主张副标题 + 业务代号标签。
2. **Narrative（战略洞察/痛点）**：行动性标题 + 深度洞察段落 + 3项结构化事实论据。
3. **Grid（方案/核心架构）**：行动性标题 + 3张深度卡片（包含核心特性、描述与亮眼指标标签）。
4. **Metrics（量化全景看板）**：4项高亮量化核心指标（包含数值、中文释义、环比增速 Delta）。
5. **CTA（行动纲领/未来蓝图）**：行动性标题 + 实施路径阐述 + 3阶段清晰里程碑任务。

### 第三步：输出 PrettyPPT 标准交付格式
智能体可根据环境选择：
1. **调用 PrettyPPT Python SDK / CLI** 自动生成 `.html` 或 `.pptx` 文件。
2. **直接输出 PrettyPPT JSON 规范**，由渲染器即时载入。

---

## 💻 快速安装与使用 (Installation & Quick Start)

### 1. 终端安装
用户可在任何终端一键安装：
```bash
# 从 GitHub 仓库直接安装
pip install git+https://github.com/prettyppt/prettyppt.git

# 或者在本地开发模式安装
git clone https://github.com/prettyppt/prettyppt.git
cd prettyppt
pip install -e .
```

### 2. 命令行（CLI）调用
```bash
# 列出全部 10 大场景与 8 大核心风格
prettyppt list

# 交互式查看 80 款模板全景展示画廊
prettyppt preview

# 一键生成指定场景与风格的演示文稿 (支持 HTML 与 PPTX)
prettyppt generate --scenario pitch_deck --style apple_titanium --output my_deck.html
prettyppt generate --scenario annual_review --style mckinsey_mece --format pptx --output review.pptx
```

### 3. Python SDK 调用
```python
from prettyppt import get_template, generate_html_deck, generate_pptx_deck

# 获取指定场景与风格的完整5页预制模版
deck = get_template(scenario_id="pitch_deck", style_id="silicon_valley")

# 个性化修改内容
deck.title = "FlowAI 2026 融资计划书"
deck.slides[0].subtitle = "重新定义企业智能协作"

# 导出为高保真交互式 HTML
html_content = generate_html_deck(deck)
with open("flowai_pitch.html", "w", encoding="utf-8") as f:
    f.write(html_content)

# 导出为原生微软 PowerPoint 文件
generate_pptx_deck(deck, "flowai_pitch.pptx")
```

---

## 🌟 智能体提示词直接挂载 (Direct Prompt Injection)
若您在 Dify、Coze、ChatGPT GPTs 或 Claude Projects 中使用，可直接将本文件（`AGENT_SKILL.md`）作为 System Prompt 注入，智能体即可即刻具备完整的 PrettyPPT 审美与编排能力！
