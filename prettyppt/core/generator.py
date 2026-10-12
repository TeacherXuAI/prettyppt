"""
Multi-Format Generator for PrettyPPT
Generates:
1. Interactive, standalone responsive HTML decks (with navigation, animations, fullscreen, and print support)
2. Native Microsoft PowerPoint (.pptx) widescreen presentations via python-pptx
"""

import os
from typing import Optional
from prettyppt.core.models import Presentation, Slide, Theme

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{{ pres.title }} · PrettyPPT</title>
<script src="https://www.gstatic.com/antigravity/web/dev/tailwindcss.min.js"></script>
<style>
* { box-sizing: border-box; margin: 0; padding: 0; }
:root {
  --bg: {{ theme.bg_color }};
  --text: {{ theme.text_color }};
  --accent: {{ theme.accent_color }};
  --accent2: {{ theme.secondary_accent }};
  --card-bg: {{ theme.card_bg }};
  --card-border: {{ theme.card_border }};
  --ff: {{ theme.font_family }};
}
body {
  background: #09090B;
  color: #F4F4F5;
  font-family: var(--ff);
  overflow: hidden;
  height: 100vh;
  display: flex;
  flex-direction: column;
}
.deck-viewport {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 16px;
  position: relative;
}
.slide-frame {
  width: min(94vw, 1280px);
  aspect-ratio: 16 / 9;
  background: var(--bg);
  color: var(--text);
  border-radius: 14px;
  overflow: hidden;
  position: relative;
  box-shadow: 0 20px 50px rgba(0,0,0,0.4);
  display: none;
  flex-direction: column;
  transition: opacity 0.25s ease;
}
.slide-frame.active {
  display: flex;
}
.hud {
  height: 52px;
  background: #111113;
  border-top: 1px solid #27272A;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  font-size: 12px;
  color: #A1A1AA;
}
.btn {
  padding: 6px 14px;
  border-radius: 6px;
  background: #27272A;
  color: #F4F4F5;
  font-size: 12px;
  font-weight: 500;
  border: none;
  cursor: pointer;
  transition: all 0.15s;
}
.btn:hover { background: #3F3F46; color: #fff; }
.progress-bar {
  position: absolute;
  bottom: 0;
  left: 0;
  height: 3px;
  background: var(--accent);
  transition: width 0.3s ease;
}

/* Slide Specific Styles */
.slide-header {
  padding: 5% 7% 0 7%;
}
.slide-body {
  flex: 1;
  padding: 3% 7% 5% 7%;
  display: flex;
  flex-direction: column;
  justify-content: center;
}
.slide-footer {
  padding: 0 7% 3% 7%;
  display: flex;
  justify-content: space-between;
  font-size: clamp(9px, 1vw, 11px);
  opacity: 0.45;
}

/* Print Rules */
@media print {
  body { overflow: visible; height: auto; background: #fff; }
  .hud { display: none; }
  .deck-viewport { padding: 0; display: block; }
  .slide-frame { display: flex !important; page-break-after: always; width: 100vw; height: 56.25vw; border-radius: 0; box-shadow: none; margin-bottom: 20px; }
}
</style>
</head>
<body>

<div class="deck-viewport">
  {% for s in pres.slides %}
  <div class="slide-frame {% if loop.first %}active{% endif %}" id="slide-{{ loop.index0 }}">
    
    {% if s.slide_type == "cover" %}
      <!-- Cover Slide -->
      <div style="flex:1; display:flex; flex-direction:column; justify-content:center; align-items:flex-start; padding:8% 9%; position:relative; overflow:hidden">
        {% if s.eyebrow %}
        <div style="font-size:clamp(11px, 1.4vw, 14px); letter-spacing:0.18em; text-transform:uppercase; font-weight:700; color:var(--accent); margin-bottom:14px; display:flex; align-items:center; gap:8px;">
          <span style="width:20px; height:2px; background:var(--accent);"></span>
          {{ s.eyebrow }}
        </div>
        {% endif %}
        <h1 style="font-size:clamp(32px, 5.2vw, 56px); font-weight:800; line-height:1.15; letter-spacing:-0.02em; margin-bottom:16px;">
          {{ s.title }}
        </h1>
        {% if s.subtitle %}
        <div style="font-size:clamp(15px, 2vw, 22px); opacity:0.75; line-height:1.5; max-width:85%; margin-bottom:28px;">
          {{ s.subtitle }}
        </div>
        {% endif %}
        <div style="display:flex; align-items:center; gap:12px; margin-top:auto;">
          <span style="padding:4px 12px; border-radius:20px; background:var(--card-bg); border:1px solid var(--card-border); font-size:12px; font-weight:600;">
            {{ pres.scenario_id | upper }}
          </span>
          <span style="font-size:12px; opacity:0.5;">PrettyPPT · {{ theme.name_zh }}</span>
        </div>
      </div>

    {% elif s.slide_type == "narrative" %}
      <!-- Narrative Slide -->
      <div class="slide-header">
        {% if s.eyebrow %}<div style="font-size:12px; font-weight:700; color:var(--accent); letter-spacing:0.15em; text-transform:uppercase; margin-bottom:6px;">{{ s.eyebrow }}</div>{% endif %}
        <h2 style="font-size:clamp(22px, 3.2vw, 36px); font-weight:800; line-height:1.2;">{{ s.title }}</h2>
      </div>
      <div class="slide-body">
        {% if s.body %}
        <div style="font-size:clamp(14px, 1.8vw, 20px); opacity:0.85; line-height:1.6; margin-bottom:24px; padding-left:14px; border-left:3px solid var(--accent);">
          {{ s.body }}
        </div>
        {% endif %}
        {% if s.bullets %}
        <div style="display:flex; flex-direction:column; gap:12px;">
          {% for b in s.bullets %}
          <div style="display:flex; align-items:flex-start; gap:10px; font-size:clamp(13px, 1.5vw, 17px); opacity:0.9;">
            <div style="width:6px; height:6px; border-radius:50%; background:var(--accent); margin-top:8px; flex-shrink:0;"></div>
            <div>{{ b }}</div>
          </div>
          {% endfor %}
        </div>
        {% endif %}
      </div>
      <div class="slide-footer">
        <span>{{ s.footer or pres.title }}</span>
        <span>02 / 05</span>
      </div>

    {% elif s.slide_type == "grid" %}
      <!-- Grid / Cards Slide -->
      <div class="slide-header">
        {% if s.eyebrow %}<div style="font-size:12px; font-weight:700; color:var(--accent); letter-spacing:0.15em; text-transform:uppercase; margin-bottom:6px;">{{ s.eyebrow }}</div>{% endif %}
        <h2 style="font-size:clamp(22px, 3.2vw, 36px); font-weight:800; line-height:1.2;">{{ s.title }}</h2>
      </div>
      <div class="slide-body">
        <div style="display:grid; grid-template-columns:repeat(3, 1fr); gap:16px;">
          {% for c in s.cards %}
          <div style="background:var(--card-bg); border:1px solid var(--card-border); border-radius:12px; padding:20px; display:flex; flex-direction:column; justify-content:space-between; box-shadow:0 4px 14px rgba(0,0,0,0.03);">
            <div>
              {% if c.tag %}
              <span style="font-size:10px; font-weight:700; padding:2px 8px; border-radius:4px; background:var(--accent); color:#fff; display:inline-block; margin-bottom:10px;">
                {{ c.tag }}
              </span>
              {% endif %}
              <h3 style="font-size:clamp(15px, 1.8vw, 20px); font-weight:700; margin-bottom:8px;">{{ c.title }}</h3>
              <p style="font-size:clamp(12px, 1.3vw, 14px); opacity:0.75; line-height:1.5;">{{ c.desc }}</p>
            </div>
            {% if c.metric %}
            <div style="font-size:clamp(18px, 2.5vw, 28px); font-weight:800; color:var(--accent); margin-top:16px; border-top:1px solid var(--card-border); padding-top:12px;">
              {{ c.metric }}
            </div>
            {% endif %}
          </div>
          {% endfor %}
        </div>
      </div>
      <div class="slide-footer">
        <span>{{ s.footer or pres.title }}</span>
        <span>03 / 05</span>
      </div>

    {% elif s.slide_type == "metrics" %}
      <!-- Metrics Dashboard Slide -->
      <div class="slide-header">
        {% if s.eyebrow %}<div style="font-size:12px; font-weight:700; color:var(--accent); letter-spacing:0.15em; text-transform:uppercase; margin-bottom:6px;">{{ s.eyebrow }}</div>{% endif %}
        <h2 style="font-size:clamp(22px, 3.2vw, 36px); font-weight:800; line-height:1.2;">{{ s.title }}</h2>
      </div>
      <div class="slide-body">
        {% if s.body %}
        <div style="font-size:clamp(13px, 1.4vw, 16px); opacity:0.8; margin-bottom:20px;">{{ s.body }}</div>
        {% endif %}
        <div style="display:grid; grid-template-columns:repeat(4, 1fr); gap:14px; margin-bottom:20px;">
          {% for m in s.metrics %}
          <div style="background:var(--card-bg); border:1px solid var(--card-border); border-radius:12px; padding:18px; text-align:center;">
            <div style="font-size:clamp(22px, 3.5vw, 40px); font-weight:800; color:var(--accent); line-height:1.1;">
              {{ m.value }}
            </div>
            <div style="font-size:clamp(11px, 1.2vw, 13px); opacity:0.7; font-weight:600; margin-top:6px;">
              {{ m.label }}
            </div>
            {% if m.delta %}
            <div style="font-size:11px; font-weight:700; color:var(--accent2); margin-top:6px;">
              {{ m.delta }}
            </div>
            {% endif %}
          </div>
          {% endfor %}
        </div>
      </div>
      <div class="slide-footer">
        <span>{{ s.footer or pres.title }}</span>
        <span>04 / 05</span>
      </div>

    {% elif s.slide_type == "cta" %}
      <!-- CTA / Closing Slide -->
      <div class="slide-header">
        {% if s.eyebrow %}<div style="font-size:12px; font-weight:700; color:var(--accent); letter-spacing:0.15em; text-transform:uppercase; margin-bottom:6px;">{{ s.eyebrow }}</div>{% endif %}
        <h2 style="font-size:clamp(24px, 3.6vw, 42px); font-weight:800; line-height:1.2;">{{ s.title }}</h2>
      </div>
      <div class="slide-body">
        {% if s.body %}
        <div style="font-size:clamp(15px, 2vw, 22px); opacity:0.85; line-height:1.6; margin-bottom:24px;">
          {{ s.body }}
        </div>
        {% endif %}
        {% if s.bullets %}
        <div style="display:flex; flex-direction:column; gap:12px;">
          {% for b in s.bullets %}
          <div style="padding:14px 18px; border-radius:8px; background:var(--card-bg); border:1px solid var(--card-border); font-size:clamp(13px, 1.6vw, 16px); font-weight:600; display:flex; align-items:center; gap:10px;">
            <span style="color:var(--accent);">✦</span> {{ b }}
          </div>
          {% endfor %}
        </div>
        {% endif %}
      </div>
      <div class="slide-footer">
        <span>{{ s.footer or pres.title }}</span>
        <span>05 / 05</span>
      </div>
    {% endif %}

    <div class="progress-bar" style="width: {{ (loop.index / loop.length) * 100 }}%;"></div>
  </div>
  {% endfor %}
</div>

<!-- Bottom Navigation HUD -->
<div class="hud">
  <div style="display:flex; align-items:center; gap:12px;">
    <strong style="color:#fff;">{{ pres.title }}</strong>
    <span style="opacity:0.4;">|</span>
    <span>{{ theme.name_zh }} ({{ pres.scenario_id }})</span>
  </div>
  <div style="display:flex; align-items:center; gap:12px;">
    <button class="btn" onclick="prevSlide()">← 上一页 [Left]</button>
    <span id="counter" style="font-weight:700; color:#fff; min-width:44px; text-align:center;">1 / {{ pres.slides|length }}</span>
    <button class="btn" onclick="nextSlide()">下一页 [Right] →</button>
    <button class="btn" onclick="toggleFullscreen()">全屏 [F]</button>
    <button class="btn" onclick="window.print()">导出PDF [P]</button>
  </div>
</div>

<script>
let cur = 0;
const total = {{ pres.slides|length }};

function showSlide(idx) {
  if(idx < 0) idx = 0;
  if(idx >= total) idx = total - 1;
  cur = idx;
  for(let i=0; i<total; i++) {
    const el = document.getElementById('slide-' + i);
    if(el) el.classList.toggle('active', i === cur);
  }
  document.getElementById('counter').innerText = (cur + 1) + ' / ' + total;
}

function nextSlide() { showSlide(cur + 1); }
function prevSlide() { showSlide(cur - 1); }

function toggleFullscreen() {
  if (!document.fullscreenElement) {
    document.documentElement.requestFullscreen();
  } else {
    if (document.exitFullscreen) document.exitFullscreen();
  }
}

document.addEventListener('keydown', (e) => {
  if(e.key === 'ArrowRight' || e.key === ' ' || e.key === 'PageDown') {
    e.preventDefault();
    nextSlide();
  } else if(e.key === 'ArrowLeft' || e.key === 'PageUp') {
    e.preventDefault();
    prevSlide();
  } else if(e.key === 'f' || e.key === 'F') {
    toggleFullscreen();
  } else if(e.key === 'p' || e.key === 'P') {
    window.print();
  }
});
</script>
</body>
</html>
"""

def generate_html_deck(pres: Presentation) -> str:
    """Renders a standalone interactive HTML presentation.
    Supports both Jinja2 (if installed) and pure Python zero-dependency rendering.
    """
    try:
        from jinja2 import Template
        t = Template(HTML_TEMPLATE)
        return t.render(pres=pres, theme=pres.theme)
    except ImportError:
        # Robust Pure-Python Zero-Dependency Renderer
        theme = pres.theme
        slides_html = []
        for i, s in enumerate(pres.slides):
            is_active = "active" if i == 0 else ""
            progress = ((i + 1) / len(pres.slides)) * 100
            
            if s.slide_type == "cover":
                eyebrow_html = f"""<div style="font-size:clamp(11px, 1.4vw, 14px); letter-spacing:0.18em; text-transform:uppercase; font-weight:700; color:var(--accent); margin-bottom:14px; display:flex; align-items:center; gap:8px;">
                  <span style="width:20px; height:2px; background:var(--accent);"></span>
                  {s.eyebrow}
                </div>""" if s.eyebrow else ""
                
                sub_html = f"""<div style="font-size:clamp(15px, 2vw, 22px); opacity:0.75; line-height:1.5; max-width:85%; margin-bottom:28px;">
                  {s.subtitle}
                </div>""" if s.subtitle else ""

                content_html = f"""
                <div style="flex:1; display:flex; flex-direction:column; justify-content:center; align-items:flex-start; padding:8% 9%; position:relative; overflow:hidden">
                  {eyebrow_html}
                  <h1 style="font-size:clamp(32px, 5.2vw, 56px); font-weight:800; line-height:1.15; letter-spacing:-0.02em; margin-bottom:16px;">
                    {s.title}
                  </h1>
                  {sub_html}
                  <div style="display:flex; align-items:center; gap:12px; margin-top:auto;">
                    <span style="padding:4px 12px; border-radius:20px; background:var(--card-bg); border:1px solid var(--card-border); font-size:12px; font-weight:600;">
                      {pres.scenario_id.upper()}
                    </span>
                    <span style="font-size:12px; opacity:0.5;">PrettyPPT · {theme.name_zh if theme else ''}</span>
                  </div>
                </div>
                """

            elif s.slide_type == "narrative":
                eyebrow_html = f"""<div style="font-size:12px; font-weight:700; color:var(--accent); letter-spacing:0.15em; text-transform:uppercase; margin-bottom:6px;">{s.eyebrow}</div>""" if s.eyebrow else ""
                body_html = f"""<div style="font-size:clamp(14px, 1.8vw, 20px); opacity:0.85; line-height:1.6; margin-bottom:24px; padding-left:14px; border-left:3px solid var(--accent);">{s.body}</div>""" if s.body else ""
                
                bullets_html = ""
                if s.bullets:
                    b_items = "".join([f"""<div style="display:flex; align-items:flex-start; gap:10px; font-size:clamp(13px, 1.5vw, 17px); opacity:0.9;">
                      <div style="width:6px; height:6px; border-radius:50%; background:var(--accent); margin-top:8px; flex-shrink:0;"></div>
                      <div>{b}</div>
                    </div>""" for b in s.bullets])
                    bullets_html = f"""<div style="display:flex; flex-direction:column; gap:12px;">{b_items}</div>"""

                content_html = f"""
                <div class="slide-header">
                  {eyebrow_html}
                  <h2 style="font-size:clamp(22px, 3.2vw, 36px); font-weight:800; line-height:1.2;">{s.title}</h2>
                </div>
                <div class="slide-body">
                  {body_html}
                  {bullets_html}
                </div>
                <div class="slide-footer">
                  <span>{s.footer or pres.title}</span>
                  <span>{i+1:02d} / {len(pres.slides):02d}</span>
                </div>
                """

            elif s.slide_type == "grid":
                eyebrow_html = f"""<div style="font-size:12px; font-weight:700; color:var(--accent); letter-spacing:0.15em; text-transform:uppercase; margin-bottom:6px;">{s.eyebrow}</div>""" if s.eyebrow else ""
                cards_html = ""
                for c in s.cards:
                    tag_html = f"""<span style="font-size:10px; font-weight:700; padding:2px 8px; border-radius:4px; background:var(--accent); color:#fff; display:inline-block; margin-bottom:10px;">{c.tag}</span>""" if c.tag else ""
                    metric_html = f"""<div style="font-size:clamp(18px, 2.5vw, 28px); font-weight:800; color:var(--accent); margin-top:16px; border-top:1px solid var(--card-border); padding-top:12px;">{c.metric}</div>""" if c.metric else ""
                    cards_html += f"""
                    <div style="background:var(--card-bg); border:1px solid var(--card-border); border-radius:12px; padding:20px; display:flex; flex-direction:column; justify-content:space-between; box-shadow:0 4px 14px rgba(0,0,0,0.03);">
                      <div>
                        {tag_html}
                        <h3 style="font-size:clamp(15px, 1.8vw, 20px); font-weight:700; margin-bottom:8px;">{c.title}</h3>
                        <p style="font-size:clamp(12px, 1.3vw, 14px); opacity:0.75; line-height:1.5;">{c.desc}</p>
                      </div>
                      {metric_html}
                    </div>
                    """

                content_html = f"""
                <div class="slide-header">
                  {eyebrow_html}
                  <h2 style="font-size:clamp(22px, 3.2vw, 36px); font-weight:800; line-height:1.2;">{s.title}</h2>
                </div>
                <div class="slide-body">
                  <div style="display:grid; grid-template-columns:repeat(3, 1fr); gap:16px;">
                    {cards_html}
                  </div>
                </div>
                <div class="slide-footer">
                  <span>{s.footer or pres.title}</span>
                  <span>{i+1:02d} / {len(pres.slides):02d}</span>
                </div>
                """

            elif s.slide_type == "metrics":
                eyebrow_html = f"""<div style="font-size:12px; font-weight:700; color:var(--accent); letter-spacing:0.15em; text-transform:uppercase; margin-bottom:6px;">{s.eyebrow}</div>""" if s.eyebrow else ""
                body_html = f"""<div style="font-size:clamp(13px, 1.4vw, 16px); opacity:0.8; margin-bottom:20px;">{s.body}</div>""" if s.body else ""
                metrics_html = ""
                for m in s.metrics:
                    delta_html = f"""<div style="font-size:11px; font-weight:700; color:var(--accent2); margin-top:6px;">{m.delta}</div>""" if m.delta else ""
                    metrics_html += f"""
                    <div style="background:var(--card-bg); border:1px solid var(--card-border); border-radius:12px; padding:18px; text-align:center;">
                      <div style="font-size:clamp(22px, 3.5vw, 40px); font-weight:800; color:var(--accent); line-height:1.1;">
                        {m.value}
                      </div>
                      <div style="font-size:clamp(11px, 1.2vw, 13px); opacity:0.7; font-weight:600; margin-top:6px;">
                        {m.label}
                      </div>
                      {delta_html}
                    </div>
                    """

                content_html = f"""
                <div class="slide-header">
                  {eyebrow_html}
                  <h2 style="font-size:clamp(22px, 3.2vw, 36px); font-weight:800; line-height:1.2;">{s.title}</h2>
                </div>
                <div class="slide-body">
                  {body_html}
                  <div style="display:grid; grid-template-columns:repeat(4, 1fr); gap:14px; margin-bottom:20px;">
                    {metrics_html}
                  </div>
                </div>
                <div class="slide-footer">
                  <span>{s.footer or pres.title}</span>
                  <span>{i+1:02d} / {len(pres.slides):02d}</span>
                </div>
                """

            else:  # cta or fallback
                eyebrow_html = f"""<div style="font-size:12px; font-weight:700; color:var(--accent); letter-spacing:0.15em; text-transform:uppercase; margin-bottom:6px;">{s.eyebrow}</div>""" if s.eyebrow else ""
                body_html = f"""<div style="font-size:clamp(15px, 2vw, 22px); opacity:0.85; line-height:1.6; margin-bottom:24px;">{s.body}</div>""" if s.body else ""
                bullets_html = ""
                if s.bullets:
                    b_items = "".join([f"""<div style="padding:14px 18px; border-radius:8px; background:var(--card-bg); border:1px solid var(--card-border); font-size:clamp(13px, 1.6vw, 16px); font-weight:600; display:flex; align-items:center; gap:10px;">
                      <span style="color:var(--accent);">✦</span> {b}
                    </div>""" for b in s.bullets])
                    bullets_html = f"""<div style="display:flex; flex-direction:column; gap:12px;">{b_items}</div>"""

                content_html = f"""
                <div class="slide-header">
                  {eyebrow_html}
                  <h2 style="font-size:clamp(24px, 3.6vw, 42px); font-weight:800; line-height:1.2;">{s.title}</h2>
                </div>
                <div class="slide-body">
                  {body_html}
                  {bullets_html}
                </div>
                <div class="slide-footer">
                  <span>{s.footer or pres.title}</span>
                  <span>{i+1:02d} / {len(pres.slides):02d}</span>
                </div>
                """

            slide_box = f"""
            <div class="slide-frame {is_active}" id="slide-{i}">
              {content_html}
              <div class="progress-bar" style="width: {progress}%;"></div>
            </div>
            """
            slides_html.append(slide_box)

        all_slides_rendered = "\n".join(slides_html)
        theme_bg = theme.bg_color if theme else "#111113"
        theme_text = theme.text_color if theme else "#F5F5F7"
        theme_accent = theme.accent_color if theme else "#A1A1A6"
        theme_accent2 = theme.secondary_accent if theme else "#0071E3"
        theme_card_bg = theme.card_bg if theme else "rgba(255,255,255,0.05)"
        theme_card_border = theme.card_border if theme else "rgba(255,255,255,0.12)"
        theme_ff = theme.font_family if theme else "sans-serif"
        theme_name_zh = theme.name_zh if theme else "经典"

        return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{pres.title} · PrettyPPT</title>
<script src="https://www.gstatic.com/antigravity/web/dev/tailwindcss.min.js"></script>
<style>
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
:root {{
  --bg: {theme_bg};
  --text: {theme_text};
  --accent: {theme_accent};
  --accent2: {theme_accent2};
  --card-bg: {theme_card_bg};
  --card-border: {theme_card_border};
  --ff: {theme_ff};
}}
body {{
  background: #09090B;
  color: #F4F4F5;
  font-family: var(--ff);
  overflow: hidden;
  height: 100vh;
  display: flex;
  flex-direction: column;
}}
.deck-viewport {{
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 16px;
  position: relative;
}}
.slide-frame {{
  width: min(94vw, 1280px);
  aspect-ratio: 16 / 9;
  background: var(--bg);
  color: var(--text);
  border-radius: 14px;
  overflow: hidden;
  position: relative;
  box-shadow: 0 20px 50px rgba(0,0,0,0.4);
  display: none;
  flex-direction: column;
  transition: opacity 0.25s ease;
}}
.slide-frame.active {{ display: flex; }}
.hud {{
  height: 52px;
  background: #111113;
  border-top: 1px solid #27272A;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  font-size: 12px;
  color: #A1A1AA;
}}
.btn {{
  padding: 6px 14px;
  border-radius: 6px;
  background: #27272A;
  color: #F4F4F5;
  font-size: 12px;
  font-weight: 500;
  border: none;
  cursor: pointer;
  transition: all 0.15s;
}}
.btn:hover {{ background: #3F3F46; color: #fff; }}
.progress-bar {{
  position: absolute;
  bottom: 0;
  left: 0;
  height: 3px;
  background: var(--accent);
  transition: width 0.3s ease;
}}
.slide-header {{ padding: 5% 7% 0 7%; }}
.slide-body {{ flex: 1; padding: 3% 7% 5% 7%; display: flex; flex-direction: column; justify-content: center; }}
.slide-footer {{ padding: 0 7% 3% 7%; display: flex; justify-content: space-between; font-size: clamp(9px, 1vw, 11px); opacity: 0.45; }}
@media print {{
  body {{ overflow: visible; height: auto; background: #fff; }}
  .hud {{ display: none; }}
  .deck-viewport {{ padding: 0; display: block; }}
  .slide-frame {{ display: flex !important; page-break-after: always; width: 100vw; height: 56.25vw; border-radius: 0; box-shadow: none; margin-bottom: 20px; }}
}}
</style>
</head>
<body>

<div class="deck-viewport">
  {all_slides_rendered}
</div>

<div class="hud">
  <div style="display:flex; align-items:center; gap:12px;">
    <strong style="color:#fff;">{pres.title}</strong>
    <span style="opacity:0.4;">|</span>
    <span>{theme_name_zh} ({pres.scenario_id})</span>
  </div>
  <div style="display:flex; align-items:center; gap:12px;">
    <button class="btn" onclick="prevSlide()">← 上一页 [Left]</button>
    <span id="counter" style="font-weight:700; color:#fff; min-width:44px; text-align:center;">1 / {len(pres.slides)}</span>
    <button class="btn" onclick="nextSlide()">下一页 [Right] →</button>
    <button class="btn" onclick="toggleFullscreen()">全屏 [F]</button>
    <button class="btn" onclick="window.print()">导出PDF [P]</button>
  </div>
</div>

<script>
let cur = 0;
const total = {len(pres.slides)};

function showSlide(idx) {{
  if(idx < 0) idx = 0;
  if(idx >= total) idx = total - 1;
  cur = idx;
  for(let i=0; i<total; i++) {{
    const el = document.getElementById('slide-' + i);
    if(el) el.classList.toggle('active', i === cur);
  }}
  document.getElementById('counter').innerText = (cur + 1) + ' / ' + total;
}}

function nextSlide() {{ showSlide(cur + 1); }}
function prevSlide() {{ showSlide(cur - 1); }}

function toggleFullscreen() {{
  if (!document.fullscreenElement) {{
    document.documentElement.requestFullscreen();
  }} else {{
    if (document.exitFullscreen) document.exitFullscreen();
  }}
}}

document.addEventListener('keydown', (e) => {{
  if(e.key === 'ArrowRight' || e.key === ' ' || e.key === 'PageDown') {{
    e.preventDefault();
    nextSlide();
  }} else if(e.key === 'ArrowLeft' || e.key === 'PageUp') {{
    e.preventDefault();
    prevSlide();
  }} else if(e.key === 'f' || e.key === 'F') {{
    toggleFullscreen();
  }} else if(e.key === 'p' || e.key === 'P') {{
    window.print();
  }}
}});
</script>
</body>
</html>
"""

def generate_pptx_deck(pres: Presentation, output_path: str) -> bool:
    """Exports native Microsoft PowerPoint (.pptx) file using python-pptx."""
    try:
        from pptx import Presentation as PptxPresentation
        from pptx.util import Inches, Pt
        from pptx.dml.color import RGBColor
        from pptx.enum.text import PP_ALIGN

        prs = PptxPresentation()
        # Set 16:9 widescreen dimensions
        prs.slide_width = Inches(13.333)
        prs.slide_height = Inches(7.5)

        blank_slide_layout = prs.slide_layouts[6]

        def hex_to_rgb(hex_str: str) -> RGBColor:
            hex_str = hex_str.lstrip('#')
            if len(hex_str) == 3:
                hex_str = ''.join([c*2 for c in hex_str])
            try:
                r = int(hex_str[0:2], 16)
                g = int(hex_str[2:4], 16)
                b = int(hex_str[4:6], 16)
                return RGBColor(r, g, b)
            except Exception:
                return RGBColor(0, 0, 0)

        theme = pres.theme
        bg_rgb = hex_to_rgb(theme.bg_color) if theme else RGBColor(255, 255, 255)
        text_rgb = hex_to_rgb(theme.text_color) if theme else RGBColor(20, 20, 20)
        accent_rgb = hex_to_rgb(theme.accent_color) if theme else RGBColor(0, 102, 204)

        for s in pres.slides:
            slide = prs.slides.add_slide(blank_slide_layout)
            
            # Background
            background = slide.background
            fill = background.fill
            fill.solid()
            fill.fore_color.rgb = bg_rgb

            # Title
            tx_box = slide.shapes.add_textbox(Inches(1.0), Inches(0.8), Inches(11.33), Inches(1.5))
            tf = tx_box.text_frame
            tf.word_wrap = True
            p = tf.paragraphs[0]
            p.text = s.title
            p.font.size = Pt(38 if s.slide_type == "cover" else 28)
            p.font.bold = True
            p.font.color.rgb = text_rgb

            # Subtitle / Body
            if s.subtitle or s.body:
                p2 = tf.add_paragraph()
                p2.text = s.subtitle or s.body or ""
                p2.font.size = Pt(18)
                p2.font.color.rgb = accent_rgb

            # Bullets
            if s.bullets:
                bullet_box = slide.shapes.add_textbox(Inches(1.0), Inches(2.6), Inches(11.33), Inches(4.0))
                btf = bullet_box.text_frame
                btf.word_wrap = True
                for i, b in enumerate(s.bullets):
                    bp = btf.paragraphs[0] if i == 0 else btf.add_paragraph()
                    bp.text = f"•  {b}"
                    bp.font.size = Pt(16)
                    bp.font.color.rgb = text_rgb
                    bp.space_after = Pt(12)

            # Metrics
            if s.metrics:
                col_width = Inches(11.33 / max(len(s.metrics), 1))
                for i, m in enumerate(s.metrics):
                    left = Inches(1.0) + (col_width * i)
                    mbox = slide.shapes.add_textbox(left, Inches(2.8), col_width - Inches(0.2), Inches(3.0))
                    mtf = mbox.text_frame
                    mtf.word_wrap = True
                    mp1 = mtf.paragraphs[0]
                    mp1.text = m.value
                    mp1.font.size = Pt(36)
                    mp1.font.bold = True
                    mp1.font.color.rgb = accent_rgb
                    
                    mp2 = mtf.add_paragraph()
                    mp2.text = m.label
                    mp2.font.size = Pt(14)
                    mp2.font.color.rgb = text_rgb
                    
                    if m.delta:
                        mp3 = mtf.add_paragraph()
                        mp3.text = m.delta
                        mp3.font.size = Pt(12)
                        mp3.font.color.rgb = accent_rgb

        prs.save(output_path)
        return True
    except Exception as e:
        print(f"Error generating PPTX: {e}")
        return False
