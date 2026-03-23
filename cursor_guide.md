# Cursor Skills 参考手册

## 概述

Cursor Skills 是 Cursor 中用于为 AI 智能体扩展专门能力的开放标准。Skills 将特定领域的知识和工作流封装起来，智能体可以调用这些 Skills 来执行特定任务。

**核心特性**：

| 特性 | 说明 |
|------|------|
| **可移植性** | 技能适用于任何支持 Agent Skills 标准的 Agent |
| **版本控制** | 技能以文件形式存储，可以在代码仓库中追踪变更 |
| **可操作性** | 技能可以包含脚本、模板和参考资料，Agent 可处理这些内容 |
| **渐进式** | 技能按需加载资源，使上下文使用更加高效 |

---

## 技能的工作原理

### 自动发现机制

Cursor 启动时，会自动从技能目录中发现并加载技能，并将它们提供给 Agent 使用：

1. **扫描技能目录**：Cursor 扫描所有配置的技能目录
2. **加载元数据**：加载每个 skill 的 `name` 和 `description`
3. **提供给 Agent**：Agent 会看到所有可用技能
4. **智能调用**：Agent 根据当前上下文决定何时调用它们

### 调用方式

**自动调用**：
- Agent 判断某个 skill 相关时，会自动应用该 skill
- 基于技能的 `description` 和当前任务上下文进行匹配

**手动调用**：
- 在 Agent 对话中输入 `/` 并搜索技能名称
- 直接输入 `/skill-name` 来显式调用技能

---

## 技能目录

### 标准发现路径

Cursor 会自动从以下位置加载技能：

| 位置 | 作用域 | 说明 |
|------|--------|------|
| `.agents/skills/` | 项目级 | Agent Skills 标准路径，随仓库提交 |
| `.cursor/skills/` | 项目级 | Cursor 专用路径，随仓库提交 |
| `~/.cursor/skills/` | 用户级（全局） | 全局技能，不提交到仓库 |

### 兼容性路径

为了兼容性，Cursor 还会从以下目录加载技能：

**项目级**：
- `.claude/skills/` - Claude 兼容
- `.codex/skills/` - Codex 兼容

**用户级（全局）**：
- `~/.claude/skills/` - Claude 兼容
- `~/.codex/skills/` - Codex 兼容

### 目录结构规范

**最小结构**：
```
.agents/
└── skills/
  └── my-skill/
    └── SKILL.md
```

**完整结构**（包含可选目录）：
```
.agents/
└── skills/
  └── deploy-app/
    ├── SKILL.md
    ├── scripts/
    │   ├── deploy.sh
    │   └── validate.py
    ├── references/
    │   └── REFERENCE.md
    └── assets/
      └── config-template.json
```

---

## SKILL.md 文件格式

### 基本结构

每个 Skill 都在带有 YAML 前置信息（frontmatter）的 `SKILL.md` 文件中定义：

```markdown
---
name: my-skill
description: 简要描述此技能的功能及使用时机。
---

# 我的技能

为 Agent 提供的详细指令。

## 使用时机

- 在以下情况使用此技能...
- 此技能适用于...

## 指令

- 为 Agent 提供的分步指导
- 特定领域的约定
- 最佳实践和模式
- 如需向用户澄清需求，请使用提问工具
```

### Frontmatter 字段

| 字段 | 必填 | 说明 | 约束 |
|------|------|------|------|
| `name` | Yes | 技能标识符 | 仅限小写字母、数字和连字符。必须与父文件夹名称一致。 |
| `description` | Yes | 描述技能的作用及其使用场景 | 由代理用于判断相关性 |
| `license` | No | 许可证名称或对随附许可证文件的引用 | 建议保持简短 |
| `compatibility` | No | 运行环境要求（系统软件包、网络访问等） | 最多 500 字符 |
| `metadata` | No | 用于额外元数据的任意键值映射 | 任意键值对 |
| `disable-model-invocation` | No | 禁用模型自动调用 | 当为 `true` 时，仅通过 `/skill-name` 显式调用 |

### name 字段规则

- 仅允许：小写字母（a-z）、数字（0-9）、连字符（-）
- 必须与父文件夹名称完全一致
- 不能以连字符开头或结尾
- 不能包含连续连字符

**有效示例**：
```
name: deploy-app
name: code-review
name: test-runner
```

**无效示例**：
```
name: Deploy-App      # 大写字母不允许
name: deploy_app      # 下划线不允许
name: -deploy         # 不能以连字符开头
name: deploy--app     # 连续连字符不允许
```

### description 字段规则

- 清晰描述技能的功能
- 说明使用场景和触发条件
- 包含帮助 Agent 识别相关任务的关键词

**好的示例**：
```yaml
description: 将应用部署到预发布或生产环境。在部署代码时使用，或当用户提及部署、发布或环境时使用。
```

**差的示例**：
```yaml
description: 帮助部署。
```

### disable-model-invocation 字段

默认情况下，当 agent 判断某个 skill 相关时，会自动应用该 skill。将 `disable-model-invocation` 设为 `true`，可以让该 skill 的行为类似传统的斜杠命令（slash command），只有当你在聊天中显式输入 `/skill-name` 时，才会被包含进上下文。

**使用场景**：
- 需要显式触发的操作
- 避免意外调用的敏感操作
- 类似传统命令行工具的行为

**示例**：
```yaml
---
name: reset-database
description: 重置数据库到初始状态（危险操作，必须显式调用）
disable-model-invocation: true
---
```

---

## 完整示例

### 示例 1：部署技能

```markdown
---
name: deploy-app
description: 将应用部署到预发布或生产环境。在部署代码时使用,或当用户提及部署、发布或环境时使用。
---

# Deploy App

使用提供的脚本部署应用。

## 使用方法

运行部署脚本：`scripts/deploy.sh <environment>`

其中 `<environment>` 可以是 `staging` 或 `production`。

## 部署前验证

在部署之前，运行验证脚本：`python scripts/validate.py`

## 检查清单

- [ ] 所有测试通过
- [ ] 环境变量已配置
- [ ] 数据库迁移已准备好
- [ ] 回滚计划已准备
```

### 示例 2：代码审查技能

```markdown
---
name: code-review
description: 审查代码变更，检查安全性、性能和代码质量。在审查 PR 或代码变更时使用。
---

# Code Review

执行全面的代码审查，关注代码质量、安全性和性能。

## 审查流程

1. 阅读 PR 描述和变更范围
2. 检查代码风格（参考 `references/style-guide.md`）
3. 验证安全性（参考 `references/security-checklist.md`）
4. 评估性能影响
5. 检查测试覆盖率

## 重点关注

- SQL 注入风险
- XSS 漏洞
- 认证和授权问题
- 资源泄漏
- 性能瓶颈

## 输出格式

使用 `references/review-template.md` 中的模板提供反馈。
```

### 示例 3：禁用自动调用的技能

```markdown
---
name: delete-all-data
description: 删除所有数据（危险操作，必须显式调用）
disable-model-invocation: true
---

# Delete All Data

⚠️ **警告：此操作不可逆**

此技能将删除所有数据库数据。

## 使用步骤

1. 确认已备份重要数据
2. 运行 `scripts/backup.sh` 创建最后备份
3. 执行 `scripts/delete-all.sh`
4. 验证删除结果

## 恢复

如需恢复，使用 `scripts/restore.sh <backup-file>`
```

---

## 在技能中包含脚本

### scripts/ 目录

技能可以包含 `scripts/` 目录，内含可由代理运行的可执行代码。

**规范**：
- 使用相对于技能根目录的相对路径引用脚本
- 脚本可以是任何语言（Bash、Python、JavaScript 等）
- 脚本应自包含
- 提供有用的错误信息
- 优雅地处理各种边界情况

**示例**：
```markdown
---
name: deploy-app
description: 将应用部署到预发布或生产环境。
---

# Deploy App

使用提供的脚本部署应用。

## 使用方法

运行部署脚本：`scripts/deploy.sh <environment>`

## 部署前验证

运行验证脚本：`python scripts/validate.py`
```

**目录结构**：
```
deploy-app/
├── SKILL.md
└── scripts/
    ├── deploy.sh
    └── validate.py
```

---

## 可选目录

### scripts/

| 用途 | 说明 |
|------|------|
| **功能** | Agents 可以运行的可执行代码 |
| **格式** | Bash、Python、JavaScript 等 |
| **要求** | 自包含、有错误处理 |

### references/

| 用途 | 说明 |
|------|------|
| **功能** | 按需加载的附加文档 |
| **常见文件** | REFERENCE.md、FORMS.md、特定领域文档 |
| **优势** | 保持 SKILL.md 简洁，优化上下文使用 |

**示例**：
```
references/
├── REFERENCE.md       # 技术参考
├── FORMS.md           # 表单模板
├── style-guide.md     # 代码风格指南
└── security-checklist.md  # 安全检查清单
```

### assets/

| 用途 | 说明 |
|------|------|
| **功能** | 模板、图片或数据文件等静态资源 |
| **常见内容** | 配置模板、图片、数据文件 |

**示例**：
```
assets/
├── config-template.json
├── template.html
├── diagram.png
└── data-table.csv
```

---

## 查看技能

### 在 Cursor 中查看已发现的技能

1. 打开 **Cursor Settings**
   - Mac: `Cmd+Shift+J`
   - Windows/Linux: `Ctrl+Shift+J`

2. 前往 **Rules** 标签

3. 技能会显示在 **Agent Decides** 部分中

### 技能显示信息

- 技能名称（`name`）
- 技能描述（`description`）
- 是否禁用自动调用（`disable-model-invocation`）
- 作用域（项目级 / 用户级）

---

## 从 GitHub 安装技能

### 安装步骤

1. 打开 **Cursor Settings → Rules**

2. 在 **Project Rules** 部分，点击 **Add Rule**

3. 选择 **Remote Rule (Github)**

4. 输入 GitHub 仓库的 URL

5. 点击添加

### 仓库要求

GitHub 仓库应包含符合 Agent Skills 标准的技能结构：

```
repo/
└── .agents/
    └── skills/
        └── my-skill/
            └── SKILL.md
```

---

## 迁移规则和命令到技能

### /migrate-to-skills 技能

Cursor 在 2.4 中内置了一个 `/migrate-to-skills` 技能，帮助你将现有的动态规则和斜杠命令转换为技能。

### 迁移内容

该迁移技能会转换：

| 来源类型 | 转换规则 |
|----------|----------|
| **Dynamic rules** | 使用 "Apply Intelligently" 配置的规则（`alwaysApply: false` 或未定义且未定义 `globs` 模式）→ 标准技能 |
| **Slash commands** | 用户级和工作区级命令 → 带有 `disable-model-invocation: true` 的技能 |

### 不迁移的内容

以下内容不会被迁移：

- 具有 `alwaysApply: true` 的规则（有显式触发条件）
- 具有特定 `globs` 模式的规则（行为与技能不同）
- 用户规则（不存储在文件系统中）

### 迁移步骤

1. 在 Agent 聊天中输入 `/migrate-to-skills`

2. Agent 会识别符合条件的规则和命令

3. 确认要迁移的项目

4. 在 `.cursor/skills/` 中查看生成的技能

### 迁移后的调整

迁移后，你可能需要：

1. 检查生成的技能是否正确
2. 优化 `description` 字段以提高匹配准确性
3. 调整技能内容以适应新的格式
4. 测试技能是否正常工作

---

## 最佳实践

### 1. 命名规范

- 使用小写字母、数字和连字符
- 名称应清晰反映功能
- 保持简洁但具有描述性

**好的示例**：
- `deploy-to-production`
- `code-review-security`
- `run-integration-tests`

### 2. 描述优化

- 明确说明技能的功能
- 包含触发关键词
- 说明使用场景

**好的示例**：
```yaml
description: 审查代码变更，检查安全性、性能和代码质量。在审查 PR 或代码变更时使用。
```

### 3. 资源组织

- 保持 SKILL.md 简洁（< 500 行）
- 详细内容放入 references/
- 可执行代码放入 scripts/
- 模板和资源放入 assets/

### 4. 上下文优化

- 利用渐进式加载机制
- 将详细参考材料移到单独文件
- 避免深层的引用链

### 5. 脚本编写

- 脚本应自包含
- 提供清晰的错误信息
- 优雅处理边界情况
- 包含适当的验证

### 6. 版本控制

- 技能随代码仓库提交
- 使用版本号（metadata 字段）
- 记录变更日志

---

## Cursor 特有功能

### 1. disable-model-invocation

这是 Cursor 特有的字段，允许完全禁用自动调用，使技能行为类似传统斜杠命令。

### 2. GitHub 远程安装

Cursor 支持直接从 GitHub 仓库安装技能，便于团队共享和分发。

### 3. 内置迁移工具

Cursor 提供 `/migrate-to-skills` 技能，帮助从旧版规则和命令迁移。

### 4. 兼容性路径

Cursor 自动扫描 Claude 和 Codex 的技能目录，便于从其他平台迁移。

---

## 常见问题

### Q: Cursor 会自动调用我的 skill 吗？

A: 默认情况下会。如果你希望只能手动调用，在 SKILL.md 中设置 `disable-model-invocation: true`。

### Q: 如何在 Cursor 中手动调用技能？

A: 在聊天中输入 `/` 然后搜索技能名称，或直接输入 `/skill-name`。

### Q: .cursor/skills/ 和 .agents/skills/ 有什么区别？

A: `.cursor/skills/` 是 Cursor 专用路径，`.agents/skills/` 是标准路径。两者功能相同，但 `.agents/skills/` 具有更好的跨平台兼容性。

### Q: 如何从 GitHub 安装技能？

A: 打开 Cursor Settings → Rules → Add Rule → Remote Rule (Github) → 输入仓库 URL。

### Q: 迁移后的技能在哪里？

A: 迁移后的技能会保存在 `.cursor/skills/` 目录中。

### Q: 可以使用 Claude 的技能吗？

A: 可以。Cursor 会自动发现 `.claude/skills/` 和 `~/.claude/skills/` 中的技能。

---

## Cursor vs 其他平台的差异

| 特性 | Cursor | Windsurf | Claude |
|------|--------|----------|--------|
| **自动调用** | ✅ 默认启用 | ✅ 默认启用 | ✅ 默认启用 |
| **禁用自动调用** | ✅ `disable-model-invocation` | ❌ | ❌ |
| **GitHub 远程安装** | ✅ 支持 | ❌ | ❌ |
| **内置迁移工具** | ✅ `/migrate-to-skills` | ❌ | ❌ |
| **专用路径** | `.cursor/skills/` | `.windsurf/skills/` | `.claude/skills/` |
| **标准路径** | `.agents/skills/` | `.agents/skills/` | `.agents/skills/` |
| **兼容性扫描** | Claude、Codex | Claude、Codeium | - |

---

## 相关资源

### Cursor 官方文档
- [Agent Skills 官方文档](https://cursor.com/cn/docs/skills)
- [Cursor Settings](https://cursor.com/docs/settings)

### Agent Skills 标准
- [标准规范](./agent_skills_standard.md)
- [官方规范网站](https://agentskills.io/specification)
- [示例 Skills](https://github.com/anthropics/skills)

### 参考工具
- [skills-ref 验证工具](https://github.com/agentskills/agentskills)
- [最佳实践指南](https://agentskills.io/skill-creation/best-practices)

---

## 总结

Cursor Skills 是一个强大且灵活的工具，它：

- ✅ 完全遵循 Agent Skills 开放标准
- ✅ 支持自动和手动调用
- ✅ 提供禁用自动调用的选项
- ✅ 支持 GitHub 远程安装
- ✅ 内置迁移工具
- ✅ 高度兼容其他平台
- ✅ 通过渐进式披露优化上下文使用
- ✅ 易于版本控制和团队协作

通过合理使用 Skills，你可以显著提升 Cursor Agent 在复杂任务中的准确性和效率，同时保持代码的整洁和可维护性。
