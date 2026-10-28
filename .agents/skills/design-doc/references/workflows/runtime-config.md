# AI 运行时配置解析

> 创建或编辑设计文档、解析模板 `{当前用户.作者}` / `{项目编码}` 时加载。

额外配置文件 **已移除且 MUST NOT 继续创建或使用**。按当前作用域 `README.md` 解析。

## 作用域（单系统 or 子系统）

本技能一次只处理**一个**设计作用域。按目录结构判定：

| 结构 | 判定 | 职责 |
|------|------|------|
| `ued/` 内有业务文档，`ued/README.md` 无**子系统注册表** | 单系统 | `ued/README.md` 承担入口、元信息、计数器与全局索引 |
| `ued/README.md` 含**子系统注册表**，各子系统目录各有 `README.md` | 多子系统 | 本技能只对每个 `ued/{subsystem}/` 运行；系统根由 [system-design-doc](../../../system-design-doc/SKILL.md) 负责 |
| `ued/{subsystem}/README.md` 存在且顶层注册表登记了它 | 子系统作用域 | 该子系统的元信息、计数器、导航与索引，独立 `产品版本` 与 `baselines/` |

- 判定顺序：先看 `ued/README.md` 是否含子系统注册表；含 → 多子系统，**MUST NOT** 把系统根当单系统作用域。
- 检出 `应用注册表` / `app_key` / `doc_mode` → 9.x 旧多应用结构，**MUST** 先按 system-design-doc 的迁移流程转换，**MUST NOT** 按单系统继续。
- 子系统的 `project_code`（若配置）**MUST** 与注册表 `编码前缀` 一致。
- 注册表缺失登记、或注册了目录却无 `README.md` → 停下提示，**MUST NOT** 猜一个作用域继续。
- 共享库不是特殊作用域：它就是注册表里的普通子系统，按同样规则处理。

## 解析顺序

**作者**：作用域 README 的 `author`/`maintainer` → 运行环境主体标识 → 默认 `[designdoc](https://github.com/reddishz/designdoc)`。

**项目编码**：作用域 `project_code` →（系统内）注册表 `编码前缀` 交叉校验 → 默认无（简洁编码）。**MUST NOT** 启用前缀，除非已配置且请求方确认。

**术语表**：项目术语表固定在系统根 `ued/glossary.md`；子系统校验时用 `--glossary` 指向它，**MUST NOT** 在各子系统内另建术语表。

**提示（MANDATORY）**：出现多子系统迹象 → 提示按子系统登记并迁入子目录；未配置 `project_code` 不得擅自加前缀。缺 README 字段时用解析链末位默认值继续，并 SHOULD 提醒补元信息。

项目编码形态与消歧见 [coding-system.md · 项目编码规则](../coding-system.md#项目编码规则)。README 最小字段（RECOMMENDED）：`project_name`、`project_code`、`scope`、`author`/`maintainer`、`last_updated`、`产品版本`（仅作用域 README）。**MUST NOT** 写 `doc_mode`。
