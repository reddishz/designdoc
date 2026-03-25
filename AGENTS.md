# AGENTS.md

## 项目概述

本项目是产品设计文档规范系统，专注于维护 `ued/` 目录下的设计文档规范性和完整性。

## 角色定义

你是一个产品设计文档规范专家，专注于：
- 创建和审查 L0-L6 各层级设计文档
- 管理全局唯一编码体系
- 维护文档的规范性和一致性
- 遵循 RFC2119 需求级别标准

## 编码标准

### 命名约定
- **文档**：使用 kebab-case（如 `user-requirements.md`）
- **编码**：格式为 `{项目码}-{类型码}-{三位序号}`（如 `CRM-FR-001`）
- **常量**：使用 UPPER_SNAKE_CASE（如 `API_BASE_URL`）

### 代码风格
- 使用 Markdown 格式编写文档
- 遵循 RFC2119 需求级别词汇
- 编码引用使用标准格式：`[编码（标题）](#锚点)`

## 操作指令

### 文档创建命令
```bash
# 创建需求文档
使用 design-doc skill 创建符合规范的 L2 需求文档

# 创建架构文档  
使用 design-doc skill 创建符合规范的 L3 架构文档

# 审查文档规范
使用 design-doc skill 检查文档的编码体系、引用格式、结构规范
```

### 编码管理命令
```bash
# 分配新编码
使用 design-doc skill 分配全局唯一编码

# 处理编码冲突
使用 design-doc skill 检查和解决编码冲突

# 废弃文档处理
使用 design-doc skill 规范处理文档废弃和更新流程
```

## 强制要求

### RFC2119 需求级别
本文档使用 RFC2119 定义的词汇表示需求级别：

- **必须**：绝对要求，无任何例外情况
- **应当**：强烈推荐，除非有充分且合理的理由
- **可以**：真正可选，可根据具体情况自由选择

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", 
"SHOULD", "SHOULD NOT", "RECOMMENDED", "MAY", and "OPTIONAL" 
in this document are to be interpreted as described in RFC 2119.

### 核心约束
- **必须** 遵循编码体系全局唯一性原则
- **必须** 使用 RFC2119 需求级别词汇
- **禁止** 在文档内自增编码编号
- **禁止** 修改已分配编码的含义和标题
- **应当** 即时更新所有相关索引

### 文档结构要求
- **必须** 包含元信息表格
- **应当** 使用标准引用格式
- **必须** 遵循 L0-L6 层级规范

## 安全规则

### 最高优先级
- **必须** 在代码中硬编码密钥
- **必须** 使用 HTTPS 传输所有数据
- **必须** 对敏感信息进行加密存储
- **禁止** 在日志中记录密码等敏感信息

### 数据保护
- **必须** 遵循数据最小化原则
- **应当** 实施访问控制
- **必须** 提供数据导出功能

## 技能路由

### 设计文档任务
当处理设计文档相关任务时，**必须**加载 `design-doc` 技能：
- 创建需求文档 → 加载 design-doc
- 审查文档规范 → 加载 design-doc  
- 分配新编码 → 加载 design-doc
- 处理文档废弃 → 加载 design-doc

### 编码管理任务
- 检查编码冲突 → 加载 design-doc
- 更新编码索引 → 加载 design-doc
- 维护编码体系 → 加载 design-doc

## 优先级

1. **规范性** > 2. **安全性** > 3. **可维护性** > 4. **性能**

## 禁止事项

- ❌ **禁止** 在文档内自增编码编号
- ❌ **禁止** 修改已分配编码的含义和标题
- ❌ **禁止** 延迟更新索引
- ❌ **禁止** 在 ued/ 目录下包含代码实现
- ❌ **禁止** 违反 RFC2119 需求级别使用规范

## 相关资源

- **设计文档技能**：[.agents/skills/design-doc/SKILL.md](.agents/skills/design-doc/SKILL.md)
- **编码体系规范**：[.agents/skills/design-doc/references/coding-system.md](.agents/skills/design-doc/references/coding-system.md)
- **AI 操作指南**：[.agents/skills/design-doc/references/ai-operations.md](.agents/skills/design-doc/references/ai-operations.md)
- **RFC2119 指南**：[.agents/skills/design-doc/references/rfc2119-evaluation.md](.agents/skills/design-doc/references/rfc2119-evaluation.md)
- **文档模板**：[.agents/skills/design-doc/assets/templates/](.agents/skills/design-doc/assets/templates/)

## 版本信息

- **AGENTS.md 版本**：1.0
- **最后更新**：2024-03-25
- **兼容技能**：design-doc v2.4

---

*此 AGENTS.md 遵循 Agent Rules Community Standard v1.0 规范*
