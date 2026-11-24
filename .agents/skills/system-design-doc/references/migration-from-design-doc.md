# 迁移指南

本页覆盖三类迁移场景：
1. **从 `system-design-doc` v1.x 迁移到 v2.0**（移除注册表 `角色文档` 列、建立 `ued/architecture/` 系统架构权威、清理外壳 `CMP`）；
2. **从 `design-doc` 9.x 及更早版本的旧多应用结构迁移**；
3. **从单系统升级为系统 + 子系统**。

## 目标结构（v2.0）

```text
ued/
├── README.md                         # 系统入口 + 5 列子系统注册表 + 架构入口 + 发布索引
├── glossary.md                       # 全系统唯一术语表（可选）
├── architecture/                     # 系统层专属目录
│   ├── system-architecture.md        # 系统定义、子系统职责分配、系统交互、SYS-CON、修订记录
│   └── SYS-ADR-001-*.md              # 系统级架构决策（按需）
├── releases/                         # 系统发布清单（含 architecture_rev）
├── crm/
│   ├── README.md                     # design-doc 作用域
│   ├── L2-requirements/
│   ├── L3-architecture/              # CMP 仅表达本子系统内部逻辑组件
│   ├── baselines/
│   └── ...
└── oms/
    └── ...
```

---

## 从 `system-design-doc` v1.x 迁移到 v2.0

v1.x 的核心错位在于注册表强制 `角色文档` 列绑定各子系统 L3 的 `CMP`，导致子系统角色归属倒置、`CMP` 概念混淆、且缺少系统级架构权威。迁移按以下步骤执行：

### 迁移步骤

1. **建立 `ued/architecture/system-architecture.md`**：
   - 使用 [system-architecture.md 模板](../assets/templates/system-architecture.md) 创建；
   - 将原分散在各子系统角色 `CMP` 中的「系统角色」「核心职责」「明确非职责与边界」抽回「子系统职责分配」表（以 `subsystem_key` 为主键）；
   - 将原跨子系统协作说明整理为「系统交互」表（尽量指向提供方 L4 的具体 `IF`/`ACT` 全量编码）；
   - 将原散落在根 README 或被某个普通子系统代管的跨子系统硬约束，统一收口为 `SYS-CON-xxx`（带 `<a id>` 锚点）；
   - 若存在重要跨子系统拆分/通信/安全决策，按需沉淀为 `ued/architecture/SYS-ADR-xxx-*.md`；
   - 人审确认后将 `system-architecture.md` 状态置为 `正式`，在「修订记录」表记入修订号 `1`（`版本类型 = 正式`）。
2. **更新系统根 `ued/README.md`**：
   - 注册表删除 `角色文档` 列，变为标准 5 列（`subsystem_key | 子系统名称 | 目录 | 编码前缀 | 状态`）；
   - 新增「系统架构」入口链接至 `architecture/system-architecture.md`；
   - 移除 README 中重复的子系统职责正文（避免双源漂移）。
3. **排查与清理原角色 `CMP`（MUST 逐项核查）**：
   不要机械删除或直接抹掉旧 `CMP`——先检查它是否被子系统内部的 `IF`、`DOM` 等细项引用：

   | 检查项目 | 处理方式 |
   |----------|----------|
   | 原 `CMP` 中的系统角色 | 抽取到 `system-architecture.md` 职责分配表 |
   | 原 `CMP` 中的职责边界 | 抽取到 `system-architecture.md` 职责分配表 |
   | 原 `CMP` 中的跨子系统交互 | 抽取到 `system-architecture.md` 系统交互表 |
   | 原 `CMP` 是否被子系统内 `IF` / `DOM` 的 `所属组件` 引用 | 逐一核对真实内部组件归属，将 `所属组件` 指向实际的内部逻辑组件 `CMP`（必要时新建真实内部组件 `CMP`） |
   | 原 `CMP` 本身就是真实内部组件 | 去掉其中的系统外壳/跨子系统角色表述，保留其内部组件语义 |
   | 原 `CMP` 只是纯粹的子系统外壳 | 按 `design-doc` 走正常 `废弃`（保留定义与编号，绝不删除、绝不复用） |
   | 已冻结的历史子系统基线 | **保留历史，MUST NOT 追溯修改** |
   | 当前有效子系统基线 | 按 `design-doc` 基线规则处理成员变更（已冻结则立新基线） |

4. **处理历史系统发布清单**：
   - 已发布的 `ued/releases/sys-vX.Y.yaml` **保持不可变，MUST NOT 回改补写 `architecture_rev`**（检查器对历史缺失仅报 WARNING）；
   - 迁移后所有**新建**的系统发布 **MUST** 填写 `architecture_rev`。
5. **校验**：
   ```bash
   python3 .agents/skills/system-design-doc/scripts/check_system.py -p ued
   python3 .agents/skills/design-doc/scripts/check_docs.py -p ued --cross-scope-deps
   # 再对每个子系统跑 design-doc 检查器
   ```

---

## 从旧多应用结构（design-doc 9.x）迁移

### 字段映射

| 旧（多应用） | 新（系统 + 子系统 v2.0） |
|--------------|--------------------------|
| 顶层 README「应用注册表」 | 系统 README 5 列「子系统注册表」 |
| `app_key` | `subsystem_key`（格式改为小写短横线） |
| 应用名称 | 子系统名称 |
| 应用目录 | 目录 |
| 项目编码 | 编码前缀（可空；不得为 `SYS`） |
| 应用状态 `使用中` / `已停用` | `正式` / `废弃`；未启用为 `初稿` |
| 顶层 `产品版本`（若有） | 删除；系统版本改由发布清单表达 |
| 顶层 `baselines/`（若有） | 迁入承担该职责的普通子系统；**MUST NOT** 留在根 |
| `shared/` 共享域 | 改为普通子系统（如 `shared-lib/`），登记并赋键；删除其特殊地位 |
| `doc_mode` 字段 | 删除；结构由注册表判定 |

### 迁移步骤

1. **冻结现状**：确认工作区干净，记录当前各应用 `产品版本` 与基线。
2. **建系统 README**：保留项目元信息，新增「当前结构」「系统架构」入口、「子系统注册表」（5 列）、「系统发布索引」；删除 `产品版本`、`doc_mode`、应用注册表旧列。
3. **登记子系统**：为每个应用目录建一行；键用旧 `app_key` 的合法化形式（小写、短横线）。目录通常不变。
4. **处理共享域**：把 `shared/` 当作普通子系统。
   - 若 `shared/` 有 README、`产品版本`、`baselines/`：直接登记为 `shared-lib`（或更合适的键），删掉「共享」特殊说明。
   - 若 `shared/` 只是零散文档：决定归属——放进某个子系统，或建成独立子系统并补 README / 基线。
   - **MUST NOT** 保留固定 `shared/` 语义；可以继续用该目录名，但它只是普通目录。
5. **顶层产品版本 / 基线**：若存在，迁入对应子系统或按成员归属拆分；根目录删除 `baselines/`。
6. **建立系统架构文档**：创建 `ued/architecture/system-architecture.md`，补全系统定义、各子系统职责分配、系统交互、系统级约束与修订记录并定稿（`修订版本号 = 1`）。
7. **依赖钉住**：在各子系统当前基线写入 `depends_on` / `external_deps`；目标版本按现有基线填写。这是冻结前接线：不改 `items`、不升 `full_version`、不记 `patch_log`，只刷 `updated`；**MUST** 在首个系统发布引用这些基线之前完成。
8. **术语表**：保留 `ued/glossary.md`；删除子系统内的 `glossary.md`，把条目合并到全局表。检查 `定义位置` 是否仍指向正确文档编码。
9. **系统发布**：为当前组合创建首个 `releases/sys-vX.Y.yaml`，填写 `architecture_rev: 1` 并钉住纳入的子系统与外部依赖。
10. **校验**：
    ```bash
    python3 .agents/skills/system-design-doc/scripts/check_system.py -p ued
    python3 .agents/skills/design-doc/scripts/check_docs.py -p ued/crm --glossary ued/glossary.md
    # 对每个子系统重复
    ```

## 不要做的事

- **MUST NOT** 重编号文档或细项；编码一经分配永久占用。
- **MUST NOT** 删除旧应用目录或旧外壳 `CMP` 编码；`废弃` 只改状态。
- **MUST NOT** 修改已冻结的历史子系统基线或已发布的 `releases/sys-vX.Y.yaml`。
- **MUST NOT** 保留 `app_key`、`doc_mode`、应用注册表旧列或 v1.x 的 `角色文档` 列。
- **MUST NOT** 为共享库保留特殊模板、特殊状态或固定目录要求。
- **MUST NOT** 把系统根变成设计作用域来承载 L0–L6。

## 单系统升级为系统

如果原来只有 `ued/` 单作用域，后来需要拆分：

1. 先起草 `ued/architecture/system-architecture.md`，明确拆分后的子系统键、职责分配、边界与交互（必要时记 `SYS-ADR-001`）。
2. 把对应 L0–L6 文档、`baselines/`、README 索引迁入各自子目录；原 README 改为对应子系统 README。
3. 根 README 改为系统 README + 5 列注册表 + 架构入口。
4. 为每个子系统补齐基线扩展字段 `depends_on` / `external_deps`。
5. 建首个系统发布（绑定 `architecture_rev`）。
6. 全程不重编号；跨目录链接改为相对路径，编码不变。
