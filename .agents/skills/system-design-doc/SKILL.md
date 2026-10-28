---
name: system-design-doc
description: >
  维护由多个子系统组成的系统级设计：子系统注册表、角色 / 边界 / 交互约束、
  子系统依赖与外部依赖钉住、系统发布清单与版本对齐。
  项目 `ued/README.md` 含子系统注册表时加载；单系统继续使用 design-doc。
  子系统内部的分层设计、编码与产品基线由 design-doc 负责，本技能只做系统级编排。
license: MIT
metadata:
  version: "1.3"
  author: "designdoc"
  spec-compliance: 遵循 Agent Skills 开放标准
  tags: [system, subsystem, design, documentation, release, dependency]
  triggers:
    - "系统设计"
    - "子系统"
    - "子系统注册表"
    - "系统发布"
    - "产品集发布"
    - "子系统依赖"
    - "版本对齐"
    - "接口对齐"
    - "共享库"
    - "多子系统"
  trigger_principle: >
    只要设计树由多个 design-doc 作用域组成，系统级组合、依赖与发布就必须受本技能约束；
    子系统内部仍按 design-doc 执行。
  capabilities:
    - "子系统注册与生命周期"
    - "角色、范围边界与交互约束"
    - "子系统依赖与外部依赖钉住"
    - "系统发布清单与版本对齐"
    - "跨子系统编码前缀与引用检查"
compatibility: 需能访问 `ued/` 系统根；子系统内部校验需 design-doc 技能
---

# 系统子系统设计规范

本技能约束**系统级编排**，不重复 design-doc 的文档、编码、状态与产品基线规则。系统由多个子系统组成；每个子系统是一个完整的 design-doc 作用域。

## 核心模型

| 概念 | 位置 | 职责 |
|------|------|------|
| **系统** | `ued/README.md` | 子系统注册表、角色 / 边界 / 交互约束、系统发布清单；**无** `产品版本`，**无** `baselines/` |
| **子系统** | `ued/{目录}/` | 完整的 design-doc 作用域：自有 README、计数器、索引、`产品版本` 与 `baselines/` |
| **系统发布** | `ued/releases/sys-vX.Y.yaml` | 组合锁：钉住本次纳入的子系统与外部依赖的精确版本；不是设计基线，也不要求覆盖全部 `正式` 成员 |
| **共享库** | 普通子系统 | 与业务子系统同规则；可有零个或多个；**不设固定 `shared/`** |

- 子系统之间通过**完整编码**引用，不共享同一个文档作用域。
- 系统根只做入口、注册表、跨子系统规则与发布；**MUST NOT** 成为设计文档作用域。
- 系统级设计内容（愿景、跨子系统需求、系统架构、交互契约）由**承担该职责的普通子系统**承载，或写在系统根 README 的摘要表中；本技能**不规定**固定目录。
- 术语表仍固定为 `ued/glossary.md`（全系统唯一）；子系统校验时用 `--glossary ued/glossary.md`。

## 运行时步骤

1. 判定结构：`ued/README.md` 含**子系统注册表** → 本技能适用；否则是单系统，改用 design-doc。
2. 按任务路由读对应 workflow；仅在需要时打开 rule。
3. 登记 / 激活 / 废弃子系统、创建系统发布前：先给短计划，停在人审 Checkpoint。
4. 改完运行：
   ```bash
   python3 .agents/skills/system-design-doc/scripts/check_system.py -p ued
   ```
   并对每个子系统运行：
   ```bash
   python3 .agents/skills/design-doc/scripts/check_docs.py -p ued/{子系统} --glossary ued/glossary.md
   ```
5. 系统检查器只查注册表、拓扑、依赖、发布与跨子系统引用，**不查**文档内部规则；通过 ≠ 语义正确。
6. 人审后才可定稿或创建发布；AI **MUST NOT** 自行登记、废弃或发布。

## 任务路由

| 意图 | MUST 先读 |
|------|-----------|
| 首次接入 / 不确定先读哪页 | [decision-card.md](references/decision-card.md) |
| 新建、登记、激活或废弃子系统 | [setup-subsystem.md](references/workflows/setup-subsystem.md) |
| 子系统发版、修改依赖钉住 | [subsystem-baseline.md](references/workflows/subsystem-baseline.md) |
| 创建系统发布 / 产品集发版 | [system-release.md](references/workflows/system-release.md) |
| 审查系统结构与发布 | [review-system.md](references/workflows/review-system.md) |
| 版本对齐、依赖冲突、外部依赖 | [version-alignment.md](references/version-alignment.md) |
| 接口兼容性与破坏性变更 | [compatibility.md](references/compatibility.md) |
| 从旧多应用结构迁移 | [migration-from-design-doc.md](references/migration-from-design-doc.md) |
| 注册表字段 / 状态 / 前缀 | [registry.md](references/registry.md) |
| 系统与子系统的职责边界 | [system-model.md](references/system-model.md) |
| 子系统内部设计 | 转 [design-doc](../design-doc/SKILL.md) |

## 不变量

1. 系统根 **MUST NOT** 有 `产品版本` 或 `baselines/`；系统版本只由 `releases/sys-vX.Y.yaml` 表达。
2. 注册表是系统组成的唯一真源；`subsystem_key` 一经登记**不可改、不可复用**。
3. `正式` 子系统 **MUST** 有角色文档、`产品版本` 与对应基线；`初稿` 未启用；`废弃` 不再进入新发布。
4. 共享库就是普通子系统；**MUST NOT** 为它单设固定目录、特殊状态或部署规则。
5. 子系统基线 **MUST** 用 `depends_on` / `external_deps` 钉住精确两段版本；修改依赖钉住 **MUST** 立新基线，**MUST NOT** 用 PATCH。
6. 系统发布是**不可变组合锁**；发布后 **MUST NOT** 修改，只能发新版本。
7. 公开接口破坏性变更 **MUST** 使用 MAJOR；PATCH **MUST NOT** 改变接口语义。
8. 高风险动作（登记、激活、废弃、系统发布）**MUST** 经人确认。
9. 术语在系统内只有一个权威定义；全局表固定 `ued/glossary.md`。
10. 系统检查器与 design-doc 检查器互不导入；各自只查自己规范内的部分。

## 范围与工具

| 路径 | 范围 |
|------|------|
| `ued/README.md` | 系统入口 + 子系统注册表 + 系统发布索引 |
| `ued/{子系统}/` | 子系统作用域，内部规则见 design-doc |
| `ued/releases/` | 系统发布清单（`sys-vX.Y.yaml`） |
| `ued/glossary.md` | 全系统唯一术语表 |

```bash
python3 .agents/skills/system-design-doc/scripts/check_system.py -p ued
python3 .agents/skills/system-design-doc/scripts/check_system.py -p ued --print-member-commands
python3 .agents/skills/system-design-doc/scripts/tests/run_fixtures.py
```

模板：[assets/templates/index.md](assets/templates/index.md)。

**适用**：多子系统系统的注册、依赖、版本对齐与发布。**不适用**：单系统（用 design-doc）、子系统内部设计细节、纯代码实现。

## 常见问题（短答）

- **单系统还是系统？** → 根 README 有子系统注册表才是系统；否则用 design-doc。
- **共享库怎么建？** → 按普通子系统登记；需要几个建几个；不设固定 `shared/`。
- **系统要不要产品版本？** → 不要；系统版本写在 `releases/sys-vX.Y.yaml`。
- **系统发布必须包含全部正式子系统吗？** → 不必。发布是可选快照；纳入项须为 `正式` 且依赖闭合，未纳入的正式子系统只是不在该组合内。
- **A v3.1 必须配 D v2.5 怎么表达？** → A 的基线写 `depends_on: [{subsystem: d, product_version: v2.5}]`；系统发布同时钉住两者。
- **依赖变了怎么办？** → 立新子系统基线（MINOR/MAJOR），再发新系统版本；不能 PATCH。
- **系统级文档放哪？** → 放到承担该职责的普通子系统，或写在根 README 摘要表；不新建特殊根作用域。
- **子系统怎么校验？** → `check_docs.py -p ued/{子系统} --glossary ued/glossary.md`。
