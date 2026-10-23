# 其他 AI 工具：下载、安装与使用

核对日期：2026-10-23。以下安装入口依据各工具官方文档整理；本技能尚未在每个客户端完成端到端实测。软件会更新，若界面有变化，以所链接的官方说明和当前界面为准。

## 1. 下载技能

点击 **[下载单技能 ZIP：high-school-math-feedback-v1.1.0.zip](https://raw.githubusercontent.com/LBuYi/high-school-math-feedback/main/downloads/high-school-math-feedback-v1.1.0.zip)**。

如果浏览器只显示或预览文件，请使用保存/下载功能，保留 `.zip` 后缀。也可以打开[下载目录](../downloads)，选择 ZIP 后点下载原始文件。不要把网页另存为 HTML 再改成 ZIP。

这个 ZIP 里只有一个技能文件夹，打开后应看到：

```text
high-school-math-feedback/
├── SKILL.md
├── requirements.txt
├── agents/
├── references/
├── scripts/
├── assets/
└── examples/
```

需要解压安装时，复制整个 `high-school-math-feedback` 文件夹，不能只复制 `SKILL.md`。保留原来的文件名和层级。校验值在 [SHA256SUMS.txt](../downloads/SHA256SUMS.txt)。

## 2. 选择自己的工具

### Claude 网页端／有 Skills 入口的客户端

1. 在 `Settings → Capabilities` 开启 `Code execution and file creation`。
2. 进入 `Customize → Skills`，点击 `+ → Create skill → Upload a skill`。
3. 上传上面的**单技能 ZIP**，然后启用该技能。
4. 开一个新对话，上传原题、学生作答和批改，使用下文的首次运行指令。

如果上传入口缺失，检查账号或组织的 Skills 权限；不要把“聊天里发了一个 ZIP”当成已经安装。完整仓库 ZIP 目录更深，不用于这一步。入口与 ZIP 结构依据 [Claude 使用说明](https://support.claude.com/en/articles/12512180-use-skills-in-claude)和[技能打包说明](https://support.claude.com/en/articles/12512198-how-to-create-custom-skills)。

### Claude Code 本地项目

1. 解压单技能 ZIP。
2. 在准备处理材料的项目文件夹中创建 `.claude/skills/`，把完整技能文件夹放进去。
3. 确认路径是 `项目/.claude/skills/high-school-math-feedback/SKILL.md`。
4. 在这个项目中启动 Claude Code，输入 `/high-school-math-feedback`，再附上任务要求；也可以明确要求使用该技能。

希望各本地项目都能使用时，可放到 `~/.claude/skills/high-school-math-feedback/`。`~` 指当前用户主目录。这里说的是本地会话；云端会话需要按其自己的技能加载规则设置。[Claude Code 官方说明](https://code.claude.com/docs/en/skills)

### Cursor 本地项目

1. 用 Cursor 打开准备处理材料的文件夹，使用 Agent。
2. 把解压后的完整技能文件夹放到 `项目/.cursor/skills/`。
3. 确认路径是 `项目/.cursor/skills/high-school-math-feedback/SKILL.md`。
4. 重新打开项目或开始新会话，在 Agent 输入 `/` 并选择 `high-school-math-feedback`，再说明本次材料和交付。

本仓库是独立技能包，按文件夹方式安装。Cursor 的“From GitHub Repository”插件导入另需 marketplace 配置，本仓库目前不含该配置。[Cursor 官方说明](https://cursor.com/docs/skills)

### Gemini CLI

已经安装 Gemini CLI 的用户，可在终端执行：

```text
gemini skills install https://github.com/LBuYi/high-school-math-feedback.git --path skills/high-school-math-feedback
gemini skills list --all
```

查看安装提示后完成确认，列表中应出现 `high-school-math-feedback`。进入材料所在工作目录，开启会话并明确要求使用该技能。这个命令用于 Gemini CLI，不能当成 Gemini 网页聊天中的安装命令。[Gemini CLI 官方说明](https://geminicli.com/docs/cli/skills/)

### 没有 Skills 入口的聊天工具

可以把它作为本次会话的工作说明使用，具体取决于该工具能否读附件：

1. 解压技能包，上传 `SKILL.md` 和 `references/` 中的 Markdown 文件；如果该工具明确支持解压 ZIP，也可以上传完整包并让它先列出读到的文件。
2. 要求它先读 `SKILL.md`，再按任务读取相应参考文件；随后上传学生材料。
3. 使用下文首次运行指令。新会话不一定保留这些规则，需要重新附上。

有文件阅读能力，只代表可以参考流程。没有 Python 执行、联网或文件导出能力时，只能完成对应范围的分析和草稿；不能把它说成已经跑过 SymPy、查阅过组卷网或生成了 PDF。需要完整交付时，把源稿和待完成项转到具备这些能力的环境继续处理。

## 3. 准备学生材料

第一次建议只放一名学生的一次测试，确认流程能跑通后再扩大批次。每批准备：

- 原题：题干、图形、选项、题号完整。
- 学生完整作答：不要只给最后答案，照片要能看清过程。
- 教师批改：有参考答案时一并提供。
- 简短说明：年级、学到的章节、学生代号、需要的输出、可用训练时间。

本地工具可以这样建工作目录，和技能文件夹分开存放：

```text
数学反馈工作区/
├── 本次材料/
│   ├── 原题.pdf
│   ├── 学生A作答.pdf
│   └── 教师批改.pdf
└── 本次输出/
```

如果作答和批改在同一份 PDF 中，注明即可，不必拆成两个文件。涉及多名学生时先核对身份和页码，可用代号；不要把真实材料提交到公开技能仓库。

## 4. 首次运行：复制这段话

```text
请使用 high-school-math-feedback 技能，处理我提供的原题、学生完整作答和教师批改。

先确认已读到 SKILL.md 和相关参考文件，并实际检查：
1. 能否看清 PDF、照片和学生的解题过程；
2. 能否执行 Python 和 SymPy；
3. 能否打开并核读组卷网的题目；
4. 能否生成中文数学 PDF，并将每页渲染出来检查。
缺少能力时，先完成不受影响的部分，明确留下哪些步骤待做，不把未执行说成已完成。

本次学生：【代号或姓名】；年级与章节：【填写】。
材料位置：【已上传附件，或本地文件夹】。
训练时间：【填写；没有明确限制也可说明】。
输出位置：【本次输出文件夹，或当前对话可下载文件】。
页眉左侧：【学校／机构名称】；右侧：针对补充训练。

请根据真实作答找出主要问题，不预设学生一定粗心或基础差。
反馈直接写给学生，像老师平时说话，具体指出问题，说明课下怎么做，适度督促。
新增题目先参考能实际核读的组卷网近期题或经典题，记录来源和适配理由。
题量按训练目标和负荷安排，不固定十题。题目前提供必要知识和解题切入点，标题简洁。
用高中规范步骤写详细解析；用 SymPy 核验适用结论，必要时配数学图。
分别输出：反馈 TXT、学生训练 PDF、学生解析 PDF、独立复测 PDF、教师答案与核对卡。
学生材料中不要出现内部诊断、审核记录、题源映射等教师用语，也不要提前放复测答案。
```

组卷网要求登录时：如果工具有可以接管的浏览器，由老师在该浏览器完成登录；只有搜索工具时，改用能读取的公开题或老师提供的题。技能本身不带网站账号，也不会让不同 AI 工具自动共享登录状态。

## 5. 老师检查、发放和复测

先用核对卡查看学生身份、原题题号、主要错因和待确认处，再核对训练是否对准问题、解析是否完整、符号和图形是否清楚。发现问题可以直接要求修订，例如：

```text
第3题与学生的问题不匹配，请重新参考组卷网选题；第5题解析补上分类讨论依据。
反馈第二段太像模板，结合学生具体作答重写。保留旧版，输出修订版，并同步检查题答编号。
```

先给学生反馈和训练，独立尝试后再提供训练解析。按约定日期收回独立复测的完整作答，并输入：

```text
这是学生的复测作答。请关联上一轮目标逐步核对，说明哪些问题已经改善、哪些仍需练习。
证据不够时标为待确认，不凭一次正确答案直接认定完全掌握，再安排下一轮。
```

## 6. 常见问题

| 情况 | 处理方式 |
| --- | --- |
| 安装后找不到技能 | 检查 `SKILL.md` 是否就在技能文件夹下，避免重复嵌套；再查看工具的技能列表或重开会话 |
| AI 只说“可以”，没有实际读材料 | 要求它列出已读文件、页码和学生身份，并从一题开始展示证据核对 |
| 解析只有答案 | 要求补全公式依据、条件、分类讨论和结论，保持高中答题规范 |
| 无法访问组卷网 | 使用能核读的公开页面或自行提供题目；不要补写虚假的题源 |
| 缺 SymPy 或 PDF 环境 | 让工具检测依赖，按当前权限补齐；否则交付源稿和未完成项 |
| PDF 中文乱码、缺符号、挤出页边 | 检查中文字体、TeX 依赖和逐页渲染结果，修好后再交付 |

原脚本默认使用 XeLaTeX 和 Poppler。其他宿主可采用可用的等效编译、渲染工具，但必须实际核验输出，不能仅因为系统自带“生成文件”功能就省略审校。
