# 登记与激活子系统

## 适用

- 系统第一次建立，需要登记首批子系统。
- 新增一个业务子系统或共享库。
- 子系统从 `初稿` 激活为 `正式`。
- 子系统停用为 `废弃`。

## Checkpoint（MUST）

登记、激活、废弃前，先给出短计划并等待人确认。计划至少包含：

- `subsystem_key`、中文名称、目录、编码前缀；
- 角色归属与角色文档（`CMP`）放在哪份 L3 文档；
- 与其他子系统的依赖 / 被依赖关系；
- 状态变化（`初稿` / `正式` / `废弃`）及生效时点。

AI **MUST NOT** 自行完成上述动作。

## 新建并登记

1. **定键**：`^[a-z][a-z0-9-]*$`；不可与现有键、保留名冲突。键登记后不可改、不可复用。
2. **定目录**：`ued/{目录}/`，单层、唯一；不必等于键，但建议一致。
3. **定前缀**：需要全局唯一编码时给 `[A-Z][A-Z0-9]{1,4}`；不需要则留空。前缀全系统唯一、不得复用。
4. **登记行**：在 `ued/README.md` 的子系统注册表追加一行，状态先写 `初稿`：

   ```markdown
   | crm | 客户关系 | crm/ | CRM | CRM-CMP-001 | 初稿 |
   ```

5. **建目录与 README**：按 design-doc 的 `readme-template.md` 创建 `ued/crm/README.md`。
   - 若启用前缀，`project_code` 写与注册表一致的值。
   - 链接全局术语表 `[../../glossary.md](../../glossary.md)`。
   - 建议加「系统归属」短节。
6. **写设计**：至少建立承载需求的 L2 与承载子系统角色的 L3 文档；角色 `CMP` 覆盖角色、范围边界、交互。
7. **声明依赖**：在子系统 README 中记录计划依赖；实际钉住在首份基线中写（见 [subsystem-baseline.md](subsystem-baseline.md)）。
8. **校验**：
   ```bash
   python3 .agents/skills/system-design-doc/scripts/check_system.py -p ued
   python3 .agents/skills/design-doc/scripts/check_docs.py -p ued/crm --glossary ued/glossary.md
   ```

## 激活（`初稿 → 正式`）

逐项确认：

- [ ] 注册表行存在，键 / 目录 / 前缀唯一。
- [ ] `CMP` 角色文档已定义，覆盖角色、边界、交互，且 `细项状态 = 正式`。
- [ ] 子系统 README 有 `产品版本`（`vX.Y`）。
- [ ] 已生成 `ued/crm/baselines/{vX.Y}.yaml`（`--bump-product`）。
- [ ] 基线含 `depends_on` / `external_deps`；确无依赖写 `[]`。
- [ ] 两个检查器均无 ERROR。
- [ ] 人审确认后，注册表状态改 `正式`。

## 废弃（`正式 → 废弃`）

1. **Checkpoint**：说明停用原因、受影响的系统发布、是否已有替代子系统。
2. 注册表状态改 `废弃`；目录、README、文档、基线**全部保留**。
3. 后续系统发布 **MUST NOT** 再包含它；历史发布清单不改。
4. 键、目录、前缀继续占用，**MUST NOT** 复用。
5. 如需恢复：人审后改回 `初稿`，重新走激活检查；**MUST NOT** 直接改回 `正式`。

## 共享库

共享库按同样步骤登记，**没有特殊字段或目录**：

```markdown
| shared-lib | 公共库 | shared-lib/ | LIB | LIB-CMP-001 | 正式 |
```

- 需要几个建几个；可以没有。
- 它与其他子系统的关系仍用 `depends_on` 表达。

## 禁止

- **MUST NOT** 在系统根建 `L0-vision/`–`L6-verification/` 作为「系统级作用域」。
- **MUST NOT** 为共享库固定 `shared/` 目录或特殊状态。
- **MUST NOT** 删除已登记子系统的目录或复用其键 / 前缀。
- **MUST NOT** 在未完成角色文档与基线时把子系统设为 `正式`。
