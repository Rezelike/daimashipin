# 当前上下文

## 项目目标

持续制作「Vibe知识大赏」代码知识视频，让新的 AI 对话从仓库读取已确认的制作要求、当前工作状态和往期经验，避免每期重新口述固定要求。每期仍需确定自己的选题、事实依据和画面方案。

## 已确认的通用要求

以下是便于接手的摘要；完整规则及用户反馈原句以 `.kiro/skills/vibe-knowledge-video/SKILL.md` 为准。

- 默认横屏 1920×1080、30 fps，约 60–75 秒；中文和英文同屏，不配旁白。除非本期另有要求，按 128 BPM 安排节拍；画面事件配音效，不加配乐，画面不随节拍抖动。
- 开头第 0 帧就给出问题和动作；尽早揭示答案。每一步有具体例子，事实和数据要核对来源。最后停在可看清的总结画面，直接结束，不在画面上加点赞、收藏、关注、评论或下期预告。
- 每个场景出现一个成年人比例的人物；人物不坐在桌前写作业或读书。每期设计自己的舞台、道具和版式，不照搬上一期的画面。
- 封面由用户用 ChatGPT 根据本期提示词生成：一张 4:3 横版图兼容 3:4 竖裁切，重要文字和物件集中在中间，左下留给播放量。标题默认以 `Vibe知识大赏/` 开头，总长不超过 30 字。

来源：`.kiro/skills/vibe-knowledge-video/SKILL.md` 的「User defaults」「Workflow」「Content rules」「Rhythm rules」和封面段；技术实现见 `.kiro/skills/vibe-knowledge-video/references/engine.md`，往期数据与解释见 `.kiro/skills/vibe-knowledge-video/references/lessons.md`。本期用户的明确要求可以改变这些默认值。

## 当前状态快照（2026-11-05）

- `main` 已合入制作 Skill 2.5；仓库根目录 `README.md` 列出作品、引擎和新一期的用法。已完成作品与输出分散在 `episodes/`、`sleep_or_cram/`、`bedtime_words/` 和 `out/` 等位置。
- `six-videos` 分支含 `six/plan.md`、六期事实核对材料和 `kit/figure.js`，这些文件不在当前 `main`。`six/plan.md` 的状态行写着等待用户确认，但六期对应的 PR #24–#29 已经创建且仍开放；是否批准分镜、先处理哪条及是否合并，需要以用户的最新决定和 PR 实况核对，不能只读那一行。
- `.kiro/skills/vibe-knowledge-video/references/lessons.md` 已记录往期平台数据、经验解释和待验证问题。它是本仓库的经验位置；其中的待验证问题不能直接升级为固定规则。

来源：`README.md`、主分支 `.kiro/skills/vibe-knowledge-video/SKILL.md`、`six-videos:six/plan.md`，以及 2026-11-05 查看 GitHub 分支和开放 PR 的结果。PR 与分支状态会变化，继续工作前重新查询。

## 下一步

新对话先说明要处理哪一期、哪个 PR，或要做新选题。AI 先读本文件和制作 Skill，检查目标分支及来源；已经记录的通用要求直接沿用，只追问本期真正缺少或互相冲突的信息。涉及新视频时按 Skill 的选题、分镜、预览、渲染和验证流程执行。

