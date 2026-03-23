# Agent Skills 开放标准规范

## 概述

Agent Skills 是一个轻量级、开放的标准格式，用于扩展 AI 代理的能力。该标准最初由 Anthropic 制定，现已被多个 AI 编码工具（Windsurf、Claude、Cursor、GitHub Copilot 等）采用。

**核心价值**：
- **跨平台兼容**：同一个 skill 可以在不同工具之间复用
- **渐进式加载**：优化上下文使用，只加载必要的信息
- **版本控制友好**：Skills 只是文件，易于编辑、版本控制和共享
- **组织知识捕获**：将公司、团队和用户特定的上下文打包成可重用的技能包

---

## 目录结构规范

一个 skill 是一个包含至少 `SKILL.md` 文件的目录：

```
skill-name/
├── SKILL.md              # 必需：元数据 + 指令
├── scripts/              # 可选：可执行代码
├── references/           # 可选：文档资料
├── assets/               # 可选：模板、资源
└── ...                   # 任何其他文件或目录
```

### 目录说明

**SKILL.md**（必需）
- 包含 YAML frontmatter 和 Markdown 指令
- 定义 skill 的元数据和执行逻辑

**scripts/**（可选）
- 包含代理可运行的可执行代码
- 脚本应该自包含或清楚记录依赖关系
- 包含有帮助的错误消息
- 优雅地处理边缘情况
- 支持的语言取决于代理实现（Python、Bash、JavaScript 等）

**references/**（可选）
- 包含代理可以在需要时阅读的额外文档
- 常见文件：
  - `REFERENCE.md` - 详细技术参考
  - `FORMS.md` - 表单模板或结构化数据格式
  - 特定领域文件（`finance.md`、`legal.md` 等）
- 保持单个参考文件聚焦，以减少上下文使用

**assets/**（可选）
- 包含静态资源
- 类型包括：
  - 模板（文档模板、配置模板）
  - 图片（图表、示例）
  - 数据文件（查找表、模式）

---

## SKILL.md 文件格式

### Frontmatter 字段

| 字段 | 必需 | 约束 |
|------|------|------|
| `name` | 是 | 最多 64 字符。仅允许小写字母、数字和连字符。不能以连字符开头或结尾。 |
| `description` | 是 | 最多 1024 字符。非空。描述 skill 的功能和使用场景。 |
| `license` | 否 | 许可证名称或引用的许可证文件。 |
| `compatibility` | 否 | 最多 500 字符。指示环境要求（目标产品、系统包、网络访问等）。 |
| `metadata` | 否 | 任意键值对映射，用于额外的元数据。 |
| `allowed-tools` | 否 | 空格分隔的预批准工具列表（实验性）。 |

---

### name 字段详细规则

- 长度：1-64 字符
- 仅允许 unicode 小写字母数字（`a-z`）和连字符（`-`）
- 不能以连字符开头或结尾
- 不能包含连续连字符（`--`）
- 必须与父目录名称匹配

**有效示例**：
```yaml
name: pdf-processing
name: data-analysis
name: code-review
name: deploy-to-staging
```

**无效示例**：
```yaml
name: PDF-Processing      # 大写不允许
name: -pdf                # 不能以连字符开头
name: pdf--processing     # 连续连字符不允许
name: pdf_                # 下划线不允许
name: deploy to staging   # 空格不允许
```

---

### description 字段详细规则

- 长度：1-1024 字符
- 应描述 skill 的功能和使用场景
- 应包含帮助代理识别相关任务的关键词
- 非空字符串

**好的示例**：
```yaml
description: Extracts text and tables from PDF files, fills PDF forms, and merges multiple PDFs. Use when working with PDF documents or when the user mentions PDFs, forms, or document extraction.
```

**差的示例**：
```yaml
description: Helps with PDFs.
```

---

### license 字段（可选）

- 指定应用于 skill 的许可证
- 建议保持简短（许可证名称或许可证文件的名称）

**示例**：
```yaml
license: Apache-2.0
```

```yaml
license: Proprietary. LICENSE.txt has complete terms
```

---

### compatibility 字段（可选）

- 如果提供，最多 500 字符
- 仅当 skill 有特定的环境要求时才应包含
- 可以指示目标产品、所需的系统包、网络访问需求等

**示例**：
```yaml
compatibility: Designed for Claude Code (or similar products)
```

```yaml
compatibility: Requires git, docker, jq, and access to the internet
```

大多数 skill 不需要 `compatibility` 字段。

---

### metadata 字段（可选）

- 从字符串键到字符串值的映射
- 客户端可以使用它来存储 Agent Skills 规范未定义的额外属性
- 建议使键名足够唯一，以避免意外冲突

**示例**：
```yaml
metadata:
  author: example-org
  version: "1.0"
  category: deployment
```

---

### allowed-tools 字段（可选）

- 预批准运行工具的空格分隔列表
- 实验性功能。不同代理实现之间对此字段的支持可能有所不同

**示例**：
```yaml
allowed-tools: Bash(git:*) Bash(jq:*) Read
```

---

### Body 内容（Markdown 正文）

Frontmatter 之后的 Markdown 正文包含 skill 指令。没有格式限制。编写任何有助于代理有效执行任务的内容。

**推荐部分**：
- 分步指令
- 输入和输出示例
- 常见边缘情况

**注意**：代理将在决定激活 skill 后加载整个文件一次。考虑将较长的 `SKILL.md` 内容拆分到引用文件中。

---

### 最小示例

```markdown
---
name: skill-name
description: A description of what this skill does and when to use it.
---

# Skill Instructions

Your instructions here...
```

---

### 完整示例

```markdown
---
name: pdf-processing
description: Extract PDF text, fill forms, merge files. Use when handling PDFs.
license: Apache-2.0
metadata:
  author: example-org
  version: "1.0"
  compatibility: Requires pdfplumber, pdfrw packages
---

# PDF Processing Skill

## When to use this skill
Use this skill when the user needs to work with PDF files, including:
- Extracting text or tables from PDFs
- Filling out PDF forms
- Merging multiple PDF files
- Splitting PDF documents

## How to extract text
1. Use the script at `scripts/extract.py`
2. Provide the PDF file path as an argument
3. The script will return extracted text in markdown format

## How to fill forms
1. Load the form template from `assets/form-template.pdf`
2. Map form fields using the mapping in `references/FORMS.md`
3. Save the filled form to the specified location

## Common edge cases
- Password-protected PDFs: Prompt user for password
- Scanned PDFs: Use OCR tools (see `references/ocr-guide.md`)
- Corrupted PDFs: Report error and suggest recovery options
```

---

## 渐进式披露机制

Skills 应该结构化以高效使用上下文：

### 三级加载策略

1. **元数据**（约 100 tokens）
   - `name` 和 `description` 字段
   - 在启动时为所有 skills 加载
   - 用于技能发现和匹配

2. **指令**（建议 < 5000 tokens）
   - 完整的 `SKILL.md` 正文
   - 在 skill 激活时加载
   - 包含执行逻辑和步骤

3. **资源**（按需）
   - 文件（如 `scripts/`、`references/` 或 `assets/` 中的）
   - 仅在需要时加载
   - 支持动态引用

### 最佳实践

- 将主 `SKILL.md` 保持在 500 行以下
- 将详细的参考材料移到单独的文件中
- 保持文件引用与 `SKILL.md` 仅一级深度
- 避免深层的引用链

---

## 文件引用规范

在 skill 中引用其他文件时，使用相对于 skill 根目录的路径：

```markdown
See [the reference guide](references/REFERENCE.md) for details.

Run the extraction script:
```
bash
python scripts/extract.py
```

Use the template at `assets/template.yaml` as a base.
```

**引用规则**：
- 始终使用相对路径
- 路径以 skill 根目录为基准
- 保持引用链扁平化（推荐一级深度）
- 避免循环引用

---

## 发现路径规范

兼容的 Agent Skills 客户端应在以下位置查找 skills：

### 工作区级（Workspace-level）
- `.agents/skills/`
- `.windsurf/skills/`
- `.claude/skills/`（如果启用 Claude Code 配置读取）

### 全局级（Global-level）
- `~/.agents/skills/`
- `~/.codeium/windsurf/skills/`
- `~/.claude/skills/`（如果启用 Claude Code 配置读取）

### 系统级（System-level，企业版）
- macOS: `/Library/Application Support/Windsurf/skills/`
- Linux/WSL: `/etc/windsurf/skills/`
- Windows: `C:\ProgramData\Windsurf\skills\`

---

## 验证工具

使用 `skills-ref` 参考库验证 skills：

```bash
skills-ref validate ./my-skill
```

这会检查：
- `SKILL.md` frontmatter 是否有效
- 是否遵循所有命名约定
- 目录结构是否符合规范

---

## 调用机制

### 自动调用
当任务匹配 skill 的 `description` 时，代理会自动调用该 skill。这是最常见的使用方式。

### 手动调用
用户可以通过特定语法显式调用 skill：
- `@skill-name`（常见语法）
- `/skill-name`（部分工具支持）

---

## 跨平台兼容性

以下工具支持 Agent Skills 标准：

| 工具 | 支持状态 |
|------|----------|
| Windsurf | ✅ 完全支持 |
| Claude | ✅ 完全支持 |
| Cursor | ✅ 完全支持 |
| GitHub Copilot | ✅ 完全支持 |
| VS Code | ✅ 完全支持 |
| 以及更多... | |

---

## 资源链接

- **官方规范**：https://agentskills.io/specification
- **参考库**：https://github.com/agentskills/agentskills
- **示例 Skills**：https://github.com/anthropics/skills
- **最佳实践**：https://agentskills.io/skill-creation/best-practices

---

## 核心原则总结

1. **简单性**：基于标准文件格式（Markdown + YAML）
2. **可移植性**：纯文件，易于版本控制和共享
3. **效率**：渐进式披露，优化上下文使用
4. **可扩展性**：从简单文本到复杂代码和模板都支持
5. **互操作性**：跨平台兼容，一次编写，多处使用
