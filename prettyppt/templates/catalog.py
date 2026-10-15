"""Eighty authored template recipes: narrative order, composition and art direction.

The eight design families deliberately use different geometry. A recipe is more
than a colour theme: it selects a scene-specific story and role-to-layout map.
"""
from copy import deepcopy
from .scenarios import SCENARIOS
from .styles import CORE_STYLES

FAMILIES = {
    "apple_titanium": dict(cover="cover_stage", text="statement", cards="spotlight", metrics="hero_metric", process="timeline", closing="statement", principle="单一主视觉，大标题先行；证据与说明分开呈现", density="sparse"),
    "goldman_institutional": dict(cover="cover_report", text="report", cards="ledger", metrics="metric_ledger", process="roadmap", closing="report", principle="报告式标题与摘要，左侧判断、右侧证据，细线对齐", density="balanced"),
    "silicon_valley": dict(cover="cover_split", text="split", cards="feature_columns", metrics="metric_columns", process="steps", closing="split", principle="左右分区与宽幅产品画面，功能说明形成清楚的阅读顺序", density="balanced"),
    "editorial_luxury": dict(cover="cover_editorial", text="editorial", cards="editorial_columns", metrics="metric_editorial", process="roadmap", closing="editorial", principle="非对称杂志网格，标题与正文错位，保留宽阔留白", density="sparse"),
    "feishu_workplace": dict(cover="cover_brief", text="brief", cards="numbered_rows", metrics="metric_rows", process="steps", closing="brief", principle="侧栏标识章节，正文按行动与责任顺序排列，易读优先", density="balanced"),
    "alibaba_commercial": dict(cover="cover_impact", text="impact", cards="contrast", metrics="metric_impact", process="timeline", closing="impact", principle="大字号关键事实与右侧说明形成对照，暖色只强调重点", density="sparse"),
    "mckinsey_mece": dict(cover="cover_framework", text="analysis", cards="matrix", metrics="metric_ledger", process="roadmap", closing="analysis", principle="结论、证据、行动分层；矩阵与表格使用原生可编辑元素", density="balanced"),
    "oriental_classical": dict(cover="cover_quiet", text="annotation", cards="quiet_columns", metrics="metric_quiet", process="timeline", closing="annotation", principle="右置标题与左侧注释，宋体和细线组织空间，避免装饰堆砌", density="sparse"),
}

# One row is one scenario's eight named editions, in CORE_STYLES order.
NAMES = {
    "pitch_deck": ["产品主张", "投资备忘录", "增长路径", "创始人叙事", "融资执行简报", "增长证据", "投资论证", "长期价值"],
    "annual_review": ["年度高光", "董事会年报", "增长回顾", "年度纪事", "团队复盘", "经营战报", "差距与举措", "年度札记"],
    "product_launch": ["新品舞台", "产品说明书", "功能体验", "产品画册", "版本发布简报", "核心卖点", "方案对比", "产品手记"],
    "research_report": ["研究发现", "机构研究", "趋势解读", "深度专题", "研究速览", "关键变化", "证据矩阵", "观察札记"],
    "strategy_deck": ["战略主张", "决策备忘录", "增长路线", "愿景叙事", "战略执行", "突破重点", "战略选择", "长线布局"],
    "brand_proposal": ["品牌主张", "品牌策略", "体验提案", "创意画册", "传播执行", "传播焦点", "定位论证", "品牌意境"],
    "training_deck": ["核心概念", "课程讲义", "操作工作坊", "案例读本", "实操步骤", "问题拆解", "知识框架", "学习札记"],
    "business_review": ["本期重点", "经营简报", "业务进展", "交付纪实", "行动复盘", "目标战报", "问题归因", "经营观察"],
    "keynote_speech": ["观点舞台", "主题论述", "未来体验", "故事演讲", "实践分享", "转折时刻", "论点与证据", "思想随笔"],
    "portfolio": ["作品聚光", "专业履历", "项目过程", "设计画册", "项目交付", "成果展示", "问题与方案", "创作手记"],
}

# Scene-specific structures. Optional sections are examples, never facts inserted
# into a real user's deck. The planner follows the supplied sections instead.
STORIES = {
    "pitch_deck": [("context", "客户问题"), ("solution", "产品方案"), ("evidence", "验证与进展"), ("business", "商业模式"), ("process", "资金用途与里程碑"), ("closing", "本轮合作诉求")],
    "annual_review": [("evidence", "年度结果"), ("solution", "重点项目"), ("comparison", "目标与实际"), ("context", "问题与原因"), ("process", "下一年度计划"), ("closing", "资源与决策事项")],
    "product_launch": [("context", "使用场景"), ("solution", "核心功能"), ("process", "使用流程"), ("comparison", "方案比较"), ("evidence", "验证与反馈"), ("closing", "上线与体验方式")],
    "research_report": [("context", "研究范围"), ("evidence", "主要发现"), ("comparison", "样本比较"), ("solution", "影响因素"), ("business", "局限与不确定性"), ("closing", "后续研究")],
    "strategy_deck": [("context", "现状判断"), ("comparison", "可选路径"), ("solution", "战略重点"), ("process", "阶段路线"), ("business", "资源配置"), ("closing", "决策与检查点")],
    "brand_proposal": [("context", "受众洞察"), ("solution", "品牌概念"), ("business", "内容与体验"), ("process", "传播节奏"), ("evidence", "效果衡量"), ("closing", "执行分工")],
    "training_deck": [("context", "学习目标"), ("solution", "核心方法"), ("process", "操作步骤"), ("comparison", "案例练习"), ("business", "常见问题"), ("closing", "练习与反馈")],
    "business_review": [("evidence", "本期结果"), ("solution", "项目进展"), ("comparison", "偏差分析"), ("context", "阻塞与原因"), ("process", "下期行动"), ("closing", "需协调事项")],
    "keynote_speech": [("context", "一个具体问题"), ("business", "亲历故事"), ("solution", "核心观点"), ("evidence", "例子与证据"), ("comparison", "另一种选择"), ("closing", "带走的思考")],
    "portfolio": [("context", "个人方向"), ("solution", "代表项目"), ("process", "设计过程"), ("comparison", "方案演进"), ("evidence", "成果与职责"), ("closing", "合作方式")],
}

DEFAULT_STYLES = {
    "pitch_deck": "goldman_institutional", "annual_review": "mckinsey_mece",
    "product_launch": "silicon_valley", "research_report": "goldman_institutional",
    "strategy_deck": "mckinsey_mece", "brand_proposal": "editorial_luxury",
    "training_deck": "feishu_workplace", "business_review": "feishu_workplace",
    "keynote_speech": "apple_titanium", "portfolio": "editorial_luxury",
}

def template_spec(scenario_id, style_id):
    if scenario_id not in SCENARIOS:
        raise ValueError("Unknown scenario: " + str(scenario_id))
    if style_id not in CORE_STYLES:
        raise ValueError("Template editions use the eight core styles: " + str(style_id))
    family = deepcopy(FAMILIES[style_id])
    story = list(STORIES[scenario_id])
    # Each edition has an editorial point of view as well as its own geometry.
    if style_id == "alibaba_commercial":
        story.sort(key=lambda item: 0 if item[0] == "evidence" else 1)
    elif style_id == "editorial_luxury" and scenario_id in ("portfolio", "brand_proposal", "keynote_speech"):
        story.sort(key=lambda item: 0 if item[0] in ("solution", "business") else 1)
    role_layout = {
        "cover": family["cover"], "context": family["text"],
        "solution": family["cards"], "business": family["text"],
        "evidence": family["metrics"], "comparison": "comparison",
        "process": family["process"], "closing": family["closing"],
    }
    return {
        "id": scenario_id + "/" + style_id,
        "scenario_id": scenario_id, "style_id": style_id,
        "name": SCENARIOS[scenario_id]["name_zh"] + " · " + NAMES[scenario_id][list(CORE_STYLES).index(style_id)],
        "principle": family["principle"], "density": family["density"],
        "role_layout": role_layout,
        "story": [{"role": role, "title": title, "layout": role_layout[role]} for role, title in story],
        "cover_layout": family["cover"],
    }

def list_templates(scenario_id=None):
    if scenario_id is not None and scenario_id not in SCENARIOS:
        raise ValueError("Unknown scenario: " + str(scenario_id))
    return [template_spec(sc, st) for sc in ([scenario_id] if scenario_id else SCENARIOS) for st in CORE_STYLES]
