# 🎨 PrettyPPT

<div align="center">

**Universal AI-Agent Presentation Toolkit**  
*为所有智能体量身打造的顶级审美演示文稿生成引擎与 80 款母版矩阵*

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python: 3.8+](https://img.shields.io/badge/Python-3.8+-brightgreen.svg)](https://python.org)
[![Templates: 80+](https://img.shields.io/badge/Templates-80+-purple.svg)](#-80-款核心商业母版矩阵)
[![Zero Dependency](https://img.shields.io/badge/HTML%20Export-Zero%20Dependency-orange.svg)](#-一键安装与使用)

[🌟 核心特性](#-核心特性) • [🚀 快速开始](#-一键安装与使用) • [🤖 智能体挂载教程](#-让-ai-智能体拥有-prettyppt-技能) • [🎨 80款模板矩阵](#-80-款核心商业母版矩阵) • [💻 命令行-cli](#-命令行-cli-使用)

</div>

---

## 💡 为什么需要 PrettyPPT？

市面上多数由 AI 生成的 PPT 常常面临两个致命短板：
1. **千篇一律的模板套路**：颜色俗气、排版凌乱、缺乏留白与呼吸感，完全无法用于正式的投资人路演或董事会汇报。
2. **割裂的生态绑定**：很多技能只能在某一家封闭工具中使用，无法被 ChatGPT、Claude、Cursor、Dify、Coze 等通用智能体无缝复用。

**PrettyPPT 的解决方案：**
- **全智能体通用（Universal Agent）**：一套标准的 `AGENT_SKILL.md` 规范与 Master Prompt，任何大模型即插即用。
- **顶级东西方商业审美**：萃取苹果 Keynote、高盛麦肯锡、Stripe/Linear、时尚杂志以及飞书/阿里与东方风雅的设计语法。
- **10 大场景 × 8 大设计系统 = 80 款高质感母版**：每一款均拥有经过实战验证的叙事架构与排版细节。
- **零依赖极速生成**：原生 Python 环境开箱即用，生成可全屏演示、翻页、导出 PDF 的交互式 HTML 或微软原生 PowerPoint (.pptx)。

---

## 🚀 一键安装与使用

### 1. 从 GitHub 仓库一键安装
```bash
pip install git+https://github.com/prettyppt/prettyppt.git
```

### 2. 开发者本地安装
```bash
git clone https://github.com/prettyppt/prettyppt.git
cd prettyppt
pip install -e .
```

---

## 🤖 让 AI 智能体拥有 PrettyPPT 技能

无论你使用的是哪种智能体或大模型平台，均可通过最简单的方式赋予其制作顶级 PPT 的能力：

### 方案 A：在 Claude Projects / ChatGPT GPTs / Cursor 中挂载
直接将本仓库根目录下的 [`AGENT_SKILL.md`](AGENT_SKILL.md) 添加为 Project 知识库文件或系统提示词（System Prompt）。智能体即可自动学会：
- 识别用户诉求对应的最佳场景与风格；
- 遵循 MECE 原则输出 5 页严谨骨架；
- 按照顶级排版规范填充内容。

### 方案 B：在 Python 代码中一键调用
```python
from prettyppt import get_template, generate_html_deck, generate_pptx_deck

# 1. 获取「融资路演 × 苹果钛金暗夜」的完整5页预制模版
deck = get_template(scenario_id="pitch_deck", style_id="apple_titanium")

# 2. 结合用户的个性化输入快速替换内容
deck.title = "FlowAI 融资路演"
deck.slides[0].subtitle = "新一代企业级智能工作流协同平台 · Series A"

# 3. 导出为高保真交互式 HTML (支持快捷键翻页、全屏、导出PDF)
html_str = generate_html_deck(deck)
with open("flowai_pitch.html", "w", encoding="utf-8") as f:
    f.write(html_str)

# 4. (可选) 导出为原生微软 PowerPoint (.pptx)
generate_pptx_deck(deck, "flowai_pitch.pptx")
```

---

## 🎨 80 款核心商业母版矩阵

### 10 大经典商业场景 (10 Scenarios)
| 场景 ID | 场景名称 | 典型用途 | 核心叙事骨架 |
|---|---|---|---|
| `pitch_deck` | **融资路演** | 创业融资、Pre-A 到 IPO | 10秒Hook → 紧迫痛点 → 核心方案与壁垒 → 增长飞轮指标 → 融资方案 |
| `annual_review` | **年度汇报** | 年终复盘、董事会汇报 | 年度高光 → 经营大盘看板 → 三大战略战役复盘 → 痛点归因 → 新财年目标 |
| `product_launch` | **产品发布** | 新品发布会、版本更新 | 颠覆初心 → 传统逻辑痛点 → 3大杀手级特性 → 跑分对比 → 全球发售计划 |
| `research_report` | **行业研究** | 投研报告、智库白皮书 | 报告代号背书 → 宏观驱动力 → 产业链全景图谱 → 市场规模 CAGR → 投资评级 |
| `strategy_deck` | **战略规划** | 高管战略会、OKR 拆解 | 愿景推演 → 战略定力判断 → 三大战略支柱 → 阶段路线图 → 组织保障机制 |
| `brand_proposal` | **品牌提案** | 广告策划、4A 公关方案 | 时代情绪洞察 → Big Idea 概念 → 整合营销全景 → 预期传播声量 → 落地排期 |
| `training_deck` | **培训课件** | 企业内训、知识赋能公开课 | 破除认知误区 → 结构化方法论工具 → 标杆实操剖析 → 课后7天行动清单 |
| `business_review` | **业务评审** | 双周会、季度业务例会 | 汇报周期大盘 → 核心 OKR 达成率 → 标杆交付成果 → 阻塞卡点纾困 → 下阶段攻坚 |
| `keynote_speech` | **大会演讲** | TED 风格演讲、峰会主旨 | 宏大共鸣破题 → 三大不可逆趋势洞见 → 真实故事触动 → 终极号召行动 |
| `portfolio` | **作品集展示** | 个人设计作品集、专家述职 | 个人设计哲学 → 代表作深度推演 → 业务量化赋能指标 → 核心能力雷达 |

### 8 大核心设计美学系统 (8 Core Aesthetics)
| 风格 ID | 风格名称 | 流派归属 | 视觉 DNA 与特征 |
|---|---|---|---|
| `apple_titanium` | **苹果钛金暗夜** | 欧美极简 | 钛金深空灰漫反射底质、纯白极简标题、纯净呼吸留白、克制优雅 |
| `goldman_institutional` | **高盛麦肯锡机构蓝** | 欧美权威 | 海军蓝(#00254A)、高贵金细线(#C4A84A)、Georgia衬线体、权威表格 |
| `silicon_valley` | **硅谷清新现代** | 欧美现代 | 纯净白底、圆角高质感卡片、Stripe/Linear渐变与高能指标图表 |
| `editorial_luxury` | **时尚杂志轻奢** | 欧美艺术 | 奶油米白(#FAF7F2)、修长古典衬线字、不对称艺术排版、菱形金饰 |
| `feishu_workplace` | **飞书大厂高能明朗蓝** | 中国职场 | 飞书日间灰白底(#F7F9FC)、飞书蓝(#3370FF)、工整任务流与状态栏 |
| `alibaba_commercial` | **阿里商业活力橙** | 中国职场 | 高饱和阿里橙(#FF4500)、波浪层次势能、大字号战报数据看板 |
| `mckinsey_mece` | **麦肯锡严谨MECE框架白** | 咨询标准 | 顶部结构化导航带、行动性结论标题、三位一体逻辑矩阵卡片 |
| `oriental_classical` | **东方风雅宣纸水墨** | 东方传统 | 宣纸暖白(#F7F4EB)、远山淡墨气韵、仿宋正骨排版、朱砂古印 |

*(注：系统底层还支持粗野主义、数据新闻、visionOS毛玻璃、政务红蓝等 8 款扩展风格，总计 16 款视觉系统。)*

---

## 💻 命令行 (CLI) 使用

PrettyPPT 自带直观易用的命令行工具：

```bash
# 1. 查看所有支持的 10 大场景与 8 大风格
prettyppt list

# 2. 生成「融资路演 × 苹果钛金暗夜」的高清 HTML 演示文件并自动在浏览器中打开
prettyppt generate -s pitch_deck -t apple_titanium --open

# 3. 生成「年度汇报 × 麦肯锡MECE」的 PPTX 幻灯片
prettyppt generate -s annual_review -t mckinsey_mece -f pptx -o 2026_annual_review.pptx

# 4. 在浏览器中打开 80 款母版全景交互画廊
prettyppt preview

# 5. 打印供智能体使用的完整 Master System Prompt
prettyppt prompt
```

---

## 📐 设计规范与排版铁律

所有通过 PrettyPPT 产出的文稿均严格遵守四大黄金法则：
1. **Action Title 结论先行**：正文页标题统一采用具备论断性的完整主谓短语，读者仅需扫视标题即可掌握核心脉络。
2. **MECE 原则**：模块内容相互独立、完全穷尽，严禁信息交叉重叠。
3. **视觉锚点原则（Visual Anchor）**：任何单页均包含至少一处高对比视觉焦点（高亮数据 Callout、卡片组、时间线或对比框）。
4. **留白呼吸感**：版心最低保证 8% 边距，行距保持在 1.5 - 1.8 之间，拒绝杂乱密集堆叠。

---

## 📄 开源许可证

本项目基于 [MIT 许可证](LICENSE) 开源。欢迎所有开发者、设计爱好者与智能体团队参与贡献！
