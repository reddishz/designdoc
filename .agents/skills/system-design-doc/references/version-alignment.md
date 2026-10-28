# 依赖钉住与版本对齐

## 为什么钉住

子系统独立发版，但对外接口是成对演进的。系统必须能回答：**A 的 `v3.1` 与 D 的 `v2.5` 是同一批验证过的组合**。只在 README 写「大概兼容」不够；每个子系统基线必须把依赖写成精确版本，系统发布再把整组版本锁死。

产品版本是两段式 `vX.Y`（见 design-doc `product-version.md`）；`full_version` 的 `Z` 是同一 `vX.Y` 下的工作 tip，不是依赖钉住单位。

## 子系统基线扩展字段

每个子系统基线的顶层 **SHOULD** 包含以下两字段；无依赖时写空列表：

```yaml
product_version: v3.1
full_version: v3.1.2
# ... design-doc 既有字段 ...
depends_on:
  - subsystem: oms
    product_version: v2.5
  - subsystem: shared-lib
    product_version: v1.4
external_deps:
  - name: identity-provider
    product_version: v4.0
items:
  # ...
```

### `depends_on`

| 项 | 规则 |
|----|------|
| 形态 | 列表；每项 mapping，含 `subsystem` 与 `product_version` |
| `subsystem` | 注册表中的 `subsystem_key`；**MUST** 已登记 |
| `product_version` | 两段式 `vX.Y`；**MUST** 在目标子系统存在 `baselines/{vX.Y}.yaml` |
| 自依赖 | **MUST NOT** |
| 重复 | 同一目标 **MUST NOT** 出现多次 |
| 目标状态 | **MUST** 为 `正式`（不能依赖 `初稿` / `废弃`） |
| 变更 | **MUST** 通过立新基线（MINOR/MAJOR）表达；**MUST NOT** 在 PATCH 中改 |

### `external_deps`

| 项 | 规则 |
|----|------|
| 形态 | 列表；每项 mapping，含 `name` 与 `product_version` |
| `name` | `^[a-z][a-z0-9-]*$`；**MUST NOT** 与任何已登记 `subsystem_key` 同名 |
| `product_version` | 两段式 `vX.Y`；外部系统不一定在本仓库有基线 |
| 重复 | 同一 `name` **MUST NOT** 出现多次 |
| 变更 | 同 `depends_on`：立新基线，不能 PATCH |

外部依赖若其实是本系统内的子系统，**MUST** 用 `depends_on`，不要写成 `external_deps`。

## 依赖规则

1. **精确钉住**：`vX.Y` 完全匹配；不允许范围、通配、浮动的 `latest`。
2. **闭合**：A 依赖 B，则同一系统发布必须包含 B，且 B 的版本与 A 钉住的一致。
3. **传递**：B 依赖 C，则发布也必须包含 C；系统检查器逐层校验。
4. **环**：直接自依赖 ERROR；多节点循环 WARNING，SHOULD 通过拆分或调整方向消除。
5. **目标基线存在**：钉住 `v2.5` 就必须有 `baselines/v2.5.yaml`，不能只写 README 版本。
6. **依赖变更即新基线**：`depends_on` / `external_deps` 属于基线快照的一部分；PATCH 只同步 revision 与纠错，**MUST NOT** 改依赖。立新基线时继承旧依赖，再按需修改；design-doc 的基线工具会原样保留这些扩展字段。

## 系统发布钉住

`ued/releases/sys-vX.Y.yaml`：

```yaml
release: sys-v1.0
created: 2026-10-28
note: "首个产品集发布"
subsystems:
  - subsystem: crm
    product_version: v3.1
    full_version: v3.1.2
  - subsystem: oms
    product_version: v2.5
    full_version: v2.5.4
external_deps:
  - name: identity-provider
    product_version: v4.0
```

发布清单的规则：

- 包含当时全部 `正式` 子系统，每个一次；不包含 `初稿`。
- 每项钉住 `product_version` 与 `full_version`；后者 **MUST** 出现在该基线 `patch_log` 中。
- `depends_on` 的目标必须在本清单中，且版本一致。
- 每个子系统 `external_deps` 必须在清单 `external_deps` 中有同名同版本项。
- 外部依赖版本冲突（两个子系统要求同一名字的不同 `vX.Y`）→ ERROR；必须先调整子系统基线，不能由发布清单强行二选一。
- 发布清单是**不可变**的；写错只能发新版本。

## 兼容窗口

| 变更 | 版本位 | 消费者动作 |
|------|--------|------------|
| 修缺陷、文档澄清、不改变公开接口语义 | PATCH（`full_version` Z） | 无需改钉住，可在下次 PATCH 同步 |
| 向后兼容的新增（可选字段、新操作、新事件） | MINOR | 可保持旧钉住；采用新 MINOR 需验证并立新基线更新钉住 |
| 删除 / 重命名 / 类型或语义变更 / 新增必填 | MAJOR | **MUST** 协调所有消费者，更新各自基线与系统发布 |

系统发布钉住的是**实际验证过的两段版本**，不自动跟随 MINOR。`v3.1` 的消费者不会因为提供方发了 `v3.2` 就自动升级；要升级就重验、改钉住、发新系统版本。

## 版本不对会怎样

接口契约按版本对齐。A `v3.1` 钉 D `v2.5`，而系统发布把 D 钉成 `v2.6`，即使只差一个 MINOR，也属于**未验证组合**：

- 系统检查器报依赖闭合 / 版本不一致；
- 必须要么把 A 的基线更新到 D `v2.6`（立新基线），要么在发布中把 D 保持 `v2.5`；
- **MUST NOT** 在发布说明里口头声明兼容而不改基线。

## 与 design-doc 产品基线的关系

- 子系统 `baselines/vX.Y.yaml` 仍是 design-doc 的产品基线，成员是设计细项。
- `depends_on` / `external_deps` 是本技能定义的**扩展顶层字段**，不改变 `items`、`added` / `removed` / `changed` 的语义。
- design-doc 的 PATCH / MINOR / MAJOR 工具 **MUST** 原样保留未知顶层字段；本技能的检查器读取并校验它们。
- 系统发布清单**不是** design-doc 基线，不参与 `--bump-product`。
