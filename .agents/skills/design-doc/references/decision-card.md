# 决策卡（首次接入）

> 本卡只回答「先读哪页、什么会阻断」。规则正文与取值仍是唯一表述处，本卡不复述；两者冲突时以规则正文为准并按规范缺陷修正。

## 按任务选择

| 你要做什么 | MUST 先读 | 硬阻断（不满足则停） |
|------------|-----------|----------------------|
| 改功能 / 修缺陷 / 改行为（项目有 `ued/`） | [before-code-change.md](workflows/before-code-change.md) | 设计需改而未先改文档；实现依据不在**当前**产品基线或 revision 落后 |
| 新建 / 改编码、标题、类型码 | [allocate-and-lock.md](workflows/allocate-and-lock.md) + [锁定矩阵](object-model.md#锁定矩阵mandatory) | 删除或复用已分配编码；就地改编码 ID / 类型码 / `正式`·`草案` 标题与正式含义 |
| 废弃 / 受控复活 | [item-deprecation.md](item-deprecation.md) / [doc-deprecation.md](doc-deprecation.md) + [状态定义](status-definitions.md) | 废弃字段不齐；仍有活细项就整份废弃；复活条件未逐条满足或未取得人确认 |
| 定稿 / 发版 / 基线变更 | [lifecycle.md](workflows/lifecycle.md)（Checkpoint 5）与 [baseline-change.md](workflows/baseline-change.md) | 未经人确认的定稿 / `--bump-product`；未跑检查 |
| 审查设计文档 | [review-guidelines.md](review-guidelines.md) | 包内或文档间存在未解消冲突；把冲突留给「优先级表」 |

## 最小命令集

```bash
python3 .agents/skills/design-doc/scripts/check_docs.py -p <ued路径>
python3 .agents/skills/design-doc/scripts/check_docs.py -p <ued路径> --refs {编码}
python3 .agents/skills/design-doc/scripts/check_docs.py --check-templates
```

检查通过 ≠ 语义正确；定稿、废弃、复活与基线动作仍须人确认。

## 读多少

只读 `SKILL.md` + 本卡 + 上表对应的**一个** workflow，再按该 workflow 的「MUST 另读」打开单点规则。其余文件按需，不整包预读。
