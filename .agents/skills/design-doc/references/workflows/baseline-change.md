# 产品基线 PATCH / MINOR / MAJOR

> 用户确认补丁、发版或 Checkpoint 5 确认动基线时加载。

**MUST 读**：[`product-version.md`](../product-version.md)。

执行见 [升产品版本（MANDATORY）](../product-version.md#升产品版本mandatory)。优先命令：

- 纠错 / 仅 revision 落后：`check_docs.py --bump-product --patch --note '…'`
- 新编码纳入：`--bump-product --minor`
- 主版本：`--bump-product --major`

README / 文件名两段 `vX.Y`；tip 为 `full_version`（`vX.Y.Z`）。不解冻、不改修订号、不改本文引用、不写 git/svn/构建号。定稿 **MUST NOT** 写基线或手填谱系。
