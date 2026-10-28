# 模板索引

| 模板 | 用途 | 文件 |
|------|------|------|
| 系统根 README | `ued/README.md`：结构说明、子系统注册表、系统发布索引 | [readme-system.md](readme-system.md) |
| 子系统 README 片段 | 追加到 design-doc README 的「系统归属」短节 | [readme-subsystem-overlay.md](readme-subsystem-overlay.md) |
| 系统发布清单 | `ued/releases/sys-vX.Y.yaml` | [system-release.yaml](system-release.yaml) |

## 模板边界（哨兵）

- 待复制正文只放在 `TEMPLATE:BEGIN` / `TEMPLATE:END` 之间。
- 哨兵必须成对、每个模板只出现一次；哨兵外只放使用说明，**MUST NOT** 混入实例正文。
- 实例化时剥除哨兵与哨兵外说明。
- 模板内的 `{...}` 是占位符，实例必须替换；不得把占位符留在正式文档中。

## 使用顺序

1. 先按 [../references/decision-card.md](../references/decision-card.md) 判定是系统还是单系统。
2. 系统根用 `readme-system.md`；子系统主体用 design-doc 的 `readme-template.md`，再追加 `readme-subsystem-overlay.md`。
3. 发布清单用 `system-release.yaml`，复制到 `ued/releases/sys-vX.Y.yaml` 后替换占位符。
4. 创建后运行 `check_system.py`，并逐子系统运行 design-doc 检查器。

## 不提供的模板

本技能**不提供**：

- 固定 `shared/` 共享库模板——共享库就是普通子系统。
- 系统级 L0–L6 文档模板——系统级内容放进承担职责的普通子系统。
- 系统级 `baselines/` 模板——系统发布清单不是设计基线。
