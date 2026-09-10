# design-doc

AI 驱动的产品设计文档规范库 — 让你与 AI 协作高效编写标准化的技术文档

## 为什么使用 design-doc？

| 传统方式 | 使用 design-doc |
|---------|-----------------|
| 文档格式不统一，每个团队各有风格 | 统一模板，AI 自动遵循规范 |
| 文档结构混乱，审阅困难 | L0-L6 清晰层级，按需选用 |
| 需求/设计变更难以追溯 | 全局唯一编码，全程可追溯 |
| 编写文档费时费力 | AI 辅助生成，只需补充业务细节 |

## 功能特性

- **L0-L6 完整层级** — 覆盖战略与愿景、利益相关者需求、系统/产品需求、概念架构、逻辑/系统设计、详细设计、验证与确认
- **开箱即用模板** — L0–L6 与 ADR/REF 等模板，AI 直接调用
- **统一编码体系** — 文档和细项全局唯一编码，变更可追溯
- **内置审核清单** — AI 帮你检查文档完整性和一致性
- **多 IDE 支持** — Cursor、Windsurf、Claude Code、VS Code 等主流工具自动识别

## 快速开始

### 1. 安装 skill（项目级，自动发现）

将本仓库中的 `.agents/skills/design-doc/` 复制或链接到你的项目 `.agents/skills/design-doc/`。

建议按你的本地系统与终端选择命令，不在本 README 中绑定单一平台命令。

### 2. 在 AI 助手中使用

```
帮我写一份用户认证系统的系统设计文档（L4）
```

AI 会自动：
- 选用正确的模板
- 分配唯一文档编码
- 生成符合规范的文档结构

### 3. 配置项目信息（推荐）

项目元信息登记在**当前作用域的 `ued/README.md`**（不设独立配置文件）：

| 字段 | 说明 |
|------|------|
| `doc_mode` | `single-app` 或 `multi-app` |
| `project_name` | 项目 / 应用名称 |
| `project_code` | 2-4 位大写字母的项目编码；留空即不启用前缀 |
| `scope` | 应用范围说明 |
| `author` / `maintainer` | 文档默认作者 |

多应用模式下，顶层 `ued/README.md` 只维护总入口与应用注册表，各 `ued/{app-name}/README.md` 维护自己的元信息、编码计数器与全局索引。区块写法见 [README 模板](./.agents/skills/design-doc/assets/templates/readme-template.md)。

若 `README.md` 不存在或未声明相应字段，skill 先按默认值继续工作，再提醒补齐：
- `author` = `[designdoc](https://github.com/reddishz/designdoc)`（本技能标识）
- `project_code` = `(空)`（默认不启用项目编码前缀，采用简洁编码格式，如 `FR-001`）

默认值以 [SKILL.md · AI 运行时配置解析规则](./.agents/skills/design-doc/SKILL.md#ai-运行时配置解析规则) 为准。

## 文档层级

| 层级 | 名称 | 用途 |
|-----|------|------|
| L0 | 战略与愿景 | 产品愿景、目标市场、竞争分析 |
| L1 | 利益相关者需求 | 用户画像、需求来源、业务目标 |
| L2 | 系统/产品需求 | 功能需求、非功能需求、业务规则 |
| L3 | 概念架构 | 总体架构、模块划分、技术选型 |
| L4 | 逻辑/系统设计 | 接口设计、数据模型、流程设计 |
| L5 | 详细设计 | 设计级算法、流程逻辑、状态转换、异常与配置约束 |
| L6 | 验证与确认 | 测试策略、追溯关系、验收标准、质量度量 |

> 提示：L0-L6 是完整能力集合，实际落地可按需裁剪；多数项目可先从 L2/L4 起步，无需默认全量创建。

## 支持的 IDE

| IDE | 支持状态 |
|-----|---------|
| Cursor | ✅ 自动发现 |
| Windsurf | ✅ 自动发现 |
| Claude Code | ✅ 自动发现 |
| VS Code | ✅ 自动发现 |
| GitHub Copilot | ✅ 自动发现 |

## 了解更多

### Skill 与规范

- [SKILL.md](./.agents/skills/design-doc/SKILL.md) — 完整规范说明（入口）
- [规范索引](./.agents/skills/design-doc/references/README.md) — `references/` 总览
- [编码体系](./.agents/skills/design-doc/references/coding-system.md) — 文档与细项编码规则、属性行定义集与定义块形态
- [层级体系](./.agents/skills/design-doc/references/layer-system.md) — L0-L6 层级与目录结构
- [状态定义](./.agents/skills/design-doc/references/status-definitions.md) — 标准四态（初稿/正式/草案/废弃）、锁定矩阵、版本号递增与回退
- [术语与概念](./.agents/skills/design-doc/references/glossary-conventions.md) — 词汇表与细项编码分工
- [审核指南](./.agents/skills/design-doc/references/review-guidelines.md) — 文档检查清单
- [废弃细项处理](./.agents/skills/design-doc/references/item-deprecation.md) — 细项废弃与引用更新
- [废弃文档处理](./.agents/skills/design-doc/references/doc-deprecation.md) — 整档废弃的两阶段流程
- [模板库](./.agents/skills/design-doc/assets/templates/index.md) — 文档模板索引
- [流程图指南](./.agents/skills/design-doc/assets/guides/flowchart-guide.md) — 箭头 / 表格 / Mermaid
- [静态检查脚本](./.agents/skills/design-doc/scripts/check_docs.py) — `python3 scripts/check_docs.py -p <ued 路径>`；加 `--refs <编码>` 可反查该编码的全部定义与引用位置

### 仓库参考（非业务模板）

- [参考文档索引](./docs/README.md) — Agent Skills 标准、Cursor/Windsurf/AGENTS.md 等手册

### 外部参考

- [srspub](https://srs.pub/) — 产品需求规范参考

## 许可证

[MIT License](./LICENSE) — 可自由使用于商业和非商业项目

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Agent Skills](https://img.shields.io/badge/Agent%20Skills-Standard-green.svg)](https://agentskills.io/specification)
