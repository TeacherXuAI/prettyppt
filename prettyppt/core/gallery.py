"""Offline gallery built from the same real templates that the SDK exports."""
import html
import json
from pathlib import Path
try:
    from .generator import generate_html_deck, generate_pptx_deck
    from ..templates.catalog import list_templates
    from ..templates.registry import get_template
except ImportError:
    from prettyppt.core.generator import generate_html_deck, generate_pptx_deck
    from prettyppt.templates.catalog import list_templates
    from prettyppt.templates.registry import get_template


def build_gallery(output_path, pptx_dir=None):
    records = []
    for spec in list_templates():
        deck = get_template(spec['scenario_id'], spec['style_id'])
        record = dict(spec, html=generate_html_deck(deck), pages=len(deck.slides))
        if pptx_dir:
            target = Path(pptx_dir) / (spec['id'].replace('/', '--') + '.pptx')
            target.parent.mkdir(parents=True, exist_ok=True)
            generate_pptx_deck(deck, target)
            # The download is relative to the HTML gallery location.
            import os
            record['pptx'] = os.path.relpath(target, Path(output_path).parent)
        records.append(record)
    data = json.dumps(records, ensure_ascii=False).replace('<', '\\u003c')
    document = '''<!DOCTYPE html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>PrettyPPT · 模板画廊</title><style>
*{box-sizing:border-box}body{margin:0;background:#f0eee8;color:#19221f;font-family:'PingFang SC',sans-serif}header{padding:55px 5vw 35px;border-bottom:1px solid #c5cac0}h1{font-size:42px;letter-spacing:-1.5px;margin:8px 0 15px}p{line-height:1.8}small{letter-spacing:2px}#filters{display:flex;gap:8px;flex-wrap:wrap;padding:24px 5vw}button,a.button{cursor:pointer;border:1px solid #a8b3a6;background:transparent;padding:10px 15px;border-radius:3px;font:inherit;color:inherit;text-decoration:none}button.active,button:hover{background:#183b30;color:white}#grid{padding:0 5vw 70px;display:grid;grid-template-columns:repeat(auto-fill,minmax(310px,1fr));gap:36px 24px}.card h2{font-size:19px;margin:15px 0 7px}.card p{font-size:13px;margin:0 0 12px;min-height:46px}.thumb{aspect-ratio:16/9;overflow:hidden;background:#ddd;position:relative;border:1px solid #c9cdc6;cursor:pointer}.thumb iframe{border:0;width:100%;height:100%;pointer-events:none}.card .meta{font-size:12px;color:#536258;margin:8px 0}.card button{padding:6px 11px;font-size:13px}dialog{padding:0;border:0;background:#1a1b1e;color:white;width:min(95vw,1500px);max-width:none}dialog::backdrop{background:#000b}dialog iframe{border:0;width:100%;height:75vh}#toolbar{display:flex;align-items:center;justify-content:space-between;padding:15px 20px;gap:10px;flex-wrap:wrap}#toolbar div{display:flex;gap:8px}#count{font-size:14px;margin-left:12px}footer{padding:25px 5vw;border-top:1px solid #c5cac0;font-size:13px}
</style><header><small>PRETTYPPT / TEMPLATE LIBRARY</small><h1>找到适合内容的表达方式</h1><p>10 个场景，每个场景 8 款不同版式。点击查看完整示例，或下载后交给 Agent 参考。</p><span>默认自动选模板 · 适度参考 · 按内容分页</span><span id="count"></span></header><div id="filters"></div><main id="grid"></main><footer>所有预览使用项目实际渲染器生成。演示内容与数据为虚构占位。三档参考强度：保守套用、适度参考、自由创作。</footer><dialog id="viewer"><div id="toolbar"><span id="name"></span><div><button id="download">下载 HTML</button><a class="button" id="pptx">下载 PPTX</a><button id="recipe">下载参考说明</button><button id="close">关闭</button></div></div><iframe id="deck" title="模板完整预览" sandbox="allow-scripts allow-modals allow-downloads"></iframe></dialog><script>
const records=DATA;const labels={pitch_deck:'融资路演',annual_review:'年度汇报',product_launch:'产品发布',research_report:'行业研究',strategy_deck:'战略规划',brand_proposal:'品牌提案',training_deck:'培训课件',business_review:'业务评审',keynote_speech:'大会演讲',portfolio:'作品集'};let selected='all',active=null;const grid=document.querySelector('#grid'),viewer=document.querySelector('#viewer');function save(content,name,type){const a=document.createElement('a');a.href=URL.createObjectURL(new Blob([content],{type}));a.download=name;a.click();setTimeout(()=>URL.revokeObjectURL(a.href),1000)}function open(record){active=record;document.querySelector('#name').textContent=record.name;document.querySelector('#deck').srcdoc=record.html;document.querySelector('#pptx').style.display=record.pptx?'inline':'none';document.querySelector('#pptx').href=record.pptx||'';viewer.showModal()}function draw(){grid.replaceChildren();document.querySelectorAll('#filters button').forEach(b=>b.classList.toggle('active',b.dataset.id===selected));const list=records.filter(r=>selected==='all'||r.scenario_id===selected);document.querySelector('#count').textContent=list.length+' 款模板';const observer=new IntersectionObserver(entries=>entries.forEach(e=>{if(e.isIntersecting){const frame=e.target;frame.srcdoc=frame.dataset.source;delete frame.dataset.source;observer.unobserve(frame)}}));list.forEach(record=>{const card=document.createElement('article');card.className='card';const thumb=document.createElement('div');thumb.className='thumb';const frame=document.createElement('iframe');frame.title=record.name;frame.setAttribute('sandbox','allow-scripts');frame.dataset.source=record.html.replace('</style>','nav{display:none}main{height:100vh}</style>').replace('(innerHeight-82)/810','innerHeight/810').replace('(innerWidth-24)/1440','innerWidth/1440');thumb.append(frame);thumb.onclick=()=>open(record);const title=document.createElement('h2');title.textContent=record.name;const p=document.createElement('p');p.textContent=record.principle;const meta=document.createElement('div');meta.className='meta';meta.textContent=record.pages+' 页示例 · '+(record.density==='sparse'?'舒展排版':'均衡信息密度');const button=document.createElement('button');button.textContent='查看完整模板';button.onclick=()=>open(record);card.append(thumb,title,p,meta,button);grid.append(card);observer.observe(frame)})}Object.entries({all:'全部',...labels}).forEach(([id,label])=>{const b=document.createElement('button');b.textContent=label;b.dataset.id=id;b.onclick=()=>{selected=id;draw()};document.querySelector('#filters').append(b)});document.querySelector('#close').onclick=()=>viewer.close();document.querySelector('#download').onclick=()=>save(active.html,active.id.replace('/','--')+'.html','text/html');document.querySelector('#recipe').onclick=()=>{const {html,...spec}=active;save(JSON.stringify(spec,null,2),active.id.replace('/','--')+'.json','application/json')};draw();
</script></html>'''.replace('const records=DATA;', 'const records=' + data + ';')
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    Path(output_path).write_text(document, encoding='utf-8')
    return str(Path(output_path).resolve())
