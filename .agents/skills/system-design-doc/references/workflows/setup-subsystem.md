# 登记与激活子系统

## 适用

- 系统第一次建立，需要确立系统架构并登记首批子系统。
- 新增一个业务子系统或共享库。
- 子系统从 `初稿` 激活为 `正式`。
- 子系统停用为 `废弃`。

## Checkpoint（MUST）

登记、激活、废弃前，先给出短计划并等待人确认。计划至少包含：

- `subsystem_key`、中文名称、目录、编码前缀（不得为 `SYS`）；
- 在 `ued/architecture/system-architecture.md` 中的系统角色、核心职责、明确非职责与边界；
- 与其他子系统的交互关系与依赖 / 被依赖关系；
- 若涉及拆分/合并或系统级边界变化，是否需新增 `SYS-ADR`；
- 状态变化（`初稿` / `正式` / `废弃`）及生效时点。

AI **MUST NOT** 自行完成上述动作。

## 新建并登记

1. **定键**：`^[a-z][a-z0-9-]*$`；不可与现有键、保留名（`architecture`、`releases`、`references`、`assets`、`deprecated`、`baselines`、`glossary`）冲突。键登记后不可改、不可复用。
2. **定目录**：`ued/{目录}/`，单层、唯一；不必等于键，但建议一致。
3. **定前缀**：需要全局唯一编码时给 `[A-Z][A-Z0-9]{1,4}`（**MUST NOT** 为 `SYS`）；不需要则留空。前缀全系统唯一、不得复用。
4. **登记行**：在 `ued/README.md` 的五列子系统注册表追加一行，状态先写 `初稿`：

   ```markdown
   | crm | 客户关系 | crm/ | CRM | 初稿 |
   ```

5. **在系统架构分配职责**：在 `ued/architecture/system-architecture.md` 的「子系统职责分配」表新增该 `subsystem_key` 的系统角色、核心职责、明确非职责与边界；同步更新「系统交互」表（如存在跨子系统协作）。若本次新增改变既有系统边界，同时递增架构修订号并按需记录 `SYS-ADR`。
6. **建目录与 README**：按 `design-doc` 的 `readme-template.md` 创建 `ued/crm/README.md`，并追加 `readme-subsystem-overlay.md`：
   - 若启用前缀，`project_code` 写与注册表一致的值。
   - 链接全局术语表 `[../glossary.md](../glossary.md)` 与系统架构文档 `[../architecture/system-architecture.md](../architecture/system-architecture.md)`。
7. **写子系统内部设计**：按 `design-doc` 编写 L2/L3/L4 等设计文档落实系统分配的职责；子系统内部 `CMP` 只描述本子系统的内部逻辑组件，并在需要时于 `来源` 中回指 `SYS-CON-*` / `SYS-ADR-*`。
8. **声明依赖**：在首份基线中写入 `depends_on` / `external_deps`（见 [subsystem-baseline.md](subsystem-baseline.md)）。
9. **校验**：
   ```bash
   python3 .agents/skills/system-design-doc/scripts/check_system.py -p ued
   python3 .agents/skills/design-doc/scripts/check_docs.py -p ued/crm --glossary ued/glossary.md
   ```

## 激活（`初稿 → 正式`）

逐项确认：

- [ ] 注册表行存在（五列），键 / 目录 / 前缀合法且唯一。
- [ ] `ued/architecture/system-architecture.md` 存在且有效（状态 `正式`，或 `草案` 且修订记录中已有 `正式` 修订），职责分配表已完整登记本 `subsystem_key` 的系统角色、核心职责与明确非职责。
- [ ] 子系统 README 有 `产品版本`（`vX.Y`）。
- [ ] 已生成 `ued/crm/baselines/{vX.Y}.yaml`（`--bump-product`）。
- [ ] 基线含 `depends_on` / `external_deps`；确无依赖写 `[]`。
- [ ] 两个检查器均无 ERROR。
- [ ] 人审确认后，注册表状态改 `正式`。

## 废弃（`正式 → 废弃`）

1. **Checkpoint**：说明停用原因、受影响的系统架构与发布、是否已有替代子系统。
2. 注册表状态改 `废弃`；目录、README、文档、基线**全部保留**。
3. 如影响当前系统架构，更新 `system-architecture.md`（递增修订号）并按需记录 `SYS-ADR`。
4. 后续系统发布 **MUST NOT** 再包含它；历史发布清单与历史架构修订不改。
5. 键、目录、前缀继续占用，**MUST NOT** 复用。
6. 如需恢复：人审后改回 `初稿`，重新走激活检查；**MUST NOT** 直接改回 `正式`。

## 共享库

共享库按同样步骤登记，**没有特殊字段或目录**：

```markdown
| shared-lib | 公共库 | shared-lib/ | LIB | 正式 |
```

- 需要几个建几个；可以没有。
- 其职责与边界同样在 `ued/architecture/system-architecture.md` 中定义；依赖关系用 `depends_on` 表达。

## 禁止

- **MUST NOT** 在系统根建 `L0-vision/`–`L6-verification/` 作为「系统级作用域」。
- **MUST NOT** 在注册表恢复 `角色文档` 列或用子系统 `CMP` 充当子系统系统角色。
- **MUST NOT** 为共享库固定 `shared/` 目录或特殊状态。
- **MUST NOT** 删除已登记子系统的目录或复用其键 / 前缀。
- **MUST NOT** 在系统架构未完成职责分配或缺少基线时把子系统设为 `正式`。
