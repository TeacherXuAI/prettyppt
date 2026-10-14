import json
import math
import tempfile
import unittest
import zipfile
from copy import deepcopy
from pathlib import Path
from prettyppt import create_presentation, get_template, get_all_templates, list_scenarios, list_styles, list_templates
from prettyppt.core.models import Presentation
from prettyppt.core.generator import generate_html_deck, generate_pptx_deck
from prettyppt.core.layout import compose, LayoutError, wrap_text
from prettyppt.core.inputs import read_material, load_brief
from prettyppt.core.planner import validate_brief

ROOT = Path(__file__).resolve().parents[1]

def brief(**kwargs):
    data = {'title':'客户产品介绍','purpose':'向客户介绍产品功能','sections':[{'title':'客户的问题','body':'项目资料分散，需要清楚的交接方式。','sources':['原始资料第2页']}]}
    data.update(kwargs)
    return data

class TestTemplates(unittest.TestCase):
    def test_matrix_and_structural_distinction(self):
        self.assertEqual(len(list_scenarios()), 10)
        self.assertEqual(len(list_styles(True)), 8)
        self.assertEqual(len(list_templates()), 80)
        for scenario in list_scenarios():
            geometries = []
            for spec in list_templates(scenario['id']):
                deck = get_template(spec['scenario_id'], spec['style_id'])
                self.assertTrue(deck.is_demo)
                self.assertEqual(len(deck.slides), 7)
                nodes = compose(deck, deck.slides[0], 0)
                geometries.append(tuple((n['kind'], n['x'], n['y'], n['w'], n['h']) for n in nodes))
            self.assertEqual(len(set(geometries)), 8, scenario['id'])

    def test_every_template_exports_and_every_text_stays_in_canvas(self):
        for deck in get_all_templates():
            self.assertIn('演示示例', generate_html_deck(deck))
            for i, slide in enumerate(deck.slides):
                for node in compose(deck, slide, i):
                    self.assertLessEqual(node['x'] + node['w'], 1441)
                    self.assertLessEqual(node['y'] + node['h'], 811)

    def test_unknown_ids_are_not_silently_replaced(self):
        with self.assertRaises(ValueError): get_template('typo', 'apple_titanium')
        with self.assertRaises(ValueError): get_template('pitch_deck', 'typo')

class TestPlanning(unittest.TestCase):
    def test_defaults_infer_purpose_and_never_insert_demo_data(self):
        deck = create_presentation(brief())
        self.assertEqual(deck.mode, 'moderate')
        self.assertEqual(deck.scenario_id, 'product_launch')
        self.assertEqual(deck.style_id, 'silicon_valley')
        self.assertFalse(deck.is_demo)
        self.assertNotIn('FlowAI', deck.to_json())
        self.assertNotIn('审计', deck.to_json())
        self.assertEqual(deck.slides[-1].sources, ['原始资料第2页'])

    def test_pagination_preserves_long_material(self):
        text = ''.join('第%d项资料需要完整保留。' % i for i in range(200))
        deck = create_presentation(brief(sections=[{'title':'完整资料','body':text}]))
        self.assertGreater(len(deck.slides), 5)
        self.assertEqual(''.join(s.body or '' for s in deck.slides), text)

    def test_moderate_adapts_four_items_while_conservative_preserves_family(self):
        data=brief(sections=[{'title':'四个功能','cards':[{'title':str(i),'desc':'资料中的功能说明。'} for i in range(4)]}])
        moderate=create_presentation(data)
        conservative=create_presentation(data,mode='conservative')
        self.assertEqual(moderate.slides[1].layout,'matrix')
        self.assertNotEqual(conservative.slides[1].layout,'matrix')
        self.assertEqual(sum(len(s.cards) for s in moderate.slides),4)
        self.assertEqual(sum(len(s.cards) for s in conservative.slides),4)

    def test_three_modes_preserve_same_facts(self):
        data=brief(sections=[{'title':'事实','body':'原文给出的事实。','bullets':['客户 A 已确认','客户 B 待反馈']}, {'title':'数据','metrics':[{'value':'12','label':'样本数','delta':'截至六月'}]}])
        for mode in ('conservative','moderate','free'):
            deck=create_presentation(data,mode=mode)
            text=deck.to_json()
            for fact in ('原文给出的事实。','客户 A 已确认','客户 B 待反馈','样本数','截至六月'):
                self.assertIn(fact,text)

    def test_free_composition_and_design(self):
        data=json.loads((ROOT/'examples/free-layout.json').read_text())
        data['design']={'bg_color':'#FFF4E6','text_color':'#20160A'}
        deck=create_presentation(data)
        self.assertEqual(deck.slides[0].layout,'custom')
        self.assertEqual(deck.theme.bg_color,'#FFF4E6')
        self.assertIn('客户更需要清楚的交接', generate_html_deck(deck))
        with self.assertRaises(ValueError): create_presentation(data,mode='conservative')

    def test_custom_out_of_bounds_and_bad_content_layout_fail(self):
        data=brief(mode='free',sections=[{'title':'A','elements':[{'kind':'text','text':'越界','x':1400,'y':20,'w':200,'h':100}]}])
        with self.assertRaises(LayoutError): create_presentation(data)
        with self.assertRaises(ValueError): create_presentation(brief(mode='free',sections=[{'title':'A','body':'完整正文','layout':'cover_stage'}]))

    def test_page_count_is_explicit_without_data_loss(self):
        deck=create_presentation(brief(),pages=1)
        self.assertEqual(len(deck.slides),1)
        with self.assertRaises(ValueError): create_presentation(brief(),pages=20)

    def test_table_and_chart_pagination_preserves_all_values(self):
        rows=[[str(i),i*3] for i in range(13)]
        data=brief(sections=[{'title':'表格','table':{'headers':['编号','值'],'rows':rows}}, {'title':'趋势','chart':{'categories':[str(i) for i in range(15)],'series':[{'name':'样本','values':list(range(15))}]}}])
        deck=create_presentation(data)
        self.assertEqual([r for s in deck.slides if s.table for r in s.table['rows']], rows)
        self.assertEqual([v for s in deck.slides if s.chart for v in s.chart['series'][0]['values']], list(range(15)))

    def test_table_cell_overflow_is_explicit(self):
        data=brief(sections=[{'title':'长单元格','table':{'headers':['A','B','C'],'rows':[['长文字'*150,'B','C']]}}])
        with self.assertRaises(LayoutError): generate_html_deck(create_presentation(data))

    def test_mixed_evidence_gets_compatible_pages(self):
        data=brief(sections=[{'title':'项目进展','body':'客户仍在试用。',
            'cards':[{'title':'交接','desc':'补齐归档资料。'}],
            'metrics':[{'value':'8','label':'参与人数'}],
            'table':{'headers':['状态'],'rows':[['待反馈']]}}])
        for mode in ('conservative','moderate','free'):
            deck=create_presentation(data,mode=mode)
            output=generate_html_deck(deck)
            for fact in ('客户仍在试用。','补齐归档资料。','参与人数','待反馈'):
                self.assertIn(fact,output)

    def test_invalid_data_errors(self):
        invalid=[brief(sections=[]),brief(mode='unknown'),brief(style_id='not-a-style'),brief(sections=[{'title':'A','chart':{'categories':['x'],'series':[{'name':'a','values':[math.nan]}]}}]),brief(sections=[{'title':'A','table':{'headers':['x','y'],'rows':[[1]]}}])]
        for item in invalid:
            with self.assertRaises(ValueError): create_presentation(item)

    def test_roundtrip_preserves_every_field(self):
        deck=create_presentation(json.loads((ROOT/'examples/product-brief.json').read_text()))
        self.assertEqual(Presentation.from_dict(deck.to_dict()).to_dict(),deck.to_dict())

class TestExports(unittest.TestCase):
    def test_chinese_punctuation_and_short_line_wrapping(self):
        text='这里是一段中文说明，让句号和逗号跟随前文。'
        lines=wrap_text(text,10)
        self.assertEqual(''.join(lines),text)
        self.assertFalse(any(line.startswith(('，','。')) for line in lines))
        self.assertEqual(''.join(wrap_text('把分散资料整理成可共享的工作笔记',17)),'把分散资料整理成可共享的工作笔记')

    def test_edited_source_cannot_inject_html_through_theme(self):
        deck=create_presentation(brief())
        deck.theme.bg_color='red"><script>alert(1)</script>'
        with self.assertRaises(LayoutError): generate_html_deck(deck)

    def test_html_escapes_user_data_and_is_offline(self):
        deck=create_presentation(brief(title='<script>alert(1)</script>'))
        text=generate_html_deck(deck)
        self.assertIn('&lt;script&gt;',text)
        self.assertNotIn('<script>alert(1)</script>',text)
        self.assertNotIn('gstatic.com',text)
        self.assertNotIn('src="http',text)

    def test_pptx_editable_evidence_and_notes(self):
        from pptx import Presentation as PptxPresentation
        deck=create_presentation(json.loads((ROOT/'examples/product-brief.json').read_text()))
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'deck.pptx'
            self.assertTrue(generate_pptx_deck(deck,path))
            exported=PptxPresentation(path)
            self.assertEqual(len(exported.slides),len(deck.slides))
            self.assertTrue(any(s.has_chart for p in exported.slides for s in p.shapes))
            self.assertTrue(any(s.has_table for p in exported.slides for s in p.shapes))
            texts='\n'.join(s.text for p in exported.slides for s in p.shapes if s.has_text_frame)
            for field in ('资料归档','版本记录','保留修改时间和修改说明。'):
                self.assertIn(field,texts.replace('\n',''))
            notes='\n'.join(p.notes_slide.notes_text_frame.text for p in exported.slides)
            self.assertIn('示例产品资料，第 3 节',notes)
            with zipfile.ZipFile(path) as archive:
                self.assertTrue(any(p.startswith('ppt/embeddings/') for p in archive.namelist()))

    def test_markdown_source_changes_output(self):
        with tempfile.TemporaryDirectory() as directory:
            p=Path(directory)/'source.md';p.write_text('# 培训资料\n\n## 步骤\n\n唯一输入事实 ABC123。',encoding='utf-8')
            data=load_brief([p],'新同事培训')
            deck=create_presentation(data)
            self.assertIn('唯一输入事实 ABC123',generate_html_deck(deck))
            self.assertEqual(deck.scenario_id,'training_deck')

    def test_docx_text_extraction(self):
        with tempfile.TemporaryDirectory() as directory:
            p=Path(directory)/'source.docx'
            with zipfile.ZipFile(p,'w') as z:
                z.writestr('word/document.xml','<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:body><w:p><w:r><w:t>原始资料 42</w:t></w:r></w:p></w:body></w:document>')
            self.assertEqual(read_material(p)['text'],'原始资料 42')

    def test_webp_is_embedded_in_native_pptx(self):
        from PIL import Image
        from pptx import Presentation as PptxPresentation
        with tempfile.TemporaryDirectory() as directory:
            source=Path(directory)/'sample.webp'
            Image.new('RGB',(80,40),'#123456').save(source)
            deck=create_presentation(brief(sections=[{'title':'用户图片','image_url':str(source)}]))
            target=Path(directory)/'image.pptx'
            generate_pptx_deck(deck,target)
            exported=PptxPresentation(target)
            pictures=[s for p in exported.slides for s in p.shapes if s.shape_type == 13]
            self.assertEqual(len(pictures),1)
            self.assertEqual(pictures[0].image.size,(80,40))

    def test_prompt_matches_actual_skill(self):
        from prettyppt.prompts.master_prompt import get_master_prompt
        self.assertEqual((ROOT/'SKILL.md').read_text(),(ROOT/'AGENT_SKILL.md').read_text())
        self.assertIn('默认自动选模板、适度参考、按内容决定页数',get_master_prompt())
        self.assertNotIn('5 页标准黄金骨架',get_master_prompt())

if __name__=='__main__': unittest.main()
