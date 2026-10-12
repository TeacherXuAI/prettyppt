"""
Command Line Interface for PrettyPPT
Provides commands to list, generate, preview, and export presentation decks.
"""

import sys
import argparse
import os
import webbrowser

# Ensure package root is in sys.path
package_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if package_root not in sys.path:
    sys.path.insert(0, package_root)

from prettyppt.templates.registry import list_scenarios, list_styles, get_template
from prettyppt.core.generator import generate_html_deck, generate_pptx_deck
from prettyppt.prompts.master_prompt import get_master_prompt

def cmd_list(args):
    print("=" * 65)
    print("🎨 PrettyPPT · 10 大商业场景 (10 Scenarios)")
    print("=" * 65)
    for s in list_scenarios():
        print(f" • [{s['id']:<16}] {s['name_zh']} ({s['name']}) - {s['badge']}")
    
    print("\n" + "=" * 65)
    print("✨ PrettyPPT · 8 大核心设计系统 (8 Core Aesthetics)")
    print("=" * 65)
    for st in list_styles(only_core=True):
        print(f" • [{st['id']:<22}] {st['name_zh']} ({st['category'].upper()}) - {st['badge']}")
    print(f"\n💡 总计支持 10 场景 × 8 核心风格 = 80 套预制母版系统！")

def cmd_generate(args):
    scenario = args.scenario
    style = args.style
    fmt = args.format.lower()
    output = args.output

    if not output:
        ext = ".pptx" if fmt == "pptx" else ".html"
        output = f"prettyppt_{scenario}_{style}{ext}"

    print(f"🚀 正在合成演示文稿...")
    print(f"   • 场景: {scenario}")
    print(f"   • 风格: {style}")
    print(f"   • 格式: {fmt.upper()}")
    print(f"   • 输出: {output}")

    deck = get_template(scenario, style)

    if fmt == "pptx":
        success = generate_pptx_deck(deck, output)
        if success:
            print(f"✅ 成功生成 PowerPoint 演示文稿: {output}")
        else:
            print(f"❌ 导出 PPTX 失败，请检查 python-pptx 是否已安装。")
            sys.exit(1)
    else:
        html = generate_html_deck(deck)
        with open(output, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"✅ 成功生成高保真交互式 HTML 演示文稿: {output}")

    if args.open:
        abs_path = os.path.abspath(output)
        webbrowser.open(f"file://{abs_path}")

def cmd_prompt(args):
    print(get_master_prompt())

def cmd_preview(args):
    viewer_path = os.path.join(os.path.dirname(__file__), "viewers", "gallery.html")
    if os.path.exists(viewer_path):
        print(f"🌐 正在打开 PrettyPPT 80款模板全景画廊...")
        webbrowser.open(f"file://{os.path.abspath(viewer_path)}")
    else:
        print(f"画廊文件位于: {viewer_path}")

def main():
    parser = argparse.ArgumentParser(
        prog="prettyppt",
        description="PrettyPPT: Universal AI-Agent Presentation Toolkit (80+ Curated Aesthetic Templates)"
    )
    subparsers = parser.add_subparsers(dest="command", help="子命令")

    # list
    p_list = subparsers.add_parser("list", help="列出全部支持的场景与设计系统")
    p_list.set_defaults(func=cmd_list)

    # generate
    p_gen = subparsers.add_parser("generate", help="合成指定场景与风格的演示文稿")
    p_gen.add_argument("-s", "--scenario", default="pitch_deck", help="场景 ID (默认: pitch_deck)")
    p_gen.add_argument("-t", "--style", default="apple_titanium", help="风格 ID (默认: apple_titanium)")
    p_gen.add_argument("-f", "--format", default="html", choices=["html", "pptx"], help="输出格式: html 或 pptx (默认: html)")
    p_gen.add_argument("-o", "--output", help="输出文件路径")
    p_gen.add_argument("--open", action="store_true", help="生成后自动在浏览器中打开")
    p_gen.set_defaults(func=cmd_generate)

    # prompt
    p_prompt = subparsers.add_parser("prompt", help="打印供智能体使用的 Master Agent Prompt")
    p_prompt.set_defaults(func=cmd_prompt)

    # preview
    p_prev = subparsers.add_parser("preview", help="在浏览器中打开 80 模板全景画廊")
    p_prev.set_defaults(func=cmd_preview)

    args = parser.parse_args()
    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
