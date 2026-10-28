# 产品基线 PATCH / MINOR / MAJOR

> 用户确认补丁、发版或 Checkpoint 5 确认动基线时加载。

**MUST 读**：[`product-version.md`](../product-version.md)。

执行见 [升产品版本（MANDATORY）](../product-version.md#升产品版本mandatory)。先判断这次是「更新当前基线的 revision」还是「立新基线」：

- 更新当前基线（revision 同步、澄清纠错；**首份基线**另可增删成员）：`check_docs.py --bump-product --patch --note '…'`
- 首份之后的成员变化，或冻结独立参考点（对外发版、里程碑、评估基线）：`--bump-product --minor`
- 主版本：`--bump-product --major`

**首份基线**（`prev` 为空，通常是 `v1.0`）可在尚无后继时反复增删成员；首份之后，成员集合在创建时固定，成员进出 **MUST** 立新基线。PATCH 不冻结基线、不留历史内容。README / 文件名两段 `vX.Y`；tip 为 `full_version`（`vX.Y.Z`），是当前工作 tip 而非不可变快照标识。MINOR/MAJOR 立新基线后，旧文件即成历史基线、只读。不解冻、不改修订号、不改本文引用、不写 git/svn/构建号。定稿 **MUST NOT** 写基线或手填谱系。
