---
name: design-doc
description: 规范项目产品设计文档（ued/目录）的层级体系、目录结构、格式和模板。当用户需要创建或审查 L0-L6 层级的设计文档（愿景、需求、架构、系统设计、详细设计、验证策略等）时使用此 skill。不适用于代码实现、部署运维(docs/)或用户手册类文档。
license: Apache-2.0
metadata:
  version: "2.0"
  spec-compliance: 遵循 Agent Skills 开放标准
compatibility: 需能访问 ued/ 目录，可选 git config 用户名获取
---

# 产品设计文档规范（UED）

## 当前用户

- 作者：!`cat ued/.doc-config.json 2>/dev/null | grep -o '"author"[[:space:]]*:[[:space:]]*"[^"]*"' | head -1 | sed 's/.*"author"[[:space:]]*:[[:space:]]*"//' | sed 's/"$//' | grep -v '^$' || git config user.name 2>/dev/null || echo '产品架构组'`
- 项目编码：!`cat ued/.doc-config.json 2>/dev/null | grep -o '"project_code"[[:space:]]*:[[:space:]]*"[^"]*"' | head -1 | sed 's/.*"project_code"[[:space:]]*:[[:space:]]*"//' | sed 's/"$//' | grep -v '^$' || echo $DESIGN_DOC_PROJECT_CODE 2>/dev/null || echo 'DEFAULT'`

## 用户配置

创建或编辑设计文档时，"作者"和"项目编码"字段使用上方注入的值。

**获取优先级**（高到低）：

**作者字段**：
1. 项目配置文件 `ued/.doc-config.json` 中的 `author` 字段
2. 当前 `git config user.name`
3. 默认值：`产品架构组`

**项目编码字段**：
1. 项目配置文件 `ued/.doc-config.json` 中的 `project_code` 字段
2. 环境变量 `DESIGN_DOC_PROJECT_CODE`
3. 默认值：`DEFAULT`

**配置文件格式**（`ued/.doc-config.json`）：

```json
{
  "author": "张三",
  "project_code": "CRM"
}
```

若配置文件不存在，首次使用本 skill 创建文档时，应询问用户称呼和项目编码并创建该文件。

**项目编码规则**：
- 长度：2-4位大写字母
- 只能包含字母 A-Z
- 建议体现项目或产品线特征
- 企业内统一分配管理

**有效示例**：`CRM`、`ERP`、`CMS`、`COM`、`HRS`

## 基本原则

**真值源优先级**：当本文件与 `references/` 下的专项文件发生冲突时，**以 `references/` 下的专项文件为准**。专项文件提供更详细和最新的规范定义。

**单一事实来源（SSoT）**：全系统遵循 SSoT 约定：
- 所有文档拥有唯一编号
- 所有明确细项（需求、规则、约束、假定、流程等）拥有独立的全局唯一编码
- 编码一经分配不可删除，废弃的编码标注为"已废弃"并保留，后续编码继续递增
- 互相引用以唯一编码为准，必要时附带标题
- 下层可引用上层，上层无需引用下层（默认上层全覆盖下层）
- 任何层级均可引用 REF（外部参考资料）编码
- 审核时逐层检查下层是否违背上层

**核心约束**：`ued/` 下所有文档**不得包含代码和具体实现**。只允许设计性内容：规则、约束、逻辑、流程、概念、假定、标准、策略等。

## 范围界定

| 目录 | 范围 | 说明 |
|------|------|------|
| `ued/` | 产品规划与研发设计（L0-L6） | 本 skill 管辖 |
| `docs/` | 部署运维、用户手册等 | 不在本 skill 范围内 |

## 快速使用

### 创建设计文档

1. 确定所属层级（L0-L6）和归属（全局/子系统）
2. 分配文档编码（在对应层级中取下一个可用编号）
3. 从 [模板库](assets/templates/index.md) 选取对应模板
4. 按目录规范放置到正确位置
5. 为文档中的每个明确细项分配全局唯一编码
6. 填充内容，确保元信息、细项编码清单和变更记录完整
7. 更新 `ued/README.md` 全局编码索引

### 审核设计文档

使用 [审核指南](references/review-guidelines.md) 进行全面检查，确保合规性和一致性。

## 详细规范

- [编码体系](references/coding-system.md) - 文档和细项编码规则
- [层级体系](references/layer-system.md) - L0-L6 层级定义和目录结构
- [状态定义](references/status-definitions.md) - 标准状态值集合和流转规则
- [模板库](assets/templates/index.md) - 各层级文档模板索引
- [审核指南](references/review-guidelines.md) - 文档审核流程和检查项

## 多工具兼容

本 skill 遵循 [Agent Skills 开放标准](https://agentskills.io/specification)，存放于通用路径 `.agents/skills/design-doc/`。

支持该标准的工具（Cursor、Windsurf、Claude、GitHub Copilot、VS Code 等）可自动发现和加载。不支持通用标准的工具需通过翻译脚本单独适配。

若宿主项目存在根目录 README.md，可补充更多使用说明。
