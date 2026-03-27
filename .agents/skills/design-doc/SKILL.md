---
name: design-doc
description: 规范项目产品设计文档（ued/目录）的层级体系、目录结构、格式和模板。当用户需要创建或审查设计文档（包括战略与愿景、利益相关者需求、系统/产品需求、概念架构、逻辑/系统设计、详细设计、验证与确认等）时使用此 skill。
license: Apache-2.0
metadata:
  version: "2.5"
  author: "产品架构组"
  spec-compliance: 遵循 Agent Skills 开放标准
  tags: [design, documentation, product, architecture, specification]
  triggers:
    - "创建设计文档"
    - "编写需求文档"
    - "评审设计方案"
    - "分配功能编码"
    - "废弃业务细项"
    - "更新全局索引"
    - "维护设计文档"
  trigger_principle: "设计文档维护涉及复杂的编码体系和规范约束，需要明确的人工意图确认以避免误触发复杂流程"
  capabilities:
    - "多层级设计文档生成 (L0-L6)"
    - "全局唯一编码管理与冲突检测"
    - "自动化文档规范性审查"
    - "跨文档引用一致性维护"
compatibility: 需能访问 ued/ 目录，可选从运行环境获取当前用户名信息
---

# 产品设计文档规范（UED）

## 用户配置

创建或编辑设计文档时，模板中的 `{当前用户.作者}` 与 `{项目编码}` 按以下规则解析。

**获取优先级**（高到低）：

**作者字段**：
1. 项目配置文件 `ued/.doc-config.json` 中的 `author` 字段
2. 运行环境可识别的当前用户名信息（如工具可获取）
3. 默认值：`产品架构组`

**项目编码字段（高级扩展用法）**：
1. 项目配置文件 `ued/.doc-config.json` 中的 `project_code` 字段
2. 环境变量 `DESIGN_DOC_PROJECT_CODE`
3. **默认值**：无（即禁用项目编码前缀，采用简洁编码格式）

**启用规则**：AI **MUST NOT** 启用项目编码前缀，除非已显式配置且用户明确确认。默认情况下，一律采用简洁编码格式（如 `FR-001`）。

**配置文件格式**（`ued/.doc-config.json`）：
```json
{
  "author": "张三",
  "project_code": "CRM" 
}
```

若配置文件不存在，首次使用时**直接采用默认值继续工作**：
- `author = 产品架构组`
- `project_code = (空)`

随后**应当建议**用户补充或编辑 `ued/.doc-config.json`，特别是当检测到目录中存在多个子项目迹象时。

**项目编码规则（高级模式下）**：
- 长度：2-4位大写字母
- 只能包含字母 A-Z
- 有效示例：`CRM`、`ERP`、`CMS`、`COM`、`HRS`

## 入口介绍

**详细规范**请参考 `references/` 目录下的专项文档：
- 编码体系：[references/coding-system.md](references/coding-system.md)
- 层级体系：[references/layer-system.md](references/layer-system.md)
- 状态定义：[references/status-definitions.md](references/status-definitions.md)
- 废弃处理：[references/deprecation-guide.md](references/deprecation-guide.md)
- 审核指南：[references/review-guidelines.md](references/review-guidelines.md)
- AI 操作指南：[references/ai-operations.md](references/ai-operations.md)
- RFC2119 规范：[references/rfc2119-evaluation.md](references/rfc2119-evaluation.md)
- RFC2119 模板写法：[references/rfc2119-templates.md](references/rfc2119-templates.md)
- 项目 AGENTS.md 指南：[references/project-agents-guide.md](references/project-agents-guide.md)
- 文档模板：[assets/templates/](assets/templates/)

## 主要任务

### 创建设计文档
- L0-L6 各层级设计文档
- 利益相关者需求、系统/产品需求、概念架构、逻辑/系统设计、详细设计、验证与确认等

### 审查文档
- 检查文档规范性和一致性
- 编码体系完整性验证

### 编码管理
- 分配全局唯一编码
- 处理编码冲突和废弃

---

*详细操作指南请参考 references/ 目录下的专项文档*

## 核心原则

**真值源优先级**：当本文件与 `references/` 下的专项文件发生冲突时，**以 `references/` 下的专项文件为准**。

**单一事实来源（SSoT）**：
- 所有文档拥有唯一编号
- 所有明确细项拥有独立的全局唯一编码
- 编码一经分配不可删除，废弃的编码标注为"已废弃"并保留
- 细项定义、细项编码清单、全局索引一律使用完整编码
- 互相引用以唯一编码为准，必要时附带标题
- 下层可引用上层，上层无需引用下层
- 任何层级均可引用 REF（外部参考资料）编码

**核心约束**：`ued/` 下所有文档**不得包含可执行代码和具体实现片段**。只允许设计性内容，例如算法、流程、状态、规则、逻辑、领域模型、接口契约、异常策略、配置约束与决策说明。

**AI 操作约束（MUST COMPLY）**：
- **编码含义锁定（MUST NOT VIOLATE）**：
  - MUST NOT：修改已分配编码的ID、类型、标题或业务含义
  - MUST NOT：接受任何修改编码含义的请求
  - MUST：拒绝此类请求并引导用户走废弃+新增流程
  - MUST：在分配编码前检查引用关系避免冲突
- **修改请求拒绝（MANDATORY）**：收到修改已分配编码含义的请求时必须拒绝
- **正确流程指导（REQUIRED）**：指导用户走废弃+新增流程
- **冲突检测（MANDATORY）**：修改前必须检查编码引用关系

## 快速操作指南

### 创建新文档

1. **环境初始化**：使用 `LS` 或 `Read` 确认 `ued/` 目录结构。
2. **选择层级**：根据用户需求（L0-L6）从 `assets/templates/` 读取对应模板。
3. **内容生成**：按模板结构生成内容，**MUST NOT** 包含具体实现代码。
4. **人类确认（Checkpoint 1）**：生成草稿后，**MUST** 暂停并请求用户确认文档大纲与核心细项。
5. **编码分配**：确认后，遵循“分配新编码”流程分配 ID。
6. **索引同步**：立即更新 `ued/README.md` 与文档末尾清单。
7. **自我反思与优化**：完成后，AI 应主动检查文档逻辑一致性，并向用户提出 1-2 条优化建议。

### 分配新编码

**强制流程**（必须严格遵循）：
1. **读取计数器**：读取 `ued/README.md` 中的“编码计数器”。
2. **冲突检测**：使用 `Grep` 或 `SearchCodebase` 确认目标编码在 `ued/` 目录下未被使用。
3. **获取编号**：获取下一个可用编号（如 FR-015）。
4. **即时更新**：更新文档清单 + 全局索引 + 计数器。
5. **验证一致性**：确认索引与正文编码完全一致。
6. **人类确认（Checkpoint 2）**：涉及大规模编码变更或废弃时，**MUST** 在执行前请求用户二次确认。

### 处理编码含义变更请求

**违规行为识别与拒绝**：
当用户要求修改已分配编码的含义时，AI **MUST** 按以下方式响应：

```
❌ 违规检测：禁止修改已分配编码的含义（违反编码锁定原则）
⚠️  系统约束：编码一经分配，其ID、类型、标题和业务含义永不修改
✅ 正确流程：
1. 人类确认：询问用户是否确定要废弃原编码 {原编码}
2. 执行废弃：标注原编码为"已废弃"并记录变更原因
3. 分配新码：为新含义分配下一个可用编码（如 FR-016）
4. 影响评估：提示用户检查受影响的下层引用关系
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

**处理原则**：
- 废弃细项必须保留，标注废弃状态
- 反向追溯所有引用，同步标注废弃
- 废弃状态可以传播，导致引用方也废弃

**标记格式**：
```markdown
### {项目码}-{类型码}-{序号} 细项标题 ~~已废弃~~

**细项状态**：已废弃
**废弃时间**：YYYY-MM-DD
**废弃原因**：{具体原因}
**替代方案**：{替代细项编码}（如有）
**废弃人**：{废弃人姓名}
```

## 范围界定

| 目录 | 范围 | 说明 |
|------|------|------|
| `ued/L0-*` | 战略与愿景 | 产品愿景、商业目标、成功标准 |
| `ued/L1-*` | 利益相关者需求 | 用户分析、场景描述、高阶约束 |
| `ued/L2-*` | 系统/产品需求 | 功能需求、非功能需求、用例 |
| `ued/L3-*` | 概念架构 | 架构目标、原则、子系统划分 |
| `ued/L4-*` | 逻辑/系统设计 | 领域模型、接口契约、模块职责 |
| `ued/L5-*` | 详细设计 | 设计级算法、流程逻辑、状态转换、异常与配置约束 |
| `ued/L6-*` | 验证与确认 | 测试策略、需求追溯、验收标准 |

## 专项规范

详细规范请参考 `references/` 目录：

- **编码体系**：[references/coding-system.md](references/coding-system.md)
- **层级体系**：[references/layer-system.md](references/layer-system.md)
- **状态定义**：[references/status-definitions.md](references/status-definitions.md)
- **审核指南**：[references/review-guidelines.md](references/review-guidelines.md)
- **废弃处理**：[references/deprecation-guide.md](references/deprecation-guide.md)

## 模板和工具

### 文档模板

从 `assets/templates/` 选择对应模板：
- **L0 战略与愿景**：[assets/templates/l0-strategy.md](assets/templates/l0-strategy.md)
- **L1 利益相关者需求**：[assets/templates/l1-stakeholder.md](assets/templates/l1-stakeholder.md)
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

- **AI 操作指南**：[references/ai-operations.md](references/ai-operations.md)
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

## 常见问题

**Q: 如何分配新编码？**
A: 必须遵循编码分配强制流程，读取计数器→搜索确认→分配编码→立即更新索引。

**Q: 可以修改已分配编码的含义吗？**
A: 绝对不可以。已分配编码的含义和标题永不修改，需要变更时走废弃+新增流程。

**Q: 废弃的细项如何处理？**
A: 保留细项，标注废弃状态，追溯所有引用并同步标注废弃。

**Q: 文档中可以包含代码吗？**
A: 不可以包含可执行代码、脚本、SQL、配置片段等实现内容；但可以包含算法、流程、逻辑、模型、约束、状态机和决策说明。

---

*详细规范请参考 `references/` 目录下的专项文档。*
