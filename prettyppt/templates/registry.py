"""
Template Registry for PrettyPPT
Provides dynamic lookup and synthesis of all 80 core templates (10 Scenarios × 8 Core Styles),
and supports the full 160 matrix (10 Scenarios × 16 Styles).
"""

from typing import List, Dict, Any, Optional
from prettyppt.core.models import Presentation, Slide, Theme, MetricItem, CardItem
from prettyppt.templates.scenarios import SCENARIOS
from prettyppt.templates.styles import CORE_STYLES, ALL_STYLES

def list_scenarios() -> List[Dict[str, Any]]:
    """Returns all 10 scenario definitions."""
    return list(SCENARIOS.values())

def list_styles(only_core: bool = False) -> List[Dict[str, Any]]:
    """Returns styles (8 core or all 16)."""
    styles_dict = CORE_STYLES if only_core else ALL_STYLES
    return list(styles_dict.values())

def get_style_theme(style_id: str) -> Theme:
    """Builds a Theme object from style_id."""
    raw = ALL_STYLES.get(style_id) or CORE_STYLES["apple_titanium"]
    return Theme(
        id=raw["id"],
        name=raw["name"],
        name_zh=raw["name_zh"],
        category=raw["category"],
        mode=raw["mode"],
        bg_color=raw["bg_color"],
        text_color=raw["text_color"],
        accent_color=raw["accent_color"],
        secondary_accent=raw["secondary_accent"],
        card_bg=raw["card_bg"],
        card_border=raw["card_border"],
        font_family=raw["font_family"],
        description=raw["description"],
    )

def _build_scenario_deck(scenario_id: str, style_id: str) -> Presentation:
    """Synthesizes a complete 5-slide deck for any scenario x style combination."""
    sc = SCENARIOS.get(scenario_id) or SCENARIOS["pitch_deck"]
    theme = get_style_theme(style_id)

    # Contextual tailoring by scenario
    scenario_content = {
        "pitch_deck": {
            "title": "FlowAI",
            "subtitle": "新一代企业级智能工作流协同平台 · Series A 股权融资",
            "eyebrow": "2026 INVESTOR DECK · 融资金额 $30,000,000",
            "p2_title": "企业正陷入重复性业务流程的效能泥潭",
            "p2_body": "全球知识工作者每年平均消耗 340 小时在孤岛系统的反复数据搬运与审批流转中，传统 RPA 维护成本高企，通用大模型缺乏业务上下文落地能力。",
            "p2_bullets": [
                "数据孤岛严重：企业平均使用 88 款 SaaS 工具，数据割裂无协同",
                "维护成本暴增：传统低代码流程面对需求微调极易脆弱失效",
                "安全与合规红线：通用公有云大模型难以进入核心金融与涉密生产流",
            ],
            "p3_title": "自研轻量调度引擎，构建端到端自动化飞轮",
            "cards": [
                CardItem("毫秒级智能调度", "自研轻量路由算法，复杂跨系统任务端到端响应低于 120ms", tag="核心专利", metric="120ms"),
                CardItem("200+ 开箱集成", "深度兼容 ERP、CRM、工单系统与主流代码托管平台，零改造接入", tag="即插即用", metric="200+"),
                CardItem("自愈型执行架构", "流程异常自诊断与自适应回滚，生产环境高可用率达 99.98%", tag="高可用", metric="99.98%"),
            ],
            "p4_title": "核心商业化指标全线超预期增长",
            "p5_title": "融资方案与战略里程碑",
            "p5_body": "本轮拟融资 3,000 万美元，用于新一代多模态流程大模型底层研发（40%）、全球销售体系搭建（35%）与战略生态并购（25%）。",
            "p5_bullets": [
                "2026 Q4：完成美欧合规节点部署，进入 Fortune 500 核心供应商名录",
                "2027 Q2：实现单季度正向经营性现金流，ARR 突破 $5,000 万",
                "2028 Q1：启动纳斯达克/港交所主板 IPO 上市辅导路径",
            ],
        },
        "annual_review": {
            "title": "2026 年度经营总览与战略战役复盘",
            "subtitle": "守正笃行，韧性生长 · 董事会暨管理层年度汇报",
            "eyebrow": "ANNUAL REVIEW 2026 · CONFIDENTIAL",
            "p2_title": "逆势破局：全年经营大盘与财务基本面",
            "p2_body": "面对宏观周期波动，公司坚定执行'聚焦高毛利核心业务'战略，全年营收超额完成预算目标 138%，组织人效同比提升 46%。",
            "p2_bullets": [
                "营收高质量增长：SaaS 订阅收入占比从 48% 跃升至 72%",
                "降本增效成果显著：研发人均产值突破 180 万元，销管费率下降 12pt",
                "客户结构优化：客单价超 50 万标杆大客户贡献营收超 60%",
            ],
            "p3_title": "年度三大战略战役全面打赢",
            "cards": [
                CardItem("战役一：核心引擎重构", "自主研发下一代高性能架构按期上线，全网计算成本直降 38%", tag="技术破局", metric="100%交付"),
                CardItem("战役二：出海攻坚战", "成功拓展东南亚与欧洲六国市场，海外营收占比突破 25%", tag="增量引擎", metric="+210% YoY"),
                CardItem("战役三：组织精益化", "推行全面敏捷团队机制，端到端交付周期从 45 天压缩至 18 天", tag="人效跃迁", metric="45d → 18d"),
            ],
            "p4_title": "年度核心经营指标全景看板",
            "p5_title": "新财年核心战略定力与重点战役",
            "p5_body": "新一年度我们将继续锚定'AI原生商业化闭环'，推进技术壁垒深筑与全球化纵深拓展。",
            "p5_bullets": [
                "主营业务目标：力争新财年实现营收 8.5 亿元，经调整净利润破亿",
                "产品纵深：发布 2.0 原生大模型解决方案，建立垂直行业护城河",
                "组织演进：建立全球化分布式研发与本地化交付交付网络",
            ],
        },
        "product_launch": {
            "title": "Project Nebula ✦ 颠覆性亮相",
            "subtitle": "重新定义企业智能交互方式 · 2026 秋季全球新品发布",
            "eyebrow": "SPECIAL KEYNOTE EVENT · LIVE",
            "p2_title": "为什么今天的企业依然被繁琐绑架？",
            "p2_body": "技术在突飞猛进，但人机交互的方式依然停留在上个时代。点击、复制、等待——我们要做的，是让计算机真正理解你的意图并主动完成任务。",
            "p2_bullets": [
                "告别复杂表单：全自然语言意图直达，所想即所得",
                "跨越应用壁垒：打破孤立软件边界，全域自动化流转",
                "真正安全可控：企业级端侧加密推理，数据不出域",
            ],
            "p3_title": "重塑生产力的三大突破性特性",
            "cards": [
                CardItem("Neural Flow 引擎", "自研自适应多模态智能体，准确推断跨软件长链路复杂操作", tag="全球首创", metric="99.4%准确率"),
                CardItem("端侧秒级推理", "深度量化剪枝技术，支持千亿参数模型在普通工作站离线运行", tag="极致能效", metric="15ms极速"),
                CardItem("企业权限沙盒", "军工级权限隔离体系，确保每一次自动操作均具备可审计日志", tag="合规安全", metric="零越权"),
            ],
            "p4_title": "权威基准测试与性能大跃迁",
            "p5_title": "全球发售时间表与生态合作计划",
            "p5_body": "Project Nebula 今日起正式开启全球限量先行者体验，首批 100 家行业领军企业已深度部署。",
            "p5_bullets": [
                "开发者预览版：即刻向认证开发者全量推送 SDK 与 OpenAPI",
                "企业尊享版：2026 年 11 月 15 日全球多区域机房同步开服",
                "先行者权益：首期签约客户享终身 VIP 架构师 1 对 1 驻场支持",
            ],
        },
        "research_report": {
            "title": "2026 全球人工智能产业深度洞察报告",
            "subtitle": "从模型竞技到生产力平权 · 产业图谱、商业化路径与资本格局",
            "eyebrow": "GLOBAL INDUSTRY RESEARCH · Q4 2026",
            "p2_title": "宏观态势：大模型产业步入商业化务实验收期",
            "p2_body": "资本市场从纯参数军备竞赛逐步回归商业化投入产出比。能够切入真实复杂生产流程、具备高黏性与高复购能力的场景化方案正在享受最高估值溢价。",
            "p2_bullets": [
                "算力供给重构：自研专用 ASIC 与轻量端侧推理占比攀升",
                "开源生态平权：开源前沿模型性能逼近闭源，企业自部署比例达 38%",
                "监管规范成型：全球合规法案相继落地，合规能力成为核心进入门槛",
            ],
            "p3_title": "产业链核心参与者图谱与护城河",
            "cards": [
                CardItem("基础层（算力与网络）", "高带宽存储（HBM）与数据中心液冷技术成为关键瓶颈，集中度极高", tag="资本密集", metric="CR3 85%"),
                CardItem("模型层（泛化与垂直）", "通用基座趋于寡头化，垂直领域行业专业大模型毛利优势凸显", tag="差异突围", metric="3-5×毛利"),
                CardItem("应用层（Agent协同）", "多智能体协作经济爆发，企业级工作流自动化成为首要落地入口", tag="蓝海红利", metric="+180%增速"),
            ],
            "p4_title": "全球市场容量与复合增速预测",
            "p5_title": "产业投资洞察与标的筛选矩阵",
            "p5_body": "建议重点超配具备私域数据壁垒、深度嵌合企业工作流的应用龙头，谨慎对待纯套壳型工具类产品。",
            "p5_bullets": [
                "超配建议：具备高转换成本的垂直工作流操作系统标的",
                "中性建议：纯模型训练平台，面临云厂商双向挤压风险",
                "风险提示：算力电力供应短缺、跨国数据流动合规审查加剧",
            ],
        },
        "strategy_deck": {
            "title": "2026–2028 三年中长期战略规划",
            "subtitle": "夯实基盘 · 穿透周期 · 铸造世界级智能协同底座",
            "eyebrow": "STRATEGY ROADMAP · STRATEGIC PLANNING",
            "p2_title": "战略推演：我们身处何处，未来去往何方？",
            "p2_body": "未来三年是行业格局定型的决胜窗口期。必须在规模效应形成不可逆壁垒之前，完成从单点优势向生态型操作系统的全面跃迁。",
            "p2_bullets": [
                "阶段一（基盘巩固）：筑牢国内企业级标杆心智，营收突破 5 亿",
                "阶段二（横向扩展）：完成多模态与软硬一体化拓展，跨国布局破局",
                "阶段三（生态繁荣）：打造开放开发者生态，平台型收入占比超 40%",
            ],
            "p3_title": "驱动未来的三大战略支柱",
            "cards": [
                CardItem("支柱一：技术领航", "坚持核心算法全栈自研，在推理成本与安全性上建立绝对代差优势", tag="根本底座", metric="研发投入35%"),
                CardItem("支柱二：客户成功", "打造端到端专属咨询专家交付体系，将头部标杆 NRR 稳定在 140% 以上", tag="增长生命线", metric="NRR 140%+"),
                CardItem("支柱三：全球生态", "联合顶尖芯片厂商与全球系统集成商，共建开放应用繁荣生态", tag="护城河", metric="1,000+伙伴"),
            ],
            "p4_title": "三年关键战略目标拆解矩阵",
            "p5_title": "资源保障与组织机制革新",
            "p5_body": "战略决定组织，组织决定成败。我们将建立面向业务结果的特种作战小队机制，确保军令必达。",
            "p5_bullets": [
                "阵型重构：打破部门墙，设立以客户成功为核心的闭环作战单元",
                "激励倾斜：拿出 15% 战略期期权池，重奖关键战役卓越功勋团队",
                "容错文化：设立专项创新孵化基金，鼓励高风险高价值颠覆式探索",
            ],
        },
        "brand_proposal": {
            "title": "新纪元品牌焕新提案",
            "subtitle": "让科技拥有温度，让每一次协作成为艺术 · 整合营销策划案",
            "eyebrow": "BRAND REIMAGINED · PROPOSAL 2026",
            "p2_title": "时代洞察：当数字工具变成冰冷的数据机器",
            "p2_body": "受众对冰冷单调的'降本增效'话术早已产生审美疲劳。当代先锋企业需要的是既能解决效率瓶颈，又能激发团队审美与创造力的文化图腾。",
            "p2_bullets": [
                "疲惫的职场人渴望被赋能，而非被工具异化与规训",
                "高成长型创新企业正在用工作方式重塑雇主品牌吸引力",
                "美学体验正在成为企业级采购决策中决定性的隐形溢价",
            ],
            "p3_title": "核心创意概念：Flow with Elegance",
            "cards": [
                CardItem("美学赋能", "每一帧界面均按照现代艺术设计准则雕琢，工作如行云流水", tag="视觉哲学", metric="美感溢价"),
                CardItem("人本协同", "弱化冷酷指令感，强化智能体与人类同事之间的温润协作感", tag="情感共鸣", metric="满意度98%"),
                CardItem("先锋态度", "携手顶尖独立设计师与建筑师，联名打造'未来工作空间'概念", tag="跨界破圈", metric="3大重磅联名"),
            ],
            "p4_title": "全域整合传播声量规划与指标",
            "p5_title": "落地排期与全球发布方案",
            "p5_body": "以一场高规格的先锋设计艺术展拉开品牌焕新大幕，实现全网从圈层引爆到大众出圈的品效协同。",
            "p5_bullets": [
                "阶段一（蓄势预热）：先锋思想家纪录片《工作的未来艺术》全网首映",
                "阶段二（爆发大事件）：沉浸式未来办公艺术装置展全球巡回",
                "阶段三（长尾转化）：'百万创作者效率扶持计划'启动，沉淀品牌资产",
            ],
        },
        "training_deck": {
            "title": "企业级 AI 智能体实战训练营",
            "subtitle": "从业务痛点识别到落地闭环 · 核心工作流搭建实操指南",
            "eyebrow": "ENTERPRISE EMPOWERMENT · TRAINING 2026",
            "p2_title": "破除迷思：为什么大部分 AI 尝试都变成了鸡肋？",
            "p2_body": "很多团队以为引入了大模型就能立竿见影，却往往陷入'闲聊很惊艳、干活全靠手'的窘境。根本原因在于缺乏流程解构与工具链串联的方法论。",
            "p2_bullets": [
                "误区一：拿开放式提示词去应付严密的结构化业务交付",
                "误区二：缺乏中间状态可审计与异常回溯的兜底机制",
                "误区三：没有把数据接入权限与员工真实工作流打通",
            ],
            "p3_title": "四步闭环实战法：从定义到生产上线",
            "cards": [
                CardItem("Step 1: 业务动作原子化", "将长链条流程拆解为独立的判断节点与执行节点，明确输入输出规范", tag="拆解", metric="规范化"),
                CardItem("Step 2: 知识库私域增强", "构建精准企业知识检索体系，杜绝模型幻觉与不严谨表达", tag="固本", metric="准确率99%"),
                CardItem("Step 3: 多智能体协同装配", "专人专岗：审查Agent、执行Agent与复核Agent各司其职", tag="协作", metric="高可靠"),
            ],
            "p4_title": "训练营成效数据与标杆学员成果",
            "p5_title": "课后实践作业与行动清单",
            "p5_body": "培训的结束只是效率革命的起点。请每位学员在下周五前完成本部门第一个自动化试点流程的搭建。",
            "p5_bullets": [
                "Day 1-2：梳理出本岗位耗时前 3 名的重复机械工作任务",
                "Day 3-4：使用内置模板库完成初版自动化流的编排配置与自测",
                "Day 5：参与组内跨部门路演展示，优秀成果直通全公司推广部署",
            ],
        },
        "business_review": {
            "title": "2026 Q3 业务评审与交付进展汇报",
            "subtitle": "聚焦核心目标达成 · 剖析阻塞卡点 · 决战年度攻坚",
            "eyebrow": "BUSINESS REVIEW · Q3 2026",
            "p2_title": "大盘审视：主要业务线 KPI/OKR 达成总览",
            "p2_body": "本季度整体业务线保持强劲履约势能，核心营收指标达成率达 104.2%，大客户交付准时率保持在行业标杆水平。",
            "p2_bullets": [
                "核心业务A线：提前两周突破单季度 1.2 亿元签约大关",
                "创新业务B线：新客获取成本环比优化 24%，形成自我造血正循环",
                "客户保障C线：重大线上事故为 0，客户满意度综合评分 4.92 / 5.0",
            ],
            "p3_title": "重点攻坚成果与亮点业务复盘",
            "cards": [
                CardItem("标杆大客户交付", "某头部银行全行核心业务流程迁移平稳落地，一次性通过验收", tag="里程碑", metric="¥1,800万"),
                CardItem("核心算力成本优化", "推行精细化资源调度，在业务量翻倍的前提下算力开支同比下降 18%", tag="降本增效", metric="-18%成本"),
                CardItem("渠道生态破局", "新签约战略合作伙伴 42 家，代理渠道贡献商机占比突破 30%", tag="渠道扩容", metric="42家新伙伴"),
            ],
            "p4_title": "关键量化指标环比对比全览",
            "p5_title": "问题卡点剖析与下阶段作战排期",
            "p5_body": "虽然大盘健康，但依然存在中端销售线索转化周期偏长、交付人力局部紧张的问题，已制定针对性纾困措施。",
            "p5_bullets": [
                "资源诉求：紧急增补 5 名资深方案架构师，支援华东区重点项目抢收",
                "流程优化：简化合同内审流转环节，将商务签约平均周期由 14 天缩至 7 天",
                "年终冲刺：全面启动 Q4'雷霆战役'，确保全年集团超额利润激励到手",
            ],
        },
        "keynote_speech": {
            "title": "重新想象每一个人的力量",
            "subtitle": "在剧变时代的转折点，做点燃火种的开拓者 · 主题演讲",
            "eyebrow": "KEYNOTE ADDRESS · SUMMIT 2026",
            "p2_title": "我们正在见证历史，还是正在被历史塑造？",
            "p2_body": "人类历史上每一次生产工具的剧烈跃迁，都会伴随着巨大的迷茫与重构。但真正推动时代向前的，永远不是机器本身，而是紧握工具的那些不甘平庸的心灵。",
            "p2_bullets": [
                "工业革命解放了人类的体力，信息革命延伸了人类的眼界",
                "而今天的智能革命，正在把每一个人从琐碎的平庸中彻底解放",
                "不要问未来会带来什么，要问我们准备把世界塑造成什么模样",
            ],
            "p3_title": "通往明天的三个笃定信念",
            "cards": [
                CardItem("专注不可替代的创造力", "把能被算法穷举的交给算法，把需要温度、共情与判断的留给人类", tag="核心心法", metric="独一无二"),
                CardItem("永远站在前沿学习", "好奇心是抵御时代侵蚀的最佳护甲，终身学习者在这个时代无所畏惧", tag="认知进阶", metric="无限可能"),
                CardItem("做难而正确的事情", "快钱与捷径往往是平庸的陷阱，唯有构筑不可替代的深度才能穿透周期", tag="长期主义", metric="历久弥新"),
            ],
            "p4_title": "时代浪潮中的先锋足迹与印记",
            "p5_title": "行动，就在每一个当下的瞬间",
            "p5_body": "历史从不驻足等待观望者。愿我们在新时代的狂澜里，做奔腾的浪花，不做被冲刷的泥沙。",
            "p5_bullets": [
                "拥抱工具，勇敢尝试哪怕最微小的一次创新实践",
                "点燃身边的同路人，让每一次协同迸发出不可思议的火花",
                "致所有的开拓者：未来已来，让我们顶峰相见！",
            ],
        },
        "portfolio": {
            "title": "设计驱动增长 · 个人作品提案",
            "subtitle": "用系统化美学与工程思维，为数千万用户创造极致体验",
            "eyebrow": "PORTFOLIO & CASE ARCHIVE · 2026",
            "p2_title": "设计哲学：美学是最高的效能，克制是最高的奢华",
            "p2_body": "我深信优秀的产品设计绝不仅是视觉表层的装饰，而是对复杂业务逻辑的极致提炼与驯服。好的设计让用户感受不到界面的存在，只沉浸在顺畅的流动中。",
            "p2_bullets": [
                "数据与直觉兼备：以定性用户深度访谈为起点，以定量转化数据为标尺",
                "系统化组件思维：构建高扩展性设计系统，赋能跨职能团队百倍提效",
                "跨学科工程视野：兼通前端代码与视觉美学，消弭设计到落地的代沟",
            ],
            "p3_title": "三大主导操盘代表项目复盘",
            "cards": [
                CardItem("Project Alpha: 交易大厅重构", "重塑千万级专业交易员工作台，首屏信息密度与操作容错率大幅提升", tag="核心操盘", metric="+42%留存"),
                CardItem("Design System: 流水线设计语言", "从 0 到 1 搭建全公司跨端统一组件库，产品开发交付提速 3 倍", tag="体系中台", metric="120+组件"),
                CardItem("Project Pulse: 消费级体验创新", "打造颠覆行业常识的丝滑交互动效体系，斩获国际红点最佳设计大奖", tag="设计大奖", metric="Red Dot Winner"),
            ],
            "p4_title": "专业影响力与项目成果数据雷达",
            "p5_title": "能力模型全景与合作愿景",
            "p5_body": "期待加入具备卓越野心与美学追求的顶尖团队，共同定义下一代人机协作的世界级标杆体验。",
            "p5_bullets": [
                "专业专长：企业级产品体验架构 / 全端设计系统工程 / 品牌美学全案",
                "协同方式：擅长与战略高管、产品负责人及核心技术架构师深度共创",
                "联系方式：hello@designer.portfolio · 随时欢迎深入交流",
            ],
        },
    }

    content = scenario_content.get(scenario_id, scenario_content["pitch_deck"])
    def_metrics = sc.get("default_metrics", [])
    metric_items = [MetricItem(m["value"], m["label"], m.get("delta")) for m in def_metrics]

    slides = [
        # Slide 1: Cover
        Slide(
            slide_type="cover",
            title=content["title"],
            subtitle=content["subtitle"],
            eyebrow=content["eyebrow"],
            footer=f"PrettyPPT · {sc['name_zh']} · {theme.name_zh}",
        ),
        # Slide 2: Narrative / Context
        Slide(
            slide_type="narrative",
            title=content["p2_title"],
            eyebrow=f"01 / 战略背景与痛点洞察 · {sc['name_zh']}",
            body=content["p2_body"],
            bullets=content["p2_bullets"],
            footer=f"{content['title']} · 绝密材料",
        ),
        # Slide 3: Solution / Core Architecture
        Slide(
            slide_type="grid",
            title=content["p3_title"],
            eyebrow=f"02 / 核心能力与壁垒架构 · {sc['name_zh']}",
            cards=content["cards"],
            footer=f"{content['title']} · 架构总览",
        ),
        # Slide 4: Data & Metrics
        Slide(
            slide_type="metrics",
            title=content["p4_title"],
            eyebrow=f"03 / 量化指标全景看板 · {sc['name_zh']}",
            metrics=metric_items,
            body="所有量化数据均经严格内部审计与多维校验，持续保持高位稳健复合增长态势。",
            footer=f"{content['title']} · 数据看板",
        ),
        # Slide 5: CTA / Conclusion
        Slide(
            slide_type="cta",
            title=content["p5_title"],
            eyebrow=f"04 / 行动纲领与未来展望 · {sc['name_zh']}",
            body=content["p5_body"],
            bullets=content["p5_bullets"],
            footer=f"{content['title']} · 决胜未来",
        ),
    ]

    return Presentation(
        title=content["title"],
        scenario_id=scenario_id,
        style_id=style_id,
        subtitle=content["subtitle"],
        author="PrettyPPT Agent",
        date="2026",
        theme=theme,
        slides=slides,
    )

def get_template(scenario_id: str, style_id: str) -> Presentation:
    """Retrieves a specific template from the 80/160 matrix."""
    return _build_scenario_deck(scenario_id, style_id)

def get_all_templates(only_core: bool = True) -> List[Presentation]:
    """Generates all templates across the matrix (80 core or 160 all)."""
    styles_list = CORE_STYLES.keys() if only_core else ALL_STYLES.keys()
    decks = []
    for sc_id in SCENARIOS.keys():
        for st_id in styles_list:
            decks.append(_build_scenario_deck(sc_id, st_id))
    return decks
