# 现有项目与语言资源的取舍

2026-11-17对照修订。核读的是下列指定文件或章节，未安装、未运行其网站，也未逐篇复核教育技能所列研究。以下为本技能自行整理的实施取舍，不是原项目原文或教学效果验证。

| 参考资料与实际核读范围 | 采用的思路 | 本项目的调整 |
| --- | --- | --- |
| [wrong-question-review的技能正文](https://github.com/jayv29/wrong-question-review-skill/blob/main/wrong-question-review/SKILL.md)：流程、题号映射和反馈更新规则 | 用稳定编号关联原题、练习及历史反馈；先查索引再读相关原件 | 不默认每题三道，不照搬固定复习日期；未报告题目不视为全对，两次自报全对不直接判掌握 |
| [wrong-notebook](https://github.com/wttwins/wrong-notebook/blob/main/README.md)功能说明及[数据结构](https://github.com/wttwins/wrong-notebook/blob/main/prisma/schema.prisma) | 原图、题目、标签与复习记录分开保存，按时间和目标筛选 | 保留实际作答与审核证据，不能仅由掌握等级字段判断能力；不引入其部署与账户系统 |
| [MistakeBook README](https://github.com/Liangbiaoyong/MistakeBook/blob/main/README.md)的录入、复习及存储结构 | 原图留存、每次复习独立事件，索引与原件分开 | 不只在模型自报低置信时核对；关键符号仍回看原图；题库合并不能删除学生重复错误 |
| [作答差距分析](https://github.com/GarethManning/education-agent-skills/blob/main/skills/curriculum-assessment/gap-analysis-from-student-work/SKILL.md)与[错因分析](https://github.com/GarethManning/education-agent-skills/blob/main/skills/self-regulated-learning/error-analysis-protocol/SKILL.md)的输入、分析及限制章节 | 具体正确步骤、目标差距、短问区分候选原因 | 不强制三类错因，不因提示后改对就判粗心，不把单次表现当长期能力或照搬其预计时长 |
| [逐步减少提示](https://github.com/GarethManning/education-agent-skills/blob/main/skills/memory-learning-science/worked-example-fading-designer/SKILL.md)的方法与示例 | 帮助随实际需要提供，最终用无提示新题检查 | 不固定补步骤题数或始终从最后一步开始撤；示例须另算，未核对的例题不进入题库 |
| [Humanizer](https://github.com/blader/humanizer/blob/main/SKILL.md)的工作流程及声音校准；[Humanizer-zh](https://github.com/op7418/Humanizer-zh/blob/main/SKILL.md)的编辑约束、流程和中文表达检查 | 作者样本优先；检查段落结构、重复和事实是否改变 | 不用词语黑名单，不编细节使文字显得具体，不把文风检查说成AI检测结果 |
| [EEF家校沟通指南网页](https://educationendowmentfoundation.org.uk/education-evidence/guidance-reports/supporting-parents)及其[一页建议摘要](https://d2tic4wvo1iusb.cloudfront.net/production/eef-guidance-reports/supporting-parents/EEF_Parental_Engagement_Summary_of_recommendations.pdf)文字 | 信息与孩子本人学习有关，沟通尊重且可回应，家长配合应可行 | 用于适配本项目家长消息，不照搬英国学校场景或声称已验证本项目效果；未完整研读长报告，未完整核验摘要版面图示 |

既有间隔复习和教研方法继续按[诊断与训练](research-informed-feedback.md)、[首轮教研核读](research-reading-notes.md)执行。本次是流程和语言整改，不代表新核读组卷网题面，不替换已有数学题及教师原批。

外部模型的实收意见及采纳记录属于具体项目的评审档案，不随技能混入真实学生材料；通用用法见[外部审阅](external-review.md)。

本次另经用户明确授权，将同一份仅含通用流程与虚构情境的匿名说明分别交给DeepSeek和WorkBuddy，各取得一次文字意见；二者未收到学生卷面、成绩或工程文件。采用其具体描述原答、承认可见正确步骤、降低家长判题负担等建议；不照搬样稿中自行指定最值类型、未确认的辅导计划、强制每条反馈重述复测流程或按词语机械判断的做法。评审建议和重写样例分别审核，多模型一致不等于内容正确。

## 2026-11-18 反馈流程审查

| 核读材料 | 怎样用于本项目 |
| --- | --- |
| [Feedback Quality Analyser](https://github.com/GarethManning/education-agent-skills/blob/main/skills/memory-learning-science/feedback-quality-analyser/SKILL.md) 的核对问题、改写示例和限制 | 检查目标、具体证据和下一步。其改写例出现原始反馈未提供的作答引文，本项目需要原件或已核对的转录才引用学生的话。教师内部可用核对表，家长消息保持自然。 |
| [AI Feedback Design Principles](https://github.com/GarethManning/education-agent-skills/blob/main/skills/ai-learning-science/ai-feedback-design-principles/SKILL.md) 的反馈详略原则与示例 | 可指出应检查的条件，把判断与计算留给孩子。需要讲解时另给例子。把订正和完整解析安排在容易分开的交付环节。 |
| [MathDial 的数据说明](https://github.com/eth-nlped/mathdial/blob/main/README.md)及[示例首条对话](https://github.com/eth-nlped/mathdial/blob/main/data/example.jsonl) | 借鉴按提示前后记录表现。公开示例中，老师在一处混淆一打半和两打半，学生口头认同后仍重复原错法。反馈中的量与术语仍须验算，独立作答用新题检验。来源为教师与模拟学生的对话。 |
| [OATutor 的状态字段说明](https://github.com/CAHLR/OATutor/blob/main/analyzeStudentState-parameters.md)与[题卡源码](https://github.com/CAHLR/OATutor/blob/main/src/components/problem-layout/ProblemCard.js)开头的提示配置 | 借鉴按题记提示和尝试情况。作答结果、目标步骤及独立性分别核对，按老师掌握的实际完成条件记录。 |
| [Eedi 诊断题说明](https://www.eedi.com/data-and-competitions)与[EEF《Developing Independent Learners》的反馈章节](https://educationendowmentfoundation.org.uk/16-19/developing-independent-learners/feedback) | 错选项用于提出候选原因，再让学生说出理由。留出能按反馈行动的机会，用真实订正和变式结果观察效果。EEF 章节的研究对象与本项目人群存在差异，借鉴做法，各批效果跟随实收作答。 |

上述项目及文章用于方法对照。实际改写、分流与数学例子见[反馈审查](feedback-review.md)，材料发放和核对见[复测与交付](retest-and-delivery.md)。
