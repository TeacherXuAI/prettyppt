# PrettyPPT brief 和自由布局

顶层 `title`、非空 `sections` 必填。`purpose`、`audience`、`subtitle` 建议填写。默认 `scenario_id: auto`、`style_id: auto`、`mode: moderate`、`cover: true`。Agent 负责从原始资料提炼成 brief，CLI 负责可复现的规划与渲染。

```json
{
  "title": "一页笔记产品介绍",
  "purpose": "向潜在客户介绍产品和使用方式",
  "audience": "客户团队负责人",
  "subtitle": "把工作资料整理成可共享的笔记",
  "sections": [
    {"title": "客户当前的问题", "role": "context", "body": "项目资料分散，交接时需要重复解释。", "bullets": ["文档分散在不同位置", "最新结论难以确认"], "sources": ["产品资料.docx 第 2 节"]},
    {"title": "资料整理流程", "role": "process", "cards": [{"title": "收集", "desc": "上传项目原始资料。"}, {"title": "整理", "desc": "按主题归类并保留原文链接。"}, {"title": "共享", "desc": "把同一份笔记提供给项目成员。"}], "sources": ["产品资料.docx 第 3 节"]}
  ]
}
```

每节：

- `title` 必填，尽量短而准确。`role` 可为 `context / solution / evidence / comparison / process / business / closing`，表示叙事用途，不强制插入对应内容。
- `body` 字符串，`bullets` 字符串数组。长段落会分页，内容不会用省略号截掉。过长标题需由 Agent 改写。
- `cards`: `[{"title":"名称","desc":"说明","tag":"可选标签","metric":"可选原文数值"}]`。用于并列内容或步骤。
- `metrics`: `[{"value":"76%","label":"完成率","delta":"较上期增加 5 个百分点","subtext":"截至 6 月"}]`。value 保留单位，均来自原始资料。
- `table`: `{"headers":["项目","当前值"],"rows":[["样本量",128],["完成率","76%"]]}`。每页自动拆分行数，支持 1–6 列；过宽或单元格过长须由 Agent 重新组织。
- `chart`: `{"kind":"column","unit":"万元","categories":["一月","二月"],"series":[{"name":"收入","values":[20,25]}]}`。kind 为 bar/column/line，支持 1–3 组数值。自动按类别分页，保留所有数据。
- `image_url` 本地图片路径。相对路径相对于 brief 文件目录；PNG/JPEG/GIF/WebP。图片按比例完整显示。
- `sources` 字符串数组，`notes` 字符串，进入 PPTX 备注和源文件，不自动出现在观众正文。
- `mode` 可为 `conservative / moderate / free`。`design`、`layout` 和 `elements` 自定义仅用于 free。其他模式遇到自定义元素会明确报错。

## 自由档

单节可指定一个已实现布局：

- 文字：statement, report, split, editorial, brief, impact, analysis, annotation
- 并列内容：spotlight, ledger, feature_columns, editorial_columns, numbered_rows, contrast, matrix, quiet_columns
- 步骤：timeline, steps, roadmap
- 数字：hero_metric, metric_ledger, metric_columns, metric_editorial, metric_rows, metric_impact, metric_quiet
- 证据：table, chart, image

全稿可提供 `design` 覆盖 `bg_color / text_color / accent_color / secondary_accent`，颜色为 `#RRGGBB`。整体字体由主模板选择，默认中文使用 PingFang SC，宋体风格用 Songti SC；其他设备需有可替代中文字体。

新构图使用 `elements`。画布 1440×810，常用安全区 x=88..1352、y=80..714，页码位于底部。每个元素包含 `kind, x, y, w, h`。文本另有 `text, size`（像素）、`color, bold, align`，kind 可为 text/line/rect/image/table/chart。image 使用本地 `path`，table/chart 使用 `data`，与上方格式相同。布局器检查边界和文字容量，文字保持可编辑。

```json
{"title":"本期观察","elements":[
  {"kind":"text","x":90,"y":110,"w":1200,"h":100,"size":56,"bold":true,"text":"客户更需要清楚的交接"},
  {"kind":"text","x":90,"y":330,"w":520,"h":260,"size":35,"text":"让接手的人找到资料，也理解做出选择的原因。"},
  {"kind":"text","x":800,"y":420,"w":500,"h":180,"size":27,"text":"来自用户访谈的观察，需要进一步用试用结果验证。"}
]}
```

自由布局不会自动执行代码、访问远程 URL 或将用户资料发送给模型服务。自定义元素必须带实际内容，不能只提供“做漂亮一些”的布局描述。

## 指定页数与检查

默认由实际资料量决定页数。`--pages N` 是严格的页数断言，包含封面。N=1 默认不加封面。若实际需要更多页，CLI 给出所需页数并退出；Agent 应编辑 brief 的段落与结构后重试。不要删除用户要求保留的证据。

最终 `.deck.json` 是已分页的可编辑结构，可用 `prettyppt render` 重导出。生成 HTML 后实际打开逐页看，PPTX 用可用的演示文稿渲染器检查。跨平台字体与渲染器可能造成轻微差异。
