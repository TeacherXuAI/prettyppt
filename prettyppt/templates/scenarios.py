"""Scenario metadata only. Real decks never inherit example business metrics."""
_ROWS = [
 ('pitch_deck','Pitch Deck','融资路演','投资交流','客户问题、产品方案、证据与融资用途'),
 ('annual_review','Annual Review','年度汇报','年度复盘','年度结果、目标差距、原因与下一年度安排'),
 ('product_launch','Product Launch','产品发布','产品介绍','使用场景、核心功能、使用流程与体验方式'),
 ('research_report','Research Report','行业研究','研究报告','范围、方法、发现、证据与研究局限'),
 ('strategy_deck','Strategy Deck','战略规划','战略讨论','现状、选项、战略重点、阶段路线与资源'),
 ('brand_proposal','Brand Proposal','品牌提案','品牌与传播','受众、品牌概念、内容体验与执行安排'),
 ('training_deck','Training Deck','培训课件','课程与实操','学习目标、方法、步骤、案例与练习'),
 ('business_review','Business Review','业务评审','经营与交付','本期结果、项目进展、偏差与下期行动'),
 ('keynote_speech','Keynote Speech','大会演讲','演讲与分享','问题、故事、观点、证据与思考'),
 ('portfolio','Portfolio','作品集','作品与经历','个人方向、代表项目、过程、结果与职责'),
]
SCENARIOS = {row[0]:dict(zip(('id','name','name_zh','badge','description'),row)) for row in _ROWS}
