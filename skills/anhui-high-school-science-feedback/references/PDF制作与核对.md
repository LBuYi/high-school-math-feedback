# PDF 制作与核对

先按[输出内容与排版规范](输出内容与排版规范.md)逐卷列出文件、标题和题号。各卷内部让训练与解析共用题面。家长反馈 PDF 用定稿 TXT 直接编译。TXT 用 UTF-8，两个自然段间空一行。

## 学生解析的答题规范

用“解”或“证明”交代起笔。关键式子的前后写必要依据和连接语，一问一答。结尾明确写出所求、存在性、单位或结论。数学交代定义域、分类、端点、取等和范围。物理写研究对象、过程、正方向、所用规律、带单位的计算及方向。化学写有关状态、反应条件、粒子依据和守恒。生物学写明比较组、指标、数据关系和该条件下的结论。详略根据题目，学生能用已学方法读通每一步。

## 在当前设备生成 PDF

1. 复制 [A4 模板](../assets/preamble.tex)到本批工作目录，训练和解析共用题面。栏目单独一行，可用 `\parttitle{原错题}` 等。正文 12 pt，基线 18 pt。多问可用 `\subquestion` 分行，整题只用一次 `\questionwithspace` 或在题后用一次 `\workarea`。解析各问用 `\solutionpart` 启行。按[小问排印](handout-typesetting.md)核对关键推导和分页。
2. 有 XeLaTeX、Poppler 的 `pdftoppm` 和 Python `pypdf` 时，用本包沿用数学 v1.4.12 的[编译脚本](../scripts/compile_pdf.py)。每份输出用新的目录，`--student`填页内姓名或示例标签。可用 `--engine`、`--renderer`指定本机可执行文件。只编译自己写的可信 TeX 源。

```text
python <技能目录>/scripts/compile_pdf.py training.tex --out-dir build-training --kind training --student 示例学生 --expect-a4 --complete-feedback
python <技能目录>/scripts/compile_pdf.py solutions.tex --out-dir build-solutions --kind student_solutions --student 示例学生 --expect-a4 --complete-feedback
python <技能目录>/scripts/compile_pdf.py 家长反馈.txt --out-dir build-family --kind family_feedback --student 示例学生 --expect-a4
```

3. 当前设备缺 XeLaTeX 时，可使用本机已有的 PDF 工具或导出功能。用浏览器时，将可信静态 HTML 的打印样式设为 `@page { size: A4; margin: 20mm; }`，用该浏览器能正确显示的 MathML 或公式图，将本机可用中文字体用于正文。通过“打印 → 另存为 PDF”导出，关闭浏览器自带的日期和网址页眉页脚。再按本节逐组检查公式、栏目、留白和实际页图。仍无法生成时写清具体缺项和已完成的内容。
4. 逐页查看 PDF 渲染页。核对各卷分别成对、专题与考法相符、学生册没有原答及待核提示，再按[讲义用语与排印](handout-typesetting.md)看文字、关系符号、上下标、图表单位和分页。多问自成行，作答留白与各问书写量相符。原题缺失、只出独立练习时可省略编译命令的完全栏目选项，仍核对每道练习的配套解析。家长 PDF 按 TXT 核对正文。脚本报告的目检状态按实际结果填写。

四科以实际训练或复测 PDF 及其解析做[逐题验收](item-release-review.md)。数学、物理按[配图要求](paper-reference-and-figures.md)区分题面图与解题图。只给得数、关键推理缺漏或必要图不清时先修订，化学概念另按[专项核验](化学概念题验收.md)执行。
