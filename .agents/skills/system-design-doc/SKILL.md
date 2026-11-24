---
name: system-design-doc
description: >
  维护由多个子系统组成的系统级设计与编排：系统架构描述与子系统职责分配、
  系统交互、系统级约束（SYS-CON）与架构决策（SYS-ADR）、子系统注册表、
  依赖钉住与绑定架构修订的系统发布清单。
  项目 `ued/README.md` 含子系统注册表时加载；单系统继续使用 design-doc。
  子系统内部的分层设计、组件（CMP）、编码与产品基线由 design-doc 负责。
license: MIT
metadata:
  version: "2.1"
  author: "designdoc"
  spec-compliance: 遵循 Agent Skills 开放标准
  tags: [system, subsystem, architecture, design, documentation, release, dependency]
  triggers:
    - "系统设计"
    - "系统架构"
    - "子系统"
    - "子系统注册表"
    - "职责分配"
    - "系统发布"
    - "产品集发布"
    - "子系统依赖"
    - "版本对齐"
    - "接口对齐"
    - "共享库"
    - "多子系统"
    - "SYS-ADR"
    - "SYS-CON"
  trigger_principle: >
    只要设计树由多个 design-doc 作用域组成，系统级架构权威、子系统职责分配、
    跨子系统依赖与发布组合就必须受本技能约束；子系统内部仍按 design-doc 执行。
  capabilities:
    - "系统架构描述与子系统职责分配权威"
    - "跨子系统交互、SYS-CON 约束与 SYS-ADR 决策"
    - "子系统注册与生命周期管理"
    - "子系统依赖与外部依赖精确钉住"
    - "绑定 architecture_rev 的系统发布清单与版本对齐"
    - "跨子系统编码前缀、SYS 命名空间与引用检查"
compatibility: 需能访问 `ued/` 系统根；子系统内部校验需 design-doc 技能
---

# 系统级设计规范（多子系统）

本技能确立多子系统项目的**系统级架构权威**与**组合发布编排**，不重复 `design-doc` 的分层文档、内部组件（`CMP`）、编码与产品基线规则。系统由多个子系统组成；每个子系统是一个完整的 `design-doc` 作用域。

## 核心模型

| 视角 / 概念 | 位置 | 职责 |
|-------------|------|------|
| **系统入口与注册表** | `ued/README.md` | 当前结构、5 列子系统注册表、架构入口、系统发布索引；**无** `产品版本`、`baselines/` 或职责正文副本 |
| **系统架构** | `ued/architecture/system-architecture.md` | 系统定义、**子系统职责分配（唯一真源）**、系统交互、系统级约束（`SYS-CON`）、固定格式修订记录 |
| **系统级决策** | `ued/architecture/SYS-ADR-*.md` | 跨子系统架构决策（拆分/合并、通信模式、信任边界等）；不进入子系统 ADR 计数器 |
| **子系统** | `ued/{目录}/` | 完整 `design-doc` 作用域：落实系统分配的职责；`CMP` 仅表达内部逻辑组件；自有 `产品版本` 与 `baselines/` |
| **系统发布** | `ued/releases/sys-vX.Y.yaml` | 不可变组合锁：钉住纳入的子系统版本、外部依赖版本与 `architecture_rev`；不是设计基线 |
| **共享库** | 普通子系统 | 与业务子系统同规则；可有零个或多个；**不设固定 `shared/`** |

- 系统层保留前缀 `SYS`（仅 `SYS-CON` / `SYS-ADR`），不建立第二套 L0–L6、产品基线或全局编码计数器。
- 术语表固定为 `ued/glossary.md`（全系统唯一）；子系统校验时用 `--glossary ued/glossary.md`。

## 运行时步骤

1. 判定结构：`ued/README.md` 含**子系统注册表** → 本技能适用；否则是单系统，改用 `design-doc`。
2. 按任务路由读对应 workflow 或 rule；按需加载，不一次通读全部文件。
3. 变更系统架构职责划分、登记 / 激活 / 废弃子系统、创建系统发布前：先给短计划，停在人审 Checkpoint。
4. 改完运行：
   ```bash
   python3 .agents/skills/system-design-doc/scripts/check_system.py -p ued
   ```
   并对每个子系统运行：
   ```bash
   python3 .agents/skills/design-doc/scripts/check_docs.py -p ued/{子系统} --glossary ued/glossary.md
   ```
   跨子系统细项 `依赖`（成环 / 指向他子系统 `初稿`）另跑：
   ```bash
   python3 .agents/skills/design-doc/scripts/check_docs.py -p ued --cross-scope-deps
   ```
5. 检查器校验注册表、系统架构对齐、`SYS-*` 命名空间、依赖、发布与跨子系统引用；通过 ≠ 架构划分语义正确。
6. 人审后才可定稿系统架构、激活/废弃子系统或创建发布；AI **MUST NOT** 擅自执行高风险动作。

## 任务路由

| 意图 | MUST 先读 |
|------|-----------|
| 首次接入 / 不确定先读哪页 | [decision-card.md](references/decision-card.md) |
| 系统与子系统的职责模型与权威边界 | [system-model.md](references/system-model.md) |
| 编写或更新系统架构、`SYS-CON`、`SYS-ADR` | [architecture-description.md](references/architecture-description.md) |
| 注册表字段 / 状态 / 前缀 / 激活前置 | [registry.md](references/registry.md) |
| 新建、登记、激活或废弃子系统 | [setup-subsystem.md](references/workflows/setup-subsystem.md) |
| 子系统发版、修改依赖钉住 | [subsystem-baseline.md](references/workflows/subsystem-baseline.md) |
| 创建系统发布 / 产品集发版 | [system-release.md](references/workflows/system-release.md) |
| 审查系统架构、结构与发布 | [review-system.md](references/workflows/review-system.md) |
| 版本对齐、依赖冲突、外部依赖 | [version-alignment.md](references/version-alignment.md) |
| 技能升级后让系统层文档跟随新规范（`规范版本目标` / 封面 `规范版本`） | [spec-upgrade.md](references/spec-upgrade.md) |
| 接口兼容性与破坏性变更 | [compatibility.md](references/compatibility.md) |
| 从旧多应用结构或 v1.x 迁移至 v2.0 | [migration-from-design-doc.md](references/migration-from-design-doc.md) |
| 子系统内部设计（L0–L6、内部 CMP） | 转 [design-doc](../design-doc/SKILL.md) |

## 不变量

1. 系统根 **MUST NOT** 有 `产品版本`、`baselines/`、`L0-vision/`–`L6-verification/` 或全局细项编码索引；系统版本只由 `releases/sys-vX.Y.yaml` 表达。
2. 子系统角色与职责边界的**唯一真源**在 `ued/architecture/system-architecture.md`；注册表为 5 列，**MUST NOT** 绑定子系统 `CMP` 作为角色文档，README **MUST NOT** 复述职责正文。
3. 注册表是系统组成的唯一真源；`subsystem_key` 一经登记**不可改、不可复用**；`SYS` 为系统保留前缀，子系统 **MUST NOT** 使用或定义 `SYS-*`。
4. `正式` 子系统 **MUST** 已在有效系统架构文档完成职责分配，并具备 `产品版本` 与对应基线；`初稿` 未启用；`废弃` 不再进入新发布。
5. 共享库就是普通子系统；**MUST NOT** 为它单设固定目录、特殊状态或部署规则。
6. 子系统基线 **MUST** 用 `depends_on` / `external_deps` 钉住精确两段版本；PATCH **MUST NOT** 触碰依赖块；基线进入系统发布组合后，依赖变化 **MUST** 立新基线。
7. 系统发布是**不可变组合锁**；发布后 **MUST NOT** 修改，只能发新版本；新发布 **MUST** 通过 `architecture_rev` 指向修订记录中已存在的 `正式` 架构修订。
8. 公开接口破坏性变更 **MUST** 使用 MAJOR；PATCH **MUST NOT** 改变接口语义。
9. 高风险动作（架构实质变更定稿、登记、激活、废弃、系统发布）**MUST** 经人确认。
10. 术语在系统内只有一个权威定义（`ued/glossary.md`）；系统检查器与 `design-doc` 检查器互不导入，各自只查自己规范内的部分。

## 范围与工具

| 路径 | 范围 |
|------|------|
| `ued/README.md` | 系统入口 + 5 列子系统注册表 + 系统发布索引 |
| `ued/architecture/` | 系统架构描述（`system-architecture.md`）与系统级决策（`SYS-ADR-*.md`） |
| `ued/{子系统}/` | 子系统作用域，内部规则见 `design-doc` |
| `ued/releases/` | 系统发布清单（`sys-vX.Y.yaml`） |
| `ued/glossary.md` | 全系统唯一术语表 |

```bash
python3 .agents/skills/system-design-doc/scripts/check_system.py -p ued
python3 .agents/skills/system-design-doc/scripts/check_system.py -p ued --print-member-commands
python3 .agents/skills/system-design-doc/scripts/tests/run_fixtures.py
```

模板：[assets/templates/index.md](assets/templates/index.md)。

**适用**：多子系统项目的系统级架构权威、子系统注册、依赖钉住与产品集发布。**不适用**：单系统（用 `design-doc`）、子系统内部设计细节、纯代码实现。

## 常见问题（短答）

- **单系统还是系统？** → 根 README 有子系统注册表才是系统；否则用 `design-doc`。
- **子系统角色和边界写在哪？** → 统一写在 `ued/architecture/system-architecture.md` 的职责分配表；子系统内 `CMP` 只写内部逻辑组件。
- **系统级约束和跨子系统 ADR 放哪？** → 约束在 `system-architecture.md` 用 `SYS-CON-xxx` 定义，决策放 `ued/architecture/SYS-ADR-xxx-*.md`；不放进普通子系统代管。
- **系统根需要建 L0–L6 或产品基线吗？** → 不要；系统层只维护轻量的 `architecture/` 与 `releases/`。
- **共享库怎么建？** → 按普通子系统登记与分配职责；不设固定 `shared/`。
- **系统发布必须包含全部正式子系统吗？** → 不必；纳入项须为 `正式` 且依赖闭合，并填写 `architecture_rev`。
- **依赖变了怎么办？** → 已进入系统发布组合的：立新子系统基线（MINOR/MAJOR），再发新系统版本；尚未进入的：原地修正，不升版本。两者都不经过 PATCH。
- **从 v1.x 升级怎么处理旧 `角色文档` 列和外壳 `CMP`？** → 见 [migration-from-design-doc.md](references/migration-from-design-doc.md#从-system-design-doc-v1x-迁移到-v20)。
