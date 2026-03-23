# AGENTS.md 编写规范参考手册

## 概述

AGENTS.md 是一个轻量级的、跨平台的 AI 编码代理规则标准。它为 AI 代理提供项目特定的上下文、编码标准和行为约束，被称为"机器人的 README"。

**核心价值**：

| 特性 | 说明 |
|------|------|
| **跨平台兼容** | 被多个 AI 编码工具支持（Aider、Codex、Gemini、Cursor 等） |
| **版本控制友好** | 纯文本文件，易于提交到代码仓库 |
| **简洁高效** | 基于 Markdown，无复杂格式要求 |
| **渐进式支持** | 从简单到复杂的规则都可以表达 |

---

## Agent Rules Community Standard v1.0

### 规范来源

- **官方仓库**：https://github.com/agent-rules/agent-rules
- **官方网站**：https://agent-rules.org/
- **规范文档**：https://agents.md/

### 核心要求

根据 RFC 2119 规范，关键词"**MUST**"、"**MUST NOT**"、"**REQUIRED**"、"**SHALL**"、"**SHALL NOT**"、"**SHOULD**"、"**SHOULD NOT**"、"**RECOMMENDED**"、"**MAY**"、"**OPTIONAL**" 的含义：

#### 文件名和位置

**MUST**：实现 Agent Rules 的代理必须检查项目根目录是否存在 `AGENTS.md` 文件。

**SHOULD**：如果存在，其内容应该包含在代理的上下文范围内（例如，前置或附加到提示词或系统指令）。

#### 内容格式

**MUST**：文件必须解析为自然语言指令，使用 Markdown 或纯文本格式。

**MUST**：必须用于向 AI 编码代理提供指导（例如，规则、偏好或工作流）。

**MUST NOT**：代理不能要求超出将文件读取为文本的额外结构、元数据或解析。

#### 兼容性

**MAY**：代理可以将其与任何自定义或现有配置文件一起处理，如果缺少则回退到默认值。

**MAY**：代理也可以检查并包含当前工作目录中的任何 `AGENTS.md` 文件，如果存在项目根目录的 `AGENTS.md`，则将其内容合并到上下文范围中。

---

## 文件位置规范

### 推荐位置

```bash
# 项目级（推荐，随仓库提交）
/project-root/AGENTS.md

# 用户级（全局，不提交）
~/.codex/AGENTS.md      # Codex CLI
~/.claude/CLAUDE.md     # Claude Code
~/.gemini/GEMINI.md     # Gemini CLI
```

### 目录级规则

部分工具支持目录级规则（嵌套规则）：

```bash
/project-root/
├── AGENTS.md              # 全局项目规则
├── frontend/
│   ├── AGENTS.md          # 前端特定规则
│   └── src/
│       └── components/
│           └── AGENTS.md  # 组件级规则
└── backend/
    └── AGENTS.md          # 后端特定规则
```

**加载顺序**（从全局到本地）：
1. 用户级全局规则
2. 项目根目录规则
3. 子目录规则（更具体的覆盖上层的）

---

## AGENTS.md 基本格式

### 最小示例

```markdown
# 项目规则

## 编码风格

- 使用 TypeScript 编写所有代码
- 遵循 Airbnb JavaScript 风格指南
- 文件名使用 kebab-case

## 提交规范

- 遵循 Conventional Commits
- 格式：`<type>(<scope>): <description>`
```

### 完整示例

```markdown
# AGENTS.md

## 项目概述

本项目是一个基于 Next.js 14 和 TypeScript 5.0 的 SaaS 应用，使用 Tailwind CSS 进行样式设计。

## 角色定义

你是一个专注于 React 18 和现代前端技术栈的高级前端工程师。你熟悉：
- Next.js 14 App Router
- TypeScript 5.0 strict mode
- Tailwind CSS v3
- React Server Components

## 编码标准

### 命名约定

- **组件**：PascalCase（`UserProfile.tsx`）
- **文件**：kebab-case（`user-profile.tsx`）
- **常量**：UPPER_SNAKE_CASE（`API_BASE_URL`）
- **函数**：camelCase（`getUserData`）

### 代码风格

- 使用 2 空格缩进
- 使用单引号
- 每行最大长度 80 字符
- 函数必须有明确的返回类型

### TypeScript 规则

- 严格模式：`"strict": true`
- 禁止使用 `any` 类型（必须用注释说明理由）
- 所有公共 API 必须有 JSDoc 文档
- 接口使用 `interface`，类型别名使用 `type`

## 操作指令

### 构建命令

```bash
# 开发服务器
npm run dev

# 生产构建
npm run build

# 类型检查
npm run type-check

# 代码检查
npm run lint

# 运行测试
npm test
```

### 依赖管理

- 使用 `npm` 作为包管理器
- 新依赖必须添加到 `package.json`
- 定期运行 `npm audit` 检查安全漏洞

## 安全规则

- **绝对禁止**在代码中硬编码密钥
- 所有敏感信息必须从环境变量读取
- API 密钥存储在 `.env.local` 文件中（已添加到 `.gitignore`）
- 用户输入必须进行验证和清理

## 测试要求

- 所有新代码必须有单元测试
- 测试覆盖率不得低于 80%
- 使用 Jest 作为测试框架
- PR 必须通过所有 CI 检查

## Git 工作流

### 分支策略

- `main` - 生产环境（受保护）
- `develop` - 开发环境
- `feature/<name>` - 功能分支
- `bugfix/<name>` - 修复分支

### 提交规范

遵循 Conventional Commits：

- `feat:` 新功能
- `fix:` 修复 bug
- `docs:` 文档更新
- `style:` 代码格式（不影响功能）
- `refactor:` 重构
- `test:` 测试相关
- `chore:` 构建/工具链相关

**示例**：
```
feat(auth): add OAuth2 login support

fix(api): resolve timeout issue on user creation

docs(readme): update installation instructions
```

## 禁止事项

- ❌ 使用 `any` 类型（无正当理由）
- ❌ 提交 `.env` 文件
- ❌ 硬编码配置值
- ❌ 使用已弃用的 API
- ❌ 忽略 TypeScript 错误

## 优先级

1. **安全性** > 2. **可维护性** > 3. **性能** > 4. **开发速度**

## 相关资源

- [项目 README](README.md)
- [API 文档](docs/api.md)
- [贡献指南](CONTRIBUTING.md)
```

---

## 编写最佳实践

### 1. 结构组织

**推荐使用以下结构**：

```markdown
# AGENTS.md

## 项目概述
## 角色定义
## 编码标准
### 命名约定
### 代码风格
### TypeScript 规则
## 操作指令
## 安全规则
## 测试要求
## Git 工作流
## 禁止事项
## 优先级
## 相关资源
```

### 2. 内容原则

#### 使用简洁的要点列表

✅ **好的做法**：
```markdown
## 编码标准

- 使用 TypeScript strict mode
- 所有函数必须有明确的返回类型
- 禁止使用 `any` 类型
```

❌ **避免的做法**：
```markdown
## 编码标准

在这个项目中，我们应该确保使用 TypeScript 的严格模式。另外，我们需要确保每个函数都有明确的返回类型，并且不应该使用 any 类型，因为这会导致类型安全问题...
```

#### 使用明确的指令性语言

✅ **好的做法**：
```markdown
- 所有组件必须使用 TypeScript
- 遵循 Airbnb 风格指南
```

❌ **避免的做法**：
```markdown
- 建议使用 TypeScript
- 可以参考 Airbnb 风格指南
```

#### 使用 RFC 2119 关键词

```markdown
## 必须遵守的规则

- 所有函数 MUST 有明确的返回类型
- 绝不能 MUST NOT 在代码中硬编码密钥
- SHOULD 遵循 Conventional Commits
- MAY 使用 Tailwind CSS 作为样式解决方案
```

### 3. 避免冗余信息

❌ **不要包含**：
- 徽章（badges）
- 赞助商信息
- 通用介绍（README.md 已包含）
- AI 不需要的技术细节（如详细的安装步骤）

✅ **专注于**：
- 项目特定的约束
- 编码标准
- 安全规则
- 工作流程

### 4. 上下文发现协议

建议在 AGENTS.md 中包含上下文确认协议：

```markdown
## 上下文确认

在开始工作之前，你必须：
1. 识别当前的技术栈和构建工具
2. 确认检测到的环境
3. 在继续之前明确要求用户确认
```

### 5. 自我纠正机制

```markdown
## 自我纠正

如果构建失败，你必须：
1. 检查依赖项是否正确安装
2. 验证 TypeScript 类型错误
3. 运行 `npm run lint` 检查代码风格
4. 向用户报告具体错误和建议的修复方法
```

---

## 高级用法

### 1. 引用其他文件

```markdown
## 详细的编码标准

完整的编码标准请参考：
- [编码规范文档](docs/coding-standards.md)
- [API 约定](docs/api-conventions.md)
- [数据库模式](docs/database-schema.md)
```

### 2. 条件规则

```markdown
## 环境特定规则

### 开发环境
- 使用开发服务器：`npm run dev`
- 启用详细日志
- 使用 Mock 数据

### 生产环境
- 使用生产构建：`npm run build`
- 禁用详细日志
- 使用真实 API
```

### 3. 模块特定规则

```markdown
## 模块规则

### 前端模块
- 使用 React Server Components
- 样式使用 Tailwind CSS
- 状态管理使用 Zustand

### 后端模块
- 使用 Next.js API Routes
- 数据验证使用 Zod
- ORM 使用 Prisma
```

### 4. 与 Skills 协作

```markdown
## 技能引用

当执行特定任务时，应该加载相应的技能：

- **部署任务**：加载 `deploy-to-production` 技能
- **代码审查**：加载 `code-review` 技能
- **测试运行**：加载 `run-tests` 技能
```

---

## 跨平台兼容性

### 各工具的支持情况

| 工具 | 支持状态 | 文件名 | 备注 |
|------|----------|--------|------|
| Aider | ✅ 完全支持 | `AGENTS.md` | 可在 `.aider.conf.yml` 中配置 |
| AMP | ✅ 原生支持 | `AGENTS.md` | 默认加载 |
| GitHub Copilot | ✅ 后备支持 | `AGENTS.md` | 无 Copilot instructions 时使用 |
| Google Gemini | ✅ 完全支持 | `AGENTS.md` | 可在配置中自定义文件名 |
| Kilo Code | ✅ 完全支持 | `AGENTS.md` | 继承自 Roo Code |
| OpenAI Codex | ✅ 完全支持 | `AGENTS.md` | 支持项目根和当前目录 |
| OpenCode | ✅ 完全支持 | `AGENTS.md` | 默认加载 |
| Phoenix | ✅ 完全支持 | `AGENTS.md` | 默认包含 |
| Roo Code | ✅ 完全支持 | `AGENTS.md` | 自动发现和应用 |
| Zed | ✅ 完全支持 | `AGENTS.md` | 兼容支持 |

### 创建符号链接

为了让多个工具都能读取同一个规则文件：

**Linux/macOS**：
```bash
ln -s AGENTS.md CLAUDE.md
ln -s AGENTS.md GEMINI.md
```

**Windows**：
```cmd
mklink CLAUDE.md AGENTS.md
mklink GEMINI.md AGENTS.md
```

---

## AGENTS.md vs Skills

### 本质区别

| 维度 | AGENTS.md | Skills |
|------|-----------|--------|
| **核心隐喻** | 员工手册 | 工具箱 |
| **交互模式** | 预加载（始终生效） | 按需加载（渐进式披露） |
| **上下文成本** | 高（占用初始 context） | 低（只在需要时加载） |
| **物理结构** | 静态纯文本（Markdown） | 动态文件夹（MD + 代码） |
| **执行能力** | 无执行能力 | 可执行脚本 |
| **复杂度** | 简单自然语言 | 可包含脚本、模板、资源 |
| **适用场景** | 项目规范、编码标准、架构约束 | 任务特定工作流、数据处理、API 交互 |

### 使用决策树

```
开始
  │
  ├─ 是否需要强制执行的规则？
  │   ├─ 是 → 使用 AGENTS.md
  │   └─ 否 → 继续判断
  │
  ├─ 是否需要脚本或模板？
  │   ├─ 是 → 使用 Skills
  │   └─ 否 → 继续判断
  │
  ├─ 是否是复杂的多步骤流程？
  │   ├─ 是 → 使用 Skills
  │   └─ 否 → 继续判断
  │
  └─ 即使不在想这件事，也希望这个指令应用？
      ├─ 是 → 使用 AGENTS.md
      └─ 否 → 使用 Skills
```

### 具体示例

**应该放在 AGENTS.md**：
- ❌ "绝不能提交 `.env` 文件"
- ❌ "所有函数必须有明确的返回类型"
- ❌ "文件名使用 kebab-case"
- ❌ "测试覆盖率不得低于 80%"

**应该放在 Skills**：
- ✅ "当你更改 UI 组件时，运行这些三个集成测试"
- ✅ "部署到生产环境的分步流程"
- ✅ "代码审查的安全检查清单"
- ✅ "发布笔记的格式和检查清单"

### 组合使用最佳实践

```markdown
## 技能路由规则

当处理特定类型的任务时，加载相应的技能：

- **UI 组件更改**：加载 `ui-component-review` 技能
- **API 端点开发**：加载 `api-development` 技能
- **部署操作**：加载 `deploy-to-production` 技能
- **生产错误调试**：加载 `incident-triage` 技能
```

这种模式保持规则简洁，同时让 Agent 具有适应性。

---

## 常见模式

### 1. 单一职责原则

```markdown
## 命名约定

### 文件命名
- 组件：PascalCase
- 工具函数：camelCase
- 常量：UPPER_SNAKE_CASE

### 目录结构
```
src/
  components/    # React 组件
  lib/          # 工具函数
  types/        # TypeScript 类型
  api/          # API 调用
```
```

### 2. 约束优先原则

```markdown
## 安全约束（最高优先级）

1. 绝不在代码中硬编码密钥
2. 所有 API 调用必须使用 HTTPS
3. 用户输入必须验证和清理
4. 敏感操作必须记录审计日志

## 性能约束（次要优先级）

1. 组件必须进行代码分割
2. 图片必须优化和懒加载
3. 避免不必要的重新渲染
```

### 3. 渐进式披露规则

```markdown
## 基础规则

所有代码必须：
- 使用 TypeScript
- 通过 ESLint 检查
- 有相应的测试

## 高级规则（按需）

对于以下场景，参考相应文档：
- 复杂状态管理：见 [状态管理指南](docs/state-management.md)
- 性能优化：见 [性能优化文档](docs/performance.md)
- 安全最佳实践：见 [安全指南](docs/security.md)
```

---

## 错误示例 vs 正确示例

### ❌ 错误示例 1：过于冗长

```markdown
# AGENTS.md

欢迎使用我们的项目！这是一个非常棒的 SaaS 应用，使用了很多现代技术。我们希望你能够帮助我们编写高质量的代码。在这个项目中，我们使用 TypeScript，因为它提供了很好的类型安全性。我们建议你也使用它...

（冗长的介绍，AI 不需要）
```

### ✅ 正确示例 1：简洁明了

```markdown
# AGENTS.md

## 技术栈

- Next.js 14 App Router
- TypeScript 5.0 strict mode
- Tailwind CSS v3

## 强制要求

- 所有代码必须使用 TypeScript
- 禁止使用 `any` 类型
- 必须通过 ESLint 检查
```

### ❌ 错误示例 2：模糊不清

```markdown
## 编码标准

- 尽量使用 TypeScript
- 可以参考 Airbnb 风格指南
- 测试覆盖率最好高一些
```

### ✅ 正确示例 2：明确指令

```markdown
## 编码标准

- 所有代码 MUST 使用 TypeScript strict mode
- 遵循 Airbnb JavaScript 风格指南
- 测试覆盖率不得低于 80%
```

### ❌ 错误示例 3：混合职责

```markdown
## 部署流程

1. 运行 `npm run build`
2. 运行 `npm run deploy`
3. 检查生产环境
4. 如果失败，回滚...
（这是多步骤流程，应该放在 Skills 中）
```

### ✅ 正确示例 3：路由到 Skills

```markdown
## 部署要求

- 部署前必须通过所有测试
- 必须使用 `deploy-to-production` 技能
- 必须有回滚计划
```

---

## 模板和示例

### 简单项目模板

```markdown
# AGENTS.md

## 项目概述

[简短描述项目和技术栈]

## 编码标准

- [列出编码标准]

## 操作指令

```bash
# 构建
npm run build

# 测试
npm test
```

## Git 规范

- [列出提交规范]
```

### 复杂项目模板

```markdown
# AGENTS.md

## 项目概述

[详细描述项目、技术栈、架构]

## 角色定义

你是一个 [角色名称]，熟悉：
- [技术栈 1]
- [技术栈 2]
- [技术栈 3]

## 编码标准

### 命名约定
[详细命名规则]

### 代码风格
[详细风格指南]

### TypeScript 规则
[TypeScript 特定规则]

## 操作指令

### 开发
[开发命令]

### 构建
[构建命令]

### 测试
[测试命令]

### 部署
[部署要求]

## 安全规则

[安全约束和最佳实践]

## 测试要求

[测试覆盖率、框架要求]

## Git 工作流

### 分支策略
[分支命名规则]

### 提交规范
[Conventional Commits 规范]

## 优先级

[优先级排序]

## 技能路由

[何时使用哪个技能]

## 禁止事项

[明确的禁止列表]

## 相关资源

[链接到其他文档]
```

---

## 维护和更新

### 版本控制

- 将 `AGENTS.md` 提交到代码仓库
- 记录重大变更
- 使用 Git 历史追踪规则演变

### 团队协作

```markdown
## 规则变更

所有规则变更必须：
1. 在团队会议上讨论
2. 更新此文档
3. 通知所有开发者
4. 更新相关 Skills（如果有）
```

### 定期审查

```markdown
## 审查周期

- 每季度审查一次规则的有效性
- 根据项目发展更新规则
- 移除过时的约束
- 添加新的最佳实践
```

---

## 工具和资源

### 验证工具

虽然 AGENTS.md 没有严格的验证工具，但可以：

1. **使用 Markdown linter** 检查格式
2. **使用文本分析工具** 检查清晰度
3. **人工审查** 确保规则的合理性

### 参考资源

- **Agent Rules 官方规范**：https://agent-rules.org/
- **AGENTS.md 规范**：https://agents.md/
- **Agent Skills 标准**：https://agentskills.io/
- **Conventional Commits**：https://www.conventionalcommits.org/

### 示例仓库

- [Aider conventions](https://github.com/paul-gauthier/aider/blob/main/CONVENTIONS.md)
- [Cline rules](https://github.com/modular-brainiac/cline-rules)
- [GitHub Copilot instructions](https://github.com/github/awesome-copilot)

---

## 常见问题

### Q1: AGENTS.md 和 README.md 有什么区别？

**A**: README.md 是给人类看的，包含徽章、赞助商、详细安装步骤等。AGENTS.md 是给 AI 看的，只包含 AI 需要知道的规则和约束。

### Q2: 应该写多长的 AGENTS.md？

**A**: 保持简洁，建议 200-500 行。详细内容应该引用其他文档或放在 Skills 中。

### Q3: 可以包含代码示例吗？

**A**: 可以，但要保持简洁。代码示例应该是说明性的，不是教程。

### Q4: 如何处理冲突的规则？

**A**: 使用明确的优先级系统。例如：安全 > 可维护性 > 性能 > 开发速度。

### Q5: 如何让团队遵守 AGENTS.md？

**A**:
1. 将规则集成到 CI/CD 流程
2. 使用 linter 和 formatter 自动执行
3. 定期审查代码
4. 在 PR 中强制检查

### Q6: AGENTS.md 可以动态生成吗？

**A**: 可以，但建议保持静态。动态生成的规则可能导致不一致。

---

## 总结

### 核心原则

1. **简洁优先**：保持文件简短，避免冗余
2. **明确指令**：使用清晰的指令性语言
3. **结构化**：使用一致的章节结构
4. **可维护**：定期审查和更新
5. **跨平台兼容**：遵循标准规范

### 最佳实践清单

- [ ] 文件位于项目根目录
- [ ] 使用清晰的 Markdown 格式
- [ ] 使用要点列表而非段落
- [ ] 使用 RFC 2119 关键词（MUST/SHOULD/MAY）
- [ ] 避免冗余信息（徽章、赞助商等）
- [ ] 包含项目特定的约束
- [ ] 包含编码标准和风格指南
- [ ] 包含安全规则
- [ ] 包含操作指令
- [ ] 包含 Git 工作流
- [ ] 与 Skills 协作（路由规则）
- [ ] 定期审查和更新

### 与其他文档的关系

```
项目文档层级：

1. README.md           - 项目介绍（面向人类）
2. AGENTS.md           - 项目规则（面向 AI）
3. CONTRIBUTING.md     - 贡献指南（面向人类）
4. docs/               - 详细文档（面向人类和 AI）
5. .agents/skills/     - 技能包（面向 AI）
```

---

## 附录：完整示例仓库

### 小型项目 AGENTS.md

```markdown
# AGENTS.md

## 项目概述

个人博客，使用 Next.js 14 和 TypeScript。

## 编码标准

- 使用 TypeScript strict mode
- 遵循 Prettier 配置
- 组件使用 PascalCase

## 操作指令

```bash
npm run dev    # 开发服务器
npm run build  # 生产构建
npm test       # 运行测试
```

## Git 规范

- 遵循 Conventional Commits
- PR 必须通过 CI 检查
```

### 大型项目 AGENTS.md

```markdown
# AGENTS.md

## 项目概述

企业级 SaaS 平台，微服务架构，包含前端、后端和多个子服务。

## 角色定义

你是一个全栈工程师，熟悉：
- Next.js 14 App Router（前端）
- NestJS（后端）
- PostgreSQL（数据库）
- Docker（容器化）
- Kubernetes（编排）

## 编码标准

### 命名约定

- **前端组件**：PascalCase
- **API 路由**：kebab-case
- **数据库表**：snake_case
- **环境变量**：UPPER_SNAKE_CASE

### 代码风格

- 前端：ESLint + Prettier
- 后端：ESLint + Prettier
- 统一使用 2 空格缩进

### TypeScript 规则

- 严格模式：`"strict": true`
- 禁止 `any` 类型
- 所有公共 API 必须有 JSDoc

## 操作指令

### 前端开发

```bash
cd frontend
npm run dev        # 开发服务器
npm run build      # 生产构建
npm run type-check # 类型检查
npm run lint       # 代码检查
npm test           # 运行测试
```

### 后端开发

```bash
cd backend
npm run dev        # 开发服务器
npm run build      # 生产构建
npm run type-check # 类型检查
npm run lint       # 代码检查
npm test           # 运行测试
npm run migrate    # 数据库迁移
```

### 部署

```bash
# 使用 deploy-to-production 技能
npm run deploy:staging
npm run deploy:production
```

## 安全规则

### 最高优先级

1. 绝不在代码中硬编码密钥
2. 所有 API 通信必须使用 HTTPS
3. 用户输入必须验证和清理（使用 Zod）
4. 敏感操作必须记录审计日志
5. 定期运行 `npm audit` 检查安全漏洞

### 认证和授权

- 使用 JWT 进行身份验证
- 使用 RBAC 进行访问控制
- 敏感端点必须验证用户权限
- 密码必须使用 bcrypt 哈希

### 数据保护

- 敏感数据必须加密存储
- 个人信息必须匿名化处理
- 遵守 GDPR 和 CCPA 合规要求

## 测试要求

### 单元测试

- 所有业务逻辑必须有单元测试
- 使用 Jest 作为测试框架
- 测试覆盖率不得低于 80%

### 集成测试

- API 端点必须有集成测试
- 数据库操作必须有测试
- 使用 Supertest 进行 API 测试

### E2E 测试

- 关键用户流程必须有 E2E 测试
- 使用 Playwright 进行 E2E 测试
- E2E 测试在 CI 中运行

## Git 工作流

### 分支策略

- `main` - 生产环境（受保护）
- `develop` - 开发环境
- `feature/<ticket-id>-<description>` - 功能分支
- `bugfix/<ticket-id>-<description>` - 修复分支
- `hotfix/<ticket-id>-<description>` - 紧急修复

### 提交规范

遵循 Conventional Commits：

- `feat:` 新功能
- `fix:` 修复 bug
- `docs:` 文档更新
- `style:` 代码格式
- `refactor:` 重构
- `perf:` 性能优化
- `test:` 测试相关
- `chore:` 构建/工具链
- `ci:` CI/CD 相关

**示例**：
```
feat(auth): add OAuth2 login support with Google

fix(api-123): resolve timeout issue on user creation

perf(frontend): optimize image loading with lazy loading

ci(cicd): add automated deployment to staging
```

### PR 要求

- PR 标题必须遵循 Conventional Commits
- PR 描述必须包含：
  - 变更说明
  - 相关 Issue 链接
  - 测试说明
  - 截图（如果是 UI 变更）
- 所有检查必须通过
- 至少一个 Reviewer 批准

## 技能路由

### 前端开发

- **UI 组件开发**：加载 `ui-component-dev` 技能
- **状态管理**：加载 `state-management` 技能
- **性能优化**：加载 `frontend-optimization` 技能

### 后端开发

- **API 开发**：加载 `api-development` 技能
- **数据库操作**：加载 `database-operations` 技能
- **认证实现**：加载 `auth-implementation` 技能

### 部署和运维

- **部署到预发布**：加载 `deploy-to-staging` 技能
- **部署到生产**：加载 `deploy-to-production` 技能
- **错误调查**：加载 `incident-triage` 技能

## 优先级

1. **安全性** > 2. **合规性** > 3. **可维护性** > 4. **性能** > 5. **开发速度**

## 禁止事项

### 绝对禁止

- ❌ 在代码中硬编码密钥
- ❌ 提交 `.env` 文件到仓库
- ❌ 使用 `eval()` 或类似危险函数
- ❌ 绕过类型检查
- ❌ 忽略安全警告

### 不推荐

- ⚠️ 使用 `any` 类型（必须有注释说明理由）
- ⚠️ 直接操作 DOM（使用 React Refs）
- ⚠️ 使用已弃用的 API
- ⚠️ 忽略 TypeScript 错误
- ⚠️ 跳过测试

## 相关资源

- [项目 README](README.md)
- [贡献指南](CONTRIBUTING.md)
- [API 文档](docs/api.md)
- [数据库模式](docs/database-schema.md)
- [部署指南](docs/deployment.md)
- [安全指南](docs/security.md)

## 规则变更

所有规则变更必须：
1. 在团队会议中讨论
2. 更新此文档
3. 通知所有开发者
4. 更新相关 Skills（如果有）
5. 记录变更日志

## 审查周期

- 每季度审查一次规则的有效性
- 根据项目发展更新规则
- 移除过时的约束
- 添加新的最佳实践
```

---

## 结语

AGENTS.md 是连接人类开发者与 AI 代理的桥梁。一个编写良好的 AGENTS.md 可以：

- ✅ 提高 AI 代理的工作质量
- ✅ 减少沟通成本
- ✅ 确保代码一致性
- ✅ 加速开发流程
- ✅ 降低错误率

记住：**简洁、明确、可维护**是编写 AGENTS.md 的三大原则。

开始编写你的 AGENTS.md 吧！
