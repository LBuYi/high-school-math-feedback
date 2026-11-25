# 同卷多人的本地批量处理

先确认原卷和解析版本，再逐份核看学生作答和批改。共用原题、完整解答和选题依据。每个孩子的作答、待核对处、练习与家长稿单独登记。手写核读见[手写页核读](handwriting-review.md)，选题见[题源](question-research.md)，家长稿见[老师发给家长的学习反馈](family-feedback.md)。

## 批次记录

在学生材料所在工作区保存一份 JSON，文件由老师或 Agent 核读和整理后写入。需要纯反馈时可直接依据作答写，批量脚本用于生成完整分册和记录增量。

| 字段 | 内容 |
| --- | --- |
| `schema_version`、`batch_id` | 当前结构版本 1、固定批次编号 |
| `exam` | `version`、原卷 `paper` 和原解析 `key` 的文件相对路径和 SHA-256、`items` 中的原题。题目编号用 Q1、Q2 等。 |
| `bank` | 练习和复测按编号保存 `prompt`、`solution`、`level`、`goal`、`source`。题干和解答是已核对的 TeX 片段，写明适用分支和边界。 |
| 原题和题库的核验字段 | `checked_content_sha256` 是 `prompt + "\n" + solution` 按 UTF-8 编码的 SHA-256。先独立验题再登记。改题干或解答需重验。 |
| `students` | 数组。每人有唯一 `id` 如 S01、`name`、`pairing`、`exam_version`、`card` 的文件信息和 `page`。只有卷卡已配对且版本相符的学生进入生成。 |
| 每人的作答和计划 | `answers` 按原题编号记录 `response`、`mark`、`process`，旧记录的 `student_line` 可保留，但不输出在学生页。`groups` 每组有 `original`、`title`、`keypoints`、有顺序的 `practice`。`retest` 为有顺序的复测题编号。 |
| 每人的反馈和核对 | `feedback` 为家长可转发正文，`focus`、`criterion`、`estimated_time`、`teaching_status` 为教师所需文字。`timing.before` 和 `timing.after` 记录实际审核用时，未发生则为 null。 |
| 待核对点 | 批次 `pending_class` 与学生 `pending` 可记录缺材料和模糊答法。补交资料通过 `add-page` 登记。 |

每组可填 `redo_space` 调整原题作答区，采用 `32mm` 一类长度，未填留 32 mm。`redo_note` 可放经核对的简短易错提醒，按可信 TeX 输入，不填学生错答或逐步提示。重做题可能跨页时在小问处分开编排。现有数据不必迁移，旧 `student_line` 仍留原记录。

多问题可在已有 `prompt` 字段内先写共用题干，再用 `\subquestion{1}{题干}` 等顺序分行。题干内不加作答区，由原有整题留白字段控制。对应 `solution` 使用 `\solutionpart{1}` 等分问，论证用正常段落与独立公式。原字段和核验摘要结构不变。批量生成后逐页核对编号、顺序和分页。

源文件项使用 `path` 和 `sha256`。所有 `path` 相对于工作区。题干、解析和段首要点只使用核读过的本地 TeX 片段。转录来自图像或人工核对，没有过程的选项只记录所见。

## 命令

从工作目录运行，`SKILL_DIR` 代表解压后的技能目录。默认工作区是记录所在文件夹，需要上级材料时显式提供 `--workspace`。PDF 生成复用技能自带模板和[编译检查](pdf-production.md)。先用 `inspect_runtime.py` 检查当前设备。

```text
python SKILL_DIR/scripts/batch.py check 批次记录.json
python SKILL_DIR/scripts/batch.py build 批次记录.json
python SKILL_DIR/scripts/batch.py add-page 批次记录.json --student S01 --question Q1 --page 作答补页.png --note "第1题补页"
```

`check` 显示待重建、可复用和待核对。`build` 输出独立的学生训练、学生解析、复测和教师答案，以及家长 TXT 和教师核对卡。成品写入新版本目录，自动检查通过后再更新 `交付/当前交付.json`。旧清单和旧记录快照可回查，教师仍须看实际 PDF 页面。更改文字时复用已通过的 PDF，换题时重建引用题目的册子。一张补页先进入待核对，确认有新证据再更新对应训练与稿件。

## 回收复测

实际布置时在学生记录的 `assigned_retest` 写入 `sha256`、`question_ids`，取自该次交付清单中本人的复测条目。逐题提交可追加 `retest_attempts`，每条包含 `paper_sha256`、`question`、实际日期 `date`、`answer`、`step`、`independence` 和作答原件 `source`。校验本题属于当时的复测版本，教师卡据实显示已交题和仍待交题。只有答案时可以注明关键过程待补。按[复测规则](retest-and-delivery.md)判断学习进展。
