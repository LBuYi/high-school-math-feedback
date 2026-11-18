# 在另一台设备安装

发送通用技能 ZIP，或将已发布的下载链接给对方。解压后应有一层 `high-school-math-feedback` 文件夹，里面直接包含 `SKILL.md`、`references`、`scripts` 与 `assets`。

## Codex

将整份文件夹放入目标项目的 `.agents/skills/` 文件夹。需要在此设备上的多个项目使用时，可放入用户目录的 `.agents/skills/`。Windows 用户目录通常是 `C:\Users\当前Windows用户名`，macOS 和 Linux 可从 `~/.agents/skills` 找到。新开项目对话，在消息中输入 `$high-school-math-feedback` 后说明本轮要求。项目里的学生材料由目标设备单独提供。 [Codex 技能目录](https://learn.chatgpt.com/docs/build-skills#where-codex-loads-local-skills)

## 其他 Agent

使用支持导入 Agent Skills 的入口，按宿主要求选择单技能 ZIP 或解压后的整个文件夹。也可以让工具读取本包的 `SKILL.md` 以及同目录附件，照任务提示执行。核读手写 PDF 需要图像读取能力，自动编译需要可用的 XeLaTeX、渲染器和相关 Python 依赖。不同设备按[能力与替代方式](runtime-and-capabilities.md)核对。

可直接发送下面这句话，再附原卷、学生作答和批改。

> 使用 high-school-math-feedback，核对这批原题、作答和批改。先给老师发家长的反馈文字，按原错因生成学生练习和分开的解析、复测。按本机能力核验数学、纸型和字体。
