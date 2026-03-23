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

- **L0-L6 完整层级** — 覆盖愿景、需求、概念架构、系统设计、详细设计、验证策略
- **开箱即用模板** — L0–L6 与 ADR/REF 等模板，AI 直接调用
- **统一编码体系** — 文档和细项全局唯一编码，变更可追溯
- **内置审核清单** — AI 帮你检查文档完整性和一致性
- **多 IDE 支持** — Cursor、Windsurf、Claude Code、VS Code 等主流工具自动识别

## 快速开始

### 1. 安装 skill（项目级，自动发现）

```bash
# 克隆到你的项目
cp -r .agents/skills/design-doc /your-project/.agents/skills/
```

或创建符号链接：

```bash
ln -sfn /path/to/designdoc/.agents/skills/design-doc /your-project/.agents/skills/design-doc
```

### 2. 在 AI 助手中使用

```
帮我写一份用户认证系统的系统设计文档（L4）
```

AI 会自动：
- 选用正确的模板
- 分配唯一文档编码
- 生成符合规范的文档结构

### 3. 配置作者信息（可选）

在 `ued/.doc-config.json` 中配置：

```json
{
  "author": "你的名字"
}
```

## 文档层级

| 层级 | 名称 | 用途 |
|-----|------|------|
| L0 | 战略愿景 | 产品愿景、目标市场、竞争分析 |
| L1 | 干系人需求 | 用户画像、需求来源、业务目标 |
| L2 | 需求定义 | 功能需求、非功能需求、业务规则 |
| L3 | 概念架构 | 总体架构、模块划分、技术选型 |
| L4 | 系统设计 | 接口设计、数据模型、流程设计 |
| L5 | 详细设计 | 实现细节、算法说明、配置说明 |
| L6 | 验证策略 | 测试计划、验收标准、上线方案 |

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

- [Skill 入口](./.agents/skills/design-doc/README.md) — 目录说明与导航
- [SKILL.md](./.agents/skills/design-doc/SKILL.md) — 完整规范说明
- [规范索引](./.agents/skills/design-doc/references/README.md) — `references/` 总览
- [编码体系](./.agents/skills/design-doc/references/coding-system.md) — 文档编码规则
- [审核指南](./.agents/skills/design-doc/references/review-guidelines.md) — 文档检查清单
- [模板库](./.agents/skills/design-doc/assets/templates/index.md) — 文档模板索引
- [辅助指南](./.agents/skills/design-doc/assets/guides/README.md) — 流程图与 AI 编码说明（非模板）

### 仓库参考（非业务模板）

- [参考文档索引](./docs/README.md) — Agent Skills 标准、Cursor/Windsurf/AGENTS.md 等手册

### 外部参考

- [srspub](https://srs.pub/) — 产品需求规范参考

## 许可证

[MIT License](./LICENSE) — 可自由使用于商业和非商业项目

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Agent Skills](https://img.shields.io/badge/Agent%20Skills-Standard-green.svg)](https://agentskills.io/specification)
