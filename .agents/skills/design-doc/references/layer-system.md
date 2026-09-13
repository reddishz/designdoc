# 层级体系详细规范

## 层级定义

| 层级 | 名称 | 目录 | 核心问题 | 写什么 |
|------|------|------|----------|--------|
| L0 | 战略与愿景 | `L0-vision/` | 为什么做 | 愿景、市场、GOL、MET、范围边界；路线图另档 |
| L1 | 利益相关者需求 | `L1-stakeholder/` | 谁需要什么 | STK、SCN、高阶约束；规划总览另档。业务目标仍用 L0 GOL，不在本层重写 |
| L2 | 系统/产品需求 | `L2-requirements/` | 必须满足什么 | FR、NFR、UC、RUL、AC、CON/ASM。写对外黑盒约束，不写系统如何组织或如何实现 |
| L3 | 概念架构 | `L3-architecture/` | 准备用怎样的系统组织来满足 | PRN、CMP、宏观决策（ADR）。是选定的解，不是特性清单 |
| L4 | 逻辑/系统设计 | `L4-system-design/` | 这个组织如何落成契约与结构 | IF、ACT、DOM、模块协作。MUST NOT 在本层定义 FR |
| L5 | 详细设计 | `L5-detail-design/` | 局部机制如何算、如何转、如何配 | ALG、FLW、CON；组件引用 L3 CMP。MUST NOT 定义 FR/NFR/AC/UC |
| L6 | 验证与确认 | `L6-verification/` | 如何证明满足要求 | 测试策略、TC、追溯矩阵（非代码） |
| REF | 参考与引用 | `references/` | （横切） | 外部资料来源（文档、链接），供所有层级引用 |
| ADR | 架构决策记录 | `L3-architecture/`（与层级文档平放，无独立目录） | 为什么这样组织 | 宏观架构级决策的一事一档，见 [type-profiles.md · ADR 与 DEC 的定位](type-profiles.md#adr-与-dec-的定位) |

**层级关系**：每一级为下一级提供依据和约束，同时是上一级的细化。非严格瀑布，可迭代渐进。

### 分层问题（对层判据）

选层看它回答哪一句，不要按「有没有流程 / 有没有模块」堆内容：

- **L2 是约束，L3 是选定的解**。L2 写系统必须满足什么（黑盒承诺，不写实现）；L3 写准备用怎样的原则与子系统去满足。产品「准备提供什么能力」仍用 L2 的 FR 表达，用路线图主题或文档内分组编目；由 CMP 的 `满足需求` 回指。**MUST NOT** 另造特性类型码，也 **MUST NOT** 把 L3 改写成特性说明书。
- **定义与引用分离**。类型码的定义层见 [coding-system.md · 细项定义层级](coding-system.md#细项定义层级mandatory)。他层只链接，MUST NOT 因为「这段在讲算法」就把 FR 定义在 L5。L5 出现「系统应当」的对外承诺时，先补 L2 的 FR，本稿用 `ALG` / `CON` / `RUL` 回指。
- **业务流程只保留两层**。用户可见路径 → L2 `UC`；系统/模块内路径 → L4/L5 `FLW`。不要在 L3 再开一套「概念流程」类型。
- **L4 与 L5**。L4 把 L3 的组织落成可对接的契约与结构；L5 写局部算法、状态与配置。组件定义留在 L3，L5 只引用。L5 **MUST NOT** 定义 `FR` / `NFR` / `AC` / `UC`。

**ADR 不占层级、归属 L3**：ADR 是**文档编码**（`ADR-{三位序号}`）而非层级，其序号为全局序号、不含层级，因此 MUST NOT 写进目录路径；ADR 文件直接存放在 `L3-architecture/`，靠文件名前缀区分。**MUST NOT** 单设 `adr/` 子目录。

归属 L3 的依据是内容职责而非方便：ADR 论证的是技术栈选型、子系统划分、数据一致性策略等「怎么组织系统」的问题，这正是 L3 概念架构的职责；L2 表达「系统必须做什么」，不承载架构论证。若某个取舍只是需求级的（如「本轮不做离线模式」），用 `DEC` / `PRN` 细项而非 ADR。作用域尚未建 `L3-architecture/` 时，随首份 ADR 创建该目录（有 ADR 即有 L3 内容）。

### 按需启用原则

- 层级是能力全集，不是每次交付清单。
- 默认按最小必要集启动，**不要求**从 L0 连续写到 L6。
- 在上游指令未指定层级时，建议先从 L2 或 L4 起步，再按识别到的语义信号向上/向下补齐追溯链。
- 默认先给出分层建议并执行，不把“先反问层级”作为前置步骤。
- **补齐信号**：出现愿景、商业目标、成功指标、路线图主题 → L0；出现角色分层、利益相关者诉求、业务场景冲突 → L1；出现明确功能需求、非功能约束、验收口径 → L2；出现原则、子系统划分、宏观技术决策 → L3；出现接口契约、领域对象、动作 → L4；出现算法、配置约束、模块内流程 → L5；出现测试场景、追溯覆盖 → L6。L5 文稿里出现对外「系统应当」而 L2 尚无对应 FR 时，补的是 L2，不是在 L5 定义 FR。未命中则先不建对应层；命中后再补建并建立追溯引用。判据见上文《分层问题》。

**术语**：模板中「概念架构」与目录名 `L3-architecture` 指同一层级（`architecture` 表示架构蓝图，非代码实现）。

**业务与领域用语**：当多文档、多角色需对齐同一套名词时，可采用**项目级词汇表**。单应用模式下登记在 `ued/README.md`；多应用模式下登记在 `ued/{app-name}/README.md`，必要时在顶层 `ued/README.md` 追加跨应用词汇表入口；与细项编码的分工见 [glossary-conventions.md](glossary-conventions.md)。

## 目录结构规范

### 单层模式（默认）

单应用项目直接在 `ued/` 根下维护文档；`ued/README.md` 同时承担项目元信息、文档入口、编码计数器与全局索引。

```
ued/
├── README.md                # 项目元信息 + 文档索引 + 编码计数器 + 全局编码索引
├── L0-vision/
├── L1-stakeholder/
├── L2-requirements/
├── L3-architecture/         # 层级文档与 ADR-*.md 同目录平放
├── L4-system-design/
├── L5-detail-design/
├── L6-verification/
├── references/              # 外部参考资料
└── assets/                  # 图片、附件等资源
```

### 多应用模式

当同一个 `ued/` 下需要维护多个独立应用时，**MUST** 将应用拆分到 `ued/{app-name}/` 子目录。顶层 `ued/README.md` 只承担总入口、应用注册表、公共规则与跨应用导航；每个应用目录的 `README.md` 才是该应用的元信息与编码索引真值源。

```
ued/
├── README.md                # 多应用总入口 + 应用注册表 + 跨应用规则
├── shared/                  # 可选，共享文档域
│   ├── README.md            # 共享文档索引
│   ├── L0-vision/
│   ├── L1-stakeholder/
│   └── references/
├── crm/                     # 应用目录
│   ├── README.md            # 应用元信息 + 应用索引 + 编码计数器 + 应用级全局编码索引
│   ├── L2-requirements/
│   ├── L3-architecture/
│   ├── L4-system-design/
│   ├── L5-detail-design/
│   └── L6-verification/
└── oms/                     # 另一个应用（按需裁剪层级）
    ├── README.md
    ├── L2-requirements/
    └── L4-system-design/
```

**裁剪原则**：层级目录按需创建，不必每级都有。空目录不必预建。

**顶层 README 约束（多应用模式）**：
- **MUST** 包含 `doc_mode = multi-app`
- **MUST** 包含应用注册表，至少列出应用名称、目录、项目编码、状态（取标准四态：`初稿` 已登记未启用 / `正式` 在用 / `废弃` 已停用）
- **MUST NOT** 作为某个具体应用的 `project_code` 真值源
- **SHOULD** 仅登记共享文档和跨应用规则，不维护每个应用的细项级全量索引

## 命名规则

- **层级目录**：`L{N}-{英文短名}/`，如 `L3-architecture/`
- **应用目录**：小写英文，短横线分隔，如 `crm/`、`order-center/`
- **文件名格式**：`L{N}-{三位编号}-{描述}.md`
- **ADR 文件名**：`ADR-{三位编号}-{描述}.md`，存放于 `L3-architecture/`（ADR 归属 L3，见《层级定义》），**MUST NOT** 单设 `adr/` 子目录
- **REF 文件名**：`REF-{三位编号}-{描述}.md`
- **文件名禁止使用中文**，以兼容各类文件系统和版本管理系统。描述部分使用英文或拼音，小写，短横线分隔
- **此规则仅限文件名和目录名**，文档内容（标题、正文、表格、描述等）一律使用中文

示例：
```
L0-001-product-vision.md
L2-003-user-permission-req.md
L3-002-microservice-arch.md
L5-012-payment-flow-design.md
L6-001-integration-test-strategy.md
ADR-005-choose-redis-as-cache.md
REF-001-iso25010-quality-model.md
REF-002-jingpin-fenxi-baogao.md
```
