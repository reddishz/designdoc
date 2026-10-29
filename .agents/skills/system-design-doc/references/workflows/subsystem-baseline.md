# 子系统基线：依赖钉住与发版

## 适用

- 子系统首次生成产品基线。
- 子系统 revision / 成员变化，需要 PATCH 或立新基线。
- `depends_on` / `external_deps` 需要补全、新增、删除或改版本。

子系统内部的产品基线规则（首份、PATCH、MINOR、MAJOR、谱系）**完全按 design-doc**；本页只补充系统协作字段与流程。

## 先判断动作

| 变化 | 动作 |
|------|------|
| 仅正式细项 revision 同步、澄清纠错 | PATCH：`--bump-product --patch` |
| 首份基线开发期增删成员 | PATCH（仅首份） |
| 非首份成员进出 | MINOR/MAJOR 立新基线 |
| 基线未进入系统发布组合：依赖块缺字段、`[]` 或需调整 | 原地修正，不升版本（[冻结前修正](#冻结前修正)） |
| 基线已进入系统发布组合：依赖增删或改版本 | **MUST** 立新基线（MINOR/MAJOR），并发新系统版本 |
| 需要冻结独立参考点 | MINOR/MAJOR |

依赖钉住是基线快照的一部分；**MUST NOT** 通过 PATCH 修改，冻结前修正也不经过 PATCH（不升 Z、不记 `patch_log`）。

## 首份基线

1. 确认 README `产品版本`（初值 `v1.0`）。
2. 生成首份基线：
   ```bash
   python3 .agents/skills/design-doc/scripts/check_docs.py -p ued/crm \
     --bump-product --note "首份基线"
   ```
3. 在 `ued/crm/baselines/v1.0.yaml` 的 `items:` 之前写入依赖字段（无依赖写 `[]`）：
   ```yaml
   depends_on:
     - subsystem: oms
       product_version: v2.5
   external_deps:
     - name: identity-provider
       product_version: v4.0
   ```
4. 确认目标版本存在：`ued/oms/baselines/v2.5.yaml`；目标子系统状态为 `正式`。
5. 运行系统检查器。

## 冻结前修正

基线尚未进入任何系统发布组合时，依赖块可以原地调整（缺字段、`[]`、非空皆可），不必立新基线：

1. 直接编辑当前 `baselines/vX.Y.yaml` 的 `depends_on` / `external_deps`；不改 `items`。
2. `full_version` 不变，`patch_log` 不追加；只更新 `updated`。
3. 目标必须 `正式` 且有对应基线文件（见[依赖字段写法](#依赖字段写法)）。
4. 运行系统检查器。

`[]` 表示「已声明无依赖」，不是「未声明」；允许它被修正的理由是基线未冻结，而不是字段为空。基线一旦出现在 `releases/sys-*.yaml` 中即冻结；闭合规则要求清单内子系统的传递依赖同在该清单，间接被依赖的基线也会被列入，不会漏判。此后只能在**新基线**里调整依赖。

## 冻结后依赖变化（立新基线）

1. **Checkpoint**：列出变化的目标、旧版本、新版本、受影响消费者。
2. 立新基线：
   ```bash
   python3 .agents/skills/design-doc/scripts/check_docs.py -p ued/crm \
     --bump-product --minor --note "依赖 oms v2.5 → v2.6"
   ```
   design-doc 会把旧基线的 `depends_on` / `external_deps` 原样继承到新文件。
3. 在新基线中修改依赖字段——这是**新基线创建动作**的一部分，不是 PATCH。
4. 确认新目标基线存在；若目标还未发版，先完成目标子系统发版。
5. 运行系统检查器；再考虑系统发布。

## 依赖字段写法

```yaml
depends_on:
  - subsystem: oms
    product_version: v2.5
  - subsystem: shared-lib
    product_version: v1.4
external_deps:
  - name: identity-provider
    product_version: v4.0
```

规则：

- `product_version` 只写两段 `vX.Y`，不写 `full_version`。
- 同一目标 / 同一外部名只能出现一次。
- 不能自依赖。
- 外部依赖名不能与已登记 `subsystem_key` 同名。
- 目标必须是 `正式` 子系统，且有对应基线文件。

## PATCH 时会发生什么

design-doc 的 PATCH / MINOR / MAJOR 工具会**原样保留**未知顶层字段（包括 `depends_on` / `external_deps`）。因此：

- PATCH 不会丢依赖，但**不允许**改依赖；
- MINOR/MAJOR 会继承旧依赖，供你在新基线中调整；
- 若发现工具写回后依赖字段消失，按规范缺陷处理，先修工具再继续。

## 校验

```bash
python3 .agents/skills/system-design-doc/scripts/check_system.py -p ued
python3 .agents/skills/design-doc/scripts/check_docs.py -p ued/crm --glossary ued/glossary.md
```

系统检查器会验证：

- 依赖目标已登记且 `正式`；
- 目标 `vX.Y` 基线存在；
- 无自依赖、无重复、无外部名冲突；
- 系统发布（若已存在）闭合。

## 禁止

- **MUST NOT** 用 PATCH 改依赖钉住。
- **MUST NOT** 在基线进入系统发布组合后原地改依赖；只能立新基线。
- **MUST NOT** 钉住不存在的目标版本。
- **MUST NOT** 依赖 `初稿` / `废弃` 子系统。
- **MUST NOT** 把系统发布清单当作子系统基线，或反过来。
- **MUST NOT** 为「兼容」在发布说明里口头放宽钉住而不改基线。
