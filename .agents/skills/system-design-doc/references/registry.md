# 子系统注册表

注册表位于系统根 `ued/README.md`，是系统组成的**唯一真源**（回答「系统包含哪些子系统及其生命周期状态」）。子系统的系统角色与职责边界由 [architecture-description.md](architecture-description.md) 规定的 `ued/architecture/system-architecture.md` 权威定义，注册表不承载职责正文，也不再绑定子系统内部 `CMP`。

系统检查器以「同时包含 `subsystem_key`、`目录`、`状态` 列的表」识别系统。

## 表结构

```markdown
## 子系统注册表

| subsystem_key | 子系统名称 | 目录 | 编码前缀 | 状态 |
|---------------|------------|------|----------|------|
| crm | 客户关系 | crm/ | CRM | 正式 |
| oms | 订单中心 | oms/ | OMS | 正式 |
| shared-lib | 公共库 | shared-lib/ | LIB | 正式 |
```

五列 **MUST** 齐备，列名 **MUST** 与上表一致（`subsystem_key` 保持英文）。允许在五列之后追加说明列，但不得改变前五列语义，也 **MUST NOT** 保留 v1.x 的 `角色文档` 列（检出旧列直接报 ERROR，请按 [migration-from-design-doc.md](migration-from-design-doc.md#从-system-design-doc-v1x-迁移到-v20) 迁移）。

## 字段规则

### `subsystem_key`

- 格式：`^[a-z][a-z0-9-]*$`；建议短、稳定、可读。
- 全系统唯一；**登记后不可改、不可复用**（含 `废弃` 后）。
- 不使用保留名：`architecture`、`releases`、`references`、`assets`、`deprecated`、`baselines`、`glossary`。
- 不以 `l0`–`l6` 开头（避免与 design-doc 层级目录混淆）。

### `子系统名称`

非空中文名称；用于导航，可维护性调整，不影响键。

### `目录`

- 相对 `ued/` 的**单层目录**，写作 `{目录}/`；**MUST** 是 `ued/` 的直接子目录。
- 全系统唯一；目录 **MUST** 存在，且含 `README.md`。
- 目录与 `subsystem_key` **不要求相等**，但建议一致；键才是稳定标识。
- **MUST NOT** 使用保留目录（`architecture`、`releases`、`references`、`assets`、`deprecated`、`baselines`）或 `L0-vision`–`L6-verification` 形态。
- 子系统目录内 **MUST NOT** 再出现嵌套的 design-doc 作用域。

### `编码前缀`

- 可空；非空时格式 `^[A-Z][A-Z0-9]{1,4}$`，全系统唯一，**不得复用**。
- **MUST NOT** 使用系统保留前缀 `SYS`。
- 非空时 **MUST** 与该子系统 `README.md` 的 `project_code` 完全一致。
- 子系统 README 的 `project_code` 非空时，注册表 **MUST** 登记同一前缀。
- 前缀用于该子系统全部定义编码；子系统内部引用 **MAY** 省略该前缀，跨子系统引用 **MUST** 写全量编码。
- 前缀规则与消歧见 design-doc 的 `coding-system.md`；本技能只做系统级唯一性与一致性校验。

### `状态`

只取三态：

| 状态 | 含义 | 要求 |
|------|------|------|
| `初稿` | 已登记、尚未启用 | 目录与 README 存在；架构职责分配与基线可暂未就绪 |
| `正式` | 在用 | 系统架构文档有效且已分配本子系统职责、README `产品版本` 与对应基线齐备 |
| `废弃` | 已停用、保留追溯 | 目录与文档保留；不再进入新系统发布 |

`草案` **不适用**于子系统注册表，出现即 ERROR。`废弃` 后如需恢复，须人审后改为 `初稿`，重新走激活检查；`subsystem_key` 与编码前缀不变。

## 系统根 README

系统根 `ued/README.md` **MUST** 包含：

1. 项目元信息：`project_name`、`scope`（说明为系统 + 子系统）、`author`、`last_updated`。
2. **当前结构**说明：本仓库为系统 + 子系统；系统级架构在 `architecture/`，子系统内部按 design-doc。
3. **系统架构入口**：链接至 `architecture/system-architecture.md`（与 `architecture/` 下的 `SYS-ADR` 目录），不复制职责正文。
4. **子系统注册表**（五列）。
5. **系统发布索引**：`发布 | 日期 | 说明 | 清单`，指向 `releases/sys-vX.Y.yaml`。

系统根 README **MUST NOT**：

- 有 `产品版本` 字段；
- 有 `baselines/` 目录；
- 有 `文档索引`、`编码计数器`、`全局编码索引`（这些属于子系统）；
- 承载 `L0-vision/`–`L6-verification/` 层级目录或重复维护子系统职责正文。

系统根允许：`README.md`、`glossary.md`、`architecture/`、`releases/`、`references/`（原始资料）、`assets/`、`deprecated/`。

## 子系统 README

子系统 README 按 design-doc 模板创建，并补充：

- 若启用编码前缀，`project_code` **MUST** 与注册表一致（且不得为 `SYS`）。
- 必须链接全局术语表：`[../glossary.md](../glossary.md)`（从子系统根 `ued/{subsystem}/README.md` 指向 `ued/glossary.md`）。
- 建议增加「系统归属」短节：链接系统根 README、系统架构文档 `../architecture/system-architecture.md` 与发布清单 `../releases/`。

## 激活与废弃

**激活（`初稿 → 正式`）前置**：

1. 注册表行已登记，键 / 目录 / 前缀合法且唯一。
2. `ued/architecture/system-architecture.md` 存在且有效（状态 `正式`，或 `草案` 且修订记录含 `正式` 修订），且职责分配表已完整登记本 `subsystem_key` 的角色、核心职责、明确非职责与边界。
3. 子系统 README `产品版本` 已设置，且 `baselines/{vX.Y}.yaml` 已生成。
4. 基线已声明 `depends_on` / `external_deps`（确无依赖写空列表）。
5. 系统检查器与该子系统的 design-doc 检查器均通过。

**废弃（`正式 → 废弃`）**：

1. 人审确认；历史系统发布与历史架构修订不改。
2. 注册表状态改 `废弃`；目录、README、文档与基线保留。
3. 如影响当前系统架构，更新 `system-architecture.md`（递增修订号）并在需要时补充 `SYS-ADR`。
4. 后续系统发布 **MUST NOT** 再包含该子系统。
5. 编码、键、前缀继续占用，**MUST NOT** 复用。
