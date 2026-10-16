# AI 运行时配置解析

> 创建或编辑设计文档、解析模板 `{当前用户.作者}` / `{项目编码}` 时加载。

额外配置文件 **已移除且 MUST NOT 继续创建或使用**。按当前作用域 `README.md` 解析。

## 作用域

1. **单应用**：业务文档在 `ued/` 下 → `ued/README.md` 承担入口、元信息、计数器与全局索引。
2. **多应用**：每应用在 `ued/{app-name}/`。
3. **多应用顶层 README**：仅总入口与应用注册表，**MUST NOT** 充当某应用的项目编码来源。
4. **应用级 README**：该应用的元信息、计数器、导航与索引。

## 解析顺序

**作者**：作用域 README 的 `author`/`maintainer` → 运行环境主体标识 → 默认 `[designdoc](https://github.com/reddishz/designdoc)`。

**项目编码**：作用域 `project_code` →（多应用）顶层注册表交叉校验 → 默认无（简洁编码）。**MUST NOT** 启用前缀，除非已配置且请求方确认。

**提示（MANDATORY）**：多应用迹象 → 提示迁入子目录并注册；未配置 `project_code` 不得擅自加前缀。缺 README 字段时用解析链末位默认值继续，并 SHOULD 提醒补元信息。

项目编码形态与消歧见 [coding-system.md · 项目编码规则](../coding-system.md#项目编码规则)。README 最小字段（RECOMMENDED）：`project_name`、`project_code`、`doc_mode`、`scope`、`author`/`maintainer`、`产品版本`。
