---
name: design-doc
description: 规范 AI 在 `ued/` 目录下创建、修改、审查产品设计文档时的行为规则、层级体系、目录结构、格式与模板选择。用于约束 AI 按既定意图生成战略与愿景、利益相关者需求、系统/产品需求、概念架构、逻辑/系统设计、详细设计、验证与确认等文档。
license: MIT
metadata:
  version: "5.0"
  author: "designdoc"
  spec-compliance: 遵循 Agent Skills 开放标准
  tags: [design, documentation, product, architecture, specification]
  triggers:
    - "设计文档"
    - "需求文档"
    - "设计方案"
    - "增加功能"
    - "废弃功能"
    - "设计规范"
    - "文档规范"
    - "功能需求"
  trigger_principle: "设计文档维护涉及复杂的编码体系和规范约束，需要明确的人工意图确认以避免误触发复杂流程"
  capabilities:
    - "多层级设计文档生成 (L0-L6)"
    - "全局唯一编码管理与冲突检测"
    - "自动化文档规范性审查"
    - "跨文档引用一致性维护"
compatibility: 需能访问 ued/ 目录，可选从运行环境获取当前执行主体标识
---

# 产品设计文档规范（UED）

本 skill **约束 AI 的执行方式**，不是人类写作教程。规则本体在 `references/`；本文只承载身份、不变量索引与可执行程序。包内同一规则只允许一种表述，发现不一致当轮合并。措辞强度见 [coding-system.md · 需求级别说明](references/coding-system.md#需求级别说明)。

**两类动作**：写 / 改 / 审查 `ued/` 文档 → 按下方程序；**据文档实现代码** → 先读 [据文档实现](#据文档实现消费侧mandatory)。

## 不变量索引

| 主题 | 单点 |
|------|------|
| 对象 × 字段 × 状态、锁定与动作 | [object-model.md](references/object-model.md) |
| 编码形态、类型码表、属性封闭集、定义块、引用、本文引用、分配 | [coding-system.md](references/coding-system.md) |
| `IF` / `ACT` / `PLN`、UC / FR / FLW、ADR 与 DEC | [type-profiles.md](references/type-profiles.md) |
| 四态、门控、版本号、流转伴随 / 记录型含义 | [status-definitions.md](references/status-definitions.md) |
| 细项 / 文档作废步骤 | [item-deprecation.md](references/item-deprecation.md) / [doc-deprecation.md](references/doc-deprecation.md) |
| 检查项 | [review-guidelines.md](references/review-guidelines.md) |
| 层级与目录 | [layer-system.md](references/layer-system.md) |
| 词汇表 | [glossary-conventions.md](references/glossary-conventions.md) |
| 模板边界与整篇型共用 | [assets/templates/index.md](assets/templates/index.md) |

- **引用锚点**：细项编码与文档编码是 `ued/` 内唯一允许的语义引用锚点；**MUST NOT** 用章节编号（`§x.y`、`第 x 章`、`见上文`）。跨文件链接路径 MUST 以 `./` 或 `../` 开头（见 [交叉引用规则 · 链接路径](references/coding-system.md#链接路径mandatory)）。可独立成立的规则 MUST 先落码再被引用。规范条文本身不纳入细项编码，指向条款用 `文件#标题锚点`。
- **存在性锁定**：编号一经分配永久占用，任何状态 **MUST NOT** 删除或复用；放弃走作废。权限切片见 [object-model.md · 锁定矩阵](references/object-model.md#锁定矩阵mandatory)。
- **`ued/` 不得含可执行代码**（算法、契约、状态机可以）。REF 可收录外部资料中的代码示例。
- **层级按最小必要**：未指定时默认 L2 或 L4，**MUST NOT** 无指令一次生成 L0–L6。对层判据与补齐信号见 [layer-system.md · 分层问题](references/layer-system.md#分层问题对层判据) / [按需启用原则](references/layer-system.md#按需启用原则)。
- **模板即复制源**：`assets/templates/` 违例等同规范违例。哨兵见 [模板边界](assets/templates/index.md#模板边界哨兵)，共用填写规则见 [整篇型模板共用](assets/templates/index.md#整篇型模板共用)。

## AI 运行时配置解析规则

AI 在创建或编辑设计文档时，模板中的 `{当前用户.作者}` 与 `{项目编码}` 按当前作用域的 `README.md` 解析；额外配置文件 **已移除且 MUST NOT 继续创建或使用**。

**作用域判定规则**：
1. **单应用模式**：若业务文档直接位于 `ued/` 下，则 `ued/README.md` 同时承担入口、项目元信息、编码模式、编码计数器与全局索引。
2. **多应用模式**：若存在多个应用，则每个应用 **MUST** 位于 `ued/{app-name}/` 子目录下。
3. **多应用顶层 README**：`ued/README.md` 仅承担多应用总入口、应用注册表、公共规则与跨应用导航，**MUST NOT** 作为某个具体应用的项目编码来源。
4. **多应用应用级 README**：`ued/{app-name}/README.md` 承担该应用的项目元信息、编码模式、编码计数器、文档导航与应用级全局索引。

**解析顺序**（各字段分别按下列顺序取第一个可用值）：

**作者字段**：
1. 当前作用域 `README.md` 中的项目元信息字段（如 `author` / `maintainer`）
2. 运行环境可识别的当前执行主体标识（如工具可获取）
3. 默认值：`[designdoc](https://github.com/reddishz/designdoc)`（本技能标识，原样写入，渲染为可追溯链接）

**项目编码字段（高级扩展用法）**：
1. 当前作用域 `README.md` 中的项目元信息字段 `project_code`
2. 顶层 `ued/README.md` 的应用注册表中，与目标应用目录匹配的 `project_code`（仅多应用模式下辅助校验）
3. **默认值**：无（即禁用项目编码前缀，采用简洁编码格式）

**启用规则**：AI **MUST NOT** 启用项目编码前缀，除非已显式配置且请求发起方明确确认。默认情况下，一律采用简洁编码格式（如 `FR-001`）。

**提示规则（MANDATORY）**：
- 当 AI 识别到 `ued/` 下存在多个应用或多个独立业务域的设计文档时，**MUST** 提示将应用迁移到 `ued/{app-name}/` 子目录，并在顶层 `ued/README.md` 注册应用编码，同时在应用级 `README.md` 中定义 `project_code`。
- 当 AI 识别到当前仓库已存在某一应用的设计文档，而当前任务是在此基础上新增另一应用的设计文档时，**MUST** 在创建前提示采用多应用模式，并为新应用补齐子目录 `README.md` 与顶层应用注册表。
- 若尚未配置 `project_code`，AI **MUST** 先提示补充配置，再进入编码分配阶段；未获确认前，**MUST NOT** 擅自启用前缀。
- 上述提示的目标是确保多个应用并存时，编码、索引、引用与废弃追溯仍可保持全局唯一且语义清晰。

若作用域 `README.md` 不存在或未声明相应字段，首次使用时**直接采用上述解析链末位的默认值继续工作**。

随后 AI **SHOULD** 提醒补充或编辑对应作用域的 `README.md` 元信息区块，特别是当检测到目录中存在多个应用或新增独立应用迹象时。

**项目编码规则（高级模式下）**：2-5 位、大写字母开头，其余各位可为大写字母或数字（如 `CRM`、`ERP`、`W3T`）；MUST NOT 与类型码同形，也 MUST NOT 形如 `L` 加数字。完整字符集与消歧约束见 [coding-system.md · 项目编码规则](references/coding-system.md#项目编码规则)。

**README 元信息最小字段（RECOMMENDED）**：`project_name`、`project_code`、`doc_mode`（`single-app` 或 `multi-app`）、`scope`、`author` / `maintainer`。

## 快速操作指南

| Checkpoint | 时机 | 暂停条件 |
|------------|------|----------|
| 1 | 生成初稿后 | 确认大纲与核心细项 |
| 2 | 分配编码 | 批量新增或核心业务规则变更 |
| 3 | 大规模编码变更或废弃前 | 二次确认 |
| 4 | 标注 `废弃` 前 | 确认废弃原因与替代方案 |
| 5 | 本轮实质修改收尾 | 提交提示 + 本轮未冻结对象定稿确认 |

写作与审查门禁：起草前声明「引用只用编码」；可独立语义先落码；审查命中章节编号引用即 A 级阻断；复查确认零章节编号引用；未过门禁不得合并或正式发布。

### 创建新文档

1. 确认 `ued/` 目录结构。
2. 按任务意图从 `assets/templates/` 取对应模板；**默认按需裁剪，禁止无指令全量生成 L0-L6**。
3. 按模板生成，**MUST NOT** 含具体实现代码。
4. **Checkpoint 1**：暂停，等确认大纲与核心细项。
5. 确认后按「分配新编码」分配 ID。
6. 立即更新当前作用域 `README.md` 与文档末尾清单（状态列默认 `初稿`）。单应用改 `ued/README.md`；多应用改 `ued/{app-name}/README.md`，仅应用注册或跨应用导航时再改顶层。
7. 自检：与上层目标无冲突；标题适度宽泛（[标题命名规范](references/coding-system.md#标题命名规范适度宽泛)）；类型码只在定义层写定义块（[细项定义层级](references/coding-system.md#细项定义层级mandatory)）——详细设计里的「系统应当」先落到 L2 的 FR / NFR；按 [review-guidelines.md](references/review-guidelines.md) 过一遍锁定、措辞与流程。

### 分配新编码

1. 读当前作用域 `README.md` 对应类型码的「下一可用编号」。
2. 一律用该号；发现缺口（不分状态）先修索引或补废弃记录，**MUST NOT** 直接分配缺口编号。
3. 用 Grep 确认目标编码在 `ued/` 未被使用。
4. **Checkpoint 2**：批量或核心规则变更时暂停确认标题与定义。
5. 在索引表按编码数字升序插入，**MUST NOT** 追加到小节末尾。
6. 更新文档清单 + 全局索引 + 计数器；「下一可用编号」= 新编号 + 1。
7. 验证正文、清单、README 三方一致，升序、无缺口、变更记录倒序。
8. **Checkpoint 3**：大规模变更或废弃前二次确认。

分配步骤见上文；缺口与计数器等式见 [object-model.md · 锁定矩阵](references/object-model.md#锁定矩阵mandatory)；索引操作见 [coding-system.md · 编码分配管理](references/coding-system.md#编码分配管理)。

### 处理编码含义变更请求

响应触发（三类）：（a）改已分配编码的 ID 或类型码——**不区分状态**；（b）改已 `正式` / `草案` 对象的**标题**；（c）改已 `正式` 编码的业务含义。`初稿` 改标题（须同步引用）与 `初稿` / `草案` 改正文不属此列。通道见 [object-model.md · 锁定矩阵](references/object-model.md#锁定矩阵mandatory)。AI **MUST** 按以下方式响应（对请求发起方复述本框即可，不必另套话术）：

```
❌ 违规检测：禁止就地修改编码 ID / 类型码（绝对锁定）；禁止修改 `正式` / `草案` 对象的标题；禁止修改已正式化编码的业务含义
⚠️  系统约束：编码 ID 与类型码一经分配永不修改（与状态无关）；标题与业务含义自进入正式基线后永不就地修改
✅ 正确流程：
1. 判定对象状态：`初稿` → 走下方"初稿处理"；`正式` / `草案` → 走下方"废弃 + 新增"
2. 初稿处理：改标题 → 先用 `check_docs.py --refs {编码}` 定位全部引用处并同步修改；类型码用错 → 确认后作废该细项（`初稿→废弃`），再按分配流程以正确类型码新建（原编号永不复用）
3. 正式 / 草案废弃：外部确认 → 标注原编码为"废弃"并记录原因 → 为新含义分配下一个可用编码（如 FR-016）
4. 影响评估：提示检查受影响的下层引用关系，并用 `--refs` 查看依赖两表
```

> 若诉求仅是**修订 `正式` 编码正文内容而不改变其含义与标题**，不属于违规：按 `正式→草案` 解冻（**此时递增版本号**）→ 修订 → `草案→正式` 定稿。解冻确认前 **MUST** 先 `check_docs.py --refs {编码}`，做被依赖预审并列出[须人审](references/coding-system.md#须人审不能靠号)项：改 B 则评估所有「谁依赖我」及下游「本文引用」谁会落后；改 A 则确认「我依赖谁」仍支撑新含义。**MUST NOT** 在用户确认兼容之前升钉。引用字符串变更与生效耦合不是同一张图（`来源` ≠ `依赖`，见 [coding-system.md · 追溯类属性行命名](references/coding-system.md#追溯类属性行命名mandatory)）。钉住表规则见 [本文引用](references/coding-system.md#本文引用跨文档钉住mandatory)。

### 废弃细项处理

**Checkpoint 4**：标注 `废弃` 前 **MUST** 暂停并确认原因与替代方案。`草案` 可直接废弃（最后版本号即该草案号）；`初稿→废弃` 时 `修订版本号` 保持 `1`、`废弃原因` 记「初稿期作废」。**MUST NOT** 以删除代替作废。标记后 **MUST** 按 [须人审](references/coding-system.md#须人审不能靠号) 列出「废弃后引用方是否仍成立」，等人确认后再改指或级联作废。标记格式、依赖图与引用追溯见 [item-deprecation.md](references/item-deprecation.md)。

### 废弃整份文档处理

两阶段：先原地标 `废弃` 并给**建议归档日期**；到期归档入本作用域 `deprecated/`（只归档不删除，各子项目独立，无 `active/`）。标注前 **MUST** 排查各文档「本文引用」并按 [须人审](references/coding-system.md#须人审不能靠号) 列出引用方是否仍成立。流程见 [doc-deprecation.md](references/doc-deprecation.md)。

### 修改完毕：定稿确认与提交提示

**Checkpoint 5**。给未冻结对象一个自然晋升窗口，AI **MUST NOT** 自行升格。

**时间戳前置（MUST，先于下列步骤）**：本轮改过的每份文档，`最后更新` **MUST** 刷为当天（记录型，即使不解冻、不递增 `版本`）；`创建日期` 创建后 **MUST NOT** 改。细项 `最后修订日期` 只随 `修订版本号` 递增那天动，**MUST NOT** 用文档级 `最后更新` 代替（见 [记录型字段](references/status-definitions.md#记录型字段不参与冻结)）。

1. **提交提示**：询问是否提交到 git / svn。答「暂不提交」则跳过 2–4，未冻结对象保持不变。
2. **未冻结扫描**：确认要提交时，**仅扫描本轮 AI 实际改过的文件**（以本轮会话操作清单为准，不依赖版本库差异；无法确定时只提示、不扫描），收集 `初稿` / `草案`：文档元信息 `状态`；细项定义块或清单列；缺字段者按 `变更记录` 判定（有定稿条目 → `草案`；从未定稿 → `初稿`；无法判定 → `草案`）。
3. **呈现与确认**：紧凑表格列出，支持批量口径。清单 **MUST** 附带「未冻结对象不得作为实现依据」（见 [据文档实现](#据文档实现消费侧mandatory)）。
4. **执行升格与提交**：明确确认者 → `正式`（定稿不递增版本号；缺字段补齐）。**升格 MUST 自底向上**：先细项后文档。细项定稿 **MUST** 审查该细项出边（含同文档）并提示[须人审](references/coding-system.md#须人审不能靠号)；用户只确认文档而未确认其下细项时 **MUST** 回指待定稿细项。文档定稿 **MUST** 按 [本文引用 · 文档定稿](references/coding-system.md#审查与定稿时机) 对齐钉住表并再次列出须人审项。未提及 / 略过 → 保持未冻结。然后按用户指示 `svn commit` / `git commit`（是否 push 另请示）。

**MUST NOT**：未经确认升格；扫描并提交本轮未改的历史未冻结对象；删除已分配编码或已建档文档（放弃走作废，须 Checkpoint 4；`草案` 放弃走作废，或在草案期内改正文后再定稿，由人决定）。

## 据文档实现（消费侧，MANDATORY）

AI 在被要求**依据 `ued/` 下设计文档实现或完善代码**时，**MUST** 先读本节。文档生产侧的冻结与锁定见 [status-definitions.md](references/status-definitions.md) 与 [object-model.md](references/object-model.md)。

1. **未冻结对象 MUST NOT 作为实现依据**：`细项状态` 为 `初稿` / `草案` 的细项，其标题与业务含义**仍可被改**，据它写出的代码会在定稿时静默失效。AI **MUST NOT** 依据此类细项实现、完善或重构代码，也 **MUST NOT** 依据 `状态` 为 `初稿` / `草案` 的整份文档实现（`草案` 的唯一例外通道见第 2 条）。
2. **被要求实现时 MUST 先判状态、后拒绝**：先取目标细项的 `细项状态`（缺失时按 [status-definitions.md · 缺字段的判定](references/status-definitions.md#状态即基线冻结规则mandatory) 推定）；为未冻结态则 **MUST 拒绝实现**，列出未冻结清单，并按状态给出通道：
   - `初稿`：**MUST 请用户先行定稿**，不设豁免。它从未进入基线、业务含义可能整体推翻，而定稿只需用户确认、成本极低，没有绕过的理由。
   - `草案`：请用户先行定稿；解冻轮次内确需据 `草案` 改代码时，**MUST** 由用户**逐项明确豁免**，并在文档 `变更记录` 记「按 `草案` 实现，定稿后 MUST 复核」。

   豁免只能由用户逐项授予并留痕，**MUST NOT** 由 AI 自行推定，也 **MUST NOT** 以“先按现状实现、后续再对齐”为由绕过。
3. **审查时一并提示**：[status-definitions.md · 定稿提示](references/status-definitions.md#状态即基线冻结规则mandatory) 的提示 **MUST** 含“不得作为实现依据”这一句。
4. **提交前一并呈现**：[修改完毕：定稿确认与提交提示](#修改完毕定稿确认与提交提示) 的未冻结清单 **MUST** 附带同一提示。

## 范围与模板

| 目录 | 范围 |
|------|------|
| `ued/L0-*` | 战略与愿景、产品路线图 |
| `ued/L1-*` | 利益相关者需求、产品规划总览 |
| `ued/L2-*` | 系统/产品需求、规划项 |
| `ued/L3-*` | 概念架构；内含 `ADR-*`（宏观决策一事一档，归属 L3，不设 `adr/` 子目录） |
| `ued/L4-*` | 逻辑/系统设计 |
| `ued/L5-*` | 详细设计 |
| `ued/L6-*` | 验证与确认 |
| `ued/references/` 内 `REF-*` | 外部参考资料 |

常用类型码导览：需求 `FR` `NFR` `AC` `CON` `RUL`；架构与设计 `PRN` `DEC` `CMP` `DOM` `IF` `FLW` `ALG` `ACT`；场景与前瞻 `SCN` `UC` `PLN` `RSK` `ASM` `MET`；战略与参与方 `GOL` `STK`；验证与外部 `TC` `REF`。语义单点在 [coding-system.md · 类型码表](references/coding-system.md#类型码表)。

模板选型见 [assets/templates/index.md](assets/templates/index.md)。检查工具：

- `python3 scripts/check_docs.py -p <ued 路径>`：格式与一致性（编码格式 / 唯一性 / 升序 / 缺口与计数器等式、状态四态与旧值迁移提示、正文定义与清单与全局索引三方一致、标题与引用处一致、定义块形态与属性封闭集、修订号不变式、层级门控与依据方向、`依赖` 与 `来源` 分界、正式文档待定标记、正式 FR/NFR 缺 `验证方式` 提示、版本递增时机、废弃字段与建议归档日期、REF 时效字段与复查周期、PLN 闭环、锚点可达性、章节编号引用）。「本文引用」钉住表本版由审查与定稿门控，脚本不因缺表或落后报 ERROR。
- `--refs {编码}`：反查定义 / 登记 / 引用，并列出依赖两表（谁依赖我 / 我依赖谁）；`初稿` 改标题前、解冻改内容前与任何状态作废前 **MUST** 先执行。
- `--check-templates`：模板哨兵（成对、唯一 H1、无残留外层围栏、使用说明 / 写作约束 / 技能包路径未混入待复制正文）与技能包内部 `文件.md#锚点` 可达性。
- `--instantiate {模板文件名} [--segment {段名}]`：剥除哨兵输出实例化后的正文；多段模板（`ref.md`、`readme-template.md`）用 `--segment` 取单段。
- `python3 scripts/tests/run_fixtures.py`：夹具回归（含 `ued/` 规则夹具、技能包锚点正反夹具，以及对本包 `--check-templates` 的冒烟）。每条夹具只验证一条规则；跑台只断言目标问题名，忽略夹具极简结构带来的噪声。改 `check_docs.py` 后 **MUST** 跑通；新增校验规则 **MUST** 同时补正反夹具并登记入跑台的期望表。脚本只出静态提示，不代替人工审查与定稿确认。

**适用**：创建 / 审查设计文档、分配编码、作废与更新。**不适用**：代码实现、用户手册、运维文档。最常见起步 L2 + L4；补齐信号见 [layer-system.md · 按需启用原则](references/layer-system.md#按需启用原则)。

## 常见问题

**Q: 如何分配新编码？**  
A: 读计数器「下一可用编号」→ 搜索确认未被占用 → 分配 → 立即按升序更新清单、全局索引与计数器。缺口先修、不得跳号占用。步骤见 [分配新编码](#分配新编码)。

**Q: 可以改已分配编码的标题或含义吗？**  
A: 按 [object-model.md · 锁定矩阵](references/object-model.md#锁定矩阵mandatory)。ID / 类型码永不就地改；标题自 `正式` 起锁定；仅改正文走解冻。

**Q: `初稿` 与 `草案` 有何不同？能删 `初稿` 吗？**  
A: 区别在是否曾定稿。都不能删，放弃走作废。见 [status-definitions.md · 标准四态](references/status-definitions.md#标准四态唯一生命周期状态集合) 与 [item-deprecation.md](references/item-deprecation.md)。

**Q: 定稿要升版本号吗？**  
A: 不升。唯一正规递增时机是 `正式→草案` 解冻。见 [变更流程与版本号](references/status-definitions.md#变更流程与版本号统一mandatory)。

**Q: 存量 `草稿` / `提议` / `规划状态` 怎么处理？**  
A: 就地映射到四态，不解冻、不变号。见 [存量文档迁移](references/status-definitions.md#存量文档迁移)。

**Q: 废弃的细项如何处理？**  
A: 标题加 `~~已废弃~~`，补齐 `细项状态` / `废弃时间` / `废弃原因` / `替代方案`，更新索引与引用；**原地保留、不删除**。步骤见 [item-deprecation.md](references/item-deprecation.md)。整份文档走两阶段归档，见 [doc-deprecation.md](references/doc-deprecation.md)。

**Q: 文档里可以写代码吗？**  
A: L0–L6 不可以含可执行实现；REF 可以收录外部资料中的示例。
