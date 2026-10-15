"""Content-first planning. No model service, credentials, or fabricated facts.

Agents supply an edited brief; the deterministic fallback preserves source text.
All three modes share content validation and pagination, with different freedom
over composition. Layout overflow triggers a split or a useful error.
"""
from copy import deepcopy
import math
import re

from .models import Presentation, Slide, CardItem, MetricItem, Theme
from .layout import compose, LayoutError, LAYOUTS, TEXT_LAYOUTS, CARD_LAYOUTS, METRIC_LAYOUTS, units
from ..templates.catalog import template_spec, DEFAULT_STYLES, FAMILIES
from ..templates.styles import CORE_STYLES, ALL_STYLES
from ..templates.scenarios import SCENARIOS

KEYWORDS = {
    "pitch_deck": ["融资", "投资人", "商业计划书", "路演", "pitch", "fundrais"],
    "annual_review": ["年度", "年终", "年报", "annual"],
    "product_launch": ["产品介绍", "产品发布", "新品", "产品演示", "发布会", "product", "launch"],
    "research_report": ["研究", "行业分析", "白皮书", "research"],
    "strategy_deck": ["战略", "三年规划", "strategy", "strategic"],
    "brand_proposal": ["品牌", "营销提案", "传播方案", "brand", "campaign"],
    "training_deck": ["培训", "课程", "教学", "课件", "training", "workshop", "lesson"],
    "business_review": ["月度", "季度", "业务评审", "周报", "复盘", "review"],
    "keynote_speech": ["演讲", "大会", "keynote", "speech"],
    "portfolio": ["作品集", "个人履历", "求职", "portfolio"],
}
MODE_ALIASES = {"保守": "conservative", "套用": "conservative", "适度": "moderate", "中度": "moderate", "自由": "free", "开放": "free"}

def get_theme(style_id):
    if style_id not in ALL_STYLES:
        raise ValueError("Unknown style: " + str(style_id))
    raw = ALL_STYLES[style_id]
    return Theme(**{key: raw[key] for key in Theme.__dataclass_fields__})

def infer_scenario(purpose, title=""):
    purpose, title = purpose.lower(), title.lower()
    scores = {sc: sum((5 if word in purpose else 0) + (1 if word in title else 0) for word in words) for sc, words in KEYWORDS.items()}
    selected = max(scores, key=scores.get)
    return (selected, "用途关键词匹配") if scores[selected] else ("business_review", "未匹配明确场景，采用通用简报结构")

def _string(value, field):
    if not isinstance(value, str):
        raise ValueError(field + " must be a string")
    return value

def validate_brief(brief):
    if not isinstance(brief, dict):
        raise ValueError("Brief must be a JSON object")
    if not _string(brief.get("title", ""), "title").strip():
        raise ValueError("Brief needs a title")
    sections = brief.get("sections")
    if not isinstance(sections, list) or not sections:
        raise ValueError("Brief needs a non-empty sections array")
    for i, section in enumerate(sections):
        if not isinstance(section, dict):
            raise ValueError("sections[%d] must be an object" % i)
        prefix = "sections[%d]." % i
        if not _string(section.get("title", ""), prefix + "title").strip():
            raise ValueError(prefix + "title is required")
        for key in ("body", "subtitle", "role", "notes", "image_url", "layout"):
            if key in section:
                _string(section[key], prefix + key)
        for key in ("bullets", "sources"):
            if key in section and (not isinstance(section[key], list) or not all(isinstance(v, str) for v in section[key])):
                raise ValueError(prefix + key + " must be an array of strings")
        for key, required in (("cards", ("title", "desc")), ("metrics", ("value", "label"))):
            if key in section:
                if not isinstance(section[key], list):
                    raise ValueError(prefix + key + " must be an array")
                for item in section[key]:
                    if not isinstance(item, dict) or any(not isinstance(item.get(k), str) for k in required):
                        raise ValueError(prefix + key + " has missing or non-string fields")
                    allowed = {"title", "desc", "tag", "metric"} if key == "cards" else {"value", "label", "delta", "subtext"}
                    if set(item) - allowed or any(v is not None and not isinstance(v, str) for v in item.values()):
                        raise ValueError(prefix + key + " has unsupported fields or non-text values")
        if section.get("elements"):
            if any(section.get(k) for k in ("body", "subtitle", "bullets", "cards", "metrics", "table", "chart", "image_url")):
                raise ValueError("Custom elements must contain all visible content; do not mix with other section content")
            if not isinstance(section["elements"], list):
                raise ValueError("elements must be an array")
            for node in section["elements"]:
                if not isinstance(node, dict) or node.get("kind") not in ("text", "rect", "line", "image", "table", "chart"):
                    raise ValueError("Unsupported custom element")
                if any(not isinstance(node.get(k), (int, float)) or isinstance(node.get(k), bool) or not math.isfinite(node[k]) for k in ("x", "y", "w", "h")):
                    raise ValueError("Elements need finite numeric x/y/w/h")
                if node["kind"] == "text":
                    _string(node.get("text"), "elements.text")
                    size = node.get("size", 28)
                    if not isinstance(size, (int, float)) or not 14 <= size <= 140:
                        raise ValueError("Custom text size must be 14–140")
                    if node.get("align", "left") not in ("left", "center", "right"):
                        raise ValueError("Unknown text alignment")
                if node["kind"] in ("table", "chart"):
                    validate_brief({"title": "custom", "sections": [{"title": "custom", node["kind"]: node.get("data")} ]})
                if node["kind"] == "image":
                    _string(node.get("path"), "elements.path")
                if node["kind"] in ("rect", "line") and "color" not in node:
                    raise ValueError("Lines and rectangles need a color")
                if "color" in node and not re.fullmatch(r"#[0-9a-fA-F]{6}", str(node["color"])):
                    raise ValueError("Element colours must use #RRGGBB")
        table = section.get("table")
        if table is not None:
            if not isinstance(table, dict) or not table.get("headers") or not isinstance(table.get("rows"), list):
                raise ValueError(prefix + "table requires headers and rows")
            width = len(table["headers"])
            if width > 6 or any(not isinstance(v, str) for v in table["headers"]):
                raise ValueError("Tables support 1–6 text headers; split wider tables")
            for row in table["rows"]:
                if not isinstance(row, list) or len(row) != width or any(not isinstance(v, (str, int, float)) or isinstance(v, bool) for v in row):
                    raise ValueError(prefix + "table rows must match header width")
                if any(isinstance(v, float) and not math.isfinite(v) for v in row):
                    raise ValueError("Table numbers must be finite")
            if not table["rows"]:
                raise ValueError("Table needs at least one row")
        chart = section.get("chart")
        if chart is not None:
            if not isinstance(chart, dict) or not isinstance(chart.get("categories"), list) or not chart["categories"] or not all(isinstance(v, str) for v in chart["categories"]):
                raise ValueError("Chart requires text categories")
            if chart.get("kind", "bar") not in ("bar", "column", "line"):
                raise ValueError("Chart kind must be bar, column or line")
            if not isinstance(chart.get("series"), list) or not 1 <= len(chart["series"]) <= 3:
                raise ValueError("Chart requires 1–3 series")
            for series in chart["series"]:
                if not isinstance(series, dict) or not isinstance(series.get("name"), str) or not isinstance(series.get("values"), list):
                    raise ValueError("Chart series requires a name and values")
                if len(series["values"]) != len(chart["categories"]) or not all(isinstance(v, (float, int)) and not isinstance(v, bool) and math.isfinite(v) for v in series["values"]):
                    raise ValueError("Chart values must be finite numbers matching categories")
        if not any(section.get(k) for k in ("body", "subtitle", "bullets", "cards", "metrics", "table", "chart", "image_url", "elements")):
            raise ValueError(prefix + "has no content")
    return brief

def _chunk_text(text, limit):
    # Wrapping preserves every character. Newline boundaries are retained.
    result, current = [], ""
    for char in text:
        if current and units(current + char) > limit:
            result.append(current)
            current = ""
        current += char
    if current:
        result.append(current)
    return result

def _layout(section, spec, mode, index):
    family = FAMILIES[spec["style_id"]]
    role = section.get("role", "context")
    if section.get("elements"):
        if mode != "free":
            raise ValueError("Custom elements require free mode")
        return "custom"
    if section.get("layout"):
        if mode != "free":
            raise ValueError("Explicit layout overrides require free mode")
        allowed = {"table"} if section.get("table") else {"chart"} if section.get("chart") else {"image"} if section.get("image_url") else METRIC_LAYOUTS if section.get("metrics") else CARD_LAYOUTS if section.get("cards") else TEXT_LAYOUTS
        if section["layout"] not in allowed:
            raise ValueError("Unknown layout: " + section["layout"])
        return section["layout"]
    if section.get("table"):
        return "table"
    if section.get("chart"):
        return "chart"
    if section.get("image_url"):
        return "image"
    if section.get("metrics"):
        choices = [family["metrics"], "metric_ledger", "metric_columns"]
        if mode == "moderate" and (len(section["metrics"]) > 3 or any(units(m["label"]) > 16 for m in section["metrics"])):
            return "metric_ledger"
        return choices[index % len(choices)] if mode == "free" else choices[0]
    if section.get("cards"):
        chosen = spec["role_layout"].get(role, family["cards"])
        if chosen not in CARD_LAYOUTS:
            chosen = family["cards"]
        if mode == "free":
            return [chosen, "editorial_columns", "numbered_rows"][index % 3]
        if mode == "moderate":
            if len(section["cards"]) == 4:
                return "matrix"
            if any(units(card["desc"]) > 75 for card in section["cards"]):
                return "ledger"
            if len(section["cards"]) == 1:
                return "spotlight"
        return chosen
    if mode == "conservative":
        return family["text"]
    if mode == "free":
        return [family["text"], "editorial", "statement", "annotation"][index % 4]
    if units(section.get("body", "")) > 160:
        return "report"
    if not section.get("bullets") and units(section.get("body", "")) < 65:
        return "statement"
    return family["text"]

def _section_slides(section, spec, mode, index):
    layout = _layout(section, spec, mode, index)
    base = dict(slide_type=section.get("role", "narrative"), title=section["title"], sources=section.get("sources", []), notes=section.get("notes", ""), layout=layout)
    if section.get("elements"):
        return [Slide(**base, elements=deepcopy(section["elements"]))]
    body = "\n".join(v for v in (section.get("subtitle"), section.get("body")) if v)
    bullets = [chunk for v in section.get("bullets", []) for chunk in _chunk_text(v, 90)]
    slides = []
    # Complex evidence lives on its own page so it never drops narrative text.
    for key, cls in (("cards", CardItem), ("metrics", MetricItem)):
        if section.get(key):
            items = [cls(**v) for v in section[key]]
            # A section may contain several evidence types. Each resulting
            # page must choose a layout for its own payload, not a sibling's.
            item_section = {"role": section.get("role", "context"), key: section[key]}
            if section.get("layout"):
                item_section["layout"] = section["layout"]
            item_layout = _layout(item_section, spec, mode, index)
            capacity = 4 if item_layout == "matrix" else 3
            for start in range(0, len(items), capacity):
                slides.append(Slide(**dict(base, layout=item_layout), **{key: items[start:start + capacity]}))
    if section.get("table"):
        table = section["table"]
        for start in range(0, len(table["rows"]), 5):
            slides.append(Slide(**dict(base, layout="table"), table=dict(table, rows=table["rows"][start:start + 5])))
    if section.get("chart"):
        chart = section["chart"]
        for start in range(0, len(chart["categories"]), 8):
            part = deepcopy(chart)
            part["categories"] = chart["categories"][start:start + 8]
            for dst, src in zip(part["series"], chart["series"]):
                dst["values"] = src["values"][start:start + 8]
            slides.append(Slide(**dict(base, layout="chart"), chart=part))
    if section.get("image_url"):
        slides.append(Slide(**dict(base, layout="image"), image_url=section["image_url"]))
    text_base = dict(base, layout=FAMILIES[spec["style_id"]]["text"] if slides else layout)
    body_chunks = _chunk_text(body, 180 if bullets else 380)
    if not slides and len(body_chunks) <= 1 and len(bullets) <= 3:
        slides.append(Slide(**text_base, body=body, bullets=bullets))
    else:
        for chunk in body_chunks:
            slides.append(Slide(**text_base, body=chunk))
        for start in range(0, len(bullets), 3):
            slides.append(Slide(**text_base, bullets=bullets[start:start + 3]))
    return slides

def _split_overflow(slide):
    """Reduce one overflowing page without discarding a single field."""
    for field in ("cards", "metrics", "bullets"):
        values = getattr(slide, field)
        if len(values) > 1:
            middle = len(values) // 2
            a, b = deepcopy(slide), deepcopy(slide)
            setattr(a, field, values[:middle]); setattr(b, field, values[middle:])
            b.body = None
            return [a, b]
    if slide.body and slide.bullets:
        a, b = deepcopy(slide), deepcopy(slide)
        a.bullets = []; b.body = None
        return [a, b]
    if slide.body and len(slide.body) > 60:
        middle = len(slide.body) // 2
        a, b = deepcopy(slide), deepcopy(slide)
        a.body, b.body = slide.body[:middle], slide.body[middle:]
        return [a, b]
    if len(slide.bullets) == 1 and len(slide.bullets[0]) > 50:
        middle = len(slide.bullets[0]) // 2
        a, b = deepcopy(slide), deepcopy(slide)
        a.bullets, b.bullets = [slide.bullets[0][:middle]], [slide.bullets[0][middle:]]
        return [a, b]
    if len(slide.cards) == 1 and len(slide.cards[0].desc) > 50:
        a, b = deepcopy(slide), deepcopy(slide)
        value = slide.cards[0].desc
        a.cards[0].desc, b.cards[0].desc = value[:len(value)//2], value[len(value)//2:]
        a.cards[0].metric = None
        return [a, b]
    raise LayoutError("Page cannot fit; shorten its heading/value or supply an appropriate free layout: " + slide.title)

def create_presentation(brief, purpose=None, scenario_id="auto", style_id="auto", mode=None, pages=None):
    brief = validate_brief(deepcopy(brief))
    purpose = purpose or brief.get("purpose", "")
    mode = mode or brief.get("mode", "moderate")
    mode = MODE_ALIASES.get(mode, mode)
    if mode not in ("conservative", "moderate", "free"):
        raise ValueError("Mode must be conservative, moderate or free")
    scenario_id = brief.get("scenario_id", "auto") if scenario_id == "auto" else scenario_id
    reason = "用户指定场景"
    if scenario_id == "auto":
        scenario_id, reason = infer_scenario(purpose, brief["title"])
    if scenario_id not in SCENARIOS:
        raise ValueError("Unknown scenario: " + str(scenario_id))
    style_id = brief.get("style_id", "auto") if style_id == "auto" else style_id
    if style_id == "auto":
        style_id = DEFAULT_STYLES[scenario_id]
    spec = template_spec(scenario_id, style_id)
    theme = get_theme(style_id)
    if brief.get("design"):
        if mode != "free":
            raise ValueError("Custom design overrides require free mode")
        allowed = {"bg_color", "text_color", "accent_color", "secondary_accent"}
        if set(brief["design"]) - allowed:
            raise ValueError("Unknown design override")
        for key, value in brief["design"].items():
            if key.endswith("color") and not re.fullmatch(r"#[0-9a-fA-F]{6}", value):
                raise ValueError("Design colours must use #RRGGBB")
            setattr(theme, key, value)
    deck = Presentation(title=brief["title"], scenario_id=scenario_id, style_id=style_id, theme=theme, mode=mode, template_id=spec["id"], purpose=purpose, audience=brief.get("audience", ""), is_demo=bool(brief.get("is_demo", False)), decisions={"scenario_reason": reason, "template": spec["name"], "design_principle": spec["principle"], "page_policy": "按内容容量分页，保留全部输入章节", "mode": mode})
    if pages != 1 and brief.get("cover", True):
        deck.slides.append(Slide(slide_type="cover", title=brief["title"], subtitle=brief.get("subtitle", ""), eyebrow=brief.get("audience", ""), layout=spec["cover_layout"]))
    for i, section in enumerate(brief["sections"]):
        deck.slides.extend(_section_slides(section, spec, mode, i))
    index = 0
    while index < len(deck.slides):
        try:
            compose(deck, deck.slides[index], index)
            index += 1
        except LayoutError:
            if deck.slides[index].slide_type == "cover" or deck.slides[index].elements:
                raise
            deck.slides[index:index + 1] = _split_overflow(deck.slides[index])
    if pages is not None and (not isinstance(pages, int) or pages < 1 or len(deck.slides) != pages):
        raise ValueError("Content needs %d slides; requested %s. Have the Agent edit sections to that length; content was not dropped." % (len(deck.slides), pages))
    deck.decisions["slide_count"] = len(deck.slides)
    return deck
