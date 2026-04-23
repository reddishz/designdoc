# 层级体系详细规范

## 层级定义

| 层级 | 名称 | 目录 | 核心目的 |
|------|------|------|----------|
| L0 | 战略与愿景 | `L0-vision/` | 定义项目"为什么"，商业目标与战略对齐 |
| L1 | 利益相关者需求 | `L1-stakeholder/` | 捕获各方期望、约束和成功标准 |
| L2 | 系统/产品需求 | `L2-requirements/` | 定义系统外部行为，功能与非功能需求 |
| L3 | 概念架构 | `L3-architecture/` | 高级蓝图、关键技术决策、子系统划分 |
| L4 | 逻辑/系统设计 | `L4-system-design/` | 内部结构、模块职责、接口契约、领域模型 |
| L5 | 详细设计 | `L5-detail-design/` | 组件/模块级设计指导，算法逻辑、异常策略 |
| L6 | 验证与确认 | `L6-verification/` | 测试策略、验收标准、质量度量（非代码） |
| REF | 参考与引用 | `references/` | 外部资料来源（文档、链接），供所有层级引用 |

**层级关系**：每一级为下一级提供依据和约束，同时是上一级的细化。非严格瀑布，可迭代渐进。

**按需启用原则（重要）**：
- 层级是能力全集，不是每次交付清单。
- 默认按最小必要集启动，**不要求**从 L0 连续写到 L6。
- 在上游指令未指定层级时，建议先从 L2 或 L4 起步，再按识别到的语义信号向上/向下补齐追溯链。
- 默认先给出分层建议并执行，不把“先反问层级”作为前置步骤。

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
├── L3-architecture/
│   └── adr/                 # 架构决策记录
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
│   │   └── adr/
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
- **MUST** 包含应用注册表，至少列出应用名称、目录、项目编码、状态
- **MUST NOT** 作为某个具体应用的 `project_code` 真值源
- **SHOULD** 仅登记共享文档和跨应用规则，不维护每个应用的细项级全量索引

## 命名规则

- **层级目录**：`L{N}-{英文短名}/`，如 `L3-architecture/`
- **应用目录**：小写英文，短横线分隔，如 `crm/`、`order-center/`
- **文件名格式**：`L{N}-{三位编号}-{描述}.md`
- **ADR 文件名**：`ADR-{三位编号}-{描述}.md`
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
