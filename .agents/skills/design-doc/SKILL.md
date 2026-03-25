---
name: design-doc
description: 规范项目产品设计文档（ued/目录）的层级体系、目录结构、格式和模板。当用户需要创建或审查设计文档（包括战略与愿景、利益相关者需求、系统/产品需求、概念架构、逻辑/系统设计、详细设计、验证与确认等）时使用此 skill。不适用于代码实现、部署运维(docs/)或用户手册类文档。
license: Apache-2.0
metadata:
  version: "2.4"
  spec-compliance: 遵循 Agent Skills 开放标准
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

**项目编码字段**：
1. 项目配置文件 `ued/.doc-config.json` 中的 `project_code` 字段
2. 环境变量 `DESIGN_DOC_PROJECT_CODE`
3. 默认值：`DEFAULT`

**配置文件格式**（`ued/.doc-config.json`）：
```json
{
  "author": "张三",
  "project_code": "CRM"
}
```

若配置文件不存在，首次使用时**直接采用默认值继续工作**：
- `author = 产品架构组`
- `project_code = DEFAULT`

随后**应当建议**用户补充或编辑 `ued/.doc-config.json`，而不是把首次使用强制变成交互阻塞。

**项目编码规则**：
- 长度：2-4位大写字母
- 只能包含字母 A-Z
- 建议体现项目或产品线特征
- 企业内统一分配管理

**有效示例**：`CRM`、`ERP`、`CMS`、`COM`、`HRS`

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

**AI 操作约束**：
- **编码含义锁定**：已分配编码的含义和标题**永不修改**
- **修改请求拒绝**：收到修改已分配编码含义的请求时必须拒绝
- **正确流程指导**：指导用户走废弃+新增流程
- **冲突检测**：修改前必须检查编码引用关系

## 快速操作指南

### 创建新文档

1. **选择文档类型**：根据需求选择 L0-L6 层级
2. **使用模板**：从 `assets/templates/` 选择对应模板
3. **设置编码**：遵循编码分配强制流程
4. **更新索引**：立即更新所有相关索引

### 分配新编码

**强制流程**（必须严格遵循）：
1. 读取 `ued/README.md` 中的编码计数器
2. 搜索 `ued/` 目录确认编码未被使用
3. 从计数器获取下一个编号
4. **立即更新**：文档清单 + 全局索引 + 计数器
5. 验证索引一致性

### 处理编码修改请求

**正确响应**：
```
❌ 不能直接修改编码含义
✅ 建议废弃+新增流程：
1. 标注原编码为"已废弃"
2. 分配新编码给新内容
3. 更新相关引用和索引
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
