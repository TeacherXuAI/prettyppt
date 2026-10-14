"""Export all real templates for visual QA; optional native PPTX output."""
import argparse
import json
from pathlib import Path
from prettyppt import get_all_templates, generate_html_deck, generate_pptx_deck
from prettyppt.core.layout import compose

parser = argparse.ArgumentParser()
parser.add_argument('--output', required=True)
parser.add_argument('--pptx', action='store_true')
args = parser.parse_args()
target = Path(args.output)
target.mkdir(parents=True, exist_ok=True)
pages = 0
for deck in get_all_templates():
    name = deck.template_id.replace('/', '--')
    for i, slide in enumerate(deck.slides):
        compose(deck, slide, i)
    (target / (name + '.html')).write_text(generate_html_deck(deck), encoding='utf-8')
    if args.pptx:
        generate_pptx_deck(deck, target / (name + '.pptx'))
    pages += len(deck.slides)
print(json.dumps({'templates': 80, 'pages': pages, 'output': str(target.resolve())}))
