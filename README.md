# design-doc

与 AI 协作编写标准化的产品设计文档：分层清楚、编码可追溯，定稿之后可以放心作为实现依据。

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Skill](https://img.shields.io/badge/skill-v4.8-blue.svg)](./.agents/skills/design-doc/SKILL.md)
[![Agent Skills](https://img.shields.io/badge/Agent%20Skills-Standard-green.svg)](https://agentskills.io/specification)

把本仓库的 skill 装进项目后，直接对 AI 说「写一份 L4 系统设计」即可。多数项目从需求（L2）和系统设计（L4）起步，不必一次生成全套。

## 为什么使用 design-doc？

| 没有它时 | 有它之后 |
|---------|---------|
| 文档格式不统一，每个团队各有风格 | 统一模板，AI 按同一套规范写 |
| 结构混乱，审阅困难 | L0–L6 分层，按需选用 |
| 需求改了找不到影响面 | 每条设计有唯一编码，互相用编码引用 |
| 草稿被拿去写代码，正式内容被随手改掉 | 先定稿再实现；正式内容改之前要解冻 |
| 对不对全靠人眼 | 有审核清单，也可以跑检查脚本 |

## 功能特性

- **分层文档** — 从战略、需求、架构到详细设计与验证；未指定时默认写 L2 或 L4
- **现成模板** — 含产品路线图、规划总览、架构决策（ADR）和外部资料（REF）
- **全局编码** — 文档和细项都有唯一编号，正文用编码跳转，不用「见上一节」
- **四种状态** — 初稿 / 正式 / 草案 / 废弃。正式后不就地改含义；废弃保留编号，便于追溯
- **按文档实现** — AI 写代码时只依据已定稿内容，未定稿的会先请你确认
- **可检查** — `check_docs.py` 核对编码、状态、引用是否对得上
- **多 IDE** — Cursor、Windsurf、Claude Code、VS Code 等可自动发现本 skill

## 快速开始

### 1. 安装

把本仓库的 `.agents/skills/design-doc/` 复制或链接到你项目的 `.agents/skills/design-doc/`。按本机环境和终端选用命令即可。

### 2. 开始写

```
帮我写一份用户认证系统的系统设计文档（L4）
```

AI 会选用模板、分配编码，并默认标为「初稿」。提交前会问你哪些条目要定稿。

若要按这些文档写代码，它会先看状态：还没定稿的不会直接拿去实现。

### 3. 登记项目信息（推荐）

在 `ued/README.md` 里写上项目名和作者即可，不必另配模式开关。**一个应用**就把文档放在 `ued/` 下；**多个应用**各占 `ued/{应用名}/`，顶层 README 只做总入口。

| 字段 | 说明 |
|------|------|
| `project_name` | 项目 / 应用名称 |
| `author` / `maintainer` | 默认作者 |
| `project_code` | 可选前缀；留空则用 `FR-001` 这样的简洁编码 |
| `scope` | 应用范围（可选） |

写法见 [README 模板](./.agents/skills/design-doc/assets/templates/readme-template.md)。缺字段时 skill 会用默认值继续工作，并提醒补齐。

### 4. 检查文档（可选）

```
python3 .agents/skills/design-doc/scripts/check_docs.py -p ued
```

改标题或作废某条编码前，加上 `--refs {编码}` 可列出它出现过的所有位置。

## 文档层级

各层回答哪一句、写什么，以 [层级定义](./.agents/skills/design-doc/references/layer-system.md#层级定义) 为准。摘要：

| 层级 | 名称 | 核心问题 |
|-----|------|----------|
| L0 | 战略与愿景 | 为什么做 |
| L1 | 利益相关者需求 | 谁需要什么 |
| L2 | 系统 / 产品需求 | 必须满足什么 |
| L3 | 概念架构 | 准备用怎样的系统组织来满足 |
| L4 | 逻辑 / 系统设计 | 这个组织如何落成契约与结构 |
| L5 | 详细设计 | 局部机制如何算、如何转、如何配 |
| L6 | 验证与确认 | 如何证明满足要求 |

多数项目先写 L2 和 L4，其他层用到再补。

## 支持的 IDE

| IDE | 支持状态 |
|-----|---------|
| Cursor | ✅ 自动发现 |
| Windsurf | ✅ 自动发现 |
| Claude Code | ✅ 自动发现 |
| VS Code | ✅ 自动发现 |
| GitHub Copilot | ✅ 自动发现 |

## 相关技能

动笔写设计文档之前，若想先把问题想清楚，可以搭配 [multi-angle-thinking](https://github.com/reddishz/multi-angle-thinking)：从规划、事实、感受、风险、价值、创意六个角度讨论，再落到本仓库的分层文档。

## 了解更多

规范入口是 [SKILL.md](./.agents/skills/design-doc/SKILL.md)，模板在 [模板库](./.agents/skills/design-doc/assets/templates/index.md)。其余细则：

- [规范索引](./.agents/skills/design-doc/references/README.md)
- [对象模型](./.agents/skills/design-doc/references/object-model.md) — 谁能改什么、如何作废与解冻
- [编码体系](./.agents/skills/design-doc/references/coding-system.md)
- [层级与目录](./.agents/skills/design-doc/references/layer-system.md)
- [状态定义](./.agents/skills/design-doc/references/status-definitions.md)
- [审核指南](./.agents/skills/design-doc/references/review-guidelines.md)
- [检查脚本](./.agents/skills/design-doc/scripts/check_docs.py)

Agent Skills / IDE 手册见 [docs/](./docs/README.md)。产品需求写法也可参考 [srs.pub](https://srs.pub/)。

## 许可证

[MIT License](./LICENSE) — 可用于商业和非商业项目
