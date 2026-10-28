# 产品版本与产品基线

产品版本是**产品级**发版标签，与设计对象的[修订版本号](status-definitions.md#变更流程与版本号统一mandatory)正交。产品基线是某一**两段式**产品版本（`vX.Y`）下可实现细项的快照文件。

**渊源（裁剪，非符合性目标）**：配置基线与「基线 + 已批准变更」区分参考 ISO 10007；完整版本号语义参考 SemVer（`MAJOR.MINOR.PATCH`）。本 skill **不以**这些标准的符合性为交付目标。

本技能 **MUST NOT** 在 README 维护第二份引入/退出总表，**MUST NOT** 在设计文档里登记代码仓库、构建号或包路径。消费方可自行从基线快照衍生「功能特性」视图；技能只维护基线快照本身。

## 两段式与完整版本号

| 用途 | 形态 | 例子 |
|------|------|------|
| README `产品版本`、基线**文件名**、`product_version` 字段 | 两段 `vX.Y` | `v5.26`、`baselines/v5.26.yaml` |
| 当前 tip、`full_version`、`prev`、软件展示、EVAL 精确对照 | SemVer `vX.Y.Z` | `v5.26.2`、`prev: v5.25.3` |

**MUST NOT** 按 `vX.Y.Z` 再建基线文件（禁止一 patch 一文件）。`full_version` 的前两段 **MUST** 与本文件 `product_version` 一致。

## 产品版本（记录型）

| 项 | 规则 |
|----|------|
| 承载 | 当前作用域 `README.md` 项目元信息字段 `产品版本`，取值 `vX.Y` |
| 初值 | `v1.0`（尚无基线文件时） |
| 写入 | 仅[三种动作](#三种动作)中的 MINOR/MAJOR 时改两段号；**PATCH 不改** README `产品版本` |
| 多应用 | 每个应用级 README 各自一份；顶层多应用 README **MUST NOT** 充当某一应用的产品版本源 |
| 共享作用域 | `ued/shared/` 有独立 `README.md` 时自成一个作用域，拥有自己的 `产品版本` 与 `baselines/`；**MUST NOT** 并入任一应用，也 **MUST NOT** 由顶层 README 代管 |

立新基线（MINOR/MAJOR）**不解冻**任何设计文档，**不改**修订号，**不改**本文引用钉住表；同时回写 `引入版本` / `退出版本` 缓存（首份基线在其首次冻结时回写，见[基线谱系缓存](#基线谱系缓存)）。PATCH 只更新当前工作集，不回写谱系；成员增删仅限首份基线。`引入`/`退出` 取值仍为两段 `vX.Y`（成员归属文件），不是 `vX.Y.Z`。

定稿 **MUST NOT** 写 `baselines/`。AI **MUST NOT** 未经确认自行 `--bump-product`。

### 相对当前基线的漂移

对照作用域 README 当前 `产品版本` 对应的 `baselines/{vX.Y}.yaml` 与**当前**全部 `细项状态=正式` 的细项：

| 类 | 含义 |
|----|------|
| 尚无基线文件 | 无 `baselines/{当前产品版本}.yaml`（及尚无任何 `baselines/v*.yaml`）→「待建首份基线」 |
| 未入基线 | 正式细项编码不在当前基线 `items` 中 → 首份 PATCH 纳入；非首份须立新基线 |
| 已退出正式集 | 基线有、当前已非正式 → 首份 PATCH 从 `items` 移除；非首份立新基线时进 `removed` |
| revision 落后 | 两处都有，但活正式 `修订版本号` > 基线 `revision` → 首份 PATCH 直接同步 `items.revision`（增量字段仍空）；非首份 PATCH 计入 `changed` |

标题差异（维护性名称调整）不计入漂移，见[维护性变更与基线快照](#维护性变更与基线快照)。

无待建且三类漂移皆空 → 不必更新基线。

## 产品基线（MANDATORY）

| 项 | 规则 |
|----|------|
| 含义 | 相对某两段产品版本：允许作为实现依据的细项集合（含各 tip 上的 revision） |
| 成员条件 | `细项状态 = 正式`；**全部类型码** |
| 非成员 | `初稿` / `草案` / `废弃`；**EVAL 不是基线成员** |
| 承载 | `baselines/vX.Y.yaml`（**一两段版本一文件**） |
| 可变性 | **首份基线**（作用域内最早一份，通常是 `v1.0`）在尚无后继时可用 PATCH 原地增删成员与同步 revision；**其他基线**创建后成员集合固定，仅 revision 同步可 PATCH；任一基线一旦有 `vX.Y` 后继即只读 |
| SSoT | `baselines/*.yaml`；对象上 `引入版本` / `退出版本` 为缓存 |

文档整篇 `正式` ≠ 可实现。实现门禁见下文。

**EVAL**：`对照版本` SHOULD 指向已冻结的 `vX.Y`（或该冻结基线的 tip）；对应文件是 `baselines/vX.Y.yaml`。若引用当前工作 tip `vX.Y.Z`，**MUST** 同时记录日期，并注明该 tip 会被后续 PATCH 覆盖、不可复现。

### 当前基线与历史基线

- **当前基线**是最新的 `vX.Y` 文件。**首份基线**（`prev` 为空，通常是 `v1.0`）是初始开发基线，允许在尚无后继时用 PATCH 增删成员、同步 revision、纠错。
- **首份之后**，成员集合在创建时固定；成员进出 **MUST** 立新基线。当前基线仍可用 PATCH 同步 revision、纠错。
- **历史基线**是已冻结快照：一旦存在更新的 `vX.Y` 后继，该文件 **MUST NOT** 再修改。
- **冻结只发生在立新基线时**（MINOR/MAJOR）；PATCH 不是冻结，也不形成新的历史边界。
- **PATCH 不保留历史内容**：`items` 原地覆盖，旧 tip 的成员与 revision 不单独保存；`full_version` 是当前工作 tip，不是不可变快照标识。需要可复现的对照时，使用已冻结的 `vX.Y` 基线。
- 例：`v1.0.0` → PATCH `v1.0.1`（+FR-002）→ PATCH `v1.0.2`（−FLW-001）→ MINOR `v1.1.0`（冻结；`v1.0.yaml` 自此只读；此后成员变化须立 `v1.2`）。

### 首份基线的开发期例外

| 规则 | 首份基线（通常 `v1.0`） | 其他基线 |
|------|------------------------|----------|
| 成员增删 | PATCH 原地修改 | **MUST** 立新基线（MINOR/MAJOR） |
| revision 变化 | PATCH 原地同步 | PATCH 原地同步 |
| 澄清纠错 | PATCH 原地修改 | PATCH 原地修改 |
| 出现后继之后 | 永久只读 | 永久只读 |

「首份」以 `prev` 为空判定，不写死版本字符串；存量项目从 `v5.26` 起家时，`v5.26` 就是首份基线。

### 文件布局

```text
ued/{app}/baselines/
  v5.25.yaml          # 历史：只读
  v5.26.yaml          # 当前：可 PATCH revision（首份基线另可增删成员）
```

### 快照 schema

```yaml
product_version: v5.26          # 与文件名一致；两段式
full_version: v5.26.2           # 本文件当前 tip（SemVer）
created: 2026-10-13             # 本 vX.Y 文件首次建立；此后不变
updated: 2026-10-13             # 最近一次写入（含 PATCH）
prev: v5.25.3                   # 新建本文件时前一基线 tip；PATCH 不改；首版 null
patch_log:
  - full_version: v5.26.0
    date: 2026-10-13
    note: "立新基线说明"
  - full_version: v5.26.2
    date: 2026-10-13
    note: "纠错说明"
added:   [CODE, ...]            # 相对 prev 冻结基线的成员差异；首份恒空
removed: [CODE, ...]
changed: [CODE, ...]            # 相对 prev 的 revision 增补；首份恒空
items:
  - code: FR-001
    type: FR
    title: "..."
    revision: 2
    doc: L2-001
```

| 块 | 规则 |
|----|------|
| `full_version` | MUST；前两段 = `product_version`；新建为 `vX.Y.0`；PATCH 时 Z+1；是当前工作 tip，不是不可变快照标识 |
| `created` / `updated` | MUST；新建时相同；PATCH 只改 `updated` |
| `prev` | 首版 `null`；否则 MUST 为完整 SemVer，且 `baselines/{其两段}.yaml` 存在；**MUST NOT** 按 patch 建文件名 |
| `patch_log` | MUST；每升一次 tip（含 `.0`）追加一条；**MUST NOT** 改写旧条；只记版本/日期/说明，不保存当次 `items` |
| `added`/`removed`/`changed` | 只表达**基线版本之间**的成员与 revision 差异；相对 `prev` 指向的冻结基线重算（累计值，不是相对上一 PATCH），首份基线无前驱、三块恒空；**MUST NOT** 记录开发期操作历史 |
| `items` | 首份基线的 PATCH 可增删成员（只改 `items`，不写增量字段）；其他基线创建后成员不变；按 `code` 字典序 |

存量缺 `full_version` 时检查器 WARNING，并按 `vX.Y.0` 理解；`prev` 若仍为两段 `vX.Y`，按该文件解析，WARNING 建议改为当时 tip。

### 三种动作

| 动作 | 何时 | 文件 | 版本号 |
|------|------|------|--------|
| **PATCH** | 首份基线：revision 同步、成员增删、澄清纠错（成员增删只改 `items`，增量字段恒空）；其他基线：仅 revision 同步与澄清纠错；均不冻结基线 | **更新当前** `vX.Y.yaml` | `full_version` 的 Z+1；README 两段号不变 |
| **MINOR** | 首份之后成员集合需变化（**MUST**）；或需要冻结独立参考点（对外发版、里程碑、评估基线等） | **新建** `vX.(Y+1).yaml`；旧文件冻结 | README→新两段；`full_version`=`vX.(Y+1).0`；`prev`=旧 tip |
| **MAJOR** | 见[询问规则](#何时询问) | **新建** `v(X+1).0.yaml` | README→`v(X+1).0`；`full_version`=`v(X+1).0.0` |

首份基线可以反复增删成员；首份之后，成员变化 **MUST** 立新基线；非成员变化的冻结（如对外发版）也走 MINOR/MAJOR。

工具：`check_docs.py --bump-product --patch|--minor|--major`（见脚本帮助）。

### 维护性变更与基线快照

- **不动基线**：非语义维护（统一用语、名称调整等）**MUST NOT** 改动 `baselines/vX.Y.yaml`。成员集合与 `revision` 均不变，`added` / `removed` / `changed` 均由 `code` 与 `revision` 计算，标题维护不会进入 `changed`。见 [status-definitions.md · 维护性变更](status-definitions.md#维护性变更第三维度mandatory)。
- **标题是快照**：`items.title` 记录写基线当时的标题，允许暂时落后于现行标题；标题滞后**不构成**漂移，**MUST NOT** 为刷新标题单独发版或 PATCH。
- **自然刷新**：下一次 PATCH / MINOR 重写 `items` 时按现行标题更新；历史基线文件仍为只读快照。
- **实现门禁**：只比对 `code` 是否存在、`revision` 是否对齐，**不比对标题**。

## 升产品版本（MANDATORY）

含 **PATCH**（更新当前工作集）与 **MINOR/MAJOR**（立新基线文件）。**执行时机**：用户确认或 Checkpoint 5 确认。AI **MUST NOT** 自行执行。

### 何时询问

定稿与提交提示阶段（Checkpoint 5）只要用户未选「暂不提交」，**MUST** 呈现[漂移](#相对当前基线的漂移)短表。然后：

1. **询问首份基线（MUST，尚无 `baselines/v*.yaml`）**：默认建议沿用 README 当前 `vX.Y` 生成文件（`full_version`=`vX.Y.0`），**MUST NOT** 因尚无文件就默认劝升次版本。
2. **首份基线有漂移 → 建议 PATCH（MUST 问）**：默认把首份工作集更新到最新正式集（revision 同步、成员增删；`full_version` Z+1），不改 README 两段号。PATCH 是同步动作，不是成员变更审批；成员增删只改 `items`，不写 `added`/`removed`。用户否决 → 不改基线，变动仍不可实现。
3. **非首份基线的漂移**：
   - 仅 revision 落后 → 建议 PATCH（MUST 问）。
   - 有未入基线或已退出正式集 → **MUST** 建议 MINOR 立新基线（成员集合不能原地改）；用户否决 → 新编码不可实现、退出仍未反映。
4. **询问主版本（SHOULD）**：在已决定「要 MINOR / MAJOR / 首份」或用户主动发版时，命中任一条再问是否 MAJOR（`v(X+1).0`）；否决则保持 MINOR（或首份沿用号）：
   - L0 目标 / 愿景类细项解冻或新定稿 ≥ 1
   - 新 ADR 定稿，或 ADR 废弃 ≥ 1
   - 有替代编码的废弃 ≥ 1
   - 新定稿的 FR / NFR / DEC ≥ 8，或解冻修订的 FR / NFR / DEC ≥ 5
   - AC / ALG 等支撑细项条数 **MUST NOT** 单独触发主版本询问
5. 顺序：短表 → 首份或 PATCH/MINOR 判断 → 若走立新基线且命中再问 MAJOR。无漂移且用户未要求发版 → **MUST NOT** 追问。

### 执行步骤

**PATCH**

1. 打开当前 `baselines/{README 产品版本}.yaml`。
2. 判首份：`prev` 为空即首份。首份允许成员增删；非首份若扫描出相对当前 `items` 的成员进出，**MUST** 停下改走 MINOR/MAJOR。
3. 增量字段：首份基线无前驱，`added` / `removed` / `changed` **MUST** 均为空；其他基线按相对 `prev` 冻结基线重算（累计值，不是相对上一次 PATCH）。
4. `full_version` Z+1；刷 `updated`；追加 `patch_log`；重写 `items` 与增量三块。
5. **MUST NOT** 改 README `产品版本`；MAY 在发版记录追加一行（完整版本号写入说明）。
6. **MUST NOT** 改谱系缓存：PATCH 只同步 revision；首份的成员在其首次冻结时按冻结 `items` 回写，其他基线的成员变化在立新基线时按 `added` / `removed` 回写。

**MINOR / MAJOR（立新基线）**

1. 定号：MINOR `vX.(Y+1)`，MAJOR `v(X+1).0`；首份 MAY 沿用当前两段号。
2. 新建 `baselines/{新 vX.Y}.yaml`（已存在则停下）；`full_version`=`{新}.0`；`prev`=当前文件 tip；`created`=`updated`=当天。当前文件自此成为历史基线，**MUST NOT** 再改。
3. 回写谱系：冻结首份时，其 `items` 中的成员归属**首份两段**（开发期增删不另记）；本次相对 prev 的 `added` / `removed` 归属**新两段**；`退出版本` 只写给当前已 `废弃` 的条目。
4. 更新 README `产品版本` 与发版记录。**MUST NOT** 写 git / svn / 构建号 / 包路径。

## 据文档实现与产品基线

改功能/修缺陷须先走 [before-code-change.md](workflows/before-code-change.md)。实现门禁见 [implement-from-design.md](workflows/implement-from-design.md)：目标细项 MUST `正式` 且出现在**当前** `baselines/{产品版本}.yaml` 的 `items` 中，且 revision 对齐（落后则先 PATCH）。新编码未入基线 → **MUST NOT** 实现：首份基线先 PATCH 同步当前工作集（不是成员变更审批）；已有前驱的基线 MUST 立新基线后再实现。

**运行中版本展示（SHOULD）**：发运或改行为时，SHOULD 使 `--version` / 启动日志 / 关于页等可见版本与当前基线 `full_version`（`vX.Y.Z`）一致；与 git SHA 正交。设计文档 **MUST NOT** 登记构建号或包路径。

## 基线谱系缓存

| 项 | 规则 |
|----|------|
| 真源 | `baselines/*.yaml` |
| 写入者 | 仅 MINOR/MAJOR 立新基线时回写（首份按冻结 `items` 归属 + 本次 `added` / `removed`）；PATCH 不改 |
| 取值 | 两段 `vX.Y` |
| 禁止 | 定稿/解冻/日常编辑手填；`初稿` 不得带谱系 |

首份基线创建时不写谱系；首次冻结时按冻结 `items` 把成员归属首份版本，并清掉开发期残留的同版本 `引入版本` / `退出版本`（曾在工作集加入、冻结前已退出的成员不保留首份谱系）。首份之后的成员变化只发生在立新基线时，按 `added` / `removed` 归属新版本，不重复归属旧版本。PATCH 只同步 revision，不写谱系。

## 存量迁移

1. 补 README `产品版本`（若缺）。
2. 首份或存量文件补 `full_version`（缺则视为 `vX.Y.0`）、`created`/`updated`、`patch_log`；`prev` 两段式可逐步改为 tip SemVer。
3. 首份基线若带非空 `added` / `removed` / `changed`（旧口径把开发期成员记入增量），置空；`items` 不变。
4. **MUST NOT** 把历史 `vX.Y.yaml` 拆成多个 `vX.Y.Z.yaml`。
