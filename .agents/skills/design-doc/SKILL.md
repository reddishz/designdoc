---
name: design-doc
description: 规范 AI 在 `ued/` 目录下创建、修改、审查产品设计文档时的行为规则、层级体系、目录结构、格式与模板选择。用于约束 AI 按既定意图生成战略与愿景、利益相关者需求、系统/产品需求、概念架构、逻辑/系统设计、详细设计、验证与确认等文档。
license: Apache-2.0
metadata:
  version: "2.8"
  author: "产品架构组"
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

## AI 运行时配置解析规则

AI 在创建或编辑设计文档时，模板中的 `{当前用户.作者}` 与 `{项目编码}` 按当前作用域的 `README.md` 解析；额外配置文件 **已移除且 MUST NOT 继续创建或使用**。

**作用域判定规则**：
1. **单应用模式**：若业务文档直接位于 `ued/` 下，则 `ued/README.md` 同时承担入口、项目元信息、编码模式、编码计数器与全局索引。
2. **多应用模式**：若存在多个应用，则每个应用 **MUST** 位于 `ued/{app-name}/` 子目录下。
3. **多应用顶层 README**：`ued/README.md` 仅承担多应用总入口、应用注册表、公共规则与跨应用导航，**MUST NOT** 作为某个具体应用的项目编码来源。
4. **多应用应用级 README**：`ued/{app-name}/README.md` 承担该应用的项目元信息、编码模式、编码计数器、文档导航与应用级全局索引。

**获取优先级**（高到低）：

**作者字段**：
1. 当前作用域 `README.md` 中的项目元信息字段（如 `author` / `maintainer`）
2. 运行环境可识别的当前执行主体标识（如工具可获取）
3. 默认值：`产品架构组`

**项目编码字段（高级扩展用法）**：
1. 当前作用域 `README.md` 中的项目元信息字段 `project_code`
2. 顶层 `ued/README.md` 的应用注册表中，与目标应用目录匹配的 `project_code`（仅多应用模式下辅助校验）
3. **默认值**：无（即禁用项目编码前缀，采用简洁编码格式）

**启用规则**：AI **MUST NOT** 启用项目编码前缀，除非已显式配置且请求发起方明确确认。默认情况下，一律采用简洁编码格式（如 `FR-001`）。

**提示规则（新增强制约束）**：
- 当 AI 识别到 `ued/` 下存在多个应用或多个独立业务域的设计文档时，**MUST** 提示将应用迁移到 `ued/{app-name}/` 子目录，并在顶层 `ued/README.md` 注册应用编码，同时在应用级 `README.md` 中定义 `project_code`。
- 当 AI 识别到当前仓库已存在某一应用的设计文档，而当前任务是在此基础上新增另一应用的设计文档时，**MUST** 在创建前提示采用多应用模式，并为新应用补齐子目录 `README.md` 与顶层应用注册表。
- 若尚未配置 `project_code`，AI **MUST** 先提示补充配置，再进入编码分配阶段；未获确认前，**MUST NOT** 擅自启用前缀。
- 上述提示的目标是确保多个应用并存时，编码、索引、引用与废弃追溯仍可保持全局唯一且语义清晰。

若作用域 `README.md` 不存在或未声明相应字段，首次使用时**直接采用默认值继续工作**：
- `author = 产品架构组`
- `project_code = (空)`

随后 AI **SHOULD** 提醒补充或编辑对应作用域的 `README.md` 元信息区块，特别是当检测到目录中存在多个应用或新增独立应用迹象时。

**项目编码规则（高级模式下）**：
- 长度：2-4位大写字母
- 只能包含字母 A-Z
- 有效示例：`CRM`、`ERP`、`CMS`、`COM`、`HRS`

**README 元信息最小字段（RECOMMENDED）**：
- `project_name`
- `project_code`
- `doc_mode`：`single-app` 或 `multi-app`
- `scope`
- `author` / `maintainer`

## 入口介绍

本 skill 的目标不是向人类解释如何写文档，而是**约束 AI 的执行方式**，确保 AI 在设计文档生成、修改、审查、编码管理和废弃处理时遵循统一意图、统一流程与统一停顿点。

**详细规范**请参考 `references/` 目录下的专项文档：
- 编码体系：[references/coding-system.md](references/coding-system.md)
- 层级体系：[references/layer-system.md](references/layer-system.md)
- 术语与概念：[references/glossary-conventions.md](references/glossary-conventions.md)
- 状态定义：[references/status-definitions.md](references/status-definitions.md)
- 废弃处理：[references/deprecation-guide.md](references/deprecation-guide.md)（细项废弃）
- 废弃文档处理：[references/deprecated-docs-guide.md](references/deprecated-docs-guide.md)（文档废弃）
- 审核指南：[references/review-guidelines.md](references/review-guidelines.md)
- 项目 AGENTS.md 指南：[references/project-agents-guide.md](references/project-agents-guide.md)
- 文档模板：[assets/templates/](assets/templates/)

## 主要任务

### 创建设计文档
- L0-L6 各层级设计文档
- 利益相关者需求、系统/产品需求、概念架构、逻辑/系统设计、详细设计、验证与确认等
- 产品路线图和规划文档

### 审查文档
- 检查文档规范性和一致性
- 编码体系完整性验证
- 路线图与规划的关联性检查

### 编码管理
- 分配全局唯一编码
- 处理编码冲突和废弃
- 计划项迁移跟踪

---

*详细操作指南请参考 references/ 目录下的专项文档*

## 核心原则

**真值源优先级**：当本文件与 `references/` 下的专项文件发生冲突时，**以 `references/` 下的专项文件为准**。

**措辞强度**：文中 MUST/SHOULD/「必须」「应当」等仅表示约束松紧，借鉴 RFC 2119 的常见含义，**非 RFC 认证要求**；统一定义见 [coding-system.md — 需求级别说明](references/coding-system.md#需求级别说明)。

**单一事实来源（SSoT）**：
- 所有文档拥有唯一编号
- 所有明确细项拥有独立的全局唯一编码
- 编码一经分配不可删除，废弃的编码标注为"已废弃"并保留
- 细项定义、细项编码清单、全局索引一律使用完整编码
- 互相引用以唯一编码为准，必要时附带标题
- 下层可引用上层，上层无需引用下层
- 任何层级均可引用 REF（外部参考资料）编码

**核心约束**：`ued/` 下所有文档**不得包含可执行代码和具体实现片段**。只允许设计性内容，例如算法、流程、状态、规则、逻辑、领域模型、接口契约、异常策略、配置约束与决策说明。

**层级使用约束（MANDATORY）**：
- **MUST NOT**：在未获请求发起方明确要求时，默认从 L0 一次性生成到 L6。
- **MUST**：按当前任务意图选择最小必要层级（通常单层或相邻两层）。
- **MUST**：当上游指令未指定层级时，先给出默认建议并按最小必要层级执行（默认优先 L2 或 L4），而不是先反问。
- **SHOULD**：仅在需要战略追溯时补写 L0/L1；仅在需要验证闭环时补写 L6。
- **SHOULD**：L0-L2 在未识别到相关语义前可暂不创建，待出现相关描述后再增补。

**例外情况**：REF（外部参考资料）部分不在此限制内。REF 文档可能包含外部资料中的代码示例、实现片段等引用内容，这些内容作为外部资料本身的组成部分，不受"不得包含代码"约束的限制。

**AI 操作约束（MUST COMPLY）**：
- **编码含义锁定（MUST NOT VIOLATE）**：
  - MUST NOT：修改已分配编码的ID、类型、标题或业务含义
  - MUST NOT：接受任何修改编码含义的请求
  - MUST：拒绝此类请求并引导走废弃+新增流程
  - MUST：在分配编码前检查引用关系避免冲突
- **修改请求拒绝（MANDATORY）**：收到修改已分配编码含义的请求时必须拒绝
- **正确流程指导（REQUIRED）**：明确给出废弃+新增流程
- **冲突检测（MANDATORY）**：修改前必须检查编码引用关系
- **废弃标记规范（MUST COMPLY）**：
  - MUST：废弃细项时必须标记标题删除线 `~~已废弃~~`
  - MUST：废弃细项必须包含四个必须字段：细项状态、废弃时间、废弃原因、替代方案
  - MUST：废弃后必须更新全局索引和文档清单
  - MUST：涉及大规模废弃时必须请求外部确认
  - 详细废弃操作流程见 [references/deprecation-guide.md](references/deprecation-guide.md)

## 快速操作指南

### 创建新文档

1. **环境初始化**：使用 `LS` 或 `Read` 确认 `ued/` 目录结构。
2. **选择层级**：根据任务意图（L0-L6）从 `assets/templates/` 读取对应模板；**默认按需裁剪，禁止无指令全量生成 L0-L6**。
3. **内容生成**：按模板结构生成内容，**MUST NOT** 包含具体实现代码。
4. **外部确认（Checkpoint 1）**：生成草稿后，**MUST** 暂停，等待请求发起方确认文档大纲与核心细项。
5. **编码分配**：确认后，遵循“分配新编码”流程分配 ID。
6. **索引同步**：立即更新当前作用域 `README.md` 与文档末尾清单。
   - 单应用模式：更新 `ued/README.md`
   - 多应用模式：更新 `ued/{app-name}/README.md`；仅当涉及应用注册或跨应用导航时，再更新顶层 `ued/README.md`
7. **自检与优化**：完成后，AI 应主动检查文档逻辑一致性，并输出 1-2 条后续优化建议。
   - **一致性检查**：检查新定义的细项是否与上层目标存在潜在冲突。
   - **颗粒度检查**：检查细项标题是否适度宽泛，避免过度具体（参考 [coding-system.md](references/coding-system.md#标题命名规范)）。
   - **合规性审查（MANDATORY）**：使用本技能的审查规则评审刚做的修改：
     - 编码锁定合规性：是否违反了编码含义锁定原则？
     - 约束强度检查：是否正确使用了MUST/MUST NOT等强制性表述？
     - 流程规范性：是否遵循了编码分配和废弃的正确流程？
     - 文档一致性：是否保持了所有相关文档间的约束表述一致？

### 分配新编码

**强制流程**（必须严格遵循）：
1. **读取计数器**：读取当前作用域 `README.md` 中的"编码计数器"。
   - 单应用模式：读取 `ued/README.md`
   - 多应用模式：读取目标应用目录下的 `README.md`
2. **冲突检测**：使用 `Grep` 或 `SearchCodebase` 确认目标编码在 `ued/` 目录下未被使用。
3. **获取编号**：获取下一个可用编号（如 FR-015）。
4. **外部确认（Checkpoint 2）**：如果是批量新增或涉及核心业务规则变更，**MUST** 暂停并请求确认编码标题与定义是否准确。
5. **即时更新**：更新文档清单 + 全局索引 + 计数器。
6. **验证一致性**：确认索引与正文编码完全一致。
7. **大规模变更确认（Checkpoint 3）**：涉及大规模编码变更或废弃时，**MUST** 在执行前请求二次确认。

### 处理编码含义变更请求

**违规行为识别与拒绝**：
当上游指令要求修改已分配编码的含义时，AI **MUST** 按以下方式响应：

```
❌ 违规检测：禁止修改已分配编码的含义（违反编码锁定原则）
⚠️  系统约束：编码一经分配，其ID、类型、标题和业务含义永不修改
✅ 正确流程：
1. 外部确认：询问是否确定要废弃原编码 {原编码}
2. 执行废弃：标注原编码为"已废弃"并记录变更原因
3. 分配新码：为新含义分配下一个可用编码（如 FR-016）
4. 影响评估：提示检查受影响的下层引用关系
```

**AI 响应模板**：
```
检测到请求修改已分配编码 [{编码}] 的含义。

根据编码锁定原则，已分配编码的含义和标题不可修改。
建议采用废弃+新增方式处理：
1. 废弃原编码 [{编码}]（原含义：{原标题}）
2. 分配新编码用于新含义

是否确认执行废弃操作？
```

### 废弃细项处理

**核心要旨**：
- 废弃细项必须保留，标注废弃状态
- 反向追溯所有引用，同步标注废弃
- 废弃状态可以传播，导致引用方也废弃

**外部确认（Checkpoint 4）**：在标注细项为"已废弃"前，**MUST** 暂停并请求确认废弃原因及替代方案。

**标记格式**：

废弃细项必须包含以下标记和字段：

```markdown
### {项目码}-{类型码}-{序号} 细项标题 ~~已废弃~~

**细项状态**：已废弃
**废弃时间**：YYYY-MM-DD
**废弃原因**：{具体原因}
**替代方案**：{替代细项编码}（如无替代方案，填写"无"）
```

**详细操作流程**：完整的废弃流程、引用追溯、索引更新等操作请参见 [references/deprecation-guide.md](references/deprecation-guide.md)。

## 范围界定

| 目录 | 范围 | 说明 |
|------|------|------|
| `ued/L0-*` | 战略与愿景 | 产品愿景、商业目标、成功标准、产品路线图 |
| `ued/L1-*` | 利益相关者需求 | 用户分析、场景描述、高阶约束、产品规划总览 |
| `ued/L2-*` | 系统/产品需求 | 功能需求、非功能需求、用例、计划项 |
| `ued/L3-*` | 概念架构 | 架构目标、原则、子系统划分 |
| `ued/L4-*` | 逻辑/系统设计 | 领域模型、接口契约、模块职责 |
| `ued/L5-*` | 详细设计 | 设计级算法、流程逻辑、状态转换、异常与配置约束 |
| `ued/L6-*` | 验证与确认 | 测试策略、需求追溯、验收标准 |

## 专项规范

详细规范请参考 `references/` 目录：

- **编码体系**：[references/coding-system.md](references/coding-system.md)
- **层级体系**：[references/layer-system.md](references/layer-system.md)
- **术语与概念**：[references/glossary-conventions.md](references/glossary-conventions.md)
- **状态定义**：[references/status-definitions.md](references/status-definitions.md)
- **审核指南**：[references/review-guidelines.md](references/review-guidelines.md)
- **废弃处理**：[references/deprecation-guide.md](references/deprecation-guide.md)

## 模板和工具

### 文档模板

从 `assets/templates/` 选择对应模板：
- **L0 战略与愿景**：[assets/templates/l0-strategy.md](assets/templates/l0-strategy.md)
- **L0 产品路线图**：[assets/templates/l0-roadmap.md](assets/templates/l0-roadmap.md)
- **L1 利益相关者需求**：[assets/templates/l1-stakeholder.md](assets/templates/l1-stakeholder.md)
- **L1 产品规划**：[assets/templates/planning.md](assets/templates/planning.md)
- **L2 系统/产品需求**：[assets/templates/l2-requirements.md](assets/templates/l2-requirements.md)
- **L3 概念架构**：[assets/templates/l3-concept-architecture.md](assets/templates/l3-concept-architecture.md)
- **L4 逻辑/系统设计**：[assets/templates/l4-system-design.md](assets/templates/l4-system-design.md)
- **L5 详细设计**：[assets/templates/l5-detailed-design.md](assets/templates/l5-detailed-design.md)
- **L6 验证与确认**：[assets/templates/l6-verification.md](assets/templates/l6-verification.md)

### 专项模板

- **架构决策记录**：[assets/templates/adr.md](assets/templates/adr.md)
- **项目注册表**：[assets/templates/project-registry.md](assets/templates/project-registry.md)
- **README 模板**：[assets/templates/readme-template.md](assets/templates/readme-template.md)

### 操作指南

- **流程图指南**：[assets/guides/flowchart-guide.md](assets/guides/flowchart-guide.md)

## 使用场景

### 适用场景

- ✅ 创建产品设计文档（L0-L6）
- ✅ 审查现有设计文档
- ✅ 分配和管理编码
- ✅ 处理文档废弃和更新
- ✅ 维护编码体系完整性

### 不适用场景

- ❌ 代码实现和部署文档
- ❌ 用户手册和操作指南
- ❌ 技术实现细节
- ❌ 运维和监控文档

### 默认起步建议（实战）

- **最常见起步**：L2（系统/产品需求）+ L4（逻辑/系统设计）
- **可选补充**：需要业务背景再补 L0/L1；需要验收闭环再补 L6
- **禁止误用**：不要把“完整层级能力”理解为“AI 每次都必须产出 L0-L6”

### 层级自动识别建议（先建议后补齐）

- **L0 触发信号**：出现愿景、商业目标、成功指标、路线图主题
- **L1 触发信号**：出现角色分层、利益相关者诉求、业务场景冲突
- **L2 触发信号**：出现明确功能需求、非功能约束、验收口径
- **执行策略**：未命中触发信号时先不建对应层；命中后再补建并建立追溯引用

## 常见问题

**Q: 如何分配新编码？**
A: 必须遵循编码分配强制流程，读取计数器→搜索确认→分配编码→立即更新索引。

**Q: 可以修改已分配编码的含义吗？**
A: 绝对不可以。已分配编码的含义和标题永不修改，需要变更时走废弃+新增流程。

**Q: 这个 skill 是给谁用的？**
A: 这是给 AI 用的执行规范，不是给人类阅读的写作教程。其核心目标是把 AI 的文档生成、修改、审查、编号、废弃和停顿点统一成可重复执行的规则集合。

**Q: 废弃的细项如何处理？**
A: 废弃细项必须遵循以下核心要旨：
1. 标题必须添加 `~~已废弃~~` 删除线
2. 必须包含四个字段：细项状态、废弃时间、废弃原因、替代方案（如无则填"无"）
3. 必须更新全局索引和文档清单
4. 必须追溯并处理所有引用关系

详细操作流程（反向追溯、引用处理、索引更新等）请参见 [references/deprecation-guide.md](references/deprecation-guide.md)。

**Q: 文档中可以包含代码吗？**
A: L0-L6 设计文档不可以包含可执行代码、脚本、SQL、配置片段等实现内容；但可以包含算法、流程、逻辑、模型、约束、状态机和决策说明。REF（外部参考资料）文档不在此限制内，可以包含外部资料中的代码示例和实现片段作为引用内容。

---

*详细规范请参考 `references/` 目录下的专项文档。*
