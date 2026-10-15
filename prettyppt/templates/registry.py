"""Template discovery and explicitly labelled sample decks."""
from .styles import CORE_STYLES, ALL_STYLES
from .scenarios import SCENARIOS
from .catalog import list_templates, template_spec
from ..core.planner import get_theme, create_presentation
from ..data.demos import demo_brief


def list_scenarios():
    return list(SCENARIOS.values())


def list_styles(only_core=False):
    return list((CORE_STYLES if only_core else ALL_STYLES).values())


def get_style_theme(style_id):
    return get_theme(style_id)


def get_template(scenario_id, style_id):
    # The additional 8 legacy colour themes remain available through the SDK.
    # They reuse the modern layout family and are not counted as core editions.
    core = style_id if style_id in CORE_STYLES else 'silicon_valley'
    if style_id not in ALL_STYLES:
        raise ValueError('Unknown style: ' + str(style_id))
    spec = template_spec(scenario_id, core)
    deck = create_presentation(demo_brief(scenario_id, spec), mode='conservative')
    if style_id != core:
        deck.theme = get_theme(style_id)
        deck.style_id = style_id
    return deck


def get_all_templates(only_core=True):
    return [get_template(sc, st) for sc in SCENARIOS for st in (CORE_STYLES if only_core else ALL_STYLES)]
