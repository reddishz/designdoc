---
name: design-doc
description: 规范 AI 在 `ued/` 下创建、修改、审查设计文档，以及在改功能/修缺陷/实现代码前先对照并优先修订设计文档与产品基线门禁。用于约束按既定意图维护战略与愿景、利益相关者需求、系统/产品需求、概念架构、逻辑/系统设计、详细设计、验证与确认，并约束消费侧不得绕过文档直接改行为。
license: MIT
metadata:
  version: "6.3"
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
  trigger_principle: "设计文档维护与据文档改代码均涉及编码与基线约束；改行为类请求亦应加载本技能，避免直接改代码绕过 ued/"
  capabilities:
    - "多层级设计文档生成 (L0-L6)"
    - "全局唯一编码管理与冲突检测"
    - "自动化文档规范性审查"
    - "跨文档引用一致性维护"
    - "变更代码前的设计对照与文档优先"
compatibility: 需能访问 ued/ 目录，可选从运行环境获取当前执行主体标识
---

# 产品设计文档规范（UED）

本 skill **约束 AI 的执行方式**，不是人类写作教程。规则本体在 `references/`；本文只承载身份、不变量索引与可执行程序。包内同一规则只允许一种表述，发现不一致当轮合并。措辞强度见 [coding-system.md · 需求级别说明](references/coding-system.md#需求级别说明)。

**三类动作**：

| 意图 | 先读 |
|------|------|
| 写 / 改 / 审查 `ued/` 文档 | 下方快速操作指南 |
| **改功能 / 修缺陷 / 改产品行为**（项目有 `ued/`） | [变更代码前](#变更代码前消费侧mandatory) → 必要时再 [据文档实现](#据文档实现消费侧mandatory) |
| **按已定设计实现或完善代码** | [据文档实现](#据文档实现消费侧mandatory) |

## 不变量索引

| 主题 | 单点 |
|------|------|
| 对象 × 字段 × 状态、锁定与动作 | [object-model.md](references/object-model.md) |
| 编码形态、类型码表、属性封闭集、定义块、引用、本文引用、分配 | [coding-system.md](references/coding-system.md) |
| `IF` / `ACT` / `PLN`、UC / FR / FLW、ADR 与 DEC | [type-profiles.md](references/type-profiles.md) |
| 四态、门控、修订号、流转伴随 / 记录型含义 | [status-definitions.md](references/status-definitions.md) |
| 产品版本、产品基线、升产品版本 | [product-version.md](references/product-version.md) |
| 改代码前对照文档、据文档实现门禁 | 下文 [变更代码前](#变更代码前消费侧mandatory) / [据文档实现](#据文档实现消费侧mandatory) |
| 细项 / 文档作废步骤 | [item-deprecation.md](references/item-deprecation.md) / [doc-deprecation.md](references/doc-deprecation.md) |
| 检查项 | [review-guidelines.md](references/review-guidelines.md) |
| 层级与目录 | [layer-system.md](references/layer-system.md) |
| 词汇表 | [glossary-conventions.md](references/glossary-conventions.md) |
| 模板边界与整篇型共用 | [assets/templates/index.md](assets/templates/index.md) |

- **引用锚点**：细项编码与文档编码是 `ued/` 内唯一允许的语义引用锚点；**MUST NOT** 用章节编号（`§x.y`、`第 x 章`、`见上文`）。跨文件链接路径 MUST 以 `./` 或 `../` 开头（见 [交叉引用规则 · 链接路径](references/coding-system.md#链接路径mandatory)）。可独立成立的规则 MUST 先落码再被引用。规范条文本身不纳入细项编码，指向条款用 `文件#标题锚点`。
- **存在性锁定**：编号一经分配永久占用，任何状态 **MUST NOT** 删除或复用；放弃走作废。权限切片见 [object-model.md · 锁定矩阵](references/object-model.md#锁定矩阵mandatory)。
- **`ued/` 不得含可执行代码**（算法、契约、状态机可以）。REF 可收录外部资料中的代码示例。
- **层级按最小必要**：绿场或上层尚不存在时，未指定可从 L2 或 L4 起步，**MUST NOT** 无指令一次生成 L0–L6。**增量加能力**时若已有 L0–L2（或更高），**MUST** 先向上核对再写 L3–L5，见 [按需启用原则](references/layer-system.md#按需启用原则) 与下方「新增功能需求（增量）」。对层判据见 [分层问题](references/layer-system.md#分层问题对层判据)。
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

**README 元信息最小字段（RECOMMENDED）**：`project_name`、`project_code`、`doc_mode`（`single-app` 或 `multi-app`）、`scope`、`author` / `maintainer`、`产品版本`（`vX.Y`，见 [product-version.md](references/product-version.md)）。

## 快速操作指南

| Checkpoint | 时机 | 暂停条件 |
|------------|------|----------|
| 1 | 生成初稿后 | 确认大纲与核心细项 |
| 2 | 分配编码 / 增量能力 | 批量新增、核心业务规则变更，或上层（L0–L2）需同步时列出影响 |
| 3 | 大规模编码变更或废弃前 | 二次确认 |
| 4 | 标注 `废弃` 前 | 确认废弃原因与替代方案 |
| 5 | 本轮实质修改收尾 | 提交提示 + 定稿确认；呈现基线漂移（首份基线或次版本询问；命中再问主版本） |

写作与审查门禁：起草前声明「引用只用编码」；可独立语义先落码；审查命中章节编号引用即 A 级阻断；复查确认零章节编号引用；未过门禁不得合并或正式发布。

### 新增功能需求（增量）

用户要「加功能 / 加需求 / 增强某能力」，且作用域里**已有**分层文档时，走本程序；**MUST NOT** 因「默认 L2/L4」就只在 L4/L5 落笔。绿场、或上层目录与文档皆不存在时，仍按 [按需启用](references/layer-system.md#按需启用原则) 最小集起步。

1. **向上核对（MUST）**：对照 [补齐信号](references/layer-system.md#按需启用原则)，判断本能力是否触及——L0 愿景/GOL/MET/范围；L1 STK/SCN/高阶约束；L2 FR/NFR/UC/AC 等。已有对应层文档则打开相关篇，查是否已有可复用或须改正的细项。
2. **先上后下**：缺则先补/改 L0→L1→L2（及必要的 L3），再写 L4/L5；类型码定义层见 [细项定义层级](references/coding-system.md#细项定义层级mandatory)。仅当上层已覆盖、本轮纯属契约/算法/模块内细化时，才可只改 L4/L5。
3. **呈现**：在 Checkpoint 1 或 2 用短表列出「本轮拟动的层与编码」及「判定为不需动上层的理由」；批量或核心能力变更时 **MUST** 暂停确认。
4. 其后按「创建新文档」/「分配新编码」执行落码与索引更新。

### 创建新文档

1. 确认 `ued/` 目录结构；若属增量能力，先完成上方「新增功能需求（增量）」的向上核对。
2. 按任务意图从 `assets/templates/` 取对应模板；**默认按需裁剪，禁止无指令全量生成 L0-L6**。
3. 按模板生成，**MUST NOT** 含具体实现代码。
4. **Checkpoint 1**：暂停，等确认大纲与核心细项（增量时含上层是否同步）。
5. 确认后按「分配新编码」分配 ID。
6. 立即更新当前作用域 `README.md` 与文档末尾清单（状态列默认 `初稿`）。单应用改 `ued/README.md`；多应用改 `ued/{app-name}/README.md`，仅应用注册或跨应用导航时再改顶层。
7. 自检：与上层目标无冲突；标题适度宽泛（[标题命名规范](references/coding-system.md#标题命名规范适度宽泛)）；类型码只在定义层写定义块（[细项定义层级](references/coding-system.md#细项定义层级mandatory)）——详细设计里的「系统应当」先落到 L2 的 FR / NFR；按 [review-guidelines.md](references/review-guidelines.md) 过一遍锁定、措辞与流程。

### 分配新编码

1. 读当前作用域 `README.md` 对应类型码的「下一可用编号」。
2. 一律用该号；发现缺口（不分状态）先修索引或补废弃记录，**MUST NOT** 直接分配缺口编号。
3. 用 Grep 确认目标编码在 `ued/` 未被使用。
4. **Checkpoint 2**：批量、核心规则变更、或增量能力须动上层时，暂停确认标题、定义及上层同步范围。
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

> 若诉求仅是**修订 `正式` 编码正文内容而不改变其含义与标题**，不属于违规：按 `正式→草案` 解冻（**此时该对象 `修订版本号` +1**）→ 修订 → `草案→正式` 定稿。解冻确认前 **MUST** 先 `check_docs.py --refs {编码}`，做被依赖预审并列出[须人审](references/coding-system.md#须人审不能靠号)项：改 B 则评估所有「谁依赖我」及下游「本文引用」谁会落后；改 A 则确认「我依赖谁」仍支撑新含义。**MUST NOT** 在用户确认兼容之前升钉。引用字符串变更与生效耦合不是同一张图（`来源` ≠ `依赖`，见 [coding-system.md · 追溯类属性行命名](references/coding-system.md#追溯类属性行命名mandatory)）。钉住表规则见 [本文引用](references/coding-system.md#本文引用跨文档钉住mandatory)。

### 废弃细项处理

**Checkpoint 4**：标注细项或整份文档 `废弃` 前 **MUST** 暂停并确认原因与替代方案。`草案` 可直接废弃（最后修订号即该草案号）；`初稿→废弃` 时 `修订版本号` 保持 `1`、`废弃原因` 记「初稿期作废」。**MUST NOT** 以删除代替作废。标记后 **MUST** 按 [须人审](references/coding-system.md#须人审不能靠号) 列出「废弃后引用方是否仍成立」，等人确认后再改指或级联作废。整份文档另须满足 [整份废弃的前置](references/doc-deprecation.md#整份废弃的前置mandatory)：仍有未废弃细项或仍当依据的非细项正文时 **MUST NOT** 改文档 `状态`，也 **MUST NOT** 为过门批量改细项状态。标记格式、依赖图与引用追溯见 [item-deprecation.md](references/item-deprecation.md)。

### 废弃整份文档处理

两阶段：先原地标 `废弃` 并给**建议归档日期**；到期归档入本作用域 `deprecated/`（只归档不删除，各子项目独立，无 `active/`）。标注前 **MUST** 确认全部细项已 `废弃`（缺状态视为未废弃），列出仍当依据的非细项正文标题等人审，并排查各文档「本文引用」。用户要求整份废弃但活内容仍在时 **MUST** 停下并列出缺口。误标存量 **MUST** 先恢复文档状态，**MUST NOT** 杀掉活细项来迁就封面。流程见 [doc-deprecation.md](references/doc-deprecation.md)。

### 修改完毕：定稿确认与提交提示

**Checkpoint 5**。给未冻结对象一个自然晋升窗口，AI **MUST NOT** 自行升格。

**时间戳前置（MUST，先于下列步骤）**：本轮改过的每份文档，`最后更新` **MUST** 刷为当天（记录型，即使不解冻、不加修订号）；文档与细项的 `创建日期` 创建后 **MUST NOT** 改。细项 `最后修订日期` 只随 `修订版本号` 递增那天动，**MUST NOT** 用文档级 `最后更新` 代替。本轮若改已 `正式` 细项，文档 **MUST** 已同轮解冻并 `+1`（见 [层级门控](references/status-definitions.md#层级门控文档状态--细项状态mandatory)、[流转伴随字段](references/status-definitions.md#流转伴随字段只随指定转换写入)）。

1. **提交提示**：询问是否提交到 git / svn。答「暂不提交」则跳过 2–5，未冻结对象保持不变。
2. **未冻结扫描**：确认要提交时，**仅扫描本轮 AI 实际改过的文件**（以本轮会话操作清单为准，不依赖版本库差异；无法确定时只提示、不扫描），收集 `初稿` / `草案`：文档元信息 `状态`；细项定义块或清单列；缺字段者按 `变更记录` 判定（有定稿条目 → `草案`；从未定稿 → `初稿`；无法判定 → `草案`）。
3. **呈现与确认**：紧凑表格列出未冻结对象，支持批量口径。清单 **MUST** 附带「未冻结或未入当前产品基线不得作为实现依据」（见 [据文档实现](#据文档实现消费侧mandatory)）。
4. **执行升格与提交**：明确确认者 → `正式`（定稿不加修订号；缺字段补齐；**定稿不写** `baselines/`）。**升格 MUST 自底向上**：先细项后文档。细项定稿 **MUST** 审查该细项出边（含同文档）并提示[须人审](references/coding-system.md#须人审不能靠号)；用户只确认文档而未确认其下细项时 **MUST** 回指待定稿细项。文档定稿 **MUST** 按 [本文引用 · 文档定稿](references/coding-system.md#审查与定稿时机) 对齐钉住表并再次列出须人审项。未提及 / 略过 → 保持未冻结。然后按用户指示 `svn commit` / `git commit`（是否 push 另请示）。
5. **基线漂移与升产品版本（MUST 呈现；询问见专章）**：只要本轮未选「暂不提交」，在定稿步骤之后（若无待定稿对象则紧接提交确认后）**MUST** 按 [相对当前基线的漂移](references/product-version.md#相对当前基线的漂移) 列出短表——含「待建首份基线」或未入基线 / 已退出正式集 / revision 落后（可附建议版本号）。尚无任何基线文件 → **MUST** 问是否**建立首份基线**（默认沿用当前 `产品版本` 号，勿默认劝升次版本）。已有基线且三类漂移非空 → **MUST** 问是否升**次版本**；若用户同意建/升且命中 [主版本询问条件](references/product-version.md#何时询问)，再问主/次。无待建且漂移空 → 不追问发版。用户确认或主动说「发版 / 升产品版本」时走下方程序；**MUST NOT** 未经确认自行 `--bump-product`。

**MUST NOT**：未经确认升格；扫描并提交本轮未改的历史未冻结对象；删除已分配编码或已建档文档（放弃走作废，须 Checkpoint 4；`草案` 放弃走作废，或在草案期内改正文后再定稿，由人决定）。

### 升产品版本

用户说「发版 / 升产品版本」或在 Checkpoint 5 确认要升时，按 [product-version.md · 升产品版本](references/product-version.md#升产品版本mandatory) 执行：定号（默认次版本 `+1`；命中则问主版本，否决则保持次版本；首次无快照 MAY 以当前号生成）→ 写出 `baselines/vX.Y.yaml` → 对 `added`/`removed` 回写对象 `引入版本`/`退出版本` 缓存 → 更新 README。不解冻、不改修订号、不改本文引用、不写 git / svn / 构建号。定稿 **MUST NOT** 写基线或手填谱系。优先 `check_docs.py --bump-product`。询问规则（漂移 → 次版本；主版本条件另问）见该专章。

## 变更代码前（消费侧，MANDATORY）

项目存在 `ued/`（或应用级设计文档树），且用户意图是**改功能、修缺陷/bug、改产品可观察行为、按需求实现某能力**时，AI **MUST** 先走本节，**MUST NOT** 默认直接改业务代码。「先文档、后代码」；纯笔误、与规格无关的构建/环境失败等 MAY 直接改代码，但 **MUST** 在回复中写明「未触及设计对象」。

文档生产细则见快速操作指南；冻结与基线门禁见 [据文档实现](#据文档实现消费侧mandatory)。

1. **定位**：在 `ued/` 与当前产品基线中检索相关细项（关键词、编码、`--refs`、模块/接口名）。列出候选 FR/NFR/ALG/IF/…（可附文档路径）。
2. **对照判定**（三选一，可组合）：
   - **仅实现偏离**：文档与基线正确，代码不符 → 先确认依据细项已在当前基线，再改代码（走 [据文档实现](#据文档实现消费侧mandatory)）。
   - **文档错误或过时**：设计与预期不符 → **先**按生产侧程序修订文档（`正式` 须解冻；增量能力走 [新增功能需求（增量）](#新增功能需求增量)），再经 Checkpoint 定稿/漂移询问，**然后**才改代码。
   - **文档缺失**：无对应细项 → **先**落码补设计（增量向上核对），再定稿/入基线，**然后**才实现。
3. **呈现**：改代码前用短表说明「依据哪些编码 / 是否先改文档 / 是否需升产品版本」；须人审或解冻时 **MUST** 暂停确认。
4. **禁止**：以「先改代码后面再补文档」「小改不用改设计」为由跳过本节；**MUST NOT** 在文档仍为 `初稿`/`草案` 或未入当前基线时，把该行为当作已批准规格去改代码（豁免规则同下节）。

## 据文档实现（消费侧，MANDATORY）

AI 在被要求**依据已定设计实现或完善代码**时（含 [变更代码前](#变更代码前消费侧mandatory) 判定为「仅实现偏离」之后），**MUST** 先读本节。文档生产侧见 [status-definitions.md](references/status-definitions.md) 与 [object-model.md](references/object-model.md)；产品基线见 [product-version.md](references/product-version.md)。

1. **未入当前产品基线 MUST NOT 作为实现依据**：取作用域 README 的 `产品版本`，打开 `baselines/{该版本}.yaml`；目标细项编码 **MUST** 出现在其 `items` 中（成员均为生成时的 `正式` 细项，含全部类型码）。AI **MUST NOT** 依据未列出的细项实现、完善或重构代码，也 **MUST NOT** 依据 `状态` 为 `初稿` / `草案` / `废弃` 的整份文档实现。
2. **被要求实现时 MUST 先判状态与基线、后拒绝**：
   - `初稿` / `草案` / `废弃`，或字段缺失按 [缺字段的判定](references/status-definitions.md#状态即基线冻结规则mandatory) 推定为未冻结 → **MUST 拒绝**；`初稿` 请用户定稿（不设豁免）；`草案` 请用户定稿，解冻轮次内确需据 `草案` 改代码时 **MUST** 由用户**逐项明确豁免**，并在文档 `变更记录` 记「按 `草案` 实现，定稿后 MUST 复核，且 MUST 升产品版本后方可作为基线依据」。
   - `正式` 但不在当前基线 `items` → **MUST 拒绝**，提示先「升产品版本」纳入基线（默认可升**次版本**）；**MUST NOT** 对此情形做实现豁免。
   - 无基线文件或 README 无 `产品版本` → **MUST 拒绝**，提示先建立产品基线。

   豁免只能由用户对 `草案` 逐项授予并留痕，**MUST NOT** 由 AI 自行推定，也 **MUST NOT** 以“先按现状实现、后续再对齐”为由绕过基线门禁。
3. **审查时一并提示**：[status-definitions.md · 定稿提示](references/status-definitions.md#状态即基线冻结规则mandatory) 的提示 **MUST** 含“未入当前产品基线不得作为实现依据”。
4. **提交前一并呈现**：Checkpoint 5 的未冻结清单与[基线漂移](references/product-version.md#相对当前基线的漂移)短表（见上节步骤 5）；漂移非空时的次版本询问为 **MUST**。

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

- `python3 scripts/check_docs.py -p <ued 路径>`：格式与一致性（编码格式 / 唯一性 / 升序 / 缺口与计数器等式、状态四态与旧值迁移提示、正文定义与清单与全局索引三方一致、标题与引用处一致、定义块形态与属性封闭集、修订号不变式、层级门控与依据方向、`依赖` 与 `来源` 分界、正式文档待定标记、正式 FR/NFR 缺 `验证方式` 提示、修订号递增时机、产品基线快照、基线谱系缓存取值、废弃字段与建议归档日期、废弃文档仍含未废弃细项、REF 时效字段与复查周期、PLN 闭环、锚点可达性、章节编号引用）。「本文引用」钉住表本版由审查与定稿门控，脚本不因缺表或落后报 ERROR。非细项正文是否仍当依据本版不 ERROR。
- `--bump-product [--major] [--note TEXT]`：升产品版本——按正式集生成 `baselines/vX.Y.yaml` 并更新 README（见 [product-version.md](references/product-version.md)）。
- `--refs {编码}`：反查定义 / 登记 / 引用，并列出依赖两表（谁依赖我 / 我依赖谁）；`初稿` 改标题前、解冻改内容前与任何状态作废前 **MUST** 先执行。
- `--check-templates`：模板哨兵（成对、唯一 H1、无残留外层围栏、使用说明 / 写作约束 / 技能包路径未混入待复制正文）与技能包内部 `文件.md#锚点` 可达性。
- `--instantiate {模板文件名} [--segment {段名}]`：剥除哨兵输出实例化后的正文；多段模板（`ref.md`、`readme-template.md`）用 `--segment` 取单段。
- `python3 scripts/tests/run_fixtures.py`：夹具回归（含 `ued/` 规则夹具、技能包锚点正反夹具，以及对本包 `--check-templates` 的冒烟）。每条夹具只验证一条规则；跑台只断言目标问题名，忽略夹具极简结构带来的噪声。改 `check_docs.py` 后 **MUST** 跑通；新增校验规则 **MUST** 同时补正反夹具并登记入跑台的期望表。脚本只出静态提示，不代替人工审查与定稿确认。

**适用**：创建 / 审查 / 更新设计文档；分配编码；作废；以及**变更代码前的设计对照**与**据文档实现门禁**（本技能约束次序与依据，**不代替**编写业务代码本身）。**不适用**：用户手册、运维手册、与 `ued/` 无关的纯环境琐事。绿场最常见起步 L2 + L4；增量见「新增功能需求（增量）」；改行为见「变更代码前」。

## 常见问题

**Q: 如何分配新编码？**  
A: 读计数器「下一可用编号」→ 搜索确认未被占用 → 分配 → 立即按升序更新清单、全局索引与计数器。缺口先修、不得跳号占用。步骤见 [分配新编码](#分配新编码)。

**Q: 可以改已分配编码的标题或含义吗？**  
A: 按 [object-model.md · 锁定矩阵](references/object-model.md#锁定矩阵mandatory)。ID / 类型码永不就地改；标题自 `正式` 起锁定；仅改正文走解冻。

**Q: `初稿` 与 `草案` 有何不同？能删 `初稿` 吗？**  
A: 区别在是否曾定稿。都不能删，放弃走作废。见 [status-definitions.md · 标准四态](references/status-definitions.md#标准四态唯一生命周期状态集合) 与 [item-deprecation.md](references/item-deprecation.md)。

**Q: 定稿要升修订号或产品版本吗？**  
A: 定稿不升修订号，也 **MUST NOT** 自动写基线。Checkpoint 5 **MUST** 呈现漂移：尚无基线则问是否建首份（默认可沿用当前产品版本号）；已有基线且漂移非空则问是否升**次版本**；主版本另按条件问。见 [product-version.md](references/product-version.md)。

**Q: `正式` 是否即可实现？**  
A: 否。须 `正式` **且** 出现在当前 `产品版本` 对应的 `baselines/vX.Y.yaml` 的 `items` 中；不在则先升产品版本（通常次版本）纳入基线。

**Q: 加功能能否直接写 L4/L5？**  
A: 绿场或上层不存在时可以按需从 L2/L4 起步。已有 L0–L2 时 **MUST** 先向上核对（愿景/干系人/FR 等），再写下层；见 [新增功能需求（增量）](#新增功能需求增量)。

**Q: 改功能或修 bug 能否直接改代码？**  
A: 项目有 `ued/` 时 **MUST NOT** 默认直接改代码。先走 [变更代码前](#变更代码前消费侧mandatory)：定位细项 → 判定文档/实现谁错 → 需改设计则先文档再代码；仅实现偏离则按 [据文档实现](#据文档实现消费侧mandatory) 在基线内改代码。

**Q: 存量 `草稿` / `提议` / `规划状态` 怎么处理？**  
A: 就地映射到四态，不解冻、不加修订号。见 [存量文档迁移](references/status-definitions.md#存量文档迁移)。

**Q: 废弃的细项如何处理？**  
A: 标题加 `~~已废弃~~`，补齐 `细项状态` / `废弃时间` / `废弃原因` / `替代方案`，更新索引与引用；**原地保留、不删除**。步骤见 [item-deprecation.md](references/item-deprecation.md)。整份文档走两阶段归档，见 [doc-deprecation.md](references/doc-deprecation.md)。

**Q: 文档里可以写代码吗？**  
A: L0–L6 不可以含可执行实现；REF 可以收录外部资料中的示例。
