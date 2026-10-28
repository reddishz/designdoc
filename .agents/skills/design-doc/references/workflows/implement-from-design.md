# 据文档实现（消费侧，MANDATORY）

> 依据已定设计实现或完善代码时加载（含 [before-code-change.md](before-code-change.md) 判定为「仅实现偏离」之后）。

**MUST 另读**：[`product-version.md`](../product-version.md)；状态判定见 [`status-definitions.md`](../status-definitions.md)。

1. **未入当前产品基线 MUST NOT 作为实现依据**：取 README `产品版本` → `baselines/{该版本}.yaml`；目标编码 **MUST** 在其 `items` 中。**MUST NOT** 依据未列出细项，或整篇为 `初稿`/`草案`/`废弃` 的文档实现。
2. **先判状态与基线、后拒绝**：
   - `初稿`/`草案`/`废弃`（或缺字段推定未冻结）→ **MUST 拒绝**；`草案` 豁免须用户逐项明确并留痕，且定稿后复核、升基线后方可作基线依据。
   - `正式` 但不在 `items` → **MUST 拒绝**：首份基线提示 **PATCH** 纳入，已有前驱的基线提示 **MINOR**（成员集合不能原地改）。
   - `正式` 在 `items` 但 revision 落后 → **MUST 拒绝**按新语义实现，提示 **PATCH**。
   - 无基线或无 `产品版本` → **MUST 拒绝**，提示先建基线。
3. **运行版本展示（SHOULD）**：可见版本与当前 `full_version`（`vX.Y.Z`）一致；设计文档 **MUST NOT** 登记构建号/包路径。
4. 审查/Checkpoint 5 提示须含「未入当前产品基线不得作为实现依据」；漂移按基线层级询问：首份基线走 PATCH，非首份仅 revision 落后走 PATCH、成员进出走 MINOR。
