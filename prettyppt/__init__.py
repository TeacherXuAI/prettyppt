"""
PrettyPPT: Universal AI-Agent Presentation Toolkit
80+ Curated Aesthetic Templates, Multi-Scenario Prompts & Multi-Format Slide Generation.
"""

__version__ = "0.2.0"
__author__ = "PrettyPPT Team"

from prettyppt.core.models import Presentation, Slide, Theme
from prettyppt.core.generator import generate_html_deck, generate_pptx_deck
from prettyppt.templates.registry import list_scenarios, list_styles, get_template, get_all_templates

__all__ = [
    "Presentation",
    "Slide",
    "Theme",
    "generate_html_deck",
    "generate_pptx_deck",
    "list_scenarios",
    "list_styles",
    "get_template",
    "get_all_templates",
]

from prettyppt.core.planner import create_presentation
from prettyppt.templates.catalog import list_templates, template_spec
__all__ += ["create_presentation", "list_templates", "template_spec"]
