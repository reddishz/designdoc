---
name: design-doc
description: >
  维护 ued/ 分层设计文档、需求编码、架构决策、验证/EVAL、术语表与产品基线。
  **design-doc是极其重要的技能，应作为每次开发和设计的基础。**
  项目有 ued/ 时，改功能、修缺陷或按需求实现代码前 MUST 先对照设计：
  需改设计则先文档后代码；禁止先写代码再补设计。
  亦用于创建、审查、更新设计文档与基线发版。
license: MIT
metadata:
  version: "9.0"
  author: "designdoc"
  spec-compliance: 遵循 Agent Skills 开放标准
  tags: [design, documentation, product, architecture, specification]
  triggers:
    - "设计文档"
    - "需求文档"
    - "设计方案"
    - "增加功能"
    - "改功能"
    - "修bug"
    - "修缺陷"
    - "实现"
    - "废弃功能"
    - "设计规范"
    - "文档规范"
    - "功能需求"
    - "术语"
    - "术语表"
    - "改名"
    - "更名"
    - "维护性变更"
  trigger_principle: >
    设计文档维护与据文档改代码均受编码与基线约束；
    有 ued/ 时改行为类请求亦应加载本技能，先判定设计是否要动，再动代码。
  capabilities:
    - "多层级设计文档生成 (L0-L6)"
    - "全局唯一编码管理与冲突检测"
    - "自动化文档规范性审查"
    - "跨文档引用一致性维护"
    - "全局术语表与单一权威定义"
    - "非语义文字维护与命名变更追溯"
    - "变更代码前的设计对照与文档优先"
compatibility: 需能访问 ued/ 目录，可选从运行环境获取当前执行主体标识
---

# 产品设计文档规范（UED）

本 skill **约束 AI 的执行方式**，不是人类写作教程。**规则与流程在 `references/`**；本文是运行时路由：选对 workflow、守住不变量、该停则停。

措辞强度见 [coding-system.md · 需求级别说明](references/coding-system.md#需求级别说明)。

## 一致性（无冲突）

包内与 `ued/` 内**同一规则只允许一种表述**。发现技能包两处不一致、或设计文档之间/与基线冲突 → 视为**规范缺陷**，当轮修正或列入人审后修正；**MUST NOT** 用「优先级表」掩盖冲突。定稿与发布前审查须确认无未解消冲突。

## 运行时步骤

1. 确认作用域存在 `ued/`（或应用级设计树）；解析配置见 [runtime-config.md](references/workflows/runtime-config.md)。
2. 按下方**任务路由**加载对应 workflow（**MUST read**）；仅在流程分支需要时再打开所列 rule。
3. 解冻、废弃、批量编码或动基线前：先短计划，人审停点见各 workflow 的 Checkpoint。
4. 改完跑 `check_docs.py`；通过≠语义正确。
5. **仅当**本轮改过 `ued/`、要定稿/提交、或有基线漂移须询问时，再加载 [lifecycle.md](references/workflows/lifecycle.md) 走 Checkpoint 5；未改设计文档则不必读 lifecycle。

## 任务路由

| 意图 | MUST 先读 |
|------|-----------|
| 首次接入 / 不确定先读哪页 | [decision-card.md](references/decision-card.md) |
| 增量加功能 / 加需求 | [change-feature.md](references/workflows/change-feature.md) |
| 创建新设计文档 | [create-document.md](references/workflows/create-document.md) |
| 分配编码；改 ID/类型码/正式标题或含义 | [allocate-and-lock.md](references/workflows/allocate-and-lock.md) |
| 改标题措辞 / 术语改名 / 引用路径，语义不变 | [maintenance-change.md](references/workflows/maintenance-change.md) |
| 废弃细项/文档 | [lifecycle.md](references/workflows/lifecycle.md)（作废段） |
| 定稿确认 / 提交收尾 / 基线漂移询问 | [lifecycle.md](references/workflows/lifecycle.md)（Checkpoint 5；见上「仅当」） |
| 基线 PATCH / MINOR / MAJOR | [baseline-change.md](references/workflows/baseline-change.md) |
| 写/改 EVAL | [eval-report-profile.md](references/eval-report-profile.md) + 模板 [eval.md](assets/templates/eval.md) |
| 维护术语表 / 定义术语 / 术语冲突 | [glossary-conventions.md](references/glossary-conventions.md) + 模板 [glossary.md](assets/templates/glossary.md) |
| 审查设计文档 | [review-guidelines.md](references/review-guidelines.md) |
| **改功能 / 修缺陷 / 改行为**（有 `ued/`） | [before-code-change.md](references/workflows/before-code-change.md)（**先判定设计要不要改**） |
| **按已定设计实现代码** | [implement-from-design.md](references/workflows/implement-from-design.md) |
| 维护项目 `AGENTS.md` / 约定文件 | [project-agents-guide.md](references/project-agents-guide.md) |
| 写流程图 / 判断用 Mermaid 还是箭头 | [flowchart-guide.md](assets/guides/flowchart-guide.md) |

动代码相关意图：**MUST** 先走 `before-code-change`，**MUST NOT** 默认先改业务代码。

## 不变量（任何任务）

1. 已分配编码 **MUST NOT** 删除或复用；放弃走作废。
2. 编码 ID/类型码永不就地改；`正式`/`草案` 标题与已正式业务含义不就地改**语义**（通道见 [锁定矩阵](references/object-model.md#锁定矩阵mandatory)）；不改含义的命名维护走 [维护性变更](references/workflows/maintenance-change.md)，不改状态与修订号。
3. 未入**当前**产品基线（或基线 revision 落后）的内容 **MUST NOT** 作为实现依据。
4. 语义引用只用细项/文档编码，**MUST NOT** 用章节编号；跨文件路径以 `./` 或 `../` 开头。
5. `ued/` **MUST NOT** 含可执行实现代码（算法/契约/状态机可以）。
6. 高风险生命周期与基线动作 **MUST** 经人确认（Checkpoint）；AI **MUST NOT** 自行定稿或 `--bump-product`。
7. 模板即复制源；哨兵外说明 **MUST NOT** 写入实例（[模板边界](assets/templates/index.md#模板边界哨兵)）。
8. 术语在项目内**只有一个权威定义**；全局索引固定为 `ued/glossary.md`，同名冲突 **MUST** 当轮收口，**MUST NOT** 用第二张表并存。

细则单点（按需打开，勿在任务开始时整包预读）：

| 主题 | 文件 |
|------|------|
| 对象 / 锁定 / 信息项角色 | [object-model.md](references/object-model.md) |
| 编码 / 定义块 / 引用 / 本文引用 | [coding-system.md](references/coding-system.md) |
| 类型切分（含 EVAL） | [type-profiles.md](references/type-profiles.md) |
| 四态 / 门控 / 修订号 / 维护性变更 | [status-definitions.md](references/status-definitions.md) |
| 产品版本 / 基线 | [product-version.md](references/product-version.md) |
| 层级 / 按需启用 | [layer-system.md](references/layer-system.md) |
| 术语 / 全局术语表 / `所用术语` | [glossary-conventions.md](references/glossary-conventions.md) |
| 细项 / 文档作废 | [item-deprecation.md](references/item-deprecation.md) / [doc-deprecation.md](references/doc-deprecation.md) |

## 范围与工具

| 目录 | 范围 |
|------|------|
| `ued/L0`–`L6` | 战略→验证；`EVAL-*` 在 L6；`ADR-*` 在 L3 |
| `ued/references/` 内 `REF-*` | 外部资料 |

模板：[assets/templates/index.md](assets/templates/index.md)。

```bash
python3 .agents/skills/design-doc/scripts/check_docs.py -p <ued路径>
python3 .agents/skills/design-doc/scripts/check_docs.py -p <ued路径> --bump-product --patch|--minor|--major --note '…'
python3 .agents/skills/design-doc/scripts/check_docs.py -p <ued路径> --refs {编码}
python3 .agents/skills/design-doc/scripts/tests/run_fixtures.py
```

`--check-templates` / `--instantiate` 见脚本帮助。静态检查不代替人工审查与定稿确认。

**适用**：设计文档全生命周期；有 `ued/` 时变更代码前的设计对照与据文档实现门禁（**不代替**编写业务代码）。**不适用**：与 `ued/` 无关的纯环境琐事、用户/运维手册。

## 常见问题（短答）

- **编码怎么分？** → [allocate-and-lock.md](references/workflows/allocate-and-lock.md)  
- **能改正式标题/含义吗？** → 语义不能就地改；不改含义的措辞维护走 [maintenance-change.md](references/workflows/maintenance-change.md)，其余见锁定矩阵与 allocate-and-lock  
- **定稿要升基线吗？** → 定稿不自动写基线；Checkpoint 5 按漂移问 PATCH/MINOR/MAJOR  
- **正式就能实现吗？** → 还须在当前基线 `items` 且 revision 对齐  
- **加功能只写 L4/L5？** → 已有上层则先 [change-feature.md](references/workflows/change-feature.md) 向上核对  
- **改功能/修 bug 直接改代码？** → 有 `ued/` 时否；先 [before-code-change.md](references/workflows/before-code-change.md)  
- **冲突听谁的？** → 不允许并存；当轮修正（见上文「一致性」）  
