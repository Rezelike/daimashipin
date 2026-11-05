# 项目入口

本仓库用于制作和复盘「Vibe知识大赏」代码视频。开始任务时先读根目录 `CONTEXT.md`，再按任务类型读取下面的项目材料。不要让用户重复已经记录的固定偏好；新消息中明确提出的要求优先。

## 读取顺序

1. 先读 `CONTEXT.md`，确认项目目标、当前状态、待确认事项和来源。
2. 涉及选题、分镜、制作、改片或数据复盘时，先读 `.kiro/skills/vibe-knowledge-video/references/lessons.md`，再读 `.kiro/skills/vibe-knowledge-video/SKILL.md`。后者保存现行制作要求和流程；前者的「Open questions to test」是待验证材料，不是已确认结论。不要把旧作品的参数当作通用要求。
3. 需要技术接口时读 `.kiro/skills/vibe-knowledge-video/references/engine.md`。
4. 查看正在处理的分支、PR 和对应剧集目录，核对实际文件。`README.md` 和旧剧集提供入口与例子；它们不能覆盖用户后来的明确决定。

## 工作边界

- 制作新一期时，先复用项目里已经确认的固定要求。只询问本期缺少的变量，例如选题、事实材料、不同于默认值的规格，或尚未批准的分镜。已有用户确认的选题或分镜不再重复走确认步骤。
- 项目材料出现冲突时，指出文件、分支或 PR 及其冲突之处；不要靠日期或文件名猜测。尤其不要假设 `six-videos` 分支的 `kit/figure.js` 已在 `main`，也不要把尚未合并的剧集当作主分支现状。
- `.kiro/skills/vibe-knowledge-video/SKILL.md` 中的 `/projects/sandbox`、环境安装和 `gh` 命令来自原执行环境。先检查当前环境，再选择可用的等效方式。
- 用户确认了新的长期偏好后，核对现有规则是否已覆盖，再更新唯一的现行要求位置并在 `CONTEXT.md` 留下来源。复盘中的新经验先列候选和证据，经用户决定后才写入现有的 `references/lessons.md`；不要另建一份重复的根目录经验库。
- 完成任务时报告实际改动、验证结果和仍待用户决定的事项。状态或分支改变后，更新 `CONTEXT.md` 的状态快照与来源。

