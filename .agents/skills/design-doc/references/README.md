# 专项规范（references）

与 [`SKILL.md`](../SKILL.md) 配合使用。本目录按职责分文件，`SKILL.md` 与模板以链接引用、不复述细则。包内任何两处不一致均视为**规范缺陷**，需在发现当轮修正。

## 规范细则

| 文件 | 内容 |
|------|------|
| [object-model.md](object-model.md) | 对象与字段写入者、锁定矩阵、动作 |
| [coding-system.md](coding-system.md) | 文档/细项编码形态、类型码表、属性行定义集（封闭）、定义块形态、引用与分配 |
| [type-profiles.md](type-profiles.md) | `IF` / `ACT` / `PLN` 专论，ADR 与 DEC 分界 |
| [layer-system.md](layer-system.md) | L0–L6 层级定义、目录结构与命名规则 |
| [status-definitions.md](status-definitions.md) | 状态即基线、标准四态、门控、记录型与流转伴随含义、版本号、存量迁移 |
| [item-deprecation.md](item-deprecation.md) | 细项废弃：原地标注、标记与引用追溯 |
| [doc-deprecation.md](doc-deprecation.md) | 文档废弃：两阶段（原地废弃→到期归档入各作用域 `deprecated/`）、建议归档日期 |
| [glossary-conventions.md](glossary-conventions.md) | 词汇表编写约定：与细项编码的关系、术语上升为 `DOM` 的触发条件、三层放置方式（项目级 / 文档级 / 首次出现） |
| [review-guidelines.md](review-guidelines.md) | 审核流程、检查项与一致性校验 |

## 操作与辅助

| 文件 | 内容 |
|------|------|
| [project-agents-guide.md](project-agents-guide.md) | 为宿主项目生成 AGENTS.md 的建议写法 |

## 非模板资源

| 资源 | 说明 |
|------|------|
| [flowchart-guide.md](../assets/guides/flowchart-guide.md) | 流程图：箭头 / 表格 / Mermaid 选用规则 |
| [check_docs.py](../scripts/check_docs.py) | 静态检查脚本（`--refs {编码}` 引用反查、`--check-templates` 模板哨兵 / 待复制正文禁区与技能包内部锚点、`--instantiate [--segment]` 实例化预览）；只执行规则，不定义规则 |
