# Windsurf Skills 参考手册

## 核心概念

Skills 是 Windsurf Cascade 中用于处理复杂、多步骤任务的机制。它允许将参考脚本、模板、检查清单等资源打包成文件夹，供 Cascade 调用和使用。这是让 Cascade 一致执行多步骤工作流的理想方式。

**关键特性：渐进式披露**
- 默认只显示 skill 的 `name` 和 `description` 给模型
- 只有在 Cascade 决定调用 skill 时（或你 `@mention` 它时），才会加载完整的 `SKILL.md` 内容和支持文件
- 这确保了即使定义了多个 skills，上下文窗口也能保持精简

---

## 创建 Skill

### 方式一：使用 UI（推荐）

1. 打开 Cascade 面板
2. 点击面板右上角三点，打开自定义菜单
3. 点击 `Skills` 部分
4. 点击 `+ Workspace` 创建工作区技能（项目专用），或 `+ Global` 创建全局技能
5. 命名 skill（仅允许小写字母、数字和连字符）

### 方式二：手动创建

**工作区 Skill（项目专用）**
1. 创建目录：`.windsurf/skills/<skill-name>/`
2. 添加包含 YAML frontmatter 的 `SKILL.md` 文件

**全局 Skill（所有工作区可用）**
1. 创建目录：`~/.codeium/windsurf/skills/<skill-name>/`
2. 添加包含 YAML frontmatter 的 `SKILL.md` 文件

---

## SKILL.md 文件格式

每个 skill 需要一个 `SKILL.md` 文件，包含描述 skill 元数据的 YAML frontmatter：

### 示例
```markdown
---
name: deploy-to-production
description: Guides the deployment process to production with safety checks
---

## Pre-deployment Checklist
1. Run all tests
2. Check for uncommitted changes
3. Verify environment variables

## Deployment Steps
Follow these steps to deploy safely...

[Reference supporting files in this directory as needed]
```

### 必需的 Frontmatter 字段

| 字段 | 说明 |
|------|------|
| **name** | skill 的唯一标识符（在 UI 中显示，用于 @-mentions） |
| **description** | 简短说明，显示给模型，帮助它决定何时调用该 skill |

有效名称示例：`deploy-to-staging`, `code-review`, `setup-dev-environment`

---

## 添加支持资源

将任何支持文件放在 skill 文件夹中，与 `SKILL.md` 并列。当 skill 被调用时，这些文件对 Cascade 可用：

```
.windsurf/skills/deploy-to-production/
├── SKILL.md
├── deployment-checklist.md
├── rollback-procedure.md
└── config-template.yaml
```

---

## 调用 Skills

### 自动调用
当你的请求匹配 skill 的描述时，Cascade 会自动调用该 skill 并使用其指令和资源完成任务。这是最常见的方式——你只需描述想做的事情，Cascade 会确定哪些 skills 相关。

**关键点**：skill frontmatter 中的 `description` 字段非常重要，它帮助 Cascade 理解何时调用 skill。编写描述时要清晰说明 skill 的功能和使用场景。

### 手动调用
你可以通过在 Cascade 输入中输入 `@skill-name` 来显式激活 skill。当你想确保使用特定 skill，或调用可能不会自动触发的 skill 时，这很有用。

---

## Skill 作用域

| 作用域 | 位置 | 可用性 |
|--------|------|--------|
| Workspace（工作区） | `.windsurf/skills/` | 仅当前工作区。随仓库提交。 |
| Global（全局） | `~/.codeium/windsurf/skills/` | 你机器上的所有工作区。不提交。 |
| System（系统级，企业版） | 操作系统特定（见下表） | 所有工作区，由 IT 部署。只读。 |

**跨 Agent 兼容性**：Windsurf 还会发现 `.agents/skills/` 和 `~/.agents/skills/` 中的 skills。如果启用了 Claude Code 配置读取，也会扫描 `.claude/skills/` 和 `~/.claude/skills/`。

### 系统级 Skills（企业版）

企业组织可以部署在所有工作区可用且用户无法修改的 skills：

| 操作系统 | 路径 |
|----------|------|
| macOS | `/Library/Application Support/Windsurf/skills/` |
| Linux/WSL | `/etc/windsurf/skills/` |
| Windows | `C:\ProgramData\Windsurf\skills\` |

每个 skill 是包含 `SKILL.md` 文件的子目录，就像工作区 skills 一样。

---

## 使用示例

### 部署工作流
创建包含部署脚本、环境配置和回滚程序的 skill：

```
.windsurf/skills/deploy-staging/
├── SKILL.md
├── pre-deploy-checks.sh
├── environment-template.env
└── rollback-steps.md
```

### 代码审查指南
包含风格指南、安全检查清单和审查模板：

```
.windsurf/skills/code-review/
├── SKILL.md
├── style-guide.md
├── security-checklist.md
└── review-template.md
```

### 测试流程
打包测试模板、覆盖率要求和 CI/CD 配置：

```
.windsurf/skills/run-tests/
├── SKILL.md
├── test-template.py
├── coverage-config.json
└── ci-workflow.yaml
```

---

## 最佳实践

1. **编写清晰的描述**：描述帮助 Cascade 决定何时调用 skill。具体说明 skill 的功能和使用场景。
2. **包含相关资源**：模板、检查清单和示例使 skills 更有用。想想哪些文件能帮助某人完成任务。
3. **使用描述性名称**：`deploy-to-staging` 比 `deploy1` 更好。名称应清晰表明 skill 的功能。

---

## Skills vs Rules vs Workflows

这三者都能定制 Cascade，但在**结构**、**调用方式**和**上下文成本**上有所不同：

| 特性 | Skills | Rules | Workflows |
|------|--------|-------|-----------|
| **用途** | 带支持文件的多步骤流程 | 行为指导（"如何表现"） | 可重复任务的提示模板 |
| **结构** | 包含 `SKILL.md` + 任何资源文件的文件夹 | 带有 frontmatter 的单个 `.md` 文件 | 单个 `.md` 文件 |
| **调用方式** | 模型决定（渐进式披露）或 `@mention` | `always_on` / `glob` / `model_decision` / `manual` | **仅手动**，通过 `/slash-command` |
| **在系统提示词中？** | 否——只有名称 + 描述，直到被调用 | 取决于激活模式 | 否——列为可用命令 |
| **最适合** | 需要脚本/模板的部署、代码审查、测试流程 | 编码风格、项目约定、约束 | 你显式触发的一次性运行手册 |

**经验法则**：如果 Cascade 应该自动拾取它**并且**它需要支持文件，使用 Skill。如果是短的行为约束，使用 Rule。如果你想总是自己触发它，使用 Workflow。

---

## 相关文档

如果 Skills 不是你要找的，可以看看这些其他 Cascade 功能：

- **Workflows**：通过斜杠命令调用的可重用 markdown 工作流，自动化重复性任务
- **AGENTS.md**：提供基于文件位置自动应用的目录级指令
- **Memories & Rules**：通过自动生成的记忆和用户定义的规则在对话间持久化上下文
