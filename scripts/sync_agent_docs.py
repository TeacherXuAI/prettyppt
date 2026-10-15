"""Keep root compatibility instructions and installed prompt in sync."""
from pathlib import Path
root = Path(__file__).resolve().parents[1]
source = (root / 'SKILL.md').read_text(encoding='utf-8')
(root / 'AGENT_SKILL.md').write_text(source, encoding='utf-8')
(root / 'prettyppt/prompts/agent.md').write_text(source, encoding='utf-8')
(root / 'prettyppt/prompts/brief.md').write_text((root / 'references/brief.md').read_text(encoding='utf-8'), encoding='utf-8')
