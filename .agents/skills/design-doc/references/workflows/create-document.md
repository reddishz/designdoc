# 创建新文档

> 新建 `ued/` 下整篇文档时加载。

**MUST 另读**：[`assets/templates/index.md`](../../assets/templates/index.md)、[`layer-system.md`](../layer-system.md)。增量能力先完成 [change-feature.md](change-feature.md)。

1. 确认 `ued/` 目录结构；增量则先向上核对。
2. 从 `assets/templates/` 取模板；**默认按需裁剪，禁止无指令全量生成 L0–L6**。
3. 按模板生成，**MUST NOT** 含具体实现代码。
4. **Checkpoint 1**：暂停，确认大纲与核心细项（增量时含上层是否同步）。
5. 确认后按 [allocate-and-lock.md](allocate-and-lock.md) 分配编码。
6. 立即更新当前作用域 `README.md` 与文档末尾清单（状态默认 `初稿`）。单应用改 `ued/README.md`；多应用改 `ued/{app}/README.md`。
7. 自检：与上层无冲突；标题适度宽泛；类型码只在定义层写定义块——详细设计里的「系统应当」先落到 L2 的 FR/NFR；按 [review-guidelines.md](../review-guidelines.md) 过锁定与措辞。
