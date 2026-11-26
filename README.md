# design-doc

与 AI 协作编写标准化的产品设计文档：分层清楚、编码可追溯；定稿并进入当前产品基线后，才作为实现依据。

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Skill](https://img.shields.io/badge/design--doc-v10.26-blue.svg)](./.agents/skills/design-doc/SKILL.md)
[![Skill](https://img.shields.io/badge/system--design--doc-v2.1-blue.svg)](./.agents/skills/system-design-doc/SKILL.md)
[![Agent Skills](https://img.shields.io/badge/Agent%20Skills-Standard-green.svg)](https://agentskills.io/specification)

把本仓库的 skill 装进项目后，直接对 AI 说「写一份 L4 系统设计」即可。多数项目从需求（L2）和系统设计（L4）起步，不必一次生成全套。单系统用 `design-doc`；由多个子系统组成的系统另加 `system-design-doc` 管注册表、依赖钉住与系统发布。

## 为什么使用 design-doc？

| 没有它时 | 有它之后 |
|---------|---------|
| 文档格式不统一，每个团队各有风格 | 统一模板，AI 按同一套规范写 |
| 结构混乱，审阅困难 | L0–L6 分层，按需选用 |
| 需求改了找不到影响面 | 每条设计有唯一编码，互相用编码引用 |
| 草稿被拿去写代码，正式内容被随手改掉 | 只有进了当前产品基线的正式内容才拿去写代码；改正式内容要解冻 |
| 对不对全靠人眼 | 有审核清单，也可以跑检查脚本 |

## 功能特性

- **分层文档** — 从战略、需求、架构到详细设计与验证；未指定时默认写 L2 或 L4
- **单一作用域** — `design-doc` 一次只维护一个系统或一个子系统；多子系统结构下每个 `ued/{子系统}/` 各有一套元信息、编码索引和产品基线
- **系统与子系统** — 配套的 `system-design-doc` 确立系统架构权威（`ued/architecture/` 定义子系统职责分配、系统交互、`SYS-CON` 约束与 `SYS-ADR` 决策），并维护 5 列子系统注册表、跨子系统依赖钉住和绑定 `architecture_rev` 的不可变系统发布清单
- **现成模板** — 含产品路线图、规划总览、架构决策（ADR）和外部资料（REF）
- **全局编码** — 文档和细项都有唯一编号，正文用编码跳转，不用「见上一节」
- **四种状态** — 初稿 / 正式 / 草案 / 废弃。正式后不就地改含义；废弃保留编号，便于追溯
- **术语单一权威** — 全局术语表固定为 `ued/glossary.md`，每个术语只有一个权威定义；文档可声明重点使用的术语
- **维护性变更** — 统一用语、修正措辞或引用路径、名称非语义调整等不改含义的维护，在变更记录留下 `N（维护）` 行（同号一条，后续批次追加为片段），不改状态、修订号或基线，与实质变更分开处理
- **产品基线** — 每个产品版本一份可实现细项清单；首份基线可在开发期增删成员，后续基线成员变化立新基线，写代码只认当前版
- **按文档实现** — 改功能/修 bug 先对照设计文档；实现只依据已定稿且已入当前产品基线的内容，未入基线会先拦住
- **可检查** — `check_docs.py` 核对编码、状态、引用是否对得上
- **多 IDE** — Cursor、Windsurf、Claude Code、VS Code 等可自动发现本 skill

## 版本演进

只列主线；各版细则见提交记录。

| 版本 | 主要变化 |
|------|----------|
| v10.26 | 借鉴 SQuaRE（25030 / 25019 / 25002）完善质量需求概念与评审：L6 追溯矩阵为选用汇总（列可裁剪）；MET 评价依据可来自 AC / EVAL / 外部监控（引用按关系语义区分）；新增《质量术语与质量需求的目标实体》；评审增目标实体与条件、MET 评价路径、矩阵与引用一致三项；SCN `预期结果` 选填；检查器无变更 |
| v10.25 | 依据 w3trade 案例核对修正：NFR 可验证口径分数值型 / 判定型；属性存在性定级（SHOULD 不机检）；新增《TC 测试类型与追溯》；锁定类型越层定义补记 v4.6 生效并加 WARNING；检查器新增测试类型 / 测试优先级枚举 ERROR |
| v10.24 | 修正 25010 吸收的三处语义：功能适合性子特征单列、不并入 29148 Complete；适用性表改三种判断；旧类别映射仅作人工建议 |
| v10.23 | NFR 类别按 ISO/IEC 25010:2023 改名（安全拆 Security / Safety）并给迁移提示；新增产品质量属性参考；基线整体判断增加质量属性适用性表 |
| v10.22 | 定稿增加全局交互扫描（候选之外的关键交互）；集合 Consistent 措辞改为「归入集合层面的缺陷」；比对阈值与方式记入质量报告 |
| v10.21 | 集合一致 / 可行 / 可理解补定义与判据；新增比对范围（候选取并集，全量兜底 NFR、总括词需求与 CON，小规模全量）；「只记一次」扩到集合（按根因固定顺序）；须人审增集合质量判断一行 |
| v10.20 | 正式 FR / NFR 的 `来源` 只指向自身或下层同缺来源（ERROR）；SCN 承接沿 `来源` 链追溯；修正 10.19 措辞（无编码依据归 `REF` 或 L1 的 `SCN` / `STK` / `CON`，删「Correct 的集合版」） |
| v10.19 | 正式 FR / NFR 的 `来源` 升为 MUST（缺则 ERROR）；新增 INFO「场景无需求承接」；澄清集合「完整」与「可确认」的区别及 `来源` 的覆盖范围 |
| v10.18 | 需求集合由索引与基线文件界定，定稿做增量检查、基线成员变化时做整体判断；A 类为阻断项，用户接受须记理由；逻辑连接词与 Appropriate 粒度补充 |
| v10.17 | 需求质量对齐 29148:2018：特征对应表、Correct 须人审、需求集合检查（定稿前）；定稿确认前呈现质量报告，问题按证据强度分 A / B / C；单数允许多个条件，模糊词按 5.2.7 扩充 |
| v10.16 | 文档 `作者` 统一取作用域 README 的 `author`，缺失用默认值；每次写入或修改文档时按当前值写入 |
| v10.15 | `DEC` 定义层级放宽为 L3 / L4 / L5，不再对 ADR 做特例；L2 定义 DEC 报 WARNING |
| v10.14 | 托管块精简为 6 条约束（`block=4`），步骤细则交给 Skill 与 workflow；检查器限制规则条数（上限 7） |
| v10.13 | 编码前设计 Gate 新增 M（维护性变更）判定，Gate 记录早于任何编辑，B/C/D 本回合结束等待确认；托管块 `block=3`；宿主适配与宿主无关，Cursor 规则检查改为 `--host cursor` 按需启用；多个带托管块的 AGENTS.md 报告 |
| v10.12 | 新增编码前设计 Gate（动手前输出 Gate 记录，四种判定，改 `ued/` 同样适用）、实现中范围漂移即停与完成后逐条对照；项目接入：根 `AGENTS.md` 托管块（检查块号与正文）、项目级 always-apply 常驻规则、旧式章节迁移；检查器无 `ued/` 时仍检查接入项；术语口径表，「落码」统一为「分配编码」 |
| v10.11 | 新增规范版本记录：文档封面 `规范版本` 逐篇记录已对齐的规范，作用域 README `规范版本目标` 声明升级要求，基线 `spec_version` 盖章创建时规范；升级影响表见 `references/spec-upgrade.md` |
| v10.0 | 移除内置多应用模式：`design-doc` 只管单一作用域，多子系统拆到独立 skill `system-design-doc`（注册表、依赖钉住、系统发布）；共享库按普通子系统登记，不再固定 `shared/` |
| v9.0 | 把变更分为维护性与实质性：不改含义的整理记 `N（维护）`，不动状态、修订号与基线；首份基线在开发期可原地增删成员 |
| v8.0 | 全局术语表 `ued/glossary.md` 与文档术语块，一个术语只有一个权威定义 |
| v7.0 | Skill 入口改为按场景路由，流程拆入 `workflows/`；动代码前须先对照设计 |
| v6.0 | 文档与细项统一用整数修订号；产品版本 `vX.Y` 与文档修订分离，并引入产品基线（v6.1 起为 `baselines/vX.Y.yaml`） |
| v5.0 | 跨文档引用钉住被引文档的修订号，避免按旧代际理解新内容 |
| v4.0 | 规范按对象模型拆分：对象、状态、引用、版本各归独立文档，便于按需查阅 |
| v3.0 | 状态即基线：草稿免仪式、正式冻结；废弃只作用于正式对象，并加入定稿提示 |

## 快速开始

### 1. 安装

把本仓库的 `.agents/skills/design-doc/` 复制或链接到你项目的 `.agents/skills/design-doc/`。项目由多个子系统组成时，同时复制 `.agents/skills/system-design-doc/`；两个 skill 规则独立，各自带检查器。

### 2. 开始写

```
帮我写一份用户认证系统的系统设计文档（L4）
```

AI 会选用模板、分配编码，并默认标为「初稿」。提交前会问你哪些条目要定稿。

若要改功能、修 bug 或按文档写代码，它会先对照 `ued/`：该改设计则先改文档；实现时再看状态与当前产品基线，未定稿或未入基线的不会直接拿去改代码。

### 3. 登记项目信息（推荐）

在作用域 `README.md` 里写项目名和作者即可，不必另配模式开关。**单系统**直接把文档放在 `ued/` 下；**多子系统**由 `system-design-doc` 在 `ued/README.md` 维护子系统注册表，每个 `ued/{子系统}/` 再按同一套字段登记。

| 字段 | 说明 |
|------|------|
| `project_name` | 项目 / 子系统名称 |
| `author` / `maintainer` | 默认作者 |
| `project_code` | 可选前缀；留空则用 `FR-001` 这样的简洁编码 |
| `scope` | 作用域范围（可选） |
| `产品版本` | 当前产品版标签（如 `v1.0`）；对应一份产品基线，与文档修订号无关 |

写法见 [README 模板](./.agents/skills/design-doc/assets/templates/readme-template.md)。缺字段时 skill 会用默认值继续工作，并提醒补齐。

### 4. 检查文档（可选）

```
python3 .agents/skills/design-doc/scripts/check_docs.py -p ued
```

多子系统结构下，对每个子系统分别检查，并把项目术语表指过去：

```
python3 .agents/skills/design-doc/scripts/check_docs.py -p ued/{子系统} --glossary ued/glossary.md
python3 .agents/skills/system-design-doc/scripts/check_system.py -p ued
```

改标题或作废某条编码前，加上 `--refs {编码}` 可列出它出现过的所有位置。

## 文档层级

各层回答哪一句、写什么，以 [层级定义](./.agents/skills/design-doc/references/layer-system.md#层级定义) 为准。摘要：

| 层级 | 名称 | 核心问题 |
|-----|------|----------|
| L0 | 战略与愿景 | 为什么做 |
| L1 | 利益相关者需求 | 谁需要什么 |
| L2 | 系统 / 产品需求 | 必须满足什么 |
| L3 | 概念架构 | 准备用怎样的系统组织来满足 |
| L4 | 逻辑 / 系统设计 | 这个组织如何落成契约与结构 |
| L5 | 详细设计 | 局部机制如何算、如何转、如何配 |
| L6 | 验证与确认 | 如何证明满足要求 |

多数项目先写 L2 和 L4，其他层用到再补。

## 系统与子系统

当项目由多个子系统组成时，用配套的 [system-design-doc](./.agents/skills/system-design-doc/SKILL.md)：

- 系统根 `ued/README.md` 只写当前结构、架构入口、5 列子系统注册表与系统发布索引；**不持有**产品版本或基线
- `ued/architecture/system-architecture.md` 是子系统职责分配、系统交互与系统级约束（`SYS-CON`）的唯一真源，重大跨子系统决策记为 `SYS-ADR-*.md`；子系统内部 `CMP` 仅表达内部逻辑组件
- 每个 `ued/{子系统}/` 仍按 `design-doc` 维护，各自有产品版本与 `baselines/`
- 共享库没有特殊目录：需要时按普通子系统登记，可以有一个或几个，也可以不建
- 子系统的基线可钉住它依赖的其他子系统版本（精确 `vX.Y`）；系统发布清单按需锁定一组精确版本与 `architecture_rev`，避免接口错配，不要求覆盖全部正式子系统
- 接口不兼容变更走 MAJOR；消费方钉住精确版本，PATCH 不改公开语义

## 支持的 IDE

| IDE | 支持状态 |
|-----|---------|
| Cursor | ✅ 自动发现 |
| Windsurf | ✅ 自动发现 |
| Claude Code | ✅ 自动发现 |
| VS Code | ✅ 自动发现 |
| GitHub Copilot | ✅ 自动发现 |

## 相关技能

本仓库另含 [system-design-doc](./.agents/skills/system-design-doc/SKILL.md)，用于多子系统的系统级编排；两者可单独使用，也可搭配。

动笔写设计文档之前，若想先把问题想清楚，可以搭配 [multi-angle-thinking](https://github.com/reddishz/multi-angle-thinking)：从规划、事实、感受、风险、价值、创意六个角度讨论，再落到本仓库的分层文档。

## 了解更多

`design-doc` 规范入口是 [SKILL.md](./.agents/skills/design-doc/SKILL.md)，模板在 [模板库](./.agents/skills/design-doc/assets/templates/index.md)；`system-design-doc` 入口是 [SKILL.md](./.agents/skills/system-design-doc/SKILL.md)。其余细则：

- [规范索引](./.agents/skills/design-doc/references/README.md)
- [对象模型](./.agents/skills/design-doc/references/object-model.md) — 谁能改什么、如何作废与解冻
- [编码体系](./.agents/skills/design-doc/references/coding-system.md)
- [层级与目录](./.agents/skills/design-doc/references/layer-system.md)
- [状态定义](./.agents/skills/design-doc/references/status-definitions.md)
- [术语与概念](./.agents/skills/design-doc/references/glossary-conventions.md)
- [产品版本与基线](./.agents/skills/design-doc/references/product-version.md)
- [规范版本与逐篇迁移](./.agents/skills/design-doc/references/spec-upgrade.md)
- [审核指南](./.agents/skills/design-doc/references/review-guidelines.md)
- [检查脚本](./.agents/skills/design-doc/scripts/check_docs.py)

Agent Skills / IDE 手册见 [docs/](./docs/README.md)。产品需求写法也可参考 [srs.pub](https://srs.pub/)。

## 许可证

[MIT License](./LICENSE) — 可用于商业和非商业项目
