# designdoc

> 产品设计文档 Skill 库 - 规范项目产品设计文档的层级体系、目录结构、格式和模板

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Agent Skills Standard](https://img.shields.io/badge/Agent%20Skills-Standard-green.svg)](https://agentskills.io/specification)

## 简介

本仓库是一个 Skill 库，用于规范项目产品设计文档（ued/ 目录）的层级体系、目录结构、格式和模板。包含 L0-L6 层级的设计文档模板（愿景、需求、架构、系统设计、详细设计、验证策略等）。

## 目录结构

```
designdoc/
├── .agents/
│   └── skills/
│       └── design-doc/           # design-doc skill 主目录
│           ├── SKILL.md          # 规范主文件
│           ├── assets/
│           │   └── templates/    # 文档模板
│           └── references/       # 参考文档
├── agent_skills_standard.md      # Agent Skills 标准说明
├── agents_md_guide.md            # AGENTS.md 编写指南
├── cursor_guide.md               # Cursor 使用指南
├── windsurf_guide.md             # Windsurf 使用指南
└── README.md
```

## 标准

本 skill 遵循 [Agent Skills 开放标准](https://agentskills.io/specification)。

## IDE 支持情况

### 项目级（自动发现，无需配置）

所有支持 Agent Skills 标准的工具会自动扫描 `.agents/skills/`：

| IDE / 工具 | 项目级发现路径 | 状态 |
|-----------|--------------|------|
| Cursor | `.agents/skills/`、`.cursor/skills/`、`.claude/skills/` | 已验证 |
| Windsurf | `.agents/skills/`、`.windsurf/skills/`、`.claude/skills/` | 已验证 |
| Claude Code | `.agents/skills/`、`.claude/skills/` | 已验证 |
| GitHub Copilot | `.agents/skills/` | 已验证 |
| VS Code | `.agents/skills/` | 已验证 |
| Qoder | `.qoder/skills/` | 需 symlink |

### 用户级（全局，需手动安装）

各工具的用户级扫描路径不同，建议按实际使用的工具逐个安装：

| IDE / 工具 | 用户级发现路径 | 备注 |
|-----------|--------------|------|
| Cursor | `~/.cursor/skills/` | 也扫描 `~/.claude/skills/`、`~/.codex/skills/`，但对 `.claude` 支持不完整，建议用原生路径 |
| Windsurf | `~/.codeium/windsurf/skills/` | 也扫描 `~/.agents/skills/` |
| Claude Code | `~/.claude/skills/` | |
| Qoder | `~/.qoder/skills/` | |

### 暂不支持

| IDE / 工具 | 原因 |
|-----------|------|
| Trae（CN / 国际版） | 不支持 Agent Skills 标准，仅支持 `.trae/rules/` 格式。后续如需支持可增加翻译脚本 |

## 全局安装

按使用的工具创建对应 symlink：

```bash
# Cursor（推荐优先安装）
mkdir -p ~/.cursor/skills
ln -sfn /path/to/project/.agents/skills/design-doc ~/.cursor/skills/design-doc

# Claude Code
mkdir -p ~/.claude/skills
ln -sfn /path/to/project/.agents/skills/design-doc ~/.claude/skills/design-doc

# Windsurf
mkdir -p ~/.codeium/windsurf/skills
ln -sfn /path/to/project/.agents/skills/design-doc ~/.codeium/windsurf/skills/design-doc

# Qoder
mkdir -p ~/.qoder/skills
ln -sfn /path/to/project/.agents/skills/design-doc ~/.qoder/skills/design-doc
```

## 用户配置

创建文档时，作者字段通过以下优先级自动获取：

1. 项目配置 `ued/.doc-config.json` 中的 `author` 字段
2. `git config user.name`
3. 默认值：`产品架构组`

```json
{
  "author": "张三"
}
```

## 后续扩展

如需为不支持通用标准的工具增加适配，在项目根目录添加翻译脚本（如 `sync-trae.sh`），从 `.agents/skills/design-doc/` 读取源文件并转换为目标格式。

## 许可证

本项目采用 [MIT License](LICENSE) 开源协议。
