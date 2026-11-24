# PDF 制作与核对

先按[输出内容与排版规范](输出内容与排版规范.md)确定文件、栏目和字体。家长反馈 PDF 用定稿 TXT 直接编译。TXT 用 UTF-8，两个自然段间空一行。

## 学生解析的答题规范

用“解”或“证明”交代起笔。关键式子的前后写必要依据和连接语，一问一答。结尾明确写出所求、存在性、单位或结论。数学交代定义域、分类、端点、取等和范围。物理写研究对象、过程、正方向、所用规律、带单位的计算及方向。化学写有关状态、反应条件、粒子依据和守恒。生物学写明比较组、指标、数据关系和该条件下的结论。详略根据题目，学生能用已学方法读通每一步。

## 在当前设备生成 PDF

1. 复制 [A4 模板](../assets/preamble.tex)到本批工作目录，训练和解析共用题面。栏目单独一行，可用 `\parttitle{原错题}` 等。正文 12 pt，基线 18 pt。用 `\questionwithspace`按作答量留白。根据需要写必要图、表和数据，避免缩小字体塞页。
2. 有 XeLaTeX、Poppler 的 `pdftoppm` 和 Python `pypdf` 时，用本包沿用数学 v1.4.12 的[编译脚本](../scripts/compile_pdf.py)。每份输出用新的目录，`--student`填页内姓名或示例标签。可用 `--engine`、`--renderer`指定本机可执行文件。只编译自己写的可信 TeX 源。

```text
python <技能目录>/scripts/compile_pdf.py training.tex --out-dir build-training --kind training --student 示例学生 --expect-a4 --complete-feedback
python <技能目录>/scripts/compile_pdf.py solutions.tex --out-dir build-solutions --kind student_solutions --student 示例学生 --expect-a4 --complete-feedback
python <技能目录>/scripts/compile_pdf.py 家长反馈.txt --out-dir build-family --kind family_feedback --student 示例学生 --expect-a4
```

3. 当前设备缺 XeLaTeX 时，可使用本机已有的 PDF 工具或导出功能。用浏览器时，将可信静态 HTML 的打印样式设为 `@page { size: A4; margin: 20mm; }`，用该浏览器能正确显示的 MathML 或公式图，将本机可用中文字体用于正文。通过“打印 → 另存为 PDF”导出，关闭浏览器自带的日期和网址页眉页脚。再按本节逐组检查公式、栏目、留白和实际页图。仍无法生成时写清具体缺项和已完成的内容。
4. 逐页查看本次 PDF 渲染页。核对纸型、字号与字体嵌入、公式负号与上下标、图表单位、题号、题间留白及分页。完整训练册逐组核对知识梳理和方法小结有具体内容。解析对题面重新解题并查所问各项。家长 PDF 的正文按 TXT 核对，回复使用该稿。脚本报告 `visual_status: pending`须按实际目检更新。
