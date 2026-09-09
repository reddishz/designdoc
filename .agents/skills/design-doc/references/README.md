# 专项规范（references）

与 [`SKILL.md`](../SKILL.md) 配合使用。本目录是各专项规则**完整表述的单点承载处**，`SKILL.md` 与模板一律以链接指针引用、不复述细则。包内任何两处不一致均视为**规范缺陷**，需在发现当轮修正。

## 规范细则

| 文件 | 内容 |
|------|------|
| [coding-system.md](coding-system.md) | 文档编码、细项编码、默认/扩展前缀、编码锁定与修改操作矩阵、引用规则 |
| [layer-system.md](layer-system.md) | L0–L6 层级定义、目录结构与命名规则 |
| [status-definitions.md](status-definitions.md) | 状态即基线、标准四态（初稿/正式/草案/废弃）、锁定矩阵（要素 × 状态）、记录型字段、流转与变更流程/版本号、存量文档迁移映射 |
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
| [check_docs.py](../scripts/check_docs.py) | 静态检查脚本（含 `--refs {编码}` 引用反查、`--check-templates` 模板哨兵自检、`--instantiate` 模板实例化预览）；只执行规则，不定义规则 |
