> **模板：系统根 `ued/README.md`**
>
> 仅用于「系统 + 子系统」结构。单系统请使用 design-doc 的 `readme-template.md`。
>
> **正文边界**：见 [index.md](index.md) 的模板边界说明。

---

<!-- TEMPLATE:BEGIN 系统根 ued/README.md -->
# {project_name} 系统设计总览

## 项目元信息

| 字段 | 值 |
|------|----|
| project_name | {project_name} |
| scope | 系统（含多个子系统） |
| author | {author} |
| last_updated | {YYYY-MM-DD} |

## 当前结构

本仓库为**系统 + 子系统**结构：

- 系统级：本 README 维护子系统注册表、跨子系统规则与系统发布索引。
- 子系统级：每个子系统是独立的 design-doc 作用域，拥有自己的 README、产品版本、基线与编码索引。
- 子系统内部的分层设计、编码、状态与产品基线遵循 design-doc；系统级组合、依赖与发布遵循 system-design-doc。

单系统项目不使用本模板。

## 子系统注册表

| subsystem_key | 子系统名称 | 目录 | 编码前缀 | 角色文档 | 状态 |
|---------------|------------|------|----------|----------|------|
| {subsystem_key} | {子系统名称} | {目录}/ | {PREFIX 或留空} | {PREFIX-CMP-001 或留空} | 初稿 |

- `subsystem_key` 登记后不可改、不可复用。
- `正式` 子系统必须有角色文档、`产品版本` 与对应基线。
- 共享库按普通子系统登记，不设固定 `shared/` 目录。

## 系统发布索引

| 发布 | 日期 | 说明 | 清单 |
|------|------|------|------|
| sys-v1.0 | {YYYY-MM-DD} | {说明} | [清单](releases/sys-v1.0.yaml) |

系统发布是组合锁，不是设计基线；发布后不可修改。发布按需创建，不要求覆盖全部正式子系统。

## 术语表

全局术语表：[glossary.md](glossary.md)。全系统唯一；子系统不另建 glossary。

## 子系统导航

| 子系统 | 入口 | 说明 |
|--------|------|------|
| {子系统名称} | [{目录}/README.md]({目录}/README.md) | {一句话职责} |

## 跨子系统规则

- 跨子系统引用 MUST 使用完整编码。
- 依赖 MUST 在子系统基线 `depends_on` / `external_deps` 中钉住精确两段版本。
- 接口破坏性变更 MUST 使用 MAJOR，并协调所有消费者。
<!-- TEMPLATE:END -->
