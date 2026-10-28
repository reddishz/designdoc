# 系统发布（产品集）

## 什么是系统发布

`ued/releases/sys-vX.Y.yaml` 把某一时点全部 `正式` 子系统与外部依赖锁成一个可复现的组合。它是**组合锁**，不是设计基线：

- 不含设计细项；
- 不参与 design-doc 的 PATCH / MINOR / MAJOR；
- 不可变：发布后不改，错了发新版本。

## Checkpoint（MUST）

创建系统发布前，给出短计划并等待人确认：

- 系统版本号 `sys-vX.Y`；
- 参与子系统清单（键 + 当前 `vX.Y` + `full_version`）；
- 外部依赖清单与版本；
- 本轮是否有 MAJOR 接口变更、是否所有消费者已适配；
- 与上一系统版本的差异摘要。

AI **MUST NOT** 自行创建或修改系统发布。

## 前置检查

1. 所有 `正式` 子系统都有 README `产品版本` 与对应 `baselines/{vX.Y}.yaml`。
2. 各基线无待 PATCH 的 revision 漂移；有则先 PATCH（成员变化先立新基线）。
3. 各基线的 `depends_on` / `external_deps` 已填写。
4. 依赖目标均已登记且 `正式`，目标版本基线存在。
5. 所有子系统 design-doc 检查通过。
6. 本轮 MAJOR 变更的消费者已更新基线。

## 编写发布清单

1. 选择系统版本号：
   - `sys-vX.Y` 只表达系统组合版本，与子系统版本无关；
   - 组合发生不兼容变化（如子系统 MAJOR 升级、接口不兼容）→ 升 X；
   - 仅新增 / 兼容调整 → 升 Y；
   - 不存在 `sys-vX.Y.Z`，也不存在 PATCH。
2. 新建 `ued/releases/sys-vX.Y.yaml`（已存在则拒绝覆盖）：

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

3. 在系统根 README 的系统发布索引追加一行：

   ```markdown
   | sys-v1.0 | 2026-10-28 | 首个产品集发布 | [清单](releases/sys-v1.0.yaml) |
   ```

4. 运行校验：
   ```bash
   python3 .agents/skills/system-design-doc/scripts/check_system.py -p ued
   ```

## 完整性规则

发布清单 **MUST**：

- 包含当时全部 `正式` 子系统，每个一次；
- 不包含 `初稿` 子系统（`废弃` 也不进入新发布）；
- 每项 `product_version` 两段，`full_version` 三段且前两段一致；
- 每个 `full_version` 出现在对应基线 `patch_log` 中；
- `depends_on` 的目标也在清单中，版本完全一致；
- 覆盖所有子系统的 `external_deps`，同名同版本；
- 外部依赖无版本冲突；
- `release` 与文件名一致；文件不可变。

## 发布后

- **MUST NOT** 修改该文件，包括「小修小补」。
- 发现错误 → 发新的 `sys-vX.Y`，在 `note` 说明取代关系。
- 子系统后续发版**不会**自动改变已发布清单；要采用新版本，发新的系统发布。
- 历史发布清单永远有效，用于追溯当时验证过的组合。

## 与子系统发版的顺序

```text
子系统设计/实现 → 子系统基线（PATCH/MINOR/MAJOR，含依赖钉住）
→ 各子系统检查通过 → 系统发布（组合锁）
```

**MUST NOT** 先发系统发布再补子系统基线；也 **MUST NOT** 在系统发布中写入不存在或未验证的版本。
