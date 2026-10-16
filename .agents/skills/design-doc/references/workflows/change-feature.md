# 新增功能需求（增量）

> 仅当用户要加功能/加需求/增强能力，且作用域**已有**分层文档时加载。绿场见 [layer-system.md · 按需启用](../layer-system.md#按需启用原则)。

**MUST 另读**：[`layer-system.md`](../layer-system.md)、[`coding-system.md` · 细项定义层级](../coding-system.md#细项定义层级mandatory)。

**MUST NOT** 因「默认 L2/L4」就只在 L4/L5 落笔。

1. **向上核对（MUST）**：对照 [补齐信号](../layer-system.md#按需启用原则)，判断是否触及 L0 愿景/GOL/MET/范围、L1 STK/SCN、L2 FR/NFR/UC/AC 等。已有对应层则打开相关篇，查可复用或须改正的细项。
2. **先上后下**：缺则先补/改 L0→L1→L2（及必要的 L3），再写 L4/L5。仅当上层已覆盖、本轮纯属契约/算法/模块内细化时，才可只改 L4/L5。
3. **呈现**：在 Checkpoint 1 或 2 用短表列出「本轮拟动的层与编码」及「不需动上层的理由」；批量或核心能力变更时 **MUST** 暂停确认。
4. 其后按 [create-document.md](create-document.md) / [allocate-and-lock.md](allocate-and-lock.md) 落码与索引。
