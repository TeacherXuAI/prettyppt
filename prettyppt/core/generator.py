"""Export the shared composition to offline HTML and editable PowerPoint."""
import base64
import html
import io
import mimetypes
from pathlib import Path
from .layout import WIDTH, HEIGHT, compose, wrap_text, LayoutError


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
    # Charts show source numbers directly and use a zero-inclusive numeric axis.
    esc = lambda v: html.escape(str(v))
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
        label(15 + i * 340, 25, item["name"] + (" (" + data["unit"] + ")" if data.get("unit") else ""), 18, color=colors[i])
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
                parts.append('<rect x="%s" y="%s" width="%s" height="%s" fill="%s"/>' % (min(zero_x, end_x), y, max(abs(end_x - zero_x), .2), bar_h - 2, colors[i]))
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
                    parts.append('<rect x="%s" y="%s" width="%s" height="%s" fill="%s"/>' % (x, min(cy(0), cy(value)), bar_w - 3, max(abs(cy(0) - cy(value)), .2), colors[i]))
                    label(x + bar_w / 2, cy(value) - 7 if value >= 0 else cy(value) + 20, value, 16, "middle")
                else:
                    points.append("%s,%s" % (x, cy(value)))
                    parts.append('<circle cx="%s" cy="%s" r="5" fill="%s"/>' % (x, cy(value), colors[i]))
                    label(x, cy(value) - 12, value, 16, "middle")
            if kind == "line":
                parts.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="3"/>' % (" ".join(points), colors[i]))
    parts.append('</svg>')
    return "".join(parts)


def _html_node(node, theme):
    esc = html.escape
    position = "position:absolute;left:%spx;top:%spx;width:%spx;height:%spx;" % tuple(node[k] for k in ("x", "y", "w", "h"))
    kind = node["kind"]
    if kind == "text":
        style = position + "font-size:%spx;line-height:%spx;color:%s;font-weight:%s;text-align:%s;font-family:'%s','Noto Sans CJK SC',sans-serif;white-space:pre;" % (node["size"], node["line_height"], node["color"], 700 if node["bold"] else 400, node["align"], node["font"])
        return '<div class="text" data-role="%s" style="%s">%s</div>' % (esc(node.get("role", "body"), quote=True), esc(style, quote=True), esc(node["text"]))
    if kind in ("line", "rect"):
        return '<div aria-hidden="true" style="%sbackground:%s"></div>' % (position, esc(node["color"], quote=True))
    if kind == "image":
        return '<img alt="%s" style="%sobject-fit:contain" src="%s">' % (esc(node.get("alt", "用户提供的图片"), quote=True), position, _image_data(node["path"]))
    if kind == "table":
        rows = _table_cells(node["data"], node["w"], node["h"])
        table = '<table style="%sborder-collapse:collapse;table-layout:fixed;font-size:23px;color:%s">' % (position, theme.text_color)
        for i, row in enumerate(rows):
            table += '<tr style="height:%spx">' % (node["h"] / len(rows))
            for value in row:
                tag = "th" if i == 0 else "td"
                table += '<%s style="text-align:left;vertical-align:middle;padding:8px 13px;white-space:pre;border-bottom:1px solid %s;line-height:32.66px">%s</%s>' % (tag, theme.accent_color, esc(value), tag)
            table += '</tr>'
        return table + '</table>'
    if kind == "chart":
        return '<div style="%s">%s</div>' % (position, _chart_svg(node["data"], node["w"], node["h"], theme))
    raise ValueError("Unsupported element: " + str(kind))


def generate_html_deck(pres):
    slides = []
    for i, slide in enumerate(pres.slides):
        nodes = compose(pres, slide, i)
        content = "".join(_html_node(n, pres.theme) for n in nodes)
        slides.append('<section class="slide" data-index="%s" data-layout="%s" aria-label="%s" style="background:%s">%s</section>' % (i, html.escape(slide.layout or ""), html.escape(slide.title, quote=True), pres.theme.bg_color, content))
    return '''<!DOCTYPE html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>''' + html.escape(pres.title) + '''</title><style>
+*{box-sizing:border-box}body{margin:0;background:#17191c;font-family:'PingFang SC',sans-serif}main{height:calc(100vh - 58px);display:flex;align-items:center;justify-content:center;overflow:hidden}.viewport{position:relative}.slide{width:1440px;height:810px;position:absolute;left:0;top:0;transform-origin:top left;display:none;overflow:hidden}.slide.active{display:block}nav{height:58px;display:flex;gap:18px;align-items:center;justify-content:center;color:#ddd;font-size:14px}button{background:#30343a;border:1px solid #555;color:white;padding:7px 14px;border-radius:5px;cursor:pointer}button:focus-visible{outline:3px solid #80baff}#theme{max-width:30vw;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}.text{margin:0;padding:0}svg{width:100%;height:100%}
+@page{size:1440px 810px;margin:0}@media print{body{background:white}main{display:block;height:auto;overflow:visible}.viewport{width:auto!important;height:auto!important}.slide{display:block!important;position:relative;transform:none!important;break-after:page;page-break-after:always}.slide:last-child{break-after:auto}nav{display:none}*{-webkit-print-color-adjust:exact;print-color-adjust:exact}}
+</style></head><body><main><div class="viewport">''' .replace('\n+', '\n') + "".join(slides) + '''</div></main><nav aria-label="演示控制"><button id="prev">上一页</button><span id="counter" aria-live="polite"></span><button id="next">下一页</button><button id="full">全屏</button><button id="print">导出 PDF</button><span id="theme">''' + html.escape(pres.theme.name_zh) + '''</span></nav><script>
+const slides=[...document.querySelectorAll('.slide')];let current=0;
+function show(i){current=Math.max(0,Math.min(i,slides.length-1));slides.forEach((s,n)=>s.classList.toggle('active',n===current));document.querySelector('#counter').textContent=(current+1)+' / '+slides.length;document.querySelector('#prev').disabled=current===0;document.querySelector('#next').disabled=current===slides.length-1;}
+function fit(){const scale=Math.min((innerWidth-24)/1440,(innerHeight-82)/810);const v=document.querySelector('.viewport');v.style.width=(1440*scale)+'px';v.style.height=(810*scale)+'px';slides.forEach(s=>s.style.transform='scale('+scale+')');}
+document.querySelector('#prev').onclick=()=>show(current-1);document.querySelector('#next').onclick=()=>show(current+1);document.querySelector('#print').onclick=()=>print();document.querySelector('#full').onclick=()=>document.fullscreenElement?document.exitFullscreen():document.documentElement.requestFullscreen();document.addEventListener('keydown',e=>{if(['ArrowRight','PageDown',' '].includes(e.key)){e.preventDefault();show(current+1)}if(['ArrowLeft','PageUp'].includes(e.key)){e.preventDefault();show(current-1)}});addEventListener('resize',fit);show(0);fit();
+</script></body></html>'''.replace('\n+', '\n')


def generate_pptx_deck(pres, output_path):
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
                    p.font.name = node['font']; p.font.size = Pt(node['size'] * 2 / 3)
                    p.font.bold = node['bold']; p.font.color.rgb = rgb(node['color'])
                    p.line_spacing = Pt(node['line_height'] * 2 / 3)
                    p.space_before = p.space_after = Pt(0)
                    p.alignment = {'left': PP_ALIGN.LEFT, 'right': PP_ALIGN.RIGHT, 'center': PP_ALIGN.CENTER}[node['align']]
                    for run in p.runs:
                        rpr = run._r.get_or_add_rPr()
                        ea = OxmlElement('a:ea'); ea.set('typeface', node['font']); rpr.append(ea)
            elif kind in ('line', 'rect'):
                shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, x, y, w, h)
                shape.fill.solid(); shape.fill.fore_color.rgb = rgb(node['color']); shape.line.fill.background()
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
                slide.shapes.add_picture(picture_source, int(x + (w-pw)/2), int(y + (h-ph)/2), width=pw, height=ph)
            elif kind == 'table':
                rows = _table_cells(node['data'], node['w'], node['h'])
                table = slide.shapes.add_table(len(rows), len(rows[0]), x, y, w, h).table
                for r, values in enumerate(rows):
                    for col, value in enumerate(values):
                        cell = table.cell(r, col)
                        cell.text = value; cell.margin_left = cell.margin_right = px(13)
                        cell.margin_top = cell.margin_bottom = px(8); cell.vertical_anchor = MSO_ANCHOR.MIDDLE
                        cell.fill.solid(); cell.fill.fore_color.rgb = rgb(pres.theme.bg_color)
                        for p in cell.text_frame.paragraphs:
                            p.font.name = 'PingFang SC'; p.font.size = Pt(23 * 2 / 3); p.font.bold = r == 0
                            p.font.color.rgb = rgb(pres.theme.text_color); p.space_after = Pt(0)
            elif kind == 'chart':
                data = node['data']; chart_data = CategoryChartData(); chart_data.categories = data['categories']
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
                chart.has_legend = True; chart.legend.position = XL_LEGEND_POSITION.TOP
                chart.legend.font.name = 'PingFang SC'; chart.legend.font.size = Pt(14)
                chart.legend.font.color.rgb = rgb(pres.theme.text_color)
                for axis in (chart.category_axis, chart.value_axis):
                    axis.tick_labels.font.name = 'PingFang SC'; axis.tick_labels.font.size = Pt(13)
                    axis.tick_labels.font.color.rgb = rgb(pres.theme.text_color)
                chart.value_axis.has_major_gridlines = False
                nums = [v for s in data['series'] for v in s['values']]
                chart.value_axis.minimum_scale = min(0, min(nums))
                chart.value_axis.maximum_scale = max(0, max(nums))
                if chart.value_axis.minimum_scale == chart.value_axis.maximum_scale:
                    chart.value_axis.maximum_scale += 1
                for j, series in enumerate(chart.series):
                    color = [pres.theme.accent_color, pres.theme.secondary_accent, pres.theme.text_color][j]
                    if data.get('kind') == 'line':
                        series.format.line.color.rgb = rgb(color)
                    else:
                        series.format.fill.solid(); series.format.fill.fore_color.rgb = rgb(color)
                chart.plots[0].has_data_labels = True
                labels = chart.plots[0].data_labels; labels.font.name = 'PingFang SC'; labels.font.size = Pt(11); labels.font.color.rgb = rgb(pres.theme.text_color)
                labels.show_value = True
                if data.get('unit'):
                    chart.value_axis.has_title = True; chart.value_axis.axis_title.text_frame.text = data['unit']
                    for p in chart.value_axis.axis_title.text_frame.paragraphs:
                        p.font.name = 'PingFang SC'; p.font.size = Pt(13); p.font.color.rgb = rgb(pres.theme.text_color)
            else:
                raise ValueError('Unsupported element: ' + str(kind))
        note = source.notes
        if source.sources:
            note += '\n\n资料来源\n' + '\n'.join(source.sources)
        if pres.is_demo:
            note += '\n模板演示，内容与数据为虚构占位。'
        if note:
            slide.notes_slide.notes_text_frame.text = note.strip()
    prs.save(str(output_path))
    return True
