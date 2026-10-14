import argparse
import json
import sys
import webbrowser
from pathlib import Path

# Support both direct execution and package module import
if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from prettyppt.core.inputs import load_brief, prepare_materials
    from prettyppt.core.planner import create_presentation
    from prettyppt.core.generator import generate_html_deck, generate_pptx_deck
    from prettyppt.templates.registry import list_scenarios, list_styles, get_template
    from prettyppt.templates.catalog import list_templates, template_spec
    from prettyppt.prompts.master_prompt import get_master_prompt
else:
    from .core.inputs import load_brief, prepare_materials
    from .core.planner import create_presentation
    from .core.generator import generate_html_deck, generate_pptx_deck
    from .templates.registry import list_scenarios, list_styles, get_template
    from .templates.catalog import list_templates, template_spec
    from .prompts.master_prompt import get_master_prompt


def cmd_list(args):
    for scenario in list_scenarios():
        print('%-18s %s' % (scenario['id'], scenario['name_zh']))
    print('\n八款核心设计系统')
    for style in list_styles(only_core=True):
        print('%-24s %s' % (style['id'], style['name_zh']))


def cmd_templates(args):
    records = list_templates(args.scenario)
    if args.json:
        print(json.dumps(records, ensure_ascii=False, indent=2))
    else:
        for item in records:
            print(item['id'] + '  ' + item['name'] + '\n  ' + item['principle'])


def cmd_generate(args):
    if args.demo:
        if args.input:
            raise ValueError('--demo and --input cannot be combined')
        deck = get_template('pitch_deck' if args.scenario == 'auto' else args.scenario, 'apple_titanium' if args.style == 'auto' else args.style)
    else:
        if not args.input:
            raise ValueError('Provide --input materials.md or brief.json. Use --demo only for fictional template examples.')
        brief = load_brief(args.input, args.purpose or '')
        deck = create_presentation(brief, purpose=args.purpose, scenario_id=args.scenario, style_id=args.style, mode=args.mode, pages=args.pages)
    output = Path(args.output or 'presentation').expanduser()
    output.parent.mkdir(parents=True, exist_ok=True)
    # --format controls the extension, preventing a PPTX file named .html.
    formats = ['html', 'pptx'] if args.format == 'both' else [args.format]
    paths = []
    for fmt in formats:
        target = output.with_suffix('.' + fmt)
        if fmt == 'html':
            target.write_text(generate_html_deck(deck), encoding='utf-8')
            paths.append(target.resolve())
            print('已生成：' + str(target.resolve()))
        else:
            if generate_pptx_deck(deck, target):
                paths.append(target.resolve())
                print('已生成：' + str(target.resolve()))
            else:
                print('PPTX 导出跳过：未安装 python-pptx 或无法生成')
    # Editable source is part of the handoff; it contains no hidden API keys.
    source = output.with_suffix('.deck.json')
    source.write_text(deck.to_json(), encoding='utf-8')
    print('模板：%s；参考强度：%s；页数：%d' % (deck.template_id, deck.mode, len(deck.slides)))
    print('可编辑源文件：' + str(source.resolve()))
    if args.open:
        webbrowser.open(paths[0].as_uri())


def cmd_prepare(args):
    data = prepare_materials(args.input, args.purpose)
    target = Path(args.output)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
    print('资料包：' + str(target.resolve()))


def cmd_render(args):
    if __package__ in (None, ""):
        from prettyppt.core.models import Presentation
    else:
        from .core.models import Presentation
    data = json.loads(Path(args.input).read_text(encoding='utf-8'))
    deck = Presentation.from_dict(data)
    target = Path(args.output)
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.suffix.lower() == '.pptx':
        generate_pptx_deck(deck, target)
    elif target.suffix.lower() == '.html':
        target.write_text(generate_html_deck(deck), encoding='utf-8')
    else:
        raise ValueError('Render output must end with .pptx or .html')
    print(str(target.resolve()))


def cmd_preview(args):
    viewer_path = Path(__file__).parent / 'viewers' / 'gallery.html'
    if not viewer_path.is_file():
        raise ValueError('Bundled gallery is missing; run prettyppt gallery --output gallery.html')
    webbrowser.open(viewer_path.resolve().as_uri())


def cmd_gallery(args):
    if __package__ in (None, ""):
        from prettyppt.core.gallery import build_gallery
    else:
        from .core.gallery import build_gallery
    pptx_dir = str(Path(args.output).parent / 'templates') if args.pptx else None
    path = build_gallery(args.output, pptx_dir=pptx_dir)
    print('模板画廊：' + path)
    if args.open:
        webbrowser.open(Path(path).as_uri())


def main(argv=None):
    parser = argparse.ArgumentParser(prog='prettyppt', description='资料 + 用途，自动选择模板并按内容生成演示文稿')
    sub = parser.add_subparsers(dest='command')
    sub.add_parser('list', help='查看场景与风格').set_defaults(func=cmd_list)
    template = sub.add_parser('templates', help='查看八十款模板的设计与结构')
    template.add_argument('-s', '--scenario'); template.add_argument('--json', action='store_true'); template.set_defaults(func=cmd_templates)
    gen = sub.add_parser('generate', help='从资料或 Agent brief 生成演示文稿')
    gen.add_argument('-i', '--input', nargs='+'); gen.add_argument('--purpose'); gen.add_argument('-s', '--scenario', default='auto')
    gen.add_argument('-t', '--style', default='auto'); gen.add_argument('--mode', choices=['conservative', 'moderate', 'free', '保守', '适度', '自由'])
    gen.add_argument('--pages', type=int); gen.add_argument('-f', '--format', choices=['html', 'pptx', 'both'], default='both')
    gen.add_argument('-o', '--output'); gen.add_argument('--demo', action='store_true'); gen.add_argument('--open', action='store_true'); gen.set_defaults(func=cmd_generate)
    prepare = sub.add_parser('prepare', help='提取资料，供 Agent 阅读与编排')
    prepare.add_argument('-i', '--input', nargs='+', required=True); prepare.add_argument('--purpose', default=''); prepare.add_argument('-o', '--output', default='materials.json'); prepare.set_defaults(func=cmd_prepare)
    render = sub.add_parser('render', help='重新渲染已修改的 .deck.json')
    render.add_argument('-i', '--input', required=True); render.add_argument('-o', '--output', required=True); render.set_defaults(func=cmd_render)
    sub.add_parser('preview', help='打开离线模板画廊').set_defaults(func=cmd_preview)
    gallery = sub.add_parser('gallery', help='导出八十款模板的画廊，可附可编辑 PPTX')
    gallery.add_argument('-o', '--output', default='gallery.html'); gallery.add_argument('--pptx', action='store_true'); gallery.add_argument('--open', action='store_true'); gallery.set_defaults(func=cmd_gallery)
    sub.add_parser('prompt', help='查看 Agent 执行说明').set_defaults(func=lambda args: print(get_master_prompt()))
    args = parser.parse_args(argv)
    if not hasattr(args, 'func'):
        parser.print_help(); return 0
    try:
        args.func(args)
        return 0
    except (ValueError, OSError, ImportError, KeyError, TypeError) as exc:
        parser.exit(2, 'prettyppt: ' + str(exc) + '\n')

if __name__ == '__main__':
    main()
