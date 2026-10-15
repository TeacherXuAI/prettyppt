"""Shared, editable 1440x810 composition for HTML and PowerPoint.

Text is wrapped before export so both renderers use the same line breaks. This
module raises on content that cannot fit; callers must paginate, never clip it.
"""
import math
import re
import unicodedata

WIDTH, HEIGHT = 1440, 810
CARD_LAYOUTS = {"spotlight", "ledger", "feature_columns", "editorial_columns", "numbered_rows", "contrast", "matrix", "quiet_columns", "timeline", "steps", "roadmap", "comparison"}
TEXT_LAYOUTS = {"statement", "report", "split", "editorial", "brief", "impact", "analysis", "annotation"}
METRIC_LAYOUTS = {"hero_metric", "metric_ledger", "metric_columns", "metric_editorial", "metric_rows", "metric_impact", "metric_quiet"}
COVER_LAYOUTS = {"cover_stage", "cover_report", "cover_split", "cover_editorial", "cover_brief", "cover_impact", "cover_framework", "cover_quiet"}
LAYOUTS = CARD_LAYOUTS | TEXT_LAYOUTS | METRIC_LAYOUTS | COVER_LAYOUTS | {"table", "chart", "image", "custom"}

class LayoutError(ValueError):
    pass

def units(text):
    return sum(1.0 if unicodedata.east_asian_width(c) in "WF" else (0.33 if c.isspace() else 0.57) for c in text)

def wrap_text(text, capacity):
    """Preserve characters, including long Latin words and CJK, without ellipsis."""
    lines = []
    for paragraph in str(text).split("\n"):
        if not paragraph:
            lines.append("")
            continue
        current = ""
        for char in paragraph:
            if current and units(current + char) > capacity:
                if char in "，。；：！？、）》】”’…,.!?:;%" and len(current) > 1:
                    cut = len(current) - 1
                    while cut > 1 and current[cut] in "，。；：！？、）》】”’…,.!?:;%":
                        cut -= 1
                    lines.append(current[:cut])
                    current = current[cut:] + char
                    continue
                if current[-1] in "（《【“‘(":
                    lines.append(current[:-1])
                    current = current[-1] + char
                    continue
                # Prefer a word boundary, while keeping whitespace/content intact.
                pos = current.rfind(" ")
                if pos > len(current) // 2 and char.isascii() and char.isalnum():
                    lines.append(current[:pos + 1])
                    current = current[pos + 1:] + char
                else:
                    lines.append(current)
                    current = char
            else:
                current += char
        lines.append(current)
    # Avoid a single orphan character on short headings/subtitles.
    if len(lines) == 2 and units(lines[-1]) < capacity * .3 and units(lines[0]) > capacity * .7:
        joined = "".join(lines)
        target = units(joined) / 2
        cut = 1
        while cut < len(joined) - 1 and units(joined[:cut]) < target:
            cut += 1
        while cut < len(joined) - 1 and joined[cut] in "，。；：！？、）》】”’…,.!?:;%":
            cut += 1
        if units(joined[:cut]) <= capacity and units(joined[cut:]) <= capacity:
            lines = [joined[:cut], joined[cut:]]
    return lines

class Canvas:
    def __init__(self, theme):
        self.theme = theme
        self.nodes = []
        self.font = "Songti SC" if theme.id in ("editorial_luxury", "oriental_classical") else "PingFang SC"

    def text(self, text, x, y, w, h, size=28, color=None, bold=False, align="left", role="body"):
        if not text:
            return
        lines = wrap_text(str(text), w / (size * 1.04))
        line_height = size * 1.42
        if len(lines) * line_height > h + 1:
            raise LayoutError("Text does not fit %s (%d lines in %.0fpx): %s" % (role, len(lines), h, str(text)[:45]))
        self.nodes.append(dict(kind="text", text="\n".join(lines), x=x, y=y, w=w, h=h, size=size, line_height=line_height, color=color or self.theme.text_color, bold=bold, align=align, font=self.font, role=role))

    def line(self, x, y, w, color=None, thickness=1):
        self.nodes.append(dict(kind="line", x=x, y=y, w=w, h=thickness, color=color or self.theme.accent_color))

    def block(self, x, y, w, h, color):
        self.nodes.append(dict(kind="rect", x=x, y=y, w=w, h=h, color=color))

    def payload(self, kind, x, y, w, h, **kwargs):
        self.nodes.append(dict(kind=kind, x=x, y=y, w=w, h=h, **kwargs))

def card_parts(card):
    return ("\n".join(x for x in (card.tag, card.title) if x), "\n".join(x for x in (card.desc, card.metric) if x))

def compose(pres, slide, index):
    if pres.theme is None:
        raise LayoutError("Presentation requires a theme")
    t = pres.theme
    for color in (t.bg_color, t.text_color, t.accent_color, t.secondary_accent):
        if not isinstance(color, str) or not re.fullmatch(r"#[0-9a-fA-F]{6}", color):
            raise LayoutError("Theme colours must use #RRGGBB")
    c = Canvas(t)
    layout = slide.layout or ("cover_stage" if slide.slide_type == "cover" else "feature_columns" if slide.cards else "metric_columns" if slide.metrics else "report")
    if layout not in LAYOUTS:
        raise LayoutError("Unknown layout: " + layout)
    subtitle = slide.subtitle or ""
    if layout in COVER_LAYOUTS:
        configs = {
            "cover_stage": (100, 225, 1220, 245, 76, "left", 104, 525, 1150),
            "cover_report": (150, 245, 1140, 235, 68, "left", 155, 555, 1040),
            "cover_split": (88, 185, 690, 365, 66, "left", 880, 380, 460),
            "cover_editorial": (88, 125, 1200, 300, 78, "left", 730, 545, 610),
            "cover_brief": (360, 200, 980, 315, 66, "left", 360, 560, 940),
            "cover_impact": (88, 130, 1240, 370, 86, "left", 690, 565, 640),
            "cover_framework": (88, 280, 1230, 230, 66, "left", 88, 560, 1100),
            "cover_quiet": (490, 160, 850, 360, 70, "right", 120, 570, 940),
        }
        x, y, w, h, size, align, sx, sy, sw = configs[layout]
        if layout == "cover_brief":
            c.line(88, 195, 190, t.accent_color, 5)
            c.text(slide.eyebrow or "", 88, 230, 205, 200, 23, t.accent_color)
        else:
            c.text(slide.eyebrow or "", x, max(65, y - 85), w, 55, 20, t.accent_color)
        if layout in ("cover_report", "cover_framework"):
            c.line(88, 110, 1264, t.accent_color, 3)
        c.text(slide.title, x, y, w, h, size, t.accent_color if layout == "cover_impact" else t.text_color, True, align, "title")
        c.text(subtitle, sx, sy, sw, 145, 29, role="subtitle")
    elif layout == "custom":
        for node in slide.elements:
            if node.get("kind") == "text":
                c.text(node["text"], node["x"], node["y"], node["w"], node["h"], node.get("size", 28), node.get("color"), node.get("bold", False), node.get("align", "left"))
            else:
                c.nodes.append(dict(node))
    else:
        # Titles have generous fixed space; a long heading is rejected explicitly.
        header_x = 320 if layout == "brief" else 88
        header_w = 1030 if layout == "brief" else 1264
        c.text(slide.eyebrow or "", header_x, 49, header_w, 35, 17, t.accent_color)
        c.text(slide.title, header_x, 100, header_w, 150, 47, bold=True, role="title")
        body_y = 292
        if layout in ("report", "analysis", "ledger", "metric_ledger", "table"):
            c.line(88, 260, 1264, t.accent_color, 2)
        if slide.table or layout == "table":
            if not slide.table:
                raise LayoutError("Table layout requires table data")
            c.payload("table", 88, body_y, 1264, 415, data=slide.table)
        elif slide.chart or layout == "chart":
            if not slide.chart:
                raise LayoutError("Chart layout requires chart data")
            c.payload("chart", 88, body_y, 1264, 415, data=slide.chart)
        elif slide.image_url:
            text = "\n\n".join([v for v in [slide.body, *slide.bullets] if v])
            c.payload("image", 610, body_y, 742, 414, path=slide.image_url)
            c.text(text, 88, body_y, 440, 414, 27)
        elif slide.metrics:
            render_metrics(c, slide, layout, body_y)
        elif slide.cards:
            render_cards(c, slide, layout, body_y)
        else:
            render_text(c, slide, layout, body_y)
    # Provenance belongs in notes; only user-supplied footer or demo label appears.
    footer = "演示示例 · 内容与数据为虚构占位" if pres.is_demo else slide.footer or ""
    c.text(footer, 88, 757, 1130, 28, 15, role="footer")
    c.text("%02d / %02d" % (index + 1, len(pres.slides)), 1225, 757, 127, 28, 15, align="right", role="page_number")
    for node in c.nodes:
        if node["kind"] not in ("text", "rect", "line", "image", "chart", "table"):
            raise LayoutError("Unsupported element kind")
        if "color" in node and not re.fullmatch(r"#[0-9a-fA-F]{6}", str(node["color"])):
            raise LayoutError("Element colours must use #RRGGBB")
        if not all(math.isfinite(float(node.get(k, 0))) for k in ("x", "y", "w", "h")):
            raise LayoutError("Non-finite element geometry")
        if node["x"] < 0 or node["y"] < 0 or node["w"] <= 0 or node["h"] <= 0 or node["x"] + node["w"] > WIDTH + 1 or node["y"] + node["h"] > HEIGHT + 1:
            raise LayoutError("Element falls outside the slide")
    return c.nodes

def render_text(c, slide, layout, y):
    body = slide.body or slide.subtitle or ""
    bullets = list(slide.bullets)
    if not bullets:
        c.text(body, 165 if layout == "annotation" else 88, y, 1080 if layout in ("annotation", "editorial") else 1264, 425, 32 if layout == "statement" else 29)
        return
    configs = {
        "statement": (88, 560, 31, 770, 575, 27),
        "report": (88, 385, 27, 540, 810, 27),
        "split": (88, 510, 29, 720, 630, 28),
        "editorial": (88, 610, 34, 850, 500, 25),
        "brief": (88, 175, 23, 320, 1030, 29),
        "impact": (88, 620, 39, 850, 500, 26),
        "analysis": (88, 380, 29, 560, 790, 27),
        "annotation": (910, 440, 28, 150, 660, 27),
    }
    bx, bw, bs, lx, lw, ls = configs.get(layout, configs["report"])
    c.text(body, bx, y, bw, 420, bs)
    row_height = 415 / len(bullets)
    for i, text in enumerate(bullets):
        py = y + i * row_height
        c.text(str(i + 1).zfill(2), lx, py, 50, 35, 18, c.theme.accent_color)
        c.text(text, lx + 65, py, lw - 65, row_height - 18, ls)

def render_cards(c, slide, layout, y):
    cards = slide.cards
    n = len(cards)
    if slide.body:
        c.text(slide.body, 88, y, 1264, 75, 25)
        y += 90
    available = 714 - y
    if layout in ("ledger", "numbered_rows", "roadmap", "steps"):
        row_h = available / n
        for i, card in enumerate(cards):
            title, body = card_parts(card)
            row_y = y + i * row_h
            offset = 72 if layout in ("steps", "numbered_rows") else 0
            if offset:
                c.text(str(i + 1).zfill(2), 88, row_y, 60, row_h - 12, 30, c.theme.accent_color)
            c.text(title, 88 + offset, row_y, 340 - offset, row_h - 12, 25, bold=True)
            c.text(body, 500, row_y, 850, row_h - 12, 25)
            if i < n - 1:
                c.line(88, row_y + row_h - 8, 1264, c.theme.accent_color)
    elif layout == "spotlight":
        for i, card in enumerate(cards):
            title, body = card_parts(card)
            x, cy, w, h = (88, y, 565, available) if i == 0 else (790, y + (i - 1) * available / max(n - 1, 1), 560, available / max(n - 1, 1) - 20)
            c.text(title, x, cy, w, min(110, h * .4), 33 if i == 0 else 25, c.theme.accent_color, True)
            c.text(body, x, cy + min(120, h * .44), w, h - min(120, h * .44), 29 if i == 0 else 23)
    else:
        columns = 2 if layout in ("matrix", "comparison", "contrast") else n
        rows = math.ceil(n / columns)
        widths = [540, 315, 315] if layout == "editorial_columns" and n == 3 else [(1264 - 48 * (columns - 1)) / columns] * columns
        for i, card in enumerate(cards):
            row, col = divmod(i, columns)
            x = 88 + sum(widths[:col]) + 48 * col
            cell_h = available / rows
            cy = y + row * cell_h + (col * 24 if layout == "quiet_columns" else 0)
            w = widths[col]
            title, body = card_parts(card)
            if layout == "timeline":
                c.text(str(i + 1).zfill(2), x, cy, w, 55, 30, c.theme.accent_color)
                c.line(x, cy + 65, w)
                cy += 90
                cell_h -= 90
            c.text(title, x, cy, w, 115 if rows == 1 else 85, 28 if rows == 1 else 25, c.theme.accent_color, True)
            c.text(body, x, cy + (125 if rows == 1 else 90), w, cell_h - (145 if rows == 1 else 110) - (col * 24 if layout == "quiet_columns" else 0), 25 if rows == 1 else 23)

def render_metrics(c, slide, layout, y):
    metrics = slide.metrics
    if slide.body:
        c.text(slide.body, 88, y, 1264, 80, 25)
        y += 95
    available = 714 - y
    if layout in ("metric_ledger", "metric_rows"):
        row_h = available / len(metrics)
        for i, m in enumerate(metrics):
            cy = y + i * row_h
            c.text(m.label, 88, cy, 530, row_h - 8, 26)
            c.text(m.value, 660, cy, 340, row_h - 8, 33, c.theme.text_color, True)
            c.text("\n".join(v for v in (m.delta, m.subtext) if v), 1070, cy, 280, row_h - 8, 22)
            if i < len(metrics) - 1:
                c.line(88, cy + row_h - 8, 1264)
    elif layout in ("hero_metric", "metric_impact") and len(metrics) > 1:
        first = metrics[0]
        c.text(first.value, 88, y, 620, 170, 88, c.theme.accent_color, True)
        c.text("\n".join(v for v in (first.label, first.delta, first.subtext) if v), 88, y + 190, 590, available - 190, 28)
        row_h = available / (len(metrics) - 1)
        for i, m in enumerate(metrics[1:]):
            cy = y + i * row_h
            c.text(m.value, 790, cy, 560, 67, 42, bold=True)
            c.text("\n".join(v for v in (m.label, m.delta, m.subtext) if v), 790, cy + 70, 560, row_h - 80, 23)
    else:
        width = (1264 - 45 * (len(metrics) - 1)) / len(metrics)
        for i, m in enumerate(metrics):
            cy = y + (i * 25 if layout in ("metric_editorial", "metric_quiet") else 0)
            x = 88 + i * (width + 45)
            c.text(m.value, x, cy, width, 165, 58 if len(metrics) < 4 else 45, c.theme.text_color, True)
            c.line(x, cy + 184, width)
            c.text("\n".join(v for v in (m.label, m.delta, m.subtext) if v), x, cy + 210, width, available - 210 - (cy - y), 25)
