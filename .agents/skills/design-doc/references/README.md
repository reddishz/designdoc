# 专项规范（references）

与 [`SKILL.md`](../SKILL.md) 配合：主文件只做路由；**规则**在本目录根下各文件，**流程**在 [`workflows/`](workflows/)。包内任何两处不一致均视为**规范缺陷**，发现当轮修正（**MUST NOT** 用优先级掩盖冲突）。

## 流程（workflows）

| 文件 | 何时加载 |
|------|----------|
| [workflows/change-feature.md](workflows/change-feature.md) | 增量加功能/需求 |
| [workflows/create-document.md](workflows/create-document.md) | 创建新设计文档 |
| [workflows/allocate-and-lock.md](workflows/allocate-and-lock.md) | 分配编码；含义/锁定变更 |
| [workflows/maintenance-change.md](workflows/maintenance-change.md) | 非语义维护（用语、措辞、名称、引用、结构） |
| [workflows/lifecycle.md](workflows/lifecycle.md) | 废弃；定稿与 Checkpoint 5 |
| [workflows/baseline-change.md](workflows/baseline-change.md) | 基线 PATCH/MINOR/MAJOR |
| [workflows/before-code-change.md](workflows/before-code-change.md) | 有 ued/ 时改功能/修缺陷/改行为前 |
| [workflows/implement-from-design.md](workflows/implement-from-design.md) | 据已定设计实现代码 |
| [workflows/runtime-config.md](workflows/runtime-config.md) | 解析作者/项目编码与作用域 README |

## 规范细则（rules）

| 文件 | 内容 |
|------|------|
| [object-model.md](object-model.md) | 对象与字段写入者、信息项角色、锁定矩阵、动作 |
| [coding-system.md](coding-system.md) | 编码形态、类型码、定义块、引用、本文引用与分配 |
| [type-profiles.md](type-profiles.md) | IF/ACT/PLN、UC/FR/FLW、ADR/DEC、EVAL 分界 |
| [eval-report-profile.md](eval-report-profile.md) | EVAL 正文自包含口径 |
| [layer-system.md](layer-system.md) | L0–L6、按需启用、目录命名 |
| [status-definitions.md](status-definitions.md) | 四态、门控、修订号、维护性变更、存量迁移 |
| [product-version.md](product-version.md) | 产品版本、基线、PATCH/MINOR/MAJOR |
| [item-deprecation.md](item-deprecation.md) | 细项废弃 |
| [doc-deprecation.md](doc-deprecation.md) | 整份文档废弃与归档 |
| [glossary-conventions.md](glossary-conventions.md) | 术语定义、全局术语表与 `所用术语` |
| [review-guidelines.md](review-guidelines.md) | 审核检查项 |

## 操作与辅助

| 文件 | 内容 |
|------|------|
| [project-agents-guide.md](project-agents-guide.md) | 为宿主生成 AGENTS.md（含设计优先改代码） |

## 非模板资源

| 资源 | 说明 |
|------|------|
| [flowchart-guide.md](../assets/guides/flowchart-guide.md) | 流程图选用规则 |
| [check_docs.py](../scripts/check_docs.py) | 静态检查（只执行规则，不定义规则） |
