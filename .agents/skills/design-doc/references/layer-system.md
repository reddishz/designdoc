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

**业务与领域用语**：当多文档、多角色需对齐同一套名词时，可采用**项目级词汇表**（路径自定，常见为 `ued/` 下单独文件），并在 `ued/README.md` 中登记；与细项编码的分工见 [glossary-conventions.md](glossary-conventions.md)。

## 目录结构规范

### 单层模式（默认）

```
ued/
├── README.md                # 文档索引 + 全局编码索引
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

### 多层模式（含子系统）

当项目包含可独立运行的子系统时，L2 起可按子系统拆分。顶层保留公共/跨子系统内容，子系统目录只负责自身细化部分。

```
ued/
├── README.md                # 全局索引（含全局编码索引）
├── L0-vision/               # 全局共享
├── L1-stakeholder/          # 全局共享
├── L2-requirements/         # 公共/跨子系统需求
├── L3-architecture/         # 系统级架构
│   └── adr/                 # 全局架构决策
├── L4-system-design/        # 公共设计（如有）
├── L5-detail-design/        # 公共设计（如有）
├── L6-verification/         # 公共验证策略
├── references/              # 外部参考资料（全局共享）
├── assets/
│
├── {subsystem-name}/        # 子系统目录
│   ├── README.md            # 子系统索引（含子系统编码索引）
│   ├── L2-requirements/
│   ├── L3-architecture/
│   │   └── adr/
│   ├── L4-system-design/
│   ├── L5-detail-design/
│   └── L6-verification/
│
└── {subsystem-name}/        # 另一个子系统（按需裁剪层级）
    ├── README.md
    ├── L2-requirements/
    └── L4-system-design/
```

**裁剪原则**：层级目录按需创建，不必每级都有。空目录不必预建。

## 命名规则

- **层级目录**：`L{N}-{英文短名}/`，如 `L3-architecture/`
- **子系统目录**：小写英文，短横线分隔，如 `user-service/`
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
