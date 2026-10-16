# 变更代码前（消费侧，MANDATORY）

> 项目存在 `ued/`，且用户意图是改功能、修缺陷/bug、改产品可观察行为、按需求实现某能力时 **MUST** 加载本流程。  
> **先想清楚设计要不要改，再动代码。****MUST NOT** 先写代码再补设计。

**MUST 另读（按判定）**：需改设计 → [change-feature.md](change-feature.md) / [allocate-and-lock.md](allocate-and-lock.md) / [lifecycle.md](lifecycle.md)；仅实现偏离 → [implement-from-design.md](implement-from-design.md)。

纯笔误、与规格无关的构建/环境失败等 MAY 直接改代码，但 **MUST** 在回复中写明「未触及设计对象」。

1. **定位**：在 `ued/` 与当前产品基线检索相关细项（关键词、编码、`--refs`、模块/接口名）。列出候选编码。
2. **对照判定**（三选一，可组合）：
   - **仅实现偏离**：文档与基线正确，代码不符 → 确认细项在当前基线后改代码（[implement-from-design.md](implement-from-design.md)）。
   - **文档错误或过时**：设计与预期不符 → **先**修订文档（`正式` 须解冻；增量走 [change-feature.md](change-feature.md)），经 Checkpoint 定稿/漂移询问，**然后**才改代码。
   - **文档缺失**：无对应细项 → **先**落码补设计，再定稿/入基线，**然后**才实现。
3. **呈现**：改代码前短表说明「依据哪些编码 / 是否先改文档 / 是否需动基线」；须人审或解冻时 **MUST** 暂停。
4. **禁止**：以「先改代码后面再补文档」「小改不用改设计」跳过本节；**MUST NOT** 把 `初稿`/`草案`/未入基线内容当作已批准规格去改代码（豁免见 [implement-from-design.md](implement-from-design.md)）。
