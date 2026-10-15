"""Installed copy of the actual skill protocol, not a separate five-page prompt."""
from pathlib import Path

def get_master_prompt():
    root = Path(__file__).parent
    skill = (root / 'agent.md').read_text(encoding='utf-8')
    if skill.startswith('---\n'):
        skill = skill.split('---', 2)[2].strip()
    return skill + '\n\n' + (root / 'brief.md').read_text(encoding='utf-8')
