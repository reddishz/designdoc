# 决策卡：先判断你在哪一层

## 第一步：是系统还是单系统？

看 `ued/README.md`：

- 有**子系统注册表**（含 `subsystem_key` + `目录` + `状态` 列）→ 系统，用本技能。
- 没有注册表，且 `ued/` 下没有嵌套的 design-doc 作用域 → 单系统，用 `design-doc`。
- 有嵌套作用域但没有注册表 → 结构不一致，先补注册表；**MUST NOT** 猜一种结构继续。

## 第二步：你要做什么？

| 你要做的事 | 去哪 |
|------------|------|
| 明确系统目标、子系统职责划分、交互与全局约束 | [architecture-description.md](architecture-description.md) |
| 记录跨子系统架构决策（`SYS-ADR`） | [architecture-description.md](architecture-description.md#sys-adr-文档规则) |
| 新建一个子系统 / 登记目录 / 激活 / 废弃 | [setup-subsystem.md](workflows/setup-subsystem.md) |
| 子系统要发版，或要改依赖钉住 | [subsystem-baseline.md](workflows/subsystem-baseline.md) |
| 把一组子系统作为一个产品集发布 | [system-release.md](workflows/system-release.md) |
| 审查系统架构、结构、依赖与发布 | [review-system.md](workflows/review-system.md) |
| 只改某个子系统内部设计（L0–L6、内部 `CMP`） | 转 [design-doc](../../design-doc/SKILL.md) |
| 统一术语 | `design-doc` 术语规范；全局表仍在 `ued/glossary.md` |
| 从旧多应用结构或 `system-design-doc` v1.x 迁移 | [migration-from-design-doc.md](migration-from-design-doc.md) |

## 第三步：停点

以下动作 **MUST** 先给人短计划并等待确认：

- 修改系统架构职责分配、新增/修改系统级约束或 `SYS-ADR` 定稿；
- 登记新子系统（键、目录、前缀、系统职责分配）；
- `初稿 → 正式` 激活；
- `正式 → 废弃`；
- 创建 `sys-vX.Y` 系统发布；
- 修改任何已发布清单（不允许；只能新发）。

## 常见误区

- **「在子系统 L3 写一个 `CMP` 定义本子系统的角色」**：错。子系统角色与职责边界的唯一真源在 `ued/architecture/system-architecture.md`；子系统内 `CMP` 只描述本子系统内部逻辑组件。
- **「系统级约束/架构决策塞给某个普通子系统代管」**：不要。跨子系统约束用 `SYS-CON` 写在 `system-architecture.md`，跨子系统决策用 `ued/architecture/SYS-ADR-*.md`。
- **「系统根建一整套 L0–L6 和基线」**：不要。系统层只保留轻量的 `architecture/` 与 `releases/`，不复制 `design-doc` 作用域。
- **「共享库要单独建 `shared/`」**：不需要。共享库按普通子系统登记与分配职责，可有零个或多个。
- **「系统也要一个 `产品版本`」**：不要。系统组合版本写在 `releases/sys-vX.Y.yaml`，架构演进用 `system-architecture.md` 修订号 + `architecture_rev` 追溯。
- **「依赖改了 PATCH 一下」**：不允许。PATCH 不碰依赖；基线进入系统发布组合后，依赖变化必须立新基线，冻结前可原地修正。
- **「系统发布必须包含所有正式子系统」**：不必。发布是可选快照；纳入项依赖闭合即可，未纳入的正式成员不受影响。
- **「系统发布可以改」**：不允许。发布不可变，错了发新版本。
