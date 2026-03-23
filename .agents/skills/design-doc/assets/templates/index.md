# 设计文档模板索引

> **说明**：可复制的文档骨架均在本目录（`assets/templates/`）。流程图写法、AI 编码约束等**非模板**说明见 [辅助指南](../guides/README.md)。

## 快速模板选择

### 项目管理模板

| 类型 | 模板名称 | 用途 | 模板位置 |
|------|----------|------|----------|
| README | 项目文档索引 | 全局编码索引、文档导航、编码计数器 | [readme-template.md](readme-template.md) ✅ |

### 设计文档模板（L0-L6）

| 层级 | 模板名称 | 状态值 | 主要内容 | 模板位置 |
|------|----------|--------|----------|----------|
| L0 | 战略与愿景 | 草稿/正式/废弃 | 愿景、目标、成功标准 | [l0-strategy.md](l0-strategy.md) ✅ |
| L1 | 利益相关者需求 | 草稿/正式/废弃 | 利益相关者、场景需求 | [l1-stakeholder.md](l1-stakeholder.md) ✅ |
| L2 | 系统/产品需求 | 草稿/正式/废弃 | 功能需求、非功能需求 | [l2-requirements.md](l2-requirements.md) ✅ |
| L3 | 概念架构 | 草稿/正式/废弃 | 架构原则、组件设计 | [l3-concept-architecture.md](l3-concept-architecture.md) ✅ |
| L4 | 逻辑/系统设计 | 草稿/正式/废弃 | 系统设计、接口契约 | [l4-system-design.md](l4-system-design.md) ✅ |
| L5 | 详细设计 | 草稿/正式/废弃 | 组件详细设计 | [l5-detailed-design.md](l5-detailed-design.md) ✅ |
| L6 | 验证与确认 | 草稿/正式/废弃 | 测试策略、需求追溯 | [l6-verification.md](l6-verification.md) ✅ |

### 专项模板

| 类型 | 模板名称 | 状态值 | 用途 | 模板位置 |
|------|----------|--------|------|----------|
| ADR | 架构决策记录 | 提议/采纳/拒绝/废弃/取代 | 记录重要架构决策 | [adr.md](adr.md) ✅ |
| REF | 外部参考资料 | 有效/废弃 | 管理外部参考资源 | [ref.md](ref.md) ✅ |
| README | 项目文档索引 | - | 全局编码索引、文档导航、编码计数器 | [readme-template.md](readme-template.md) ✅ |
| 项目注册表 | 项目编码管理 | - | 企业级项目编码统一管理 | [project-registry.md](project-registry.md) ✅ |
| 流程图指南 | 流程图格式规范 | - | 指导如何选择合适的流程图格式 | [../guides/flowchart-guide.md](../guides/flowchart-guide.md) ✅ |
| AI 操作指南 | 编码修改防护 | - | AI 智能体操作规范和编码防护机制 | [../guides/ai-operation-guide.md](../guides/ai-operation-guide.md) ✅ |
| 废弃处理指南 | 废弃细项处理 | - | 规范废弃细项的处理流程和标准 | [../../references/deprecation-guide.md](../../references/deprecation-guide.md) ✅ |

## 使用方法

1. **选择模板**：根据文档类型打开上表对应文件
2. **复制内容**：以模板为起点编写
3. **替换占位符**：更新 `{编号}`、`{文档名称}` 等
4. **设置状态**：从标准状态值中选择
5. **维护编码**：确保全局唯一编码

## 状态值标准

所有状态值必须符合 `references/status-definitions.md` 中的定义：

- **设计文档**：草稿/正式/废弃
- **ADR**：提议/采纳/拒绝/废弃/取代
- **REF**：有效/废弃
- **需求追溯**：待验证/已验证/失败

## 结构说明

- **模板**（本目录）：独立 `.md` 文件，按需打开，利于渐进式加载。
- **辅助指南**（[`../guides/`](../guides/README.md)）：规范与操作说明，非填空模板。
