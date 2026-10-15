from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
import json

@dataclass
class Theme:
    id: str
    name: str
    name_zh: str
    category: str  # "western" or "chinese"
    mode: str      # "light" or "dark"
    bg_color: str
    text_color: str
    accent_color: str
    secondary_accent: str
    card_bg: str
    card_border: str
    font_family: str
    description: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "name_zh": self.name_zh,
            "category": self.category,
            "mode": self.mode,
            "bg_color": self.bg_color,
            "text_color": self.text_color,
            "accent_color": self.accent_color,
            "secondary_accent": self.secondary_accent,
            "card_bg": self.card_bg,
            "card_border": self.card_border,
            "font_family": self.font_family,
            "description": self.description,
        }

@dataclass
class MetricItem:
    value: str
    label: str
    delta: Optional[str] = None
    subtext: Optional[str] = None

@dataclass
class CardItem:
    title: str
    desc: str
    tag: Optional[str] = None
    icon: Optional[str] = None
    metric: Optional[str] = None

@dataclass
class Slide:
    slide_type: str  # cover, agenda, section, narrative, metrics, grid, split, table, quote, cta
    title: str
    subtitle: Optional[str] = None
    eyebrow: Optional[str] = None
    body: Optional[str] = None
    bullets: List[str] = field(default_factory=list)
    metrics: List[MetricItem] = field(default_factory=list)
    cards: List[CardItem] = field(default_factory=list)
    footer: Optional[str] = None
    image_url: Optional[str] = None
    custom_classes: Optional[str] = None
    layout: Optional[str] = None
    sources: List[str] = field(default_factory=list)
    notes: str = ""
    table: Optional[Dict[str, Any]] = None
    chart: Optional[Dict[str, Any]] = None
    elements: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "slide_type": self.slide_type,
            "title": self.title,
            "subtitle": self.subtitle,
            "eyebrow": self.eyebrow,
            "body": self.body,
            "bullets": self.bullets,
            "metrics": [{"value": m.value, "label": m.label, "delta": m.delta, "subtext": m.subtext} for m in self.metrics],
            "cards": [{"title": c.title, "desc": c.desc, "tag": c.tag, "icon": c.icon, "metric": c.metric} for c in self.cards],
            "footer": self.footer,
            "image_url": self.image_url,
            "custom_classes": self.custom_classes,
            "layout": self.layout,
            "sources": self.sources,
            "notes": self.notes,
            "table": self.table,
            "chart": self.chart,
            "elements": self.elements,
        }

@dataclass
class Presentation:
    title: str
    scenario_id: str
    style_id: str
    subtitle: Optional[str] = None
    author: Optional[str] = None
    date: Optional[str] = None
    theme: Optional[Theme] = None
    slides: List[Slide] = field(default_factory=list)
    mode: str = "moderate"
    template_id: str = ""
    purpose: str = ""
    audience: str = ""
    is_demo: bool = False
    decisions: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "title": self.title,
            "scenario_id": self.scenario_id,
            "style_id": self.style_id,
            "subtitle": self.subtitle,
            "author": self.author,
            "date": self.date,
            "theme": self.theme.to_dict() if self.theme else None,
            "slides": [s.to_dict() for s in self.slides],
            "mode": self.mode,
            "template_id": self.template_id,
            "purpose": self.purpose,
            "audience": self.audience,
            "is_demo": self.is_demo,
            "decisions": self.decisions,
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=indent)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Presentation":
        theme_data = data.get("theme")
        theme = Theme(**theme_data) if theme_data else None

        slides = []
        for s in data.get("slides", []):
            metrics = [MetricItem(**m) for m in s.get("metrics", [])]
            cards = [CardItem(**c) for c in s.get("cards", [])]
            slide = Slide(
                slide_type=s.get("slide_type", "narrative"),
                title=s.get("title", ""),
                subtitle=s.get("subtitle"),
                eyebrow=s.get("eyebrow"),
                body=s.get("body"),
                bullets=s.get("bullets", []),
                metrics=metrics,
                cards=cards,
                footer=s.get("footer"),
                image_url=s.get("image_url"),
                custom_classes=s.get("custom_classes"),
                layout=s.get("layout"),
                sources=s.get("sources", []),
                notes=s.get("notes", ""),
                table=s.get("table"),
                chart=s.get("chart"),
                elements=s.get("elements", []),
            )
            slides.append(slide)

        return cls(
            title=data.get("title", ""),
            scenario_id=data.get("scenario_id", "pitch_deck"),
            style_id=data.get("style_id", "apple_titanium"),
            subtitle=data.get("subtitle"),
            author=data.get("author"),
            date=data.get("date"),
            theme=theme,
            slides=slides,
            mode=data.get("mode", "moderate"),
            template_id=data.get("template_id", ""),
            purpose=data.get("purpose", ""),
            audience=data.get("audience", ""),
            is_demo=data.get("is_demo", False),
            decisions=data.get("decisions", {}),
        )
