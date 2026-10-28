# 决策卡：先判断你在哪一层

## 第一步：是系统还是单系统？

看 `ued/README.md`：

- 有**子系统注册表**（含 `subsystem_key` + `目录` 列）→ 系统，用本技能。
- 没有注册表，且 `ued/` 下没有嵌套的 design-doc 作用域 → 单系统，用 design-doc。
- 有嵌套作用域但没有注册表 → 结构不一致，先补注册表；**MUST NOT** 猜一种结构继续。

## 第二步：你要做什么？

| 你要做的事 | 去哪 |
|------------|------|
| 新建一个子系统 / 登记目录 / 激活 / 废弃 | [setup-subsystem.md](workflows/setup-subsystem.md) |
| 子系统要发版，或要改依赖钉住 | [subsystem-baseline.md](workflows/subsystem-baseline.md) |
| 把一组子系统作为一个产品集发布 | [system-release.md](workflows/system-release.md) |
| 审查系统结构、依赖、发布 | [review-system.md](workflows/review-system.md) |
| 只改某个子系统内部设计 | 转 [design-doc](../design-doc/SKILL.md) |
| 统一术语 | design-doc 的术语规范；全局表仍在 `ued/glossary.md` |
| 从旧多应用结构迁过来 | [migration-from-design-doc.md](migration-from-design-doc.md) |

## 第三步：停点

以下动作 **MUST** 先给人短计划并等待确认：

- 登记新子系统（键、目录、前缀、角色归属）；
- `初稿 → 正式` 激活；
- `正式 → 废弃`；
- 创建 `sys-vX.Y` 系统发布；
- 修改任何已发布清单（不允许；只能新发）。

## 常见误区

- **「共享库要单独建 shared/」**：不需要。共享库按普通子系统登记，可有零个或多个。
- **「系统也要一个产品版本」**：不要。系统版本只在 `releases/sys-vX.Y.yaml`。
- **「系统根也放 L0/L2 文档」**：不要。放到承担职责的普通子系统，或只在根 README 写摘要。
- **「依赖改了 PATCH 一下」**：不允许。依赖钉住变化必须立新基线。
- **「系统发布可以改」**：不允许。发布不可变，错了发新版本。
