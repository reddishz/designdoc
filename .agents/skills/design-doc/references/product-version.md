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

升版/补丁**不解冻**任何设计文档，**不改**修订号，**不改**本文引用钉住表；对本次相对**前一基线文件**的 `added` / `removed` **回写** `引入版本` / `退出版本` 缓存（见[基线谱系缓存](#基线谱系缓存)）。`引入`/`退出` 取值仍为两段 `vX.Y`（成员归属文件），不是 `vX.Y.Z`。

定稿 **MUST NOT** 写 `baselines/`。AI **MUST NOT** 未经确认自行 `--bump-product`。

### 相对当前基线的漂移

对照作用域 README 当前 `产品版本` 对应的 `baselines/{vX.Y}.yaml` 与**当前**全部 `细项状态=正式` 的细项：

| 类 | 含义 |
|----|------|
| 尚无基线文件 | 无 `baselines/{当前产品版本}.yaml`（及尚无任何 `baselines/v*.yaml`）→「待建首份基线」 |
| 未入基线 | 正式细项编码不在当前基线 `items` 中 |
| 已退出正式集 | 基线有、当前已非正式 → 升版时进 `removed` |
| revision 落后 | 两处都有，但活正式 `修订版本号` > 基线 `revision` → 补丁/升版时进 `changed` |

无待建且三类漂移皆空 → 不必为发版打扰用户。

## 产品基线（MANDATORY）

| 项 | 规则 |
|----|------|
| 含义 | 相对某两段产品版本：允许作为实现依据的细项集合（含各 tip 上的 revision） |
| 成员条件 | `细项状态 = 正式`；**全部类型码** |
| 非成员 | `初稿` / `草案` / `废弃`；**EVAL 不是基线成员** |
| 承载 | `baselines/vX.Y.yaml`（**一两段版本一文件**） |
| 可变性 | **仅当前** README `产品版本` 对应文件允许 PATCH 更新；历史文件（已有更新的 `vX.Y` 后继）**MUST NOT** 再改 |
| SSoT | `baselines/*.yaml`；对象上 `引入版本` / `退出版本` 为缓存 |

文档整篇 `正式` ≠ 可实现。实现门禁见下文。

**EVAL**：`对照版本` MAY 为 `vX.Y` 或 tip `vX.Y.Z`（精确到某次 PATCH）；对应文件仍是 `baselines/vX.Y.yaml`。

### 文件布局

```text
ued/{app}/baselines/
  v5.25.yaml          # 历史：只读
  v5.26.yaml          # 当前：可 PATCH
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
added:   [CODE, ...]            # 相对 prev 文件 items
removed: [CODE, ...]
changed: [CODE, ...]
items:
  - code: FR-001
    type: FR
    title: "..."
    revision: 2
    doc: L2-001
```

| 块 | 规则 |
|----|------|
| `full_version` | MUST；前两段 = `product_version`；新建为 `vX.Y.0`；PATCH 时 Z+1 |
| `created` / `updated` | MUST；新建时相同；PATCH 只改 `updated` |
| `prev` | 首版 `null`；否则 MUST 为完整 SemVer，且 `baselines/{其两段}.yaml` 存在；**MUST NOT** 按 patch 建文件名 |
| `patch_log` | MUST；每升一次 tip（含 `.0`）追加一条；**MUST NOT** 改写旧条 |
| `added`/`removed`/`changed` | 相对 **`prev` 指向的那份基线文件** 的 `items` 重算（不是相对上一 patch 快照） |
| `items` | 完整成员表；按 `code` 字典序 |

存量缺 `full_version` 时检查器 WARNING，并按 `vX.Y.0` 理解；`prev` 若仍为两段 `vX.Y`，按该文件解析，WARNING 建议改为当时 tip。

### 三种动作

| 动作 | 何时 | 文件 | 版本号 |
|------|------|------|--------|
| **PATCH** | 仅 revision 落后 / 澄清纠错；**无**成员 `added`/`removed` | **更新当前** `vX.Y.yaml` | `full_version` 的 Z+1；README 两段号不变 |
| **MINOR** | 有新编码纳入、或能力向收口需新参考点 | **新建** `vX.(Y+1).yaml`；旧文件冻结 | README→新两段；`full_version`=`vX.(Y+1).0`；`prev`=旧 tip |
| **MAJOR** | 见[询问规则](#何时询问) | **新建** `v(X+1).0.yaml` | README→`v(X+1).0`；`full_version`=`v(X+1).0.0` |

工具：`check_docs.py --bump-product --patch|--minor|--major`（见脚本帮助）。

## 升产品版本（MANDATORY）

含 **PATCH**（更新当前 tip）与 **MINOR/MAJOR**（立新基线文件）。**执行时机**：用户确认或 Checkpoint 5 确认。AI **MUST NOT** 自行执行。

### 何时询问

定稿与提交提示阶段（Checkpoint 5）只要用户未选「暂不提交」，**MUST** 呈现[漂移](#相对当前基线的漂移)短表。然后：

1. **询问首份基线（MUST，尚无 `baselines/v*.yaml`）**：默认建议沿用 README 当前 `vX.Y` 生成文件（`full_version`=`vX.Y.0`），**MUST NOT** 因尚无文件就默认劝升次版本。
2. **仅 revision 落后（无未入基线 / 无退出）→ 建议 PATCH（MUST 问）**：默认建议「更新当前基线 tip（`full_version` Z+1），不改 README 两段号」。用户否决 → 不改基线，新 revision 仍不可实现。
3. **有未入基线或已退出正式集 → 建议 MINOR（MUST 问）**：默认 `vX.(Y+1)` 新建文件。用户否决 → 不升，新编码不可实现。
4. **询问主版本（SHOULD）**：在已决定「要 MINOR / MAJOR / 首份」或用户主动发版时，命中任一条再问是否 MAJOR（`v(X+1).0`）；否决则保持 MINOR（或首份沿用号）：
   - L0 目标 / 愿景类细项解冻或新定稿 ≥ 1
   - 新 ADR 定稿，或 ADR 废弃 ≥ 1
   - 有替代编码的废弃 ≥ 1
   - 新定稿的 FR / NFR / DEC ≥ 8，或解冻修订的 FR / NFR / DEC ≥ 5
   - AC / ALG 等支撑细项条数 **MUST NOT** 单独触发主版本询问
5. 顺序：短表 → 首份或 PATCH/MINOR 判断 → 若走立新基线且命中再问 MAJOR。无漂移 → **MUST NOT** 追问。

### 执行步骤

**PATCH**

1. 打开当前 `baselines/{README 产品版本}.yaml`。
2. 扫描正式集；若相对**本文件当前 items** 出现编码 `added`/`removed` → **MUST** 停下改走 MINOR。
3. `full_version` Z+1；刷 `updated`；追加 `patch_log`；重写 `items` 与相对 `prev` 文件的增量三块。
4. **MUST NOT** 改 README `产品版本`；MAY 在发版记录追加一行（完整版本号写入说明）。
5. 本动作无新 `added`/`removed` 编码时 **MUST NOT** 改谱系缓存。

**MINOR / MAJOR（立新基线）**

1. 定号：MINOR `vX.(Y+1)`，MAJOR `v(X+1).0`；首份 MAY 沿用当前两段号。
2. 新建 `baselines/{新 vX.Y}.yaml`（已存在则停下）；`full_version`=`{新}.0`；`prev`=当前文件 tip；`created`=`updated`=当天。
3. 回写谱系：本版相对 prev 文件的 `added`→`引入版本`，`removed`→`退出版本`（值为**新两段** `vX.Y`）。
4. 更新 README `产品版本` 与发版记录。**MUST NOT** 写 git / svn / 构建号 / 包路径。

## 据文档实现与产品基线

改功能/修缺陷须先走 [SKILL.md · 变更代码前](../SKILL.md#变更代码前消费侧mandatory)。实现门禁：目标细项 MUST `正式` 且出现在**当前** `baselines/{产品版本}.yaml` 的 `items` 中，且实现所依据的语义对应基线中的 `revision`（落后则先 PATCH 或立新基线）。新编码未入基线 → **MUST NOT** 实现（须 MINOR）。

**运行中版本展示（SHOULD）**：发运或改行为时，SHOULD 使 `--version` / 启动日志 / 关于页等可见版本与当前基线 `full_version`（`vX.Y.Z`）一致；与 git SHA 正交。设计文档 **MUST NOT** 登记构建号或包路径。

## 基线谱系缓存

| 项 | 规则 |
|----|------|
| 真源 | `baselines/*.yaml` |
| 写入者 | 仅立新基线时对 `added`/`removed` 回写；PATCH 不改 |
| 取值 | 两段 `vX.Y` |
| 禁止 | 定稿/解冻/日常编辑手填；`初稿` 不得带谱系 |

## 存量迁移

1. 补 README `产品版本`（若缺）。
2. 首份或存量文件补 `full_version`（缺则视为 `vX.Y.0`）、`created`/`updated`、`patch_log`；`prev` 两段式可逐步改为 tip SemVer。
3. **MUST NOT** 把历史 `vX.Y.yaml` 拆成多个 `vX.Y.Z.yaml`。
