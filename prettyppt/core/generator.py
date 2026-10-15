"""
Multi-Format Generator for PrettyPPT.

Generates:
1. High-fidelity, bespoke, interactive HTML presentations with authentic aesthetic
   layouts for all 8 core styles across all slides, responsive scaling, full-screen mode,
   keyboard navigation, and print/PDF support. 100% offline, zero remote dependencies.
2. Native Microsoft PowerPoint (.pptx) widescreen presentations via python-pptx with
   native editable charts, tables, shapes, and speaker notes.
"""

import base64
import html
import io
import mimetypes
import os
import re
from pathlib import Path
from typing import Optional, Dict, Any, List

from prettyppt.core.models import Presentation, Slide, Theme
from prettyppt.core.layout import WIDTH, HEIGHT, compose, wrap_text, LayoutError


def _image_data(path):
    source = Path(path).expanduser()
    if not source.is_file():
        raise ValueError("Image file does not exist: " + str(source))
    mime = mimetypes.guess_type(str(source))[0]
    if mime not in ("image/png", "image/jpeg", "image/gif", "image/webp"):
        raise ValueError("Use a local PNG, JPEG, GIF or WebP image")
    return "data:%s;base64,%s" % (mime, base64.b64encode(source.read_bytes()).decode("ascii"))


def _table_cells(data, width, height):
    if not isinstance(data, dict) or not data.get("headers") or not data.get("rows"):
        raise LayoutError("Table requires headers and data rows")
    rows = [data["headers"]] + data["rows"]
    if any(len(row) != len(data["headers"]) for row in rows):
        raise LayoutError("Table rows must match the header width")
    col_w, row_h = width / len(data["headers"]), height / len(rows)
    result = []
    for row in rows:
        cells = ["\n".join(wrap_text(str(value), (col_w - 26) / (23 * 1.04))) for value in row]
        if any(len(cell.split("\n")) * 32.66 > row_h - 16 for cell in cells):
            raise LayoutError("Table cell does not fit; shorten text or split the table")
        result.append(cells)
    return result


def _chart_svg(data, width, height, theme):
    esc = lambda v: html.escape(str(v), quote=True)
    colors = [theme.accent_color, theme.secondary_accent, theme.text_color]
    series = data["series"]
    values = [v for item in series for v in item["values"]]
    low, high = min(0, min(values)), max(0, max(values))
    if high == low:
        high = low + 1
    left, top, plot_w, plot_h = 150, 55, width - 205, height - 120
    n, count = len(data["categories"]), len(series)
    parts = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %s %s" role="img" aria-label="%s">' % (width, height, esc(data.get("title", "数据图表")))]
    
    def label(x, y, value, size=18, anchor="start", color=None):
        parts.append('<text x="%s" y="%s" fill="%s" font-size="%s" text-anchor="%s">%s</text>' % (x, y, color or theme.text_color, size, anchor, esc(value)))
        
    for i, item in enumerate(series):
        label(15 + i * 340, 25, item["name"] + (" (" + data["unit"] + ")" if data.get("unit") else ""), 18, color=colors[i % len(colors)])
    kind = data.get("kind", "bar")
    if kind == "bar":
        zero_x = left + (0 - low) / (high - low) * plot_w
        for j, cat in enumerate(data["categories"]):
            slot = plot_h / n
            label(left - 15, top + (j + .5) * slot + 6, cat, 19, "end")
            for i, item in enumerate(series):
                value = item["values"][j]
                end_x = left + (value - low) / (high - low) * plot_w
                bar_h = min(27, slot * .7 / count)
                y = top + j * slot + (slot - bar_h * count) / 2 + i * bar_h
                parts.append('<rect x="%s" y="%s" width="%s" height="%s" fill="%s"/>' % (min(zero_x, end_x), y, max(abs(end_x - zero_x), .2), bar_h - 2, colors[i % len(colors)]))
                label(end_x + (6 if value >= 0 else -6), y + bar_h - 3, value, 16, "start" if value >= 0 else "end")
    else:
        def cy(value):
            return top + (high - value) / (high - low) * plot_h
        for j, cat in enumerate(data["categories"]):
            x = left + (j + .5) * plot_w / n
            label(x, top + plot_h + 35, cat, 18, "middle")
        for i, item in enumerate(series):
            points = []
            for j, value in enumerate(item["values"]):
                x = left + (j + .5) * plot_w / n
                if kind == "column":
                    bar_w = min(48, plot_w / n * .7 / count)
                    x += (i - count / 2) * bar_w
                    parts.append('<rect x="%s" y="%s" width="%s" height="%s" fill="%s"/>' % (x, min(cy(0), cy(value)), bar_w - 3, max(abs(cy(0) - cy(value)), .2), colors[i % len(colors)]))
                    label(x + bar_w / 2, cy(value) - 7 if value >= 0 else cy(value) + 20, value, 16, "middle")
                else:
                    points.append("%s,%s" % (x, cy(value)))
                    parts.append('<circle cx="%s" cy="%s" r="5" fill="%s"/>' % (x, cy(value), colors[i % len(colors)]))
                    label(x, cy(value) - 12, value, 16, "middle")
            if kind == "line":
                parts.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="3"/>' % (" ".join(points), colors[i % len(colors)]))
    parts.append('</svg>')
    return "".join(parts)


def _html_node(node, theme):
    esc = lambda s: html.escape(str(s), quote=True)
    position = "position:absolute;left:%spx;top:%spx;width:%spx;height:%spx;" % tuple(node[k] for k in ("x", "y", "w", "h"))
    kind = node["kind"]
    if kind == "text":
        style = position + "font-size:%spx;line-height:%spx;color:%s;font-weight:%s;text-align:%s;font-family:'%s','Noto Sans CJK SC',sans-serif;white-space:pre;" % (node["size"], node["line_height"], node["color"], 700 if node["bold"] else 400, node["align"], node["font"])
        return '<div class="text" data-role="%s" style="%s">%s</div>' % (esc(node.get("role", "body")), esc(style), html.escape(str(node["text"])))
    if kind in ("line", "rect"):
        return '<div aria-hidden="true" style="%sbackground:%s"></div>' % (position, esc(node["color"]))
    if kind == "image":
        return '<img alt="%s" style="%sobject-fit:contain" src="%s">' % (esc(node.get("alt", "用户提供的图片")), position, _image_data(node["path"]))
    if kind == "table":
        rows = _table_cells(node["data"], node["w"], node["h"])
        table = '<table style="%sborder-collapse:collapse;table-layout:fixed;font-size:23px;color:%s">' % (position, theme.text_color)
        for i, row in enumerate(rows):
            table += '<tr style="height:%spx">' % (node["h"] / len(rows))
            for value in row:
                tag = "th" if i == 0 else "td"
                table += '<%s style="text-align:left;vertical-align:middle;padding:8px 13px;white-space:pre;border-bottom:1px solid %s;line-height:32.66px">%s</%s>' % (tag, theme.accent_color, html.escape(str(value)), tag)
            table += '</tr>'
        return table + '</table>'
    if kind == "chart":
        return '<div style="%s">%s</div>' % (position, _chart_svg(node["data"], node["w"], node["h"], theme))
    raise ValueError("Unsupported element: " + str(kind))


def _render_bespoke_slide(style_id: str, idx: int, total: int, pres: Presentation, s: Slide, nodes: list) -> str:
    """Renders a complete, authentic bespoke slide layout for the given style and slide index."""
    theme = pres.theme
    esc = lambda v: html.escape(str(v)) if v is not None else ""
    esc_attr = lambda v: html.escape(str(v), quote=True) if v is not None else ""

    title = esc(s.title)
    subtitle = esc(s.subtitle) if s.subtitle else ""
    eyebrow = esc(s.eyebrow) if s.eyebrow else ""
    body = esc(s.body) if s.body else ""
    bullets = [esc(b) for b in s.bullets]
    footer_text = "演示示例 · 内容与数据为虚构占位" if pres.is_demo else esc(s.footer or "")

    is_cover = (s.slide_type == "cover" or (s.layout and s.layout.startswith("cover_")))

    # 1. STYLE 1: W1 · Apple Titanium Dark (苹果钛金暗夜)
    if style_id == "apple_titanium":
        bg_style = "background:radial-gradient(ellipse at 50% 18%, #232326 0%, #121214 65%, #0A0A0C 100%); color:#F5F5F7; font-family:-apple-system,'SF Pro Display',sans-serif;"
        if is_cover:
            eyebrow_text = eyebrow or f"{esc(pres.scenario_id.upper())} · SPECIAL EVENT"
            return f"""
            <div style="width:100%;height:100%;{bg_style}display:flex;flex-direction:column;justify-content:center;align-items:center;position:relative;overflow:hidden;text-align:center;padding:7%;">
              <div style="position:absolute;width:70%;height:50%;top:-10%;background:radial-gradient(ellipse,rgba(255,255,255,.07),transparent 70%);filter:blur(40px);"></div>
              <div style="font-size:16px;letter-spacing:.22em;color:#86868B;text-transform:uppercase;font-weight:600;margin-bottom:18px;position:relative;z-index:1;">{eyebrow_text}</div>
              <h1 style="font-size:62px;font-weight:700;letter-spacing:-.03em;color:#F5F5F7;line-height:1.1;margin-bottom:20px;position:relative;z-index:1;">
                <span style="background:linear-gradient(180deg,#FFFFFF 30%,#A1A1A6 100%);-webkit-background-clip:text;-webkit-text-fill-color:transparent;">{title}</span>
              </h1>
              {f'<div style="font-size:22px;color:#86868B;font-weight:400;max-width:80%;line-height:1.5;margin-bottom:28px;position:relative;z-index:1;">{subtitle}</div>' if subtitle else ''}
              <div style="display:flex;gap:12px;position:relative;z-index:1;">
                <span style="padding:6px 18px;border-radius:20px;background:rgba(255,255,255,.08);border:1px solid rgba(255,255,255,.14);font-size:14px;color:#E5E5EA;font-weight:500;letter-spacing:.06em;">
                  {esc(pres.scenario_id.upper())}
                </span>
                <span style="padding:6px 18px;border-radius:20px;background:rgba(41,151,255,.12);border:1px solid rgba(41,151,255,.25);font-size:14px;color:#2997FF;font-weight:600;">
                  Apple Titanium Edition
                </span>
              </div>
              <div style="position:absolute;bottom:24px;left:88px;right:88px;display:flex;justify-content:space-between;font-size:13px;color:#666;">
                <span>{footer_text}</span>
                <span>01 / {total:02d}</span>
              </div>
            </div>
            """
        # Inside Slide
        content_html = _render_standard_content(s, "apple_titanium", theme)
        return f"""
        <div style="width:100%;height:100%;{bg_style}padding:60px 88px 40px;display:flex;flex-direction:column;justify-content:space-between;position:relative;box-sizing:border-box;">
          <div>
            <div style="font-size:13px;letter-spacing:.2em;color:#86868B;text-transform:uppercase;font-weight:600;margin-bottom:8px;">{eyebrow or f'0{idx+1} / OVERVIEW'}</div>
            <h2 style="font-size:42px;font-weight:700;letter-spacing:-.02em;color:#F5F5F7;line-height:1.15;margin-bottom:24px;">
              <span style="background:linear-gradient(180deg,#FFFFFF 30%,#A1A1A6 100%);-webkit-background-clip:text;-webkit-text-fill-color:transparent;">{title}</span>
            </h2>
            {content_html}
          </div>
          <div style="display:flex;justify-content:space-between;font-size:13px;color:#666;border-top:1px solid rgba(255,255,255,.06);padding-top:16px;">
            <span>{footer_text}</span>
            <span>{idx+1:02d} / {total:02d}</span>
          </div>
        </div>
        """

    # 2. STYLE 2: W2 · Goldman Institutional Navy (高盛麦肯锡机构蓝)
    elif style_id == "goldman_institutional":
        bg_style = "background:#FFFFFF; color:#00254A; font-family:'Georgia',serif;"
        if is_cover:
            return f"""
            <div style="width:100%;height:100%;{bg_style}display:flex;position:relative;box-sizing:border-box;">
              <div style="width:36%;background:linear-gradient(180deg,#00254A,#001832);display:flex;flex-direction:column;justify-content:flex-end;padding:8% 6%;">
                <div style="font-size:72px;font-weight:200;color:rgba(255,255,255,.08);line-height:1;">{esc(pres.date or ('2026' if pres.is_demo else ''))}</div>
                <div style="font-size:12px;color:rgba(255,255,255,.4);letter-spacing:.22em;text-transform:uppercase;margin-top:14px;">{eyebrow or 'GLOBAL STRATEGY RESEARCH'}</div>
              </div>
              <div style="flex:1;padding:8% 8%;display:flex;flex-direction:column;justify-content:center;position:relative;">
                <div style="width:36px;height:2px;background:#C4A84A;margin-bottom:18px;"></div>
                <h1 style="font-size:48px;font-weight:400;color:#00254A;line-height:1.2;margin-bottom:16px;">{title}</h1>
                {f'<div style="font-size:18px;color:#5A6E85;line-height:1.6;margin-bottom:28px;">{subtitle}</div>' if subtitle else ''}
                <div style="font-size:11px;color:#A0AEC0;letter-spacing:.18em;text-transform:uppercase;border-top:1px solid #E2E8F0;padding-top:14px;">
                  {('CONFIDENTIAL · FOR ACCREDITED INVESTORS ONLY' if pres.is_demo else esc(pres.audience))}
                </div>
                <div style="position:absolute;bottom:24px;left:8%;right:8%;display:flex;justify-content:space-between;font-size:12px;color:#A0AEC0;">
                  <span>{footer_text}</span>
                  <span>01 / {total:02d}</span>
                </div>
              </div>
            </div>
            """
        content_html = _render_standard_content(s, "goldman_institutional", theme)
        return f"""
        <div style="width:100%;height:100%;{bg_style}padding:50px 88px 30px;display:flex;flex-direction:column;justify-content:space-between;position:relative;box-sizing:border-box;">
          <div style="position:absolute;top:0;left:0;right:0;height:4px;background:#00254A;"></div>
          <div>
            <div style="display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid #E2E8F0;padding-bottom:10px;margin-bottom:20px;">
              <span style="font-size:12px;font-weight:700;color:#00254A;letter-spacing:.15em;text-transform:uppercase;">{eyebrow or f'EXECUTIVE BRIEFING · 0{idx+1}'}</span>
              <span style="font-size:12px;color:#718096;">RESEARCH DIVISION</span>
            </div>
            <h2 style="font-size:38px;font-weight:400;color:#00254A;line-height:1.2;margin-bottom:24px;">{title}</h2>
            {content_html}
          </div>
          <div style="display:flex;justify-content:space-between;font-size:12px;color:#718096;border-top:1px solid #E2E8F0;padding-top:12px;">
            <span>{footer_text}</span>
            <span>{idx+1:02d} / {total:02d}</span>
          </div>
        </div>
        """

    # 3. STYLE 3: W3 · Silicon Valley Clean Modern (硅谷现代)
    elif style_id == "silicon_valley":
        bg_style = "background:#FFFFFF; color:#0A2540; font-family:-apple-system,BlinkMacSystemFont,'Inter',sans-serif;"
        mesh_bg = "background:radial-gradient(ellipse at 85% 15%,rgba(99,91,255,.07),transparent 60%),radial-gradient(ellipse at 15% 85%,rgba(0,212,255,.05),transparent 50%);"
        if is_cover:
            return f"""
            <div style="width:100%;height:100%;{bg_style}display:flex;position:relative;overflow:hidden;box-sizing:border-box;">
              <div style="position:absolute;inset:0;{mesh_bg}"></div>
              <div style="flex:1;padding:7% 7%;display:flex;flex-direction:column;justify-content:center;position:relative;z-index:1;">
                <div style="font-size:15px;font-weight:800;color:#635BFF;letter-spacing:-.02em;display:flex;align-items:center;gap:8px;margin-bottom:16px;">
                  <span style="width:8px;height:8px;border-radius:50%;background:linear-gradient(135deg,#635BFF,#00D4FF);"></span>
                  {eyebrow or esc(pres.scenario_id.upper())}
                </div>
                <h1 style="font-size:52px;font-weight:800;color:#0A2540;line-height:1.15;letter-spacing:-.03em;margin-bottom:16px;">
                  {title}
                </h1>
                {f'<div style="font-size:18px;color:#8892A0;line-height:1.6;margin-bottom:24px;max-width:85%;">{subtitle}</div>' if subtitle else ''}
                <div style="display:flex;gap:10px;">
                  <span style="padding:5px 14px;border-radius:20px;background:#F8F9FF;border:1px solid #EAECFF;color:#635BFF;font-size:13px;font-weight:600;">{('Series Ready' if pres.is_demo else '资料概览')}</span>
                  <span style="padding:5px 14px;border-radius:20px;background:#F0FCFF;border:1px solid #D6F6FF;color:#0891B2;font-size:13px;font-weight:600;">Silicon Valley Edition</span>
                </div>
              </div>
              <div style="width:42%;padding:6% 6% 6% 0;display:flex;align-items:center;justify-content:center;position:relative;z-index:1;">
                <div style="width:100%;background:#0A2540;border-radius:14px;padding:22px;box-shadow:0 18px 45px rgba(10,37,64,.25);">
                  <div style="display:flex;gap:6px;margin-bottom:16px;">
                    <div style="width:8px;height:8px;border-radius:50%;background:#FF5F57;"></div>
                    <div style="width:8px;height:8px;border-radius:50%;background:#FFBD2E;"></div>
                    <div style="width:8px;height:8px;border-radius:50%;background:#28CA41;"></div>
                  </div>
                  <div style="font-size:12px;font-family:monospace;color:#00D4FF;margin-bottom:8px;">{('// Intelligent Presentation Engine' if pres.is_demo else title)}</div>
                  <div style="height:8px;background:rgba(99,91,255,.5);border-radius:4px;width:80%;margin-bottom:8px;"></div>
                  <div style="height:8px;background:rgba(0,212,255,.4);border-radius:4px;width:60%;margin-bottom:8px;"></div>
                  <div style="height:8px;background:rgba(255,255,255,.2);border-radius:4px;width:40%;"></div>
                </div>
              </div>
              <div style="position:absolute;bottom:24px;left:7%;right:7%;display:flex;justify-content:space-between;font-size:13px;color:#8892A0;z-index:2;">
                <span>{footer_text}</span>
                <span>01 / {total:02d}</span>
              </div>
            </div>
            """
        content_html = _render_standard_content(s, "silicon_valley", theme)
        return f"""
        <div style="width:100%;height:100%;{bg_style}padding:50px 88px 30px;display:flex;flex-direction:column;justify-content:space-between;position:relative;box-sizing:border-box;">
          <div style="position:absolute;inset:0;{mesh_bg};pointer-events:none;"></div>
          <div style="position:relative;z-index:1;">
            <div style="font-size:13px;font-weight:700;color:#635BFF;letter-spacing:.15em;text-transform:uppercase;margin-bottom:6px;">{eyebrow or f'0{idx+1} / PRODUCT DISCOVERY'}</div>
            <h2 style="font-size:40px;font-weight:800;color:#0A2540;letter-spacing:-.02em;margin-bottom:24px;">{title}</h2>
            {content_html}
          </div>
          <div style="display:flex;justify-content:space-between;font-size:13px;color:#8892A0;border-top:1px solid #EAECFF;padding-top:14px;position:relative;z-index:1;">
            <span>{footer_text}</span>
            <span>{idx+1:02d} / {total:02d}</span>
          </div>
        </div>
        """

    # 4. STYLE 4: W4 · Editorial Luxury (典雅杂志留白)
    elif style_id == "editorial_luxury":
        bg_style = "background:#FAF7F2; color:#1A1410; font-family:'Georgia','Songti SC',serif;"
        if is_cover:
            return f"""
            <div style="width:100%;height:100%;{bg_style}display:flex;flex-direction:column;justify-content:center;align-items:center;padding:8% 12%;text-align:center;position:relative;box-sizing:border-box;">
              <div style="font-size:13px;color:#C5A96A;letter-spacing:.25em;text-transform:uppercase;font-weight:600;margin-bottom:16px;">{eyebrow or ('MONOGRAPH · 2026' if pres.is_demo else 'MONOGRAPH')}</div>
              <h1 style="font-size:54px;font-weight:300;color:#1A1410;line-height:1.2;letter-spacing:.04em;margin-bottom:18px;">{title}</h1>
              <div style="display:flex;align-items:center;gap:10px;margin-bottom:20px;">
                <span style="height:1px;background:#D4C090;width:32px;"></span>
                <span style="width:6px;height:6px;background:#C5A96A;transform:rotate(45deg);"></span>
                <span style="height:1px;background:#D4C090;width:32px;"></span>
              </div>
              {f'<div style="font-size:18px;color:#A09070;line-height:1.7;max-width:70%;">{subtitle}</div>' if subtitle else ''}
              <div style="position:absolute;bottom:24px;left:88px;right:88px;display:flex;justify-content:space-between;font-size:12px;color:#B0A490;">
                <span>{footer_text}</span>
                <span>01 / {total:02d}</span>
              </div>
            </div>
            """
        content_html = _render_standard_content(s, "editorial_luxury", theme)
        return f"""
        <div style="width:100%;height:100%;{bg_style}padding:55px 88px 30px;display:flex;flex-direction:column;justify-content:space-between;position:relative;box-sizing:border-box;">
          <div>
            <div style="font-size:12px;color:#C5A96A;letter-spacing:.22em;text-transform:uppercase;margin-bottom:8px;">{eyebrow or f'CHAPTER 0{idx+1}'}</div>
            <h2 style="font-size:38px;font-weight:300;color:#1A1410;letter-spacing:.03em;margin-bottom:24px;">{title}</h2>
            {content_html}
          </div>
          <div style="display:flex;justify-content:space-between;font-size:12px;color:#B0A490;border-top:1px solid #EADBCC;padding-top:14px;">
            <span>{footer_text}</span>
            <span>{idx+1:02d} / {total:02d}</span>
          </div>
        </div>
        """

    # 5. STYLE 5: C1 · Feishu Workplace (飞书高效职场)
    elif style_id == "feishu_workplace":
        bg_style = "background:#F7F9FC; color:#1F2329; font-family:-apple-system,BlinkMacSystemFont,'PingFang SC',sans-serif;"
        if is_cover:
            return f"""
            <div style="width:100%;height:100%;{bg_style}padding:7% 8%;display:flex;flex-direction:column;justify-content:center;position:relative;box-sizing:border-box;">
              <div style="display:inline-block;padding:4px 12px;border-radius:4px;background:#E8F0FF;color:#3370FF;font-size:13px;font-weight:700;letter-spacing:.05em;margin-bottom:16px;width:fit-content;">
                {eyebrow or f'{esc(pres.scenario_id.upper())} · 工作空间'}
              </div>
              <h1 style="font-size:50px;font-weight:700;color:#1F2329;line-height:1.2;margin-bottom:18px;">{title}</h1>
              {f'<div style="font-size:18px;color:#646A73;line-height:1.6;margin-bottom:28px;max-width:80%;">{subtitle}</div>' if subtitle else ''}
              <div style="display:flex;gap:12px;">
                <span style="padding:6px 14px;border-radius:6px;background:#FFFFFF;border:1px solid #DEE0E3;font-size:13px;color:#1F2329;font-weight:500;">
                  {('飞书协作标准' if pres.is_demo else '工作资料')}
                </span>
                <span style="padding:6px 14px;border-radius:6px;background:#3370FF;color:#FFFFFF;font-size:13px;font-weight:600;">
                  {('全员可读文档' if pres.is_demo else '内容概要')}
                </span>
              </div>
              <div style="position:absolute;bottom:24px;left:88px;right:88px;display:flex;justify-content:space-between;font-size:12px;color:#8F959E;">
                <span>{footer_text}</span>
                <span>01 / {total:02d}</span>
              </div>
            </div>
            """
        content_html = _render_standard_content(s, "feishu_workplace", theme)
        return f"""
        <div style="width:100%;height:100%;{bg_style}padding:50px 88px 30px;display:flex;flex-direction:column;justify-content:space-between;position:relative;box-sizing:border-box;">
          <div style="position:absolute;top:0;left:0;right:0;height:3px;background:#3370FF;"></div>
          <div>
            <div style="font-size:12px;font-weight:700;color:#3370FF;letter-spacing:.15em;text-transform:uppercase;margin-bottom:6px;">{eyebrow or f'SECTION 0{idx+1}'}</div>
            <h2 style="font-size:38px;font-weight:700;color:#1F2329;margin-bottom:24px;">{title}</h2>
            {content_html}
          </div>
          <div style="display:flex;justify-content:space-between;font-size:12px;color:#8F959E;border-top:1px solid #DEE0E3;padding-top:14px;">
            <span>{footer_text}</span>
            <span>{idx+1:02d} / {total:02d}</span>
          </div>
        </div>
        """

    # 6. STYLE 6: C4 · McKinsey MECE (麦肯锡 MECE 逻辑)
    elif style_id == "mckinsey_mece":
        bg_style = "background:#FFFFFF; color:#0F2D59; font-family:-apple-system,BlinkMacSystemFont,'PingFang SC',sans-serif;"
        if is_cover:
            return f"""
            <div style="width:100%;height:100%;{bg_style}padding:7% 8%;display:flex;flex-direction:column;justify-content:center;position:relative;box-sizing:border-box;">
              <div style="width:40px;height:4px;background:#0F2D59;margin-bottom:20px;"></div>
              <div style="font-size:13px;font-weight:800;color:#165DFF;letter-spacing:.18em;text-transform:uppercase;margin-bottom:12px;">{eyebrow or 'STRATEGIC ADVISORY'}</div>
              <h1 style="font-size:50px;font-weight:800;color:#0F2D59;line-height:1.2;margin-bottom:18px;">{title}</h1>
              {f'<div style="font-size:18px;color:#4E5969;line-height:1.6;margin-bottom:28px;max-width:80%;">{subtitle}</div>' if subtitle else ''}
              <div style="padding:6px 14px;border-radius:4px;background:#F7F8FA;border:1px solid #E5E6EB;display:inline-block;width:fit-content;font-size:13px;font-weight:700;color:#0F2D59;">
                MECE FRAMEWORK · EXECUTIVE BOARD BRIEFING
              </div>
              <div style="position:absolute;bottom:24px;left:88px;right:88px;display:flex;justify-content:space-between;font-size:12px;color:#86909C;">
                <span>{footer_text}</span>
                <span>01 / {total:02d}</span>
              </div>
            </div>
            """
        content_html = _render_standard_content(s, "mckinsey_mece", theme)
        return f"""
        <div style="width:100%;height:100%;{bg_style}padding:50px 88px 30px;display:flex;flex-direction:column;justify-content:space-between;position:relative;box-sizing:border-box;">
          <div>
            <div style="border-bottom:1.5px solid #0F2D59;padding-bottom:8px;margin-bottom:14px;display:flex;justify-content:space-between;align-items:center;">
              <span style="font-size:12px;font-weight:800;color:#0F2D59;text-transform:uppercase;">{eyebrow or f'MECE FRAMEWORK · 0{idx+1}'}</span>
              <span style="font-size:12px;color:#86909C;">MANAGEMENT CONSULTING REPORT</span>
            </div>
            <h2 style="font-size:36px;font-weight:700;color:#0F2D59;margin-bottom:22px;">{title}</h2>
            {content_html}
          </div>
          <div style="display:flex;justify-content:space-between;font-size:12px;color:#86909C;border-top:1px solid #E5E6EB;padding-top:12px;">
            <span>{footer_text}</span>
            <span>{idx+1:02d} / {total:02d}</span>
          </div>
        </div>
        """

    # 7. STYLE 7: C8 · Pure Classical Oriental (东方风雅宣纸水墨)
    elif style_id == "oriental_classical":
        bg_style = "background:#F7F4EB; color:#24201D; font-family:'Songti SC','STSong','SimSun',serif;"
        if is_cover:
            return f"""
            <div style="width:100%;height:100%;{bg_style}display:flex;position:relative;overflow:hidden;box-sizing:border-box;">
              <div style="position:absolute;inset:0;background-image:radial-gradient(#2C2825 0.5px,transparent 0.5px);background-size:24px 24px;opacity:.06;"></div>
              <div style="flex:1;padding:8% 8%;display:flex;flex-direction:column;justify-content:center;z-index:2;">
                <div style="font-size:13px;color:#8C7B6B;letter-spacing:.3em;text-transform:uppercase;margin-bottom:16px;display:flex;align-items:center;gap:8px;">
                  <span style="width:24px;height:1px;background:#8C7B6B;"></span> {eyebrow or ('东方智慧 · 智能协同' if pres.is_demo else '')}
                </div>
                <h1 style="font-size:52px;font-weight:600;color:#24201D;line-height:1.25;letter-spacing:.12em;margin-bottom:18px;">
                  {title}
                </h1>
                <div style="font-size:18px;color:#6E6359;letter-spacing:.12em;line-height:1.8;border-left:2px solid #C4A27A;padding-left:14px;margin-bottom:24px;max-width:85%;">
                  {subtitle or ('以大衍之术，驭纷繁之务。格物致知，神机自运。' if pres.is_demo else '')}
                </div>
                <div style="font-size:12px;color:#9E9284;letter-spacing:.2em;">{('岁次丙午秋 · 仅呈受邀贤达' if pres.is_demo else esc(pres.date or ''))}</div>
              </div>
              <div style="width:34%;display:flex;align-items:center;justify-content:center;position:relative;z-index:2;">
                <div style="border:2px solid #A82E2E;padding:14px 18px;border-radius:2px;display:flex;flex-direction:column;align-items:center;justify-content:center;background:rgba(168,46,46,.03);">
                  <div style="writing-mode:vertical-rl;font-size:22px;font-weight:700;color:#A82E2E;letter-spacing:.25em;line-height:1.5;">
                    {('流智科技·甲子之玺' if pres.is_demo else esc(pres.author or '资料汇编'))}
                  </div>
                </div>
              </div>
              <div style="position:absolute;bottom:24px;left:88px;right:88px;display:flex;justify-content:space-between;font-size:12px;color:#8C7B6B;z-index:2;">
                <span>{footer_text}</span>
                <span>01 / {total:02d}</span>
              </div>
            </div>
            """
        content_html = _render_standard_content(s, "oriental_classical", theme)
        return f"""
        <div style="width:100%;height:100%;{bg_style}padding:50px 88px 30px;display:flex;flex-direction:column;justify-content:space-between;position:relative;box-sizing:border-box;">
          <div>
            <div style="font-size:13px;color:#8C7B6B;letter-spacing:.25em;margin-bottom:10px;">{eyebrow or f'卷0{idx+1} · 察势者明，驭变者智'}</div>
            <h2 style="font-size:38px;font-weight:600;color:#24201D;letter-spacing:.08em;margin-bottom:24px;">{title}</h2>
            {content_html}
          </div>
          <div style="display:flex;justify-content:space-between;font-size:12px;color:#8C7B6B;border-top:1px solid #E6E0D3;padding-top:12px;">
            <span>{footer_text}</span>
            <span>{idx+1:02d} / {total:02d}</span>
          </div>
        </div>
        """

    # 8. GENERAL / OTHER CORE STYLES (Alibaba Orange, Default fallbacks, etc.)
    else:
        bg = theme.bg_color if theme else "#FFFFFF"
        text_c = theme.text_color if theme else "#1D2129"
        accent_c = theme.accent_color if theme else "#3B82F6"
        bg_style = f"background:{bg}; color:{text_c}; font-family:-apple-system,BlinkMacSystemFont,'PingFang SC',sans-serif;"
        if is_cover:
            return f"""
            <div style="width:100%;height:100%;{bg_style}padding:8% 8%;display:flex;flex-direction:column;justify-content:center;position:relative;box-sizing:border-box;">
              <div style="font-size:13px;font-weight:700;color:{accent_c};letter-spacing:.2em;text-transform:uppercase;margin-bottom:14px;">{eyebrow or 'PRESENTATION'}</div>
              <h1 style="font-size:52px;font-weight:800;color:{text_c};line-height:1.15;margin-bottom:16px;">{title}</h1>
              {f'<div style="font-size:18px;color:{text_c};opacity:0.8;line-height:1.5;margin-bottom:28px;max-width:85%;">{subtitle}</div>' if subtitle else ''}
              <div style="display:flex;gap:12px;">
                <span style="padding:5px 14px;border-radius:20px;background:rgba(0,0,0,0.05);font-size:13px;font-weight:600;color:{text_c};">{esc(pres.scenario_id.upper())}</span>
                <span style="font-size:13px;opacity:0.6;color:{text_c};padding-top:5px;">PrettyPPT · {esc(theme.name_zh if theme else '')}</span>
              </div>
              <div style="position:absolute;bottom:24px;left:88px;right:88px;display:flex;justify-content:space-between;font-size:12px;opacity:0.6;">
                <span>{footer_text}</span>
                <span>01 / {total:02d}</span>
              </div>
            </div>
            """
        content_html = _render_standard_content(s, style_id, theme)
        return f"""
        <div style="width:100%;height:100%;{bg_style}padding:50px 88px 30px;display:flex;flex-direction:column;justify-content:space-between;position:relative;box-sizing:border-box;">
          <div>
            <div style="font-size:12px;font-weight:700;color:{accent_c};letter-spacing:.15em;text-transform:uppercase;margin-bottom:6px;">{eyebrow or f'PAGE 0{idx+1}'}</div>
            <h2 style="font-size:38px;font-weight:800;color:{text_c};margin-bottom:24px;">{title}</h2>
            {content_html}
          </div>
          <div style="display:flex;justify-content:space-between;font-size:12px;opacity:0.6;border-top:1px solid rgba(0,0,0,0.08);padding-top:14px;">
            <span>{footer_text}</span>
            <span>{idx+1:02d} / {total:02d}</span>
          </div>
        </div>
        """


def _render_standard_content(s: Slide, style_id: str, theme: Optional[Theme]) -> str:
    """Renders the content payload of an inner slide (cards, metrics, tables, charts, bullets, body) with style styling."""
    esc = lambda v: html.escape(str(v)) if v is not None else ""
    parts = []
    bullets = [esc(b) for b in s.bullets]

    # Lead body text if present
    if s.body:
        body_color = {
            "apple_titanium": "#A1A1A6",
            "goldman_institutional": "#4A5568",
            "silicon_valley": "#425466",
            "editorial_luxury": "#5C5042",
            "feishu_workplace": "#4E5969",
            "mckinsey_mece": "#4E5969",
            "oriental_classical": "#6E6359",
        }.get(style_id, theme.text_color if theme else "#444444")
        parts.append(f'<div style="font-size:18px;color:{body_color};line-height:1.6;margin-bottom:20px;max-width:90%;">{esc(s.body)}</div>')

    # 1. Cards / Framework pillars
    if s.cards:
        cards_html = []
        n = len(s.cards)
        cols = 2 if s.layout in ("matrix", "comparison") else (3 if n >= 3 else n)
        for c in s.cards:
            tag_html = f'<span style="font-size:11px;font-weight:700;padding:2px 8px;border-radius:4px;display:inline-block;margin-bottom:8px;">{esc(c.tag or "POINT")}</span>' if c.tag else ""
            metric_html = f'<div style="font-size:24px;font-weight:700;margin-top:14px;padding-top:8px;">{esc(c.metric)}</div>' if c.metric else ""

            if style_id == "apple_titanium":
                c_block = f"""
                <div style="background:rgba(255,255,255,.04);border:1px solid rgba(255,255,255,.09);border-radius:12px;padding:20px;display:flex;flex-direction:column;justify-content:space-between;">
                  <div>
                    <span style="font-size:11px;font-weight:600;padding:2px 8px;border-radius:12px;background:rgba(255,255,255,.08);color:#E5E5EA;display:inline-block;margin-bottom:10px;">{esc(c.tag or 'SPEC')}</span>
                    <h3 style="font-size:20px;font-weight:700;color:#FFFFFF;margin-bottom:8px;">{esc(c.title)}</h3>
                    <p style="font-size:14px;color:#86868B;line-height:1.5;">{esc(c.desc)}</p>
                  </div>
                  {f'<div style="font-size:24px;font-weight:700;color:#F5F5F7;margin-top:14px;padding-top:8px;border-top:1px solid rgba(255,255,255,.08);font-family:monospace;">{esc(c.metric)}</div>' if c.metric else ''}
                </div>
                """
            elif style_id == "goldman_institutional":
                c_block = f"""
                <div style="background:#F8FAFC;border:1px solid #E2E8F0;border-top:3px solid #00254A;border-radius:3px;padding:20px;display:flex;flex-direction:column;justify-content:space-between;">
                  <div>
                    <span style="font-size:11px;font-weight:700;color:#00254A;letter-spacing:.1em;display:inline-block;margin-bottom:6px;">{esc(c.tag or 'PILLAR')}</span>
                    <h3 style="font-size:18px;font-weight:700;color:#00254A;margin-bottom:8px;font-family:'Georgia',serif;">{esc(c.title)}</h3>
                    <p style="font-size:13px;color:#4A5568;line-height:1.6;">{esc(c.desc)}</p>
                  </div>
                  {f'<div style="font-size:22px;font-weight:700;color:#00254A;margin-top:12px;padding-top:8px;border-top:1px solid #E2E8F0;font-family:Georgia,serif;">{esc(c.metric)}</div>' if c.metric else ''}
                </div>
                """
            elif style_id == "silicon_valley":
                c_block = f"""
                <div style="background:#FFFFFF;border:1px solid #E6E8EB;border-radius:12px;padding:20px;box-shadow:0 4px 14px rgba(10,37,64,.04);display:flex;flex-direction:column;justify-content:space-between;">
                  <div>
                    <span style="font-size:11px;font-weight:700;padding:2px 8px;border-radius:20px;background:#F8F9FF;border:1px solid #EAECFF;color:#635BFF;display:inline-block;margin-bottom:8px;">{esc(c.tag or 'FEATURE')}</span>
                    <h3 style="font-size:18px;font-weight:800;color:#0A2540;margin-bottom:6px;">{esc(c.title)}</h3>
                    <p style="font-size:13px;color:#425466;line-height:1.5;">{esc(c.desc)}</p>
                  </div>
                  {f'<div style="font-size:22px;font-weight:800;color:#635BFF;margin-top:14px;padding-top:8px;border-top:1px solid #F0F2F5;">{esc(c.metric)}</div>' if c.metric else ''}
                </div>
                """
            elif style_id == "mckinsey_mece":
                c_block = f"""
                <div style="background:#F7F8FA;border:1px solid #E5E6EB;border-top:3px solid #0F2D59;border-radius:3px;padding:18px;display:flex;flex-direction:column;justify-content:space-between;">
                  <div>
                    <span style="font-size:10px;font-weight:800;color:#165DFF;letter-spacing:.08em;text-transform:uppercase;">{esc(c.tag or 'FRAMEWORK')}</span>
                    <h3 style="font-size:17px;font-weight:700;color:#0F2D59;margin:6px 0;">{esc(c.title)}</h3>
                    <p style="font-size:13px;color:#4E5969;line-height:1.5;">{esc(c.desc)}</p>
                  </div>
                  {f'<div style="font-size:20px;font-weight:800;color:#0F2D59;margin-top:12px;padding-top:6px;border-top:1px solid #E5E6EB;">{esc(c.metric)}</div>' if c.metric else ''}
                </div>
                """
            elif style_id == "feishu_workplace":
                c_block = f"""
                <div style="background:#FFFFFF;border:1px solid #DEE0E3;border-radius:8px;padding:18px;box-shadow:0 2px 6px rgba(31,35,41,.03);display:flex;flex-direction:column;justify-content:space-between;">
                  <div>
                    <span style="font-size:11px;font-weight:600;padding:2px 8px;border-radius:4px;background:#E8F0FF;color:#3370FF;display:inline-block;margin-bottom:8px;">{esc(c.tag or 'TASK')}</span>
                    <h3 style="font-size:17px;font-weight:700;color:#1F2329;margin-bottom:6px;">{esc(c.title)}</h3>
                    <p style="font-size:13px;color:#646A73;line-height:1.5;">{esc(c.desc)}</p>
                  </div>
                  {f'<div style="font-size:20px;font-weight:700;color:#3370FF;margin-top:12px;padding-top:6px;border-top:1px solid #DEE0E3;">{esc(c.metric)}</div>' if c.metric else ''}
                </div>
                """
            elif style_id == "oriental_classical":
                c_block = f"""
                <div style="background:rgba(255,255,255,.65);border:1px solid #E6E0D3;border-radius:3px;padding:20px;display:flex;flex-direction:column;justify-content:space-between;box-shadow:0 2px 6px rgba(0,0,0,.02);">
                  <div>
                    <span style="font-size:11px;font-weight:700;color:#A82E2E;letter-spacing:.15em;">{esc(c.tag or '机杼')}</span>
                    <h3 style="font-size:18px;font-weight:600;color:#24201D;margin:6px 0;letter-spacing:.06em;">{esc(c.title)}</h3>
                    <p style="font-size:13px;color:#6E6359;line-height:1.6;">{esc(c.desc)}</p>
                  </div>
                  {f'<div style="font-size:20px;font-weight:700;color:#A82E2E;margin-top:12px;padding-top:6px;border-top:1px solid #E6E0D3;font-family:serif;">{esc(c.metric)}</div>' if c.metric else ''}
                </div>
                """
            else:
                c_block = f"""
                <div style="background:rgba(0,0,0,.03);border:1px solid rgba(0,0,0,.08);border-radius:8px;padding:18px;display:flex;flex-direction:column;justify-content:space-between;">
                  <div>
                    {f'<span style="font-size:11px;font-weight:700;color:{theme.accent_color if theme else "#333"};margin-bottom:6px;display:inline-block;">{esc(c.tag)}</span>' if c.tag else ''}
                    <h3 style="font-size:17px;font-weight:700;margin-bottom:6px;">{esc(c.title)}</h3>
                    <p style="font-size:13px;opacity:0.8;line-height:1.5;">{esc(c.desc)}</p>
                  </div>
                  {f'<div style="font-size:20px;font-weight:700;margin-top:10px;padding-top:6px;border-top:1px solid rgba(0,0,0,.08);">{esc(c.metric)}</div>' if c.metric else ''}
                </div>
                """
            cards_html.append(c_block)
        parts.append(f'<div style="display:grid;grid-template-columns:repeat({cols},1fr);gap:16px;margin-bottom:20px;">{"".join(cards_html)}</div>')

    # 2. Metrics / Traction KPI blocks
    if s.metrics:
        metrics_html = []
        cols = min(len(s.metrics), 4)
        for m in s.metrics:
            delta_val = esc(m.delta) if m.delta else ""
            if style_id == "apple_titanium":
                m_block = f"""
                <div style="background:rgba(255,255,255,.04);border:1px solid rgba(255,255,255,.08);border-radius:12px;padding:20px;text-align:center;">
                  <div style="font-size:38px;font-weight:700;color:#F5F5F7;line-height:1;margin-bottom:6px;">{esc(m.value)}</div>
                  <div style="font-size:13px;color:#86868B;font-weight:500;margin-bottom:4px;">{esc(m.label)}</div>
                  {f'<div style="font-size:12px;font-weight:600;color:#2997FF;">{delta_val}</div>' if delta_val else ''}
                  <div style="height:3px;background:rgba(255,255,255,.08);margin-top:12px;border-radius:2px;overflow:hidden;">
                    <div style="width:80%;height:100%;background:linear-gradient(90deg,#2997FF,#A1A1A6);"></div>
                  </div>
                </div>
                """
            elif style_id == "goldman_institutional":
                m_block = f"""
                <div style="background:#F8FAFC;border:1px solid #E2E8F0;border-radius:3px;padding:20px;text-align:center;">
                  <div style="font-size:36px;font-weight:700;color:#00254A;line-height:1;margin-bottom:6px;font-family:'Georgia',serif;">{esc(m.value)}</div>
                  <div style="font-size:12px;color:#718096;font-weight:600;text-transform:uppercase;letter-spacing:.08em;margin-bottom:4px;">{esc(m.label)}</div>
                  {f'<div style="font-size:11px;font-weight:700;color:#C4A84A;">{delta_val}</div>' if delta_val else ''}
                </div>
                """
            elif style_id == "silicon_valley":
                m_block = f"""
                <div style="background:#FFFFFF;border:1px solid #E6E8EB;border-radius:12px;padding:20px;text-align:center;box-shadow:0 4px 14px rgba(10,37,64,.04);">
                  <div style="font-size:38px;font-weight:800;color:#0A2540;line-height:1;margin-bottom:6px;">{esc(m.value)}</div>
                  <div style="font-size:13px;color:#8892A0;font-weight:600;margin-bottom:6px;">{esc(m.label)}</div>
                  {f'<span style="padding:2px 8px;border-radius:10px;background:#F0FCFF;color:#0891B2;font-size:11px;font-weight:700;">{delta_val}</span>' if delta_val else ''}
                </div>
                """
            elif style_id == "oriental_classical":
                m_block = f"""
                <div style="background:rgba(255,255,255,.65);border:1px solid #E6E0D3;border-radius:3px;padding:18px;text-align:center;">
                  <div style="font-size:36px;font-weight:700;color:#24201D;line-height:1;margin-bottom:6px;font-family:serif;">{esc(m.value)}</div>
                  <div style="font-size:13px;color:#6E6359;letter-spacing:.1em;margin-bottom:4px;">{esc(m.label)}</div>
                  {f'<div style="font-size:11px;font-weight:600;color:#A82E2E;">{delta_val}</div>' if delta_val else ''}
                </div>
                """
            else:
                m_block = f"""
                <div style="background:rgba(0,0,0,.03);border:1px solid rgba(0,0,0,.08);border-radius:8px;padding:18px;text-align:center;">
                  <div style="font-size:36px;font-weight:800;line-height:1;margin-bottom:6px;">{esc(m.value)}</div>
                  <div style="font-size:13px;opacity:0.8;font-weight:600;margin-bottom:4px;">{esc(m.label)}</div>
                  {f'<div style="font-size:11px;font-weight:700;">{delta_val}</div>' if delta_val else ''}
                </div>
                """
            if m.subtext:
                subtext = '<div style="font-size:12px;line-height:1.5;margin-top:8px;">%s</div>' % esc(m.subtext)
                position = m_block.rfind('</div>')
                m_block = m_block[:position] + subtext + m_block[position:]
            metrics_html.append(m_block)
        parts.append(f'<div style="display:grid;grid-template-columns:repeat({cols},1fr);gap:16px;margin-bottom:20px;">{"".join(metrics_html)}</div>')

    # 3. Table if present
    if s.table:
        headers = [esc(h) for h in s.table.get("headers", [])]
        rows = [[esc(c) for c in r] for r in s.table.get("rows", [])]
        th_style = "padding:10px 14px;font-size:13px;font-weight:700;text-align:left;border-bottom:2px solid rgba(0,0,0,.15);"
        td_style = "padding:10px 14px;font-size:13px;border-bottom:1px solid rgba(0,0,0,.08);"
        if style_id == "apple_titanium":
            th_style = "padding:10px 14px;font-size:13px;font-weight:700;text-align:left;color:#F5F5F7;border-bottom:1px solid rgba(255,255,255,.15);"
            td_style = "padding:10px 14px;font-size:13px;color:#A1A1A6;border-bottom:1px solid rgba(255,255,255,.06);"
        elif style_id == "goldman_institutional":
            th_style = "padding:10px 14px;font-size:13px;font-weight:700;text-align:left;color:#00254A;background:#F8FAFC;border-bottom:2px solid #00254A;font-family:'Georgia',serif;"
            td_style = "padding:10px 14px;font-size:13px;color:#2D3748;border-bottom:1px solid #EDF2F7;font-family:'Georgia',serif;"
        
        table_rows = ''.join('<tr>' + ''.join('<td style="%s">%s</td>' % (td_style, c) for c in row) + '</tr>' for row in rows)
        table_headers = ''.join('<th style="%s">%s</th>' % (th_style, h) for h in headers)
        parts.append(f"""
        <div style="overflow-x:auto;margin-bottom:20px;">
          <table style="width:100%;border-collapse:collapse;">
            <thead><tr>{table_headers}</tr></thead>
            <tbody>{table_rows}</tbody>
          </table>
        </div>
        """)

    # 4. Chart if present
    if s.chart:
        parts.append(f'<div style="width:100%;height:320px;margin-bottom:20px;">{_chart_svg(s.chart, 1264, 320, theme)}</div>')

    if s.image_url:
        parts.append(f'<img alt="用户提供的图片" style="display:block;width:100%;height:400px;object-fit:contain;margin-bottom:20px;" src="{_image_data(s.image_url)}">')

    # 5. Bullets list if present
    if bullets:
        bullet_items = []
        for i, b in enumerate(bullets):
            if style_id == "apple_titanium":
                b_html = f"""
                <div style="display:flex;align-items:flex-start;gap:12px;margin-bottom:12px;">
                  <div style="width:7px;height:7px;border-radius:50%;background:#F5F5F7;margin-top:7px;flex-shrink:0;box-shadow:0 0 8px rgba(255,255,255,.4);"></div>
                  <div style="font-size:16px;color:#A1A1A6;line-height:1.6;">{b}</div>
                </div>
                """
            elif style_id == "goldman_institutional":
                b_html = f"""
                <div style="display:flex;gap:12px;margin-bottom:14px;padding-bottom:12px;border-bottom:1px solid #EDF2F7;align-items:flex-start;">
                  <div style="font-size:14px;font-weight:700;color:#00254A;min-width:24px;">0{i+1}.</div>
                  <div style="font-size:15px;color:#2D3748;line-height:1.6;font-family:'Georgia',serif;">{b}</div>
                </div>
                """
            elif style_id == "silicon_valley":
                b_html = f"""
                <div style="display:flex;align-items:flex-start;gap:10px;margin-bottom:12px;">
                  <div style="width:7px;height:7px;border-radius:50%;background:linear-gradient(135deg,#635BFF,#00D4FF);margin-top:7px;flex-shrink:0;"></div>
                  <div style="font-size:16px;color:#425466;line-height:1.6;">{b}</div>
                </div>
                """
            elif style_id == "oriental_classical":
                b_html = f"""
                <div style="display:flex;gap:10px;margin-bottom:14px;align-items:flex-start;">
                  <span style="color:#A82E2E;font-size:14px;font-weight:700;">〔论〕</span>
                  <div style="font-size:16px;color:#4A4036;line-height:1.7;letter-spacing:.05em;">{b}</div>
                </div>
                """
            elif style_id == "mckinsey_mece":
                b_html = f"""
                <div style="display:flex;align-items:flex-start;gap:10px;margin-bottom:12px;">
                  <div style="width:6px;height:6px;background:#0F2D59;margin-top:8px;flex-shrink:0;"></div>
                  <div style="font-size:15px;color:#1D2129;line-height:1.6;">{b}</div>
                </div>
                """
            else:
                b_html = f"""
                <div style="display:flex;align-items:flex-start;gap:10px;margin-bottom:12px;">
                  <span style="color:{theme.accent_color if theme else '#3370FF'};font-size:14px;">✦</span>
                  <div style="font-size:15px;line-height:1.6;">{b}</div>
                </div>
                """
            bullet_items.append(b_html)
        parts.append(f'<div style="margin-top:10px;">{"".join(bullet_items)}</div>')

    return "".join(parts)


def generate_html_deck(pres: Presentation) -> str:
    """
    Renders a standalone interactive HTML presentation with bespoke multi-slide aesthetic engine.
    - 100% offline, zero remote dependencies (no gstatic.com, no http scripts).
    - Checks theme colors and table cells for overflow/security, raising LayoutError when required.
    - Preserves all user-provided facts and markdown source strings.
    """
    theme = pres.theme

    # Validate source data and native layout capacity. The separate HTML layout
    # also needs browser rendering checks before delivery.
    composed_nodes_per_slide = []
    for i, slide in enumerate(pres.slides):
        nodes = compose(pres, slide, i)
        # Check table overflow if table exists
        for node in nodes:
            if node["kind"] == "table":
                _table_cells(node["data"], node["w"], node["h"])
        composed_nodes_per_slide.append(nodes)

    # Step 2: Render each slide with authentic bespoke styling
    slides_rendered = []
    total_slides = len(pres.slides)

    for i, slide in enumerate(pres.slides):
        is_active = "active" if i == 0 else ""
        nodes = composed_nodes_per_slide[i]

        # Free composition must honour the requested coordinates and colours.
        if pres.mode == "free" or slide.layout == "custom" or slide.elements:
            content = "".join(_html_node(n, theme) for n in nodes)
            slide_html = f"""
            <section class="slide {is_active}" id="slide-{i}" data-index="{i}" data-layout="{html.escape(slide.layout or '')}" aria-label="{html.escape(slide.title, quote=True)}" style="width:1440px;height:810px;position:absolute;left:0;top:0;background:{theme.bg_color};overflow:hidden;">
              {content}
            </section>
            """
        else:
            slide_inner = _render_bespoke_slide(pres.style_id, i, total_slides, pres, slide, nodes)
            slide_html = f"""
            <section class="slide {is_active}" id="slide-{i}" data-index="{i}" data-layout="{html.escape(slide.layout or '')}" aria-label="{html.escape(slide.title, quote=True)}" style="width:1440px;height:810px;position:absolute;left:0;top:0;overflow:hidden;">
              {slide_inner}
            </section>
            """
        slides_rendered.append(slide_html)

    all_slides = "".join(slides_rendered)
    title = html.escape(pres.title)
    theme_name = html.escape(theme.name_zh if theme else "经典")

    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title>
<style>
*{{box-sizing:border-box}}
body{{margin:0;background:#17191c;font-family:'PingFang SC',-apple-system,sans-serif}}
main{{height:calc(100vh - 58px);display:flex;align-items:center;justify-content:center;overflow:hidden}}
.viewport{{position:relative;width:1440px;height:810px}}
.slide{{width:1440px;height:810px;position:absolute;left:0;top:0;transform-origin:top left;display:none;overflow:hidden;border-radius:6px;box-shadow:0 20px 50px rgba(0,0,0,.4)}}
.slide.active{{display:block}}
nav{{height:58px;display:flex;gap:18px;align-items:center;justify-content:center;color:#ddd;font-size:14px;background:#111113;border-top:1px solid #27272A}}
button{{background:#30343a;border:1px solid #555;color:white;padding:7px 14px;border-radius:5px;cursor:pointer}}
button:focus-visible{{outline:3px solid #80baff}}
button:disabled{{opacity:0.4;cursor:not-allowed}}
#theme{{max-width:30vw;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;color:#A1A1AA}}
.text{{margin:0;padding:0}}
svg{{width:100%;height:100%}}
@page{{size:1440px 810px;margin:0}}
@media print{{
  body{{background:white}}
  main{{display:block;height:auto;overflow:visible}}
  .viewport{{width:auto!important;height:auto!important}}
  .slide{{display:block!important;position:relative!important;transform:none!important;break-after:page;page-break-after:always;box-shadow:none;border-radius:0;margin-bottom:0}}
  .slide:last-child{{break-after:auto}}
  nav{{display:none}}
  *{{-webkit-print-color-adjust:exact;print-color-adjust:exact}}
}}
</style>
</head>
<body>
<main>
  <div class="viewport">
    {all_slides}
  </div>
</main>
<nav aria-label="演示控制">
  <button id="prev">上一页</button>
  <span id="counter" aria-live="polite">1 / {total_slides}</span>
  <button id="next">下一页</button>
  <button id="full">全屏</button>
  <button id="print">导出 PDF</button>
  <span id="theme">{theme_name} · 完整商业演示</span>
</nav>
<script>
const slides=[...document.querySelectorAll('.slide')];
let current=0;
function show(i){{
  current=Math.max(0,Math.min(i,slides.length-1));
  slides.forEach((s,n)=>s.classList.toggle('active',n===current));
  document.querySelector('#counter').textContent=(current+1)+' / '+slides.length;
  document.querySelector('#prev').disabled=current===0;
  document.querySelector('#next').disabled=current===slides.length-1;
}}
function fit(){{
  const scale=Math.min((innerWidth-24)/1440,(innerHeight-82)/810);
  const v=document.querySelector('.viewport');
  v.style.width=(1440*scale)+'px';
  v.style.height=(810*scale)+'px';
  slides.forEach(s=>s.style.transform='scale('+scale+')');
}}
document.querySelector('#prev').onclick=()=>show(current-1);
document.querySelector('#next').onclick=()=>show(current+1);
document.querySelector('#print').onclick=()=>print();
document.querySelector('#full').onclick=()=>document.fullscreenElement?document.exitFullscreen():document.documentElement.requestFullscreen();
document.addEventListener('keydown',e=>{{
  if(['ArrowRight','PageDown',' '].includes(e.key)){{e.preventDefault();show(current+1)}}
  if(['ArrowLeft','PageUp'].includes(e.key)){{e.preventDefault();show(current-1)}}
}});
addEventListener('resize',fit);
show(0);
fit();
</script>
</body>
</html>
"""


def generate_pptx_deck(pres: Presentation, output_path: str) -> bool:
    """Exports native Microsoft PowerPoint (.pptx) file using python-pptx with editable shapes, charts, and tables."""
    try:
        from pptx import Presentation as PptxPresentation
        from pptx.util import Inches, Pt
        from pptx.dml.color import RGBColor
        from pptx.enum.shapes import MSO_SHAPE
        from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
        from pptx.enum.chart import XL_CHART_TYPE, XL_LEGEND_POSITION, XL_LABEL_POSITION
        from pptx.chart.data import CategoryChartData
        from pptx.oxml.xmlchemy import OxmlElement
        from pptx.oxml.ns import qn
        from PIL import Image

        rgb = lambda value: RGBColor.from_string(value.lstrip('#'))
        px = lambda value: Inches(value / 108)

        prs = PptxPresentation()
        prs.slide_width, prs.slide_height = px(WIDTH), px(HEIGHT)

        for i, source in enumerate(pres.slides):
            slide = prs.slides.add_slide(prs.slide_layouts[6])
            slide.background.fill.solid()
            slide.background.fill.fore_color.rgb = rgb(pres.theme.bg_color)

            for node in compose(pres, source, i):
                x, y, w, h = [px(node[k]) for k in ('x', 'y', 'w', 'h')]
                kind = node['kind']
                if kind == 'text':
                    box = slide.shapes.add_textbox(x, y, w, h)
                    tf = box.text_frame
                    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
                    tf.word_wrap = False
                    for number, line in enumerate(node['text'].split('\n')):
                        p = tf.paragraphs[0] if number == 0 else tf.add_paragraph()
                        p.text = line
                        p.font.name = node['font']
                        p.font.size = Pt(node['size'] * 2 / 3)
                        p.font.bold = node['bold']
                        p.font.color.rgb = rgb(node['color'])
                        p.line_spacing = Pt(node['line_height'] * 2 / 3)
                        p.space_before = p.space_after = Pt(0)
                        p.alignment = {'left': PP_ALIGN.LEFT, 'right': PP_ALIGN.RIGHT, 'center': PP_ALIGN.CENTER}[node['align']]
                        for run in p.runs:
                            rpr = run._r.get_or_add_rPr()
                            ea = OxmlElement('a:ea')
                            ea.set('typeface', node['font'])
                            rpr.append(ea)
                elif kind in ('line', 'rect'):
                    shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, x, y, w, h)
                    shape.fill.solid()
                    shape.fill.fore_color.rgb = rgb(node['color'])
                    shape.line.fill.background()
                    shape._element.spPr.append(OxmlElement('a:effectLst'))
                    for effect in shape._element.xpath('.//a:effectRef'):
                        effect.set('idx', '0')
                elif kind == 'image':
                    _image_data(node['path'])
                    with Image.open(node['path']) as image:
                        iw, ih = image.size
                        if image.format == 'WEBP':
                            picture_source = io.BytesIO()
                            image.convert('RGBA').save(picture_source, format='PNG')
                            picture_source.seek(0)
                        else:
                            picture_source = node['path']
                    ratio = min(w / iw, h / ih)
                    pw, ph = int(iw * ratio), int(ih * ratio)
                    slide.shapes.add_picture(picture_source, int(x + (w - pw) / 2), int(y + (h - ph) / 2), width=pw, height=ph)
                elif kind == 'table':
                    rows = _table_cells(node['data'], node['w'], node['h'])
                    table = slide.shapes.add_table(len(rows), len(rows[0]), x, y, w, h).table
                    for r, values in enumerate(rows):
                        for col, value in enumerate(values):
                            cell = table.cell(r, col)
                            cell.text = value
                            cell.margin_left = cell.margin_right = px(13)
                            cell.margin_top = cell.margin_bottom = px(8)
                            cell.vertical_anchor = MSO_ANCHOR.MIDDLE
                            cell.fill.solid()
                            cell.fill.fore_color.rgb = rgb(pres.theme.bg_color)
                            for p in cell.text_frame.paragraphs:
                                p.font.name = 'PingFang SC'
                                p.font.size = Pt(23 * 2 / 3)
                                p.font.bold = (r == 0)
                                p.font.color.rgb = rgb(pres.theme.text_color)
                                p.space_after = Pt(0)
                elif kind == 'chart':
                    data = node['data']
                    chart_data = CategoryChartData()
                    chart_data.categories = data['categories']
                    for series in data['series']:
                        chart_data.add_series(series['name'], series['values'])
                    chart_type = {'bar': XL_CHART_TYPE.BAR_CLUSTERED, 'column': XL_CHART_TYPE.COLUMN_CLUSTERED, 'line': XL_CHART_TYPE.LINE_MARKERS}[data.get('kind', 'bar')]
                    chart = slide.shapes.add_chart(chart_type, x, y, w, h, chart_data).chart
                    chart.has_title = False
                    deleted = chart._chartSpace.chart.find(qn('c:autoTitleDeleted'))
                    if deleted is None:
                        deleted = OxmlElement('c:autoTitleDeleted')
                        chart._chartSpace.chart.insert(0, deleted)
                    deleted.set('val', '1')
                    chart.has_legend = True
                    chart.legend.position = XL_LEGEND_POSITION.TOP
                    chart.legend.font.name = 'PingFang SC'
                    chart.legend.font.size = Pt(14)
                    chart.legend.font.color.rgb = rgb(pres.theme.text_color)
                    for axis in (chart.category_axis, chart.value_axis):
                        axis.tick_labels.font.name = 'PingFang SC'
                        axis.tick_labels.font.size = Pt(13)
                        axis.tick_labels.font.color.rgb = rgb(pres.theme.text_color)
                    chart.value_axis.has_major_gridlines = False
                    nums = [v for s in data['series'] for v in s['values']]
                    chart.value_axis.minimum_scale = min(0, min(nums))
                    chart.value_axis.maximum_scale = max(0, max(nums))
                    if chart.value_axis.minimum_scale == chart.value_axis.maximum_scale:
                        chart.value_axis.maximum_scale += 1
                    for j, series in enumerate(chart.series):
                        color = [pres.theme.accent_color, pres.theme.secondary_accent, pres.theme.text_color][j % 3]
                        if data.get('kind') == 'line':
                            series.format.line.color.rgb = rgb(color)
                        else:
                            series.format.fill.solid()
                            series.format.fill.fore_color.rgb = rgb(color)
                    chart.plots[0].has_data_labels = True
                    labels = chart.plots[0].data_labels
                    labels.font.name = 'PingFang SC'
                    labels.font.size = Pt(11)
                    labels.font.color.rgb = rgb(pres.theme.text_color)
                    labels.show_value = True
                    if data.get('unit'):
                        chart.value_axis.has_title = True
                        chart.value_axis.axis_title.text_frame.text = data['unit']
                        for p in chart.value_axis.axis_title.text_frame.paragraphs:
                            p.font.name = 'PingFang SC'
                            p.font.size = Pt(13)
                            p.font.color.rgb = rgb(pres.theme.text_color)
                else:
                    raise ValueError('Unsupported element: ' + str(kind))

            note = source.notes or ""
            if source.sources:
                note += '\n\n资料来源\n' + '\n'.join(source.sources)
            if pres.is_demo:
                note += '\n模板演示，内容与数据为虚构占位。'
            if note.strip():
                slide.notes_slide.notes_text_frame.text = note.strip()

        prs.save(str(output_path))
        return True
    except ImportError as exc:
        raise ImportError('PPTX export requires python-pptx and Pillow. Install PrettyPPT with its dependencies.') from exc
    except Exception as e:
        raise
