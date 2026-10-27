# AI 运行时配置解析

> 创建或编辑设计文档、解析模板 `{当前用户.作者}` / `{项目编码}` 时加载。

额外配置文件 **已移除且 MUST NOT 继续创建或使用**。按当前作用域 `README.md` 解析。

## 作用域与模式（按结构判定，无 `doc_mode` 字段）

模式**不再由字段声明**，按目录结构判定：

| 结构 | 判定 | 职责 |
|------|------|------|
| `ued/` 下有业务文档，`ued/README.md` 无应用注册表 | 单应用 | `ued/README.md` 承担入口、元信息、计数器与全局索引 |
| `ued/README.md` 含**应用注册表**（`app_key` + 目录 + `project_code`） | 多应用顶层 | 仅总入口、注册表与跨应用规则；**MUST NOT** 充当某应用的项目编码 / 产品版本 / 细项索引来源 |
| `ued/{app-name}/README.md`，且顶层注册表登记了该 `app_key` | 应用级 | 该应用的元信息、计数器、导航与索引，独立 `产品版本` 与 `baselines/` |
| `ued/shared/README.md`（可选） | 共享作用域 | 自成一个作用域，拥有自己的 `project_code`、产品版本与基线；不归任何单应用 |

- 顶层 README **MUST** 含应用注册表，而不是模式字段；应用级 README **MUST** 含 `app_key`，且与注册表一致。
- 同一作用域内模式不一致（如顶层有注册表、子目录却无 README）→ 停下提示补齐，**MUST NOT** 猜一个模式继续。

## 解析顺序

**作者**：作用域 README 的 `author`/`maintainer` → 运行环境主体标识 → 默认 `[designdoc](https://github.com/reddishz/designdoc)`。

**项目编码**：作用域 `project_code` →（多应用）顶层注册表交叉校验 → 默认无（简洁编码）。**MUST NOT** 启用前缀，除非已配置且请求方确认。

**提示（MANDATORY）**：多应用迹象 → 提示迁入子目录并注册；未配置 `project_code` 不得擅自加前缀。缺 README 字段时用解析链末位默认值继续，并 SHOULD 提醒补元信息。

项目编码形态与消歧见 [coding-system.md · 项目编码规则](../coding-system.md#项目编码规则)。README 最小字段（RECOMMENDED）：`project_name`、`project_code`、`app_key`（仅应用级）、`scope`、`author`/`maintainer`、`last_updated`、`产品版本`（仅应用级 / 单应用）。**MUST NOT** 写 `doc_mode`。
