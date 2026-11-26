# 高中错题反馈与针对训练

这里提供合肥高中理科错题反馈和通用高中数学错题反馈两套技能。提供原题、学生完整作答和教师批改后，按证据整理错因，写接近老师日常说话方式的反馈，参考组卷网设计针对训练，按原卷分别生成学生训练与逐问解析 PDF。

本仓库包含工作流程、教师口吻样本、数学核验脚本和排版模板。它由支持技能、文件读写、Python 和网页访问的 AI 工具执行；AI 服务、组卷网账号和本机编译环境需自行准备。

## 在另一台 Codex 安装或更新

把下面这段发给另一台设备上的 Codex。

~~~text
$skill-installer 请用安装器从 LBuYi/high-school-math-feedback 的 main 分支安装两个技能。
路径是 skills/anhui-high-school-science-feedback 和 skills/high-school-math-feedback。
如果已安装同名旧版，只备份这两个旧技能目录到技能扫描范围之外，再安装。不要改动其他技能。
确认 SKILL.md 的 metadata.version 分别是 1.0.12 和 1.4.17，并报告安装路径。
~~~

安装后新开会话。合肥数学、物理、化学、生物学（含单科）使用 $anhui-high-school-science-feedback，其他高中数学可用 $high-school-math-feedback。

## 合肥高中理科 v1.0.12

适用合肥市普通高中数学、物理、化学、生物学的错题反馈。根据本校教材与进度，制作家长反馈、学生分层训练和逐问规范解析。需要配练时先查课程项目的本地题库，再自行打开组卷网核读需补的题。独立验题后把优质题留在课程项目。

原错题后紧跟对应练习，卷尾综合按需设置。先独立验题，再审是否确实对应失分步骤。训练少提示，解析逐问写清，组末分点总结解题技巧。合肥家长稿正文、TXT 和 PDF 同文，学生训练、解析按原卷分册。复测另用未见的新题。

[四科技能入口](skills/anhui-high-school-science-feedback/SKILL.md) · [完整四科 SOP](skills/anhui-high-school-science-feedback/references/hefei-feedback-sop.md) · [学生解析答题规范](skills/anhui-high-school-science-feedback/references/学生解析答题规范.md) · [本地题库维护](skills/anhui-high-school-science-feedback/references/本地题库维护.md) · [解析配图](skills/anhui-high-school-science-feedback/references/solution-visuals.md)

[下载四科单技能 ZIP（v1.0.12）](downloads/anhui-high-school-science-feedback-v1.0.12.zip)

## 通用高中数学 v1.4.17


**其他 AI 工具的使用者，从这里开始：**

- [下载单技能 ZIP（v1.4.17）](https://raw.githubusercontent.com/LBuYi/high-school-math-feedback/main/downloads/high-school-math-feedback-v1.4.17.zip)：适合 Claude 上传，或解压后安装到其他工具。
- [其他 AI 工具的安装与操作流程](docs/USAGE-OTHER-AI.md)：包含 Claude、Claude Code、Cursor、Gemini CLI，以及无 Skills 入口的备用用法。
- [下载完整仓库](https://github.com/LBuYi/high-school-math-feedback/archive/refs/heads/main.zip)：包含说明、源码和下载包。完整仓库 ZIP 多了一层目录，不要直接当作单技能包上传。

Codex 安装使用上面的两技能安装提示，也可只安装通用数学路径。

其他工具的安装步骤已根据官方文档核对，见[操作指南](docs/USAGE-OTHER-AI.md)。尚未在这些客户端逐一完成端到端实测；导入成功后仍需检查网页访问、命令执行和文件导出能力。

v1.4.17 支持原错题与练习同组、整题统一答题区、可选卷尾综合和逐问分行解析。批量脚本将知识点和技巧放在解析册，不在训练页提前出现。按所考的区间、端点或分类配数学图象，正文仍写全推导。单技能包含虚构示例与本地脚本。 [另一台设备安装](skills/high-school-math-feedback/references/install-on-another-device.md) · [批量处理](skills/high-school-math-feedback/references/batch-processing.md)

## 第一次使用

把材料放到一个独立工作文件夹，尽量按学生和测试批次分类。原题、作答和批改应能一一对应，照片中的题号、公式、姓名要清楚；有教师参考答案时一起提供。

可以直接复制这段请求，替换括号中的内容：

```text
使用 $high-school-math-feedback，处理【材料文件夹】中【学生或班级】的【测试批次】。
根据原题、完整作答和教师批改分析，区分已经看到的错误和仍待确认的原因。
默认写一段老师发给家长的反馈，孩子也读得懂。结合具体作答说明问题和接下来的练法。
参考能实际读取的组卷网近期题或经典题，按学生问题设计训练，题量由训练目标决定。
原错题后接对应练习，综合题按需放卷尾。小问顺序分行，整题统一留白，不先给解题提示。解析写全高中规范步骤，配图时引用图上信息，各组末分点写解题技巧。
用 SymPy 核验适用的数学结论，必要时配数学图，并逐页检查 PDF 排版。
分别输出反馈 TXT、学生训练 PDF、学生解析 PDF、独立复测 PDF、教师答案与核对卡。
页眉左侧为【学校或机构名称】，右侧为【针对补充训练】。
```

只要反馈时可以简化为：

```text
使用 $high-school-math-feedback，只核读这批材料并写学生反馈，暂不出训练。
直接写给学生。具体指出问题，说明课下怎么练、为什么要这样做；不能从一个错答推断学习态度。
```

想学习自己的说话方式时：

```text
使用 $high-school-math-feedback，学习下面几段我自己写的反馈，提炼叙述方式。
保留当前学生的真实题号、错因和判断程度，只调整表达，不套用样本中的学生情况。
【粘贴已去除学生身份信息的反馈样本】
```

## 会得到什么

| 文件 | 内容与使用时机 |
| --- | --- |
| 反馈 TXT | 问题、具体例子、课下做法和必要的提醒，可直接复制 |
| 学生训练 PDF | 原错题重做、对应练习、按需卷尾综合和整题留白 |
| 学生解析 PDF | 与训练对应的题目、知识点、逐问解答和组末技巧，尝试后提供 |
| 独立复测 PDF | 不带提示的新题，用于核对是否能独立完成 |
| 教师答案与核对卡 | 训练和复测答案、证据、疑点及关键检查步骤 |

要求“打包学生资料”时，默认每人仅放训练、学生解析和反馈，不混入教师诊断或复测。题量不固定为十题；按实际问题、覆盖范围和负荷安排，必要时分次完成。复测没有交回前，不把“已生成练习”写成“已经掌握”。

## 运行环境

只改反馈不必安装整套排版软件。开始前让 AI 运行技能内的 `scripts/inspect_runtime.py`，按本次任务补齐能力。

| 工作 | 需要的能力 |
| --- | --- |
| 读取材料 | PDF/图片阅读能力；扫描件仍需逐页核读，不能只相信 OCR |
| 精确数学核验 | Python 与 SymPy |
| PDF 检查、打包 | Python 与 pypdf |
| 生成中文数学 PDF | XeLaTeX、ctex、中文字体；模板支持常见 Windows 字体和 Fandol 字体 |
| 渲染 PDF 检查排版 | Poppler 的 pdftoppm，或宿主提供的等效工具 |
| 数学图 | 按需使用 TikZ/PGF 或 Matplotlib |
| 参考组卷网 | 可用的浏览器/检索工具和相应访问权限 |

完整制作所需的 Python 基础依赖在 [requirements.txt](skills/high-school-math-feedback/requirements.txt)。建议在独立虚拟环境中安装：

```text
python -m pip install -r skills/high-school-math-feedback/requirements.txt
python skills/high-school-math-feedback/scripts/inspect_runtime.py
```

以上相对路径以仓库根目录为起点；通过安装器安装后，请让 AI 定位实际技能目录。本版已在 Windows、Python 3.12、SymPy 1.14.0、pypdf 6.21.2 环境验证过相关脚本；其他平台的编译器路径和字体仍需检查。MarkItDown、Matplotlib、Pillow 是按任务选择的辅助工具，不要求全部安装。

## 组卷网如何使用

技能要求核读实际题目，并记录来源、考点、条件、难度及变式关系。登录受限时由老师自行完成登录，或使用能公开读取的题目；不会把搜索摘要或未读过的页面说成已核对的题源。

仓库不附带商业题库、网站登录信息或下载权限。参考网站的能力由运行技能的 AI 工具提供；技能不会自动登录或批量抓取题库。老师也可以提供自己有权使用的题目。

## 示例与文件说明

- [虚构案例](skills/high-school-math-feedback/examples/demo.md)：演示证据、反馈和规范解析的区别；示例题为自编，不冒称来源于组卷网。
- [示例核验脚本](skills/high-school-math-feedback/examples/verify_demo.py)：精确核验示例不等式的解集。
- [主技能](skills/high-school-math-feedback/SKILL.md)：入口与范围判断。
- `references/`：材料研读、教师口吻、题源适配、数学核验、PDF 和复测归档六类工作说明。
- `scripts/`：运行检测、数学核验记录、PDF 编译审校、学生资料打包。
- `assets/`：LaTeX 版式和 JSON 清单模板。

在仓库根目录运行虚构示例：

```text
python skills/high-school-math-feedback/examples/verify_demo.py
```

运行结果只覆盖示例脚本中列出的结论。符号计算通过不能代替定义域检查、证明完整性、教师判断和 PDF 目检。

## 使用边界

技能目录只放通用方法、模板和脚本。真实学生资料与生成结果放到独立工作文件夹，不提交到公开仓库；向 Issue 提问时使用去除身份信息的例子。`.gitignore` 提供常见产物过滤，但不能代替提交前检查。

内置脚本不上传学生资料，也不自动安装软件；AI 宿主对上传材料的处理方式仍按该服务自身规则执行。技能可以减少重复制作工作，教师仍需核对原始证据、题目适配和最终交付内容。

许可证待仓库作者确认。确认前，本仓库不额外授予修改、再分发或商用许可。
