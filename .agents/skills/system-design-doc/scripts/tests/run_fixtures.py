#!/usr/bin/env python3
"""system-design-doc v2.0 夹具测试。

每个用例在临时目录中构造一个 ued/ 树，运行 check_system.py 的检查方法，
断言预期问题标题出现 / 不出现。只覆盖系统级规则；文档内部规则由
design-doc 的测试覆盖。
"""
from __future__ import annotations

import re
import sys
import tempfile
from pathlib import Path
from typing import Dict, Optional

import yaml

ROOT = Path(__file__).resolve().parent
SKILL = ROOT.parents[1]
sys.path.insert(0, str(SKILL / "scripts"))

from check_system import SystemChecker, installed_spec_version  # noqa: E402

PASS = 0
FAIL = 0


def check(name: str, cond: bool) -> None:
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  PASS {name}")
    else:
        FAIL += 1
        print(f"  FAIL {name}")


def run(root: Path) -> SystemChecker:
    c = SystemChecker(str(root / "ued"))
    c.load()
    c.check_structure()
    if c.is_system:
        c.check_registry()
        c.check_architecture()
        c.check_subsystem_dirs()
        c.check_dependencies()
        c.check_releases()
        c.check_cross_scope()
        c.check_readme_sections()
    return c


def titles(c: SystemChecker) -> list:
    return [i.title for i in c.issues]


def levels(c: SystemChecker) -> set:
    return {i.level for i in c.issues}


def has(c: SystemChecker, title: str) -> bool:
    return title in titles(c)


def no_errors(c: SystemChecker) -> bool:
    return not ({"CRITICAL", "ERROR"} & levels(c))


def write_tree(root: Path, files: Dict[str, str]) -> None:
    for rel, content in files.items():
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")


def readme(rows: str, release_rows: str = "", extra_meta: str = "",
           structure: bool = True, release_table: bool = True,
           glossary: bool = True, arch_link: bool = True,
           spec_target: Optional[str] = None) -> str:
    # None = 默认写已装版本；"" = 不写该行（用于缺失用例）
    spec_row = ("" if spec_target == "" else
                f"| 规范版本目标 | {spec_target or installed_spec_version()} |\n")
    structure_block = (
        "## 当前结构\n\n本仓库为系统 + 子系统结构；系统级与子系统级职责分离。\n\n"
        if structure else ""
    )
    arch_block = (
        "## 系统架构\n\n"
        "- 系统架构描述：[architecture/system-architecture.md](architecture/system-architecture.md)\n\n"
        if arch_link else ""
    )
    release_block = ""
    if release_table:
        release_block = (
            "## 系统发布索引\n\n"
            "| 发布 | 日期 | 说明 | 清单 |\n"
            "|------|------|------|------|\n"
            f"{release_rows}\n\n"
        )
    glossary_block = (
        "## 术语表\n\n全局术语表：[glossary.md](glossary.md)。\n\n"
        if glossary else ""
    )
    return f"""# Demo 系统设计总览

## 项目元信息

| 字段 | 值 |
|------|----|
| project_name | Demo |
| scope | 系统（含多个子系统） |
| author | tester |
| last_updated | 2026-01-01 |
{spec_row}{extra_meta}
{structure_block}{arch_block}## 子系统注册表

| subsystem_key | 子系统名称 | 目录 | 编码前缀 | 状态 |
|---------------|------------|------|----------|------|
{rows}

{release_block}{glossary_block}## 子系统导航

| 子系统 | 入口 |
|--------|------|
| CRM | [crm/README.md](crm/README.md) |
"""


def system_arch(
    resp_rows: str,
    status: str = "正式",
    rev: int = 1,
    rev_rows: Optional[str] = None,
    interaction_block: Optional[str] = None,
    constraints_block: Optional[str] = None,
) -> str:
    if rev_rows is None:
        rev_rows = f"| {rev} | 2026-01-01 | {status if status in ('正式', '初稿') else '正式'} | 初始架构 |"
    if interaction_block is None:
        interaction_block = (
            "| 提供方 | 消费方 | 交互目的 | 方式 | 契约 |\n"
            "|--------|--------|----------|------|------|\n"
            "| oms | crm | 提供订单查询与履约状态 | 接口调用 | OMS-IF-001 |"
        )
    if constraints_block is None:
        constraints_block = (
            '<a id="sys-con-001"></a>\n'
            "### SYS-CON-001：全系统统一采用 UTC 时间基准\n\n"
            "- **约束说明**：所有子系统跨服务时间戳必须使用 UTC。\n"
            "- **适用范围**：crm、oms"
        )
    return f"""# Demo 系统架构描述

| 字段 | 值 |
|------|----|
| 文档名称 | Demo 系统架构描述 |
| 状态 | {status} |
| 修订版本号 | {rev} |
| 最后更新 | 2026-01-01 |
| 规范版本 | {installed_spec_version()} |

## 系统定义

- **系统定位**：示例交易与客户管理系统。
- **系统目标**：实现客户与订单协同。

## 子系统职责分配

| subsystem_key | 系统角色 | 核心职责 | 明确非职责与边界 |
|---------------|----------|----------|------------------|
{resp_rows}

## 系统交互

{interaction_block}

## 系统级约束

{constraints_block}

## 修订记录

| 修订号 | 日期 | 版本类型 | 变更摘要 |
|--------|------|----------|----------|
{rev_rows}
"""


def sys_adr_doc(
    code: str = "SYS-ADR-001",
    status: str = "正式",
    rev: str = "1",
    impact: str = "crm, oms",
    replacement: str = "无",
) -> str:
    return f"""# {code}：拆分客户与订单子系统

| 字段 | 值 |
|------|----|
| 文档编码 | {code} |
| 状态 | {status} |
| 修订版本号 | {rev} |
| 最后更新 | 2026-01-01 |
| 规范版本 | {installed_spec_version()} |
| 影响范围 | {impact} |
| 替代方案 | {replacement} |

## 背景与问题

业务边界分离。

## 决策内容

拆分为 crm 与 oms 两个独立子系统。
"""


def sub_readme(name: str, prefix: str, pv: str) -> str:
    return f"""# {name} 设计文档索引

## 项目元信息

| 字段 | 值 |
|------|----|
| project_name | {name} |
| project_code | {prefix} |
| scope | {name} |
| author | tester |
| last_updated | 2026-01-01 |
| 产品版本 | {pv} |

## 术语表

全局术语表：[../glossary.md](../glossary.md)。
"""


def l3_comp_doc(prefix: str, body: str = "本子系统内部逻辑组件") -> str:
    code = f"{prefix}-CMP-001" if prefix else "CMP-001"
    return f"""# {code}-核心引擎组件

- **细项状态**：正式
- **修订版本号**：1
- **创建日期**：2026-01-01
- **最后修订日期**：2026-01-01
- **满足需求**：无

## 说明

{body}
"""


def l4_if_doc(prefix: str) -> str:
    code = f"{prefix}-IF-001" if prefix else "IF-001"
    return f"""# {code}-订单查询接口

- **细项状态**：正式
- **修订版本号**：1
- **创建日期**：2026-01-01
- **最后修订日期**：2026-01-01
"""


def l2_doc(prefix: str, suffix: str = "示例") -> str:
    code = f"{prefix}-L2-001" if prefix else "L2-001"
    return f"""# {code}-{suffix}

| 属性 | 值 |
|------|----|
| 文档编码 | {code} |
| 层级 | L2 |
| 修订版本号 | 1 |
| 状态 | 正式 |
| 作者 | tester |
| 创建日期 | 2026-01-01 |
| 最后更新 | 2026-01-01 |

## 变更记录

| 修订版本号 | 日期 | 作者 | 变更说明 |
|------------|------|------|----------|
| 1 | 2026-01-01 | tester | 初建 |
"""


def baseline(pv: str, full: str, deps=None, exts=None) -> str:
    data = {
        "product_version": pv,
        "full_version": full,
        "created": "2026-01-01",
        "updated": "2026-01-01",
        "prev": None,
        "patch_log": [{"full_version": full, "date": "2026-01-01", "note": "初建"}],
        "added": [],
        "removed": [],
        "changed": [],
        "depends_on": deps if deps is not None else [],
        "external_deps": exts if exts is not None else [],
        "items": [],
    }
    return yaml.safe_dump(data, allow_unicode=True, sort_keys=False)


def release_text(subs, exts=None, arch_rev: Optional[int] = 1,
                 include_arch_rev: bool = True, rel_name: str = "sys-v1.0") -> str:
    data = {
        "release": rel_name,
        "created": "2026-01-02",
        "note": "首个产品集发布",
        "subsystems": subs,
        "external_deps": exts if exts is not None else [],
    }
    if include_arch_rev:
        data["architecture_rev"] = arch_rev
    return yaml.safe_dump(data, allow_unicode=True, sort_keys=False)


def valid_files(include_shared: bool = False) -> Dict[str, str]:
    rows = [
        "| crm | 客户关系 | crm/ | CRM | 正式 |",
        "| oms | 订单中心 | oms/ | OMS | 正式 |",
    ]
    resp_rows = [
        "| crm | 客户管理 | 维护客户档案与跟进记录 | 不负责订单履约与库存 |",
        "| oms | 订单履约 | 订单创建、状态流转与履约 | 不维护客户主数据 |",
    ]
    subs = [
        {"subsystem": "crm", "product_version": "v1.0", "full_version": "v1.0.0"},
        {"subsystem": "oms", "product_version": "v2.5", "full_version": "v2.5.0"},
    ]
    if include_shared:
        rows.append("| shared-lib | 公共库 | shared-lib/ | LIB | 正式 |")
        resp_rows.append("| shared-lib | 公共基础设施 | 提供统一时间与序列化库 | 不含业务逻辑 |")
        subs.append({"subsystem": "shared-lib", "product_version": "v1.0",
                     "full_version": "v1.0.0"})
    files = {
        "ued/README.md": readme(
            "\n".join(rows),
            "| sys-v1.0 | 2026-01-02 | 首个产品集发布 | [清单](releases/sys-v1.0.yaml) |",
        ),
        "ued/architecture/system-architecture.md": system_arch("\n".join(resp_rows)),
        "ued/architecture/SYS-ADR-001-split-crm-oms.md": sys_adr_doc(),
        "ued/releases/sys-v1.0.yaml": release_text(
            subs, [{"name": "identity-provider", "product_version": "v4.0"}]),
        "ued/glossary.md": """# 全局术语表

| 属性 | 值 |
|------|----|
| 修订版本号 | 1 |
| 作者 | tester |
| 创建日期 | 2026-01-01 |
| 最后更新 | 2026-01-01 |

## 术语

| 中文名称 | 英文名称 | 定义 | 定义位置 |
|----------|----------|------|----------|
| 订单 | Order | 客户提交的购买请求。 | CRM-L2-001 |

## 变更记录

| 修订版本号 | 日期 | 作者 | 变更说明 |
|------------|------|------|----------|
| 1 | 2026-01-01 | tester | 初建 |
""",
        "ued/crm/README.md": sub_readme("客户关系", "CRM", "v1.0"),
        "ued/crm/L2-001-req.md": l2_doc("CRM"),
        "ued/crm/L3-001-arch.md": l3_comp_doc("CRM"),
        "ued/crm/baselines/v1.0.yaml": baseline(
            "v1.0", "v1.0.0",
            deps=[{"subsystem": "oms", "product_version": "v2.5"}],
            exts=[{"name": "identity-provider", "product_version": "v4.0"}]),
        "ued/oms/README.md": sub_readme("订单中心", "OMS", "v2.5"),
        "ued/oms/L2-001-req.md": l2_doc("OMS"),
        "ued/oms/L3-001-arch.md": l3_comp_doc("OMS"),
        "ued/oms/L4-001-if.md": l4_if_doc("OMS"),
        "ued/oms/baselines/v2.5.yaml": baseline(
            "v2.5", "v2.5.0", deps=[],
            exts=[{"name": "identity-provider", "product_version": "v4.0"}]),
    }
    if include_shared:
        files.update({
            "ued/shared-lib/README.md": sub_readme("公共库", "LIB", "v1.0"),
            "ued/shared-lib/L2-001-req.md": l2_doc("LIB"),
            "ued/shared-lib/L3-001-arch.md": l3_comp_doc("LIB"),
            "ued/shared-lib/baselines/v1.0.yaml": baseline("v1.0", "v1.0.0"),
        })
    return files


def case(name: str, files: Dict[str, str]) -> SystemChecker:
    tmp = tempfile.TemporaryDirectory()
    root = Path(tmp.name)
    write_tree(root, files)
    c = run(root)
    tmp.cleanup()
    return c


def main() -> int:
    print("system-design-doc v2.2 fixtures")

    # ---- 基础结构与注册表 ----
    c = case("valid", valid_files())
    check("有效系统无 ERROR", no_errors(c))
    check("有效系统无 WARNING", not c.issues)
    check("有效系统识别为系统", c.is_system)

    c = case("shared-as-subsystem", valid_files(include_shared=True))
    check("共享库作为普通子系统通过", no_errors(c))
    check("共享库被识别", "shared-lib" in [s.key for s in c.subsystems])

    # 旧 6 列注册表（含 角色文档）→ ERROR
    files = valid_files()
    files["ued/README.md"] = files["ued/README.md"].replace(
        "| subsystem_key | 子系统名称 | 目录 | 编码前缀 | 状态 |\n"
        "|---------------|------------|------|----------|------|\n"
        "| crm | 客户关系 | crm/ | CRM | 正式 |\n"
        "| oms | 订单中心 | oms/ | OMS | 正式 |",
        "| subsystem_key | 子系统名称 | 目录 | 编码前缀 | 角色文档 | 状态 |\n"
        "|---------------|------------|------|----------|----------|------|\n"
        "| crm | 客户关系 | crm/ | CRM | CRM-CMP-001 | 正式 |\n"
        "| oms | 订单中心 | oms/ | OMS | OMS-CMP-001 | 正式 |"
    )
    c = case("legacy-6col-registry", files)
    check("旧 6 列含角色文档报 ERROR", has(c, "注册表含已移除的旧列"))

    # 子系统禁用保留前缀 SYS
    files = valid_files()
    files["ued/README.md"] = files["ued/README.md"].replace(
        "| oms | 订单中心 | oms/ | OMS | 正式 |",
        "| oms | 订单中心 | oms/ | SYS | 正式 |")
    files["ued/oms/README.md"] = sub_readme("订单中心", "SYS", "v2.5")
    c = case("reserved-prefix-sys", files)
    check("子系统使用 SYS 前缀报错", has(c, "编码前缀使用系统保留词"))

    files = valid_files()
    files["ued/README.md"] = readme(
        "| crm | 客户关系 | crm/ | CRM | 正式 |",
        "| sys-v1.0 | 2026-01-02 | 首个产品集发布 | [清单](releases/sys-v1.0.yaml) |",
    )
    c = case("missing-ledger-row", files)
    check("未登记 oms 目录报错", has(c, "未登记子系统目录"))

    files = valid_files()
    files["ued/README.md"] = files["ued/README.md"].replace(
        "| 字段 | 值 |\n|------|----|\n| project_name | Demo |",
        "| 字段 | 值 |\n|------|----|\n| project_name | Demo |\n| 产品版本 | v1.0 |")
    c = case("root-product-version", files)
    check("系统根产品版本报错", has(c, "系统根不得有产品版本"))

    # 无注册表的单系统：不应报 ERROR
    single = {
        "ued/README.md": """# 单系统设计文档索引

## 项目元信息

| 字段 | 值 |
|------|----|
| project_name | Single |
| project_code | APP |
| scope | 单系统 |
| author | tester |
| last_updated | 2026-01-01 |
| 产品版本 | v1.0 |

## 文档索引

| 文档编码 | 文档标题 | 状态 |
|----------|----------|------|
| APP-L2-001 | 需求 | 正式 |
""",
        "ued/APP-L2-001-req.md": l2_doc("APP"),
        "ued/baselines/v1.0.yaml": baseline("v1.0", "v1.0.0"),
    }
    c = case("single-system", single)
    check("单系统不误报 ERROR", no_errors(c))
    check("单系统给出指引", has(c, "非系统结构"))

    files = valid_files()
    files["ued/README.md"] = files["ued/README.md"].replace(
        "| crm | 客户关系 | crm/ | CRM | 正式 |\n"
        "| oms | 订单中心 | oms/ | OMS | 正式 |",
        "| crm | 客户关系 | crm/ | CRM | 正式 |\n"
        "| crm | 客户关系副本 | oms/ | OMS | 正式 |")
    c = case("duplicate-key", files)
    check("subsystem_key 重复报错", has(c, "subsystem_key 重复"))

    files = valid_files()
    files["ued/README.md"] = files["ued/README.md"].replace(
        "| oms | 订单中心 | oms/ | OMS | 正式 |",
        "| oms | 订单中心 | crm/ | OMS | 正式 |")
    c = case("duplicate-dir", files)
    check("子系统目录重复报错", has(c, "子系统目录重复"))

    files = valid_files()
    files["ued/README.md"] = files["ued/README.md"].replace(
        "| oms | 订单中心 | oms/ | OMS | 正式 |",
        "| oms | 订单中心 | oms/ | CRM | 正式 |")
    c = case("duplicate-prefix", files)
    check("编码前缀重复报错", has(c, "编码前缀重复"))

    files = valid_files()
    files["ued/README.md"] = files["ued/README.md"].replace(
        "| oms | 订单中心 | oms/ | OMS | 正式 |",
        "| oms | 订单中心 | nope/ | OMS | 正式 |")
    c = case("missing-dir", files)
    check("子系统目录不存在报错", has(c, "子系统目录不存在"))

    files = valid_files()
    files["ued/README.md"] = files["ued/README.md"].replace(
        "| oms | 订单中心 | oms/ | OMS | 正式 |",
        "| oms | 订单中心 | oms/ | OMS | 草案 |")
    c = case("invalid-status", files)
    check("草案状态报错", has(c, "子系统状态非法"))

    files = valid_files()
    del files["ued/crm/baselines/v1.0.yaml"]
    c = case("active-no-baseline", files)
    check("正式子系统缺基线报错", has(c, "正式子系统缺基线"))

    # ---- 系统架构、职责分配、交互与约束 ----
    files = valid_files()
    del files["ued/architecture/system-architecture.md"]
    c = case("missing-arch-doc", files)
    check("有正式子系统缺架构文档报错", has(c, "缺系统架构文档"))

    files = valid_files()
    files["ued/architecture/system-architecture.md"] = system_arch(
        "| crm | 客户管理 | 维护客户档案 | 不做订单 |"
    )
    c = case("missing-sub-in-arch", files)
    check("正式子系统未分配架构职责报错", has(c, "正式子系统缺架构职责分配"))

    files = valid_files()
    files["ued/architecture/system-architecture.md"] = system_arch(
        "| crm | 客户管理 | 维护客户档案 |  |\n"
        "| oms | 订单履约 | 订单流转 | 不管客户 |"
    )
    c = case("incomplete-resp", files)
    check("正式子系统缺明确非职责报错", has(c, "正式子系统职责分配不完整"))

    files = valid_files()
    files["ued/architecture/system-architecture.md"] = system_arch(
        "| crm | 客户管理 | 维护客户档案 | 不管订单 |\n"
        "| oms | 订单履约 | 订单流转 | 不管客户 |\n"
        "| ghost | 幽灵 | 无 | 无 |"
    )
    c = case("ghost-key-in-arch", files)
    check("架构职责表含未登记子系统报错", has(c, "架构职责表含未登记子系统"))

    # 系统交互与约束显式声明无 → 不强制造表，无 ERROR/WARNING
    files = valid_files()
    files["ued/architecture/system-architecture.md"] = system_arch(
        "| crm | 客户管理 | 维护客户档案 | 不管订单 |\n"
        "| oms | 订单履约 | 订单流转 | 不管客户 |",
        interaction_block="本系统各子系统完全独立运行，当前无直接内部交互。",
        constraints_block="当前暂无独立于子系统需求的全局系统级约束。",
    )
    c = case("explicit-empty-interaction-and-con", files)
    check("交互与约束显式声明无可通过", no_errors(c) and not c.issues)

    # 交互表契约悬空与归属不符
    files = valid_files()
    files["ued/architecture/system-architecture.md"] = system_arch(
        "| crm | 客户管理 | 维护客户档案 | 不管订单 |\n"
        "| oms | 订单履约 | 订单流转 | 不管客户 |",
        interaction_block=(
            "| 提供方 | 消费方 | 交互目的 | 方式 | 契约 |\n"
            "|--------|--------|----------|------|------|\n"
            "| oms | crm | 订单查询 | 调用 | OMS-IF-999 |\n"
            "| oms | crm | 客户查询 | 调用 | CRM-CMP-001 |"
        ),
    )
    c = case("interaction-contract-checks", files)
    check("交互契约悬空告警", has(c, "系统交互契约悬空"))
    check("交互契约归属提供方不符报错", has(c, "系统交互契约归属不符"))

    # ---- SYS 命名空间与扫描隔离 ----
    files = valid_files()
    files["ued/crm/L2-001-req.md"] += "\n### SYS-CON-002：子系统越权定义\n"
    c = case("sub-define-sys-con", files)
    check("子系统定义 SYS 编码报错", has(c, "子系统不得定义 SYS 编码"))

    files = valid_files()
    files["ued/crm/SYS-ADR-002-rogue.md"] = sys_adr_doc(code="SYS-ADR-002")
    c = case("sub-define-sys-adr-doc", files)
    check("子系统定义 SYS-ADR 文档报错", has(c, "子系统不得定义 SYS 编码"))

    files = valid_files()
    files["ued/crm/L2-001-req.md"] += (
        "\n- **来源**：[SYS-CON-001（统一 UTC）](../../architecture/system-architecture.md#sys-con-001)\n"
        "- **来源**：[SYS-ADR-001（拆分决策）](../../architecture/SYS-ADR-001-split-crm-oms.md)\n"
    )
    c = case("sub-ref-sys-ok", files)
    check("子系统合法引用 SYS-CON 与 SYS-ADR 通过", no_errors(c) and not c.issues)

    files = valid_files()
    files["ued/crm/L2-001-req.md"] += "\n正文引用 `SYS-CON-999` 与 `SYS-ADR-999`。\n"
    c = case("sub-ref-sys-dangling", files)
    check("子系统普通引用悬空 SYS-CON 告警",
          any(i.title == "系统约束引用悬空" and i.level == "WARNING" for i in c.issues))
    check("子系统普通引用悬空 SYS-ADR 告警",
          any(i.title == "系统决策引用悬空" and i.level == "WARNING" for i in c.issues))

    files = valid_files()
    files["ued/crm/L2-001-req.md"] += (
        "\n- **依赖**：[SYS-CON-999（不存在）](../../architecture/system-architecture.md#sys-con-999)\n"
    )
    c = case("sub-dep-sys-dangling", files)
    check("子系统依赖悬空 SYS-CON 报错",
          any(i.title == "系统约束依赖悬空" and i.level == "ERROR" for i in c.issues))
    check("系统架构锚点不可达报错", has(c, "系统架构锚点不可达"))

    # SYS-CON 缺锚点
    files = valid_files()
    files["ued/architecture/system-architecture.md"] = system_arch(
        "| crm | 客户管理 | 维护客户档案 | 不管订单 |\n"
        "| oms | 订单履约 | 订单流转 | 不管客户 |",
        constraints_block="### SYS-CON-001：缺锚点约束\n\n- **约束说明**：测试。",
    )
    c = case("sys-con-missing-anchor", files)
    check("SYS-CON 缺锚点报错", has(c, "系统约束缺锚点"))

    # SYS-ADR 状态非法 & 影响范围含未登记 key
    files = valid_files()
    files["ued/architecture/SYS-ADR-002-bad.md"] = sys_adr_doc(
        code="SYS-ADR-002", status="无效态", impact="crm, ghost"
    )
    c = case("sys-adr-invalid", files)
    check("SYS-ADR 状态非法报错", has(c, "SYS-ADR 状态非法"))
    check("SYS-ADR 影响范围含未登记子系统报错", has(c, "SYS-ADR 影响范围含未登记子系统"))

    # 扫描隔离：architecture/ 下文档不会混入子系统 definitions / doc_code_map
    c = case("arch-isolation", valid_files())
    check("SYS-CON 未混入子系统 definitions", "SYS-CON-001" not in c.definitions)
    check("SYS-ADR 未混入子系统 doc_code_map", "SYS-ADR-001" not in c.doc_code_map)

    # ---- architecture_rev 修订追溯 ----
    # 当前架构处于草案 rev 3，历史发布引用正式 rev 1 与 rev 2 → 通过
    files = valid_files()
    files["ued/architecture/system-architecture.md"] = system_arch(
        "| crm | 客户管理 | 维护客户档案 | 不管订单 |\n"
        "| oms | 订单履约 | 订单流转 | 不管客户 |",
        status="草案",
        rev=3,
        rev_rows=(
            "| 3 | 2026-01-10 | 初稿 | 讨论拆分风控 |\n"
            "| 2 | 2026-01-05 | 正式 | 补齐交互契约 |\n"
            "| 1 | 2026-01-01 | 正式 | 初始架构 |"
        ),
    )
    files["ued/releases/sys-v1.0.yaml"] = release_text(
        [{"subsystem": "crm", "product_version": "v1.0", "full_version": "v1.0.0"},
         {"subsystem": "oms", "product_version": "v2.5", "full_version": "v2.5.0"}],
        [{"name": "identity-provider", "product_version": "v4.0"}],
        arch_rev=1,
    )
    c = case("arch-rev-history-under-draft", files)
    check("草案状态下历史发布引用历史正式修订通过", no_errors(c))

    # 发布引用初稿 rev 3 → ERROR
    files["ued/releases/sys-v1.0.yaml"] = release_text(
        [{"subsystem": "crm", "product_version": "v1.0", "full_version": "v1.0.0"},
         {"subsystem": "oms", "product_version": "v2.5", "full_version": "v2.5.0"}],
        [{"name": "identity-provider", "product_version": "v4.0"}],
        arch_rev=3,
    )
    c = case("arch-rev-draft-ref", files)
    check("发布引用初稿架构修订报错", has(c, "发布清单 architecture_rev 引用非正式修订"))

    # 发布引用未来修订 rev 99 → ERROR
    files = valid_files()
    files["ued/releases/sys-v1.0.yaml"] = release_text(
        [{"subsystem": "crm", "product_version": "v1.0", "full_version": "v1.0.0"},
         {"subsystem": "oms", "product_version": "v2.5", "full_version": "v2.5.0"}],
        [{"name": "identity-provider", "product_version": "v4.0"}],
        arch_rev=99,
    )
    c = case("arch-rev-future", files)
    check("发布引用未来架构修订报错", has(c, "发布清单 architecture_rev 超前"))

    # 发布引用不存在的修订号（当前 rev 3，但修订记录只有 1 和 3，缺 2）
    files = valid_files()
    files["ued/architecture/system-architecture.md"] = system_arch(
        "| crm | 客户管理 | 维护客户档案 | 不管订单 |\n"
        "| oms | 订单履约 | 订单流转 | 不管客户 |",
        status="正式",
        rev=3,
        rev_rows=(
            "| 3 | 2026-01-10 | 正式 | 最新 |\n"
            "| 1 | 2026-01-01 | 正式 | 初始 |"
        ),
    )
    files["ued/releases/sys-v1.0.yaml"] = release_text(
        [{"subsystem": "crm", "product_version": "v1.0", "full_version": "v1.0.0"},
         {"subsystem": "oms", "product_version": "v2.5", "full_version": "v2.5.0"}],
        [{"name": "identity-provider", "product_version": "v4.0"}],
        arch_rev=2,
    )
    c = case("arch-rev-missing-in-table", files)
    check("发布引用修订记录中不存在的修订号报错",
          has(c, "发布清单 architecture_rev 不存在于修订记录"))

    # 历史发布缺 architecture_rev → WARNING（不阻断存量不可变清单）
    files = valid_files()
    files["ued/releases/sys-v1.0.yaml"] = release_text(
        [{"subsystem": "crm", "product_version": "v1.0", "full_version": "v1.0.0"},
         {"subsystem": "oms", "product_version": "v2.5", "full_version": "v2.5.0"}],
        [{"name": "identity-provider", "product_version": "v4.0"}],
        include_arch_rev=False,
    )
    c = case("arch-rev-legacy-missing", files)
    check("历史发布缺 architecture_rev 告警不报错",
          any(i.title == "发布清单缺 architecture_rev" and i.level == "WARNING"
              for i in c.issues) and no_errors(c))

    # ---- 依赖与发布组合既有回归 ----
    files = valid_files()
    files["ued/crm/baselines/v1.0.yaml"] = baseline(
        "v1.0", "v1.0.0",
        deps=[{"subsystem": "oms", "product_version": "v9.9"}])
    c = case("dep-version-missing", files)
    check("依赖目标基线不存在报错", has(c, "depends_on 目标基线不存在"))

    files = valid_files()
    files["ued/crm/baselines/v1.0.yaml"] = baseline(
        "v1.0", "v1.0.0",
        deps=[{"subsystem": "crm", "product_version": "v1.0"}])
    c = case("self-dependency", files)
    check("自依赖报错", has(c, "子系统自依赖"))

    files = valid_files()
    files["ued/README.md"] = files["ued/README.md"].replace(
        "| oms | 订单中心 | oms/ | OMS | 正式 |",
        "| oms | 订单中心 | oms/ | OMS | 初稿 |")
    c = case("dep-target-draft", files)
    check("依赖未启用子系统报错", has(c, "depends_on 目标未启用"))

    files = valid_files()
    files["ued/releases/sys-v1.0.yaml"] = release_text(
        [{"subsystem": "crm", "product_version": "v1.0", "full_version": "v1.0.0"}],
        [{"name": "identity-provider", "product_version": "v4.0"}])
    c = case("release-closure", files)
    check("发布依赖未闭合报错", has(c, "发布依赖未闭合"))

    files = valid_files(include_shared=True)
    files["ued/releases/sys-v1.0.yaml"] = release_text(
        [{"subsystem": "crm", "product_version": "v1.0", "full_version": "v1.0.0"},
         {"subsystem": "oms", "product_version": "v2.5", "full_version": "v2.5.0"}],
        [{"name": "identity-provider", "product_version": "v4.0"}])
    c = case("release-subset", files)
    check("发布可不覆盖全部正式子系统", no_errors(c))

    files = valid_files()
    files["ued/README.md"] = files["ued/README.md"].replace(
        "| oms | 订单中心 | oms/ | OMS | 正式 |",
        "| oms | 订单中心 | oms/ | OMS | 初稿 |")
    c = case("release-draft-member", files)
    check("发布包含初稿子系统报错", has(c, "发布包含初稿子系统"))

    files = valid_files(include_shared=True)
    files["ued/README.md"] = files["ued/README.md"].replace(
        "| shared-lib | 公共库 | shared-lib/ | LIB | 正式 |",
        "| shared-lib | 公共库 | shared-lib/ | LIB | 废弃 |")
    c = case("release-deprecated-member", files)
    check("发布含废弃子系统告警",
          any(i.title == "发布含已废弃子系统" and i.level == "WARNING"
              for i in c.issues))
    check("历史清单含废弃不报错", no_errors(c))

    files = valid_files()
    files["ued/oms/baselines/v2.5.yaml"] = baseline(
        "v2.5", "v2.5.0", deps=[],
        exts=[{"name": "identity-provider", "product_version": "v4.1"}])
    c = case("external-conflict", files)
    check("发布外部依赖版本冲突报错", has(c, "发布外部依赖版本冲突"))

    files = valid_files()
    files["ued/releases/sys-v1.0.yaml"] = release_text(
        [{"subsystem": "crm", "product_version": "v1.0", "full_version": "v1.0.9"},
         {"subsystem": "oms", "product_version": "v2.5", "full_version": "v2.5.0"}],
        [{"name": "identity-provider", "product_version": "v4.0"}])
    c = case("release-tip", files)
    check("发布 tip 不在 patch_log 报错", has(c, "发布项 tip 不在 patch_log"))

    # ---- 跨子系统编码与术语既有回归 ----
    files = valid_files()
    files["ued/crm/L2-001-req.md"] += "\n# FR-001-重复编码\n\n- **细项状态**：正式\n"
    files["ued/oms/L2-001-req.md"] += "\n# FR-001-重复编码\n\n- **细项状态**：正式\n"
    c = case("cross-scope-duplicate", files)
    check("跨子系统重复编码报错", has(c, "跨子系统重复定义编码"))

    files = valid_files()
    files["ued/crm/L2-001-req.md"] += "\n# OMS-CMP-009-越界定义\n\n- **细项状态**：正式\n"
    c = case("foreign-prefix", files)
    check("定义他子系统前缀报错", has(c, "定义了他子系统前缀"))

    files = valid_files()
    files["ued/oms/L2-001-req.md"] += (
        "\n跨子系统引用 `CRM-CMP-001` 与 `CRM-L2-001`。\n")
    c = case("cross-scope-ref-ok", files)
    check("跨子系统全量细项引用可解析",
          not any(i.title == "跨子系统引用悬空" and "CRM-CMP-001" in i.detail
                  for i in c.issues))
    check("跨子系统全量文档引用可解析",
          not any(i.title == "跨子系统引用悬空" and "CRM-L2-001" in i.detail
                  for i in c.issues))

    files = valid_files()
    files["ued/crm/L2-001-req.md"] += "\n跨子系统引用 `OMS-FR-999`。\n"
    c = case("cross-scope-dangling", files)
    check("跨子系统引用悬空告警",
          any(i.title == "跨子系统引用悬空" and i.level == "WARNING"
              and "OMS-FR-999" in i.detail for i in c.issues))

    files = valid_files()
    files["ued/crm/L2-001-req.md"] += (
        "\n- **依赖**：[OMS-FR-999（不存在）](../oms/L2-001-req.md#oms-fr-999)\n")
    c = case("cross-scope-dep-dangling", files)
    check("跨子系统依赖悬空报错",
          any(i.title == "跨子系统依赖悬空" and i.level == "ERROR"
              and "OMS-FR-999" in i.detail for i in c.issues))
    check("依赖悬空不降级为普通引用告警",
          not any(i.title == "跨子系统引用悬空" and "OMS-FR-999" in i.detail
                  for i in c.issues))

    files = valid_files()
    files["ued/crm/L2-001-req.md"] += (
        "\n- **依赖**（同时有效）：[XYZ-FR-001（未知前缀）](../xyz/L2-001-req.md#xyz-fr-001)\n")
    c = case("cross-scope-dep-unknown-prefix", files)
    check("依赖指向未登记前缀报错",
          any(i.title == "依赖指向未登记前缀" and i.level == "ERROR"
              and "XYZ-FR-001" in i.detail for i in c.issues))

    files = valid_files()
    files["ued/crm/L2-001-req.md"] += (
        "\n- **依赖**：[CRM-CMP-001（核心引擎组件）](./L3-001-arch.md#crm-cmp-001)\n")
    c = case("cross-scope-dep-ok", files)
    check("同子系统依赖不报跨作用域",
          not any(i.title in ("跨子系统依赖悬空", "依赖指向未登记前缀")
                  for i in c.issues))

    files = valid_files()
    files["ued/oms/L2-001-req.md"] += (
        "\n# OMS-RUL-001-跨域规则\n\n- **细项状态**：正式\n")
    files["ued/crm/L2-001-req.md"] += (
        "\n见 [RUL-001（跨域规则）](../oms/L2-001-req.md#oms-rul-001)。\n")
    c = case("cross-scope-shorthand", files)
    check("跨作用域简写报错",
          any(i.title == "跨作用域简写" and i.level == "ERROR"
              and "RUL-001" in i.detail for i in c.issues))

    files = valid_files()
    files["ued/crm/L2-001-req.md"] += (
        "\n见 [CMP-001（核心引擎组件）](./L3-001-arch.md#crm-cmp-001)。\n")
    c = case("local-shorthand", files)
    check("本子系统简写不报跨作用域",
          not any(i.title == "跨作用域简写" for i in c.issues))

    files = valid_files()
    files["ued/crm/L2-001-req.md"] += "\n# FR-002-无前缀定义\n\n- **细项状态**：正式\n"
    c = case("definition-no-prefix", files)
    check("子系统定义缺前缀报错",
          any(i.title == "定义前缀与子系统不符" and i.level == "ERROR"
              and "FR-002" in i.detail for i in c.issues))

    files = valid_files()
    files["ued/crm/L2-001-req.md"] += "\n# XYZ-FR-003-未知前缀\n\n- **细项状态**：正式\n"
    c = case("definition-unknown-prefix", files)
    check("子系统定义未知前缀报错",
          any(i.title == "定义前缀与子系统不符" and "XYZ-FR-003" in i.detail
              for i in c.issues))

    files = valid_files()
    files["ued/oms/L2-001-req.md"] += (
        "\n# CRM-CMP-009-越界定义\n\n- **细项状态**：正式\n\n"
        "引用 `CRM-CMP-009`。\n")
    c = case("foreign-prefix-ref", files)
    check("跨子系统引用归属不符报错",
          any(i.title == "跨子系统引用前缀与定义不符" and i.level == "ERROR"
              and "CRM-CMP-009" in i.detail for i in c.issues))

    files = valid_files()
    files["ued/crm/glossary.md"] = "# 局部术语表\n"
    c = case("subsidiary-glossary", files)
    check("子系统自建术语表报错", has(c, "子系统不得自建术语表"))

    files = valid_files()
    files["ued/crm/L2-001-req.md"] += (
        "\n## 术语和概念\n\n### 客户\n\n"
        "- **中文名称**：客户\n- **英文名称**：Customer\n\n"
        "**定义**：购买方。\n")
    c = case("term-unregistered", files)
    check("术语未登记全局表报错", has(c, "术语未登记到全局表"))

    files = valid_files()
    files["ued/README.md"] = files["ued/README.md"].replace(
        "| sys-v1.0 | 2026-01-02 | 首个产品集发布 | [清单](releases/sys-v1.0.yaml) |",
        "")
    c = case("release-index-missing", files)
    check("发布未登记索引告警", has(c, "发布未登记索引"))

    # ---- 模板哨兵 smoke ----
    tpl_dir = SKILL / "assets" / "templates"
    for path in sorted(tpl_dir.glob("*.md")):
        if path.name == "index.md":
            continue
        text = path.read_text(encoding="utf-8")
        begin = text.count("TEMPLATE:BEGIN")
        end = text.count("TEMPLATE:END")
        h1 = sum(1 for line in text.splitlines() if re_match_h1(line))
        check(f"模板哨兵成对：{path.name}", begin == end == 1)
        check(f"模板 H1 ≤ 1：{path.name}", h1 <= 1)

    release_tpl = tpl_dir / "system-release.yaml"
    release_text_raw = release_tpl.read_text(encoding="utf-8")
    check("发布模板哨兵成对",
          release_text_raw.count("TEMPLATE:BEGIN") == 1
          and release_text_raw.count("TEMPLATE:END") == 1)
    body_match = re.search(
        r"#\s*TEMPLATE:BEGIN[^\n]*\n(.*?)\n#\s*TEMPLATE:END",
        release_text_raw, re.S)
    body = body_match.group(1) if body_match else ""
    body = "\n".join(line for line in body.splitlines()
                     if not line.startswith("#"))
    parsed = yaml.safe_load(body)
    check("发布模板 YAML 可解析且含 architecture_rev",
          isinstance(parsed, dict)
          and parsed.get("release") == "sys-v1.0"
          and parsed.get("architecture_rev") == 1)

    c = case("member-commands", valid_files())
    cmds = c.member_commands()
    check("成员命令数", len(cmds) == 2)
    check("成员命令含 --glossary", all("--glossary" in x for x in cmds))

    c = case("plain-design-doc-names", valid_files())
    check("无前缀设计文档名识别", not has(c, "子系统无设计文档"))

    files = valid_files()
    for old, new in (
            ("ued/crm/L2-001-req.md", "ued/crm/CRM-L2-001-req.md"),
            ("ued/crm/L3-001-arch.md", "ued/crm/CRM-L3-001-arch.md")):
        files[new] = files.pop(old)
    c = case("prefixed-design-doc-names", files)
    check("带前缀设计文档名识别", not has(c, "子系统无设计文档"))

    # ---- 规范版本目标（系统根 README） ----
    inst = installed_spec_version()
    check("已装规范版本可读", bool(inst))
    c = case("spec-target-ok", {"ued/README.md": readme("\n".join([
        "| crm | 客户关系 | crm/ | CRM | 正式 |",
        "| oms | 订单中心 | oms/ | OMS | 正式 |",
    ]), "| sys-v1.0 | 2026-01-02 | 首个产品集发布 | [清单](releases/sys-v1.0.yaml) |")})
    check("规范版本目标与已装一致不告警",
          not any("规范版本目标" in i.title for i in c.issues))
    for label, target, want in (
            ("缺规范版本目标", "", "系统 README 缺规范版本目标"),
            ("规范版本目标格式错误", "two", "系统 README 规范版本目标格式错误"),
            ("规范版本目标与已装不一致", "1.0", "系统 README 规范版本目标与已装不一致")):
        rows = "\n".join([
            "| crm | 客户关系 | crm/ | CRM | 正式 |",
            "| oms | 订单中心 | oms/ | OMS | 正式 |",
        ])
        text = readme(rows, "| sys-v1.0 | 2026-01-02 | 首个产品集发布 | [清单](releases/sys-v1.0.yaml) |",
                      spec_target=target if target else "")
        c = case("spec-target-" + label, {"ued/README.md": text})
        check(f"{label}告警", any(i.title == want and i.level == "WARNING" for i in c.issues))

    # ---- 系统架构 / SYS-ADR 逐篇规范版本 ----
    ARCH = "ued/architecture/system-architecture.md"
    ADR = "ued/architecture/SYS-ADR-001-split-crm-oms.md"
    row = f"| 规范版本 | {inst} |\n"

    def titles(c, level=None):
        return {i.title for i in c.issues if level is None or i.level == level}

    files = valid_files()
    check("夹具含逐篇规范版本行", row in files[ARCH] and row in files[ADR])
    c = case("arch-spec-ok", files)
    check("系统文档规范版本对齐无相关问题",
          not any("系统文档" in t and "规范版本" in t for t in titles(c)))

    for label, doc in (("系统架构", ARCH), ("SYS-ADR", ADR)):
        files = valid_files()
        files[doc] = files[doc].replace(row, "")
        c = case(f"{label}-spec-missing", files)
        check(f"{label}缺规范版本告警", "系统文档缺规范版本" in titles(c, "WARNING"))
        check(f"{label}缺规范版本仅一条且指向该文档",
              sum(1 for i in c.issues if i.title == "系统文档缺规范版本") == 1)

        files = valid_files()
        files[doc] = files[doc].replace(row, "| 规范版本 | 99.0 |\n")
        c = case(f"{label}-spec-ahead", files)
        check(f"{label}规范版本超前报错", "系统文档规范版本超前" in titles(c, "ERROR"))

        files = valid_files()
        files[doc] = files[doc].replace(row, "| 规范版本 | two |\n")
        c = case(f"{label}-spec-badfmt", files)
        check(f"{label}规范版本格式错误告警", "系统文档规范版本格式错误" in titles(c, "WARNING"))

        files = valid_files()
        files[doc] = files[doc].replace(row, "| 规范版本 | 1.0 |\n")
        c = case(f"{label}-spec-lag", files)
        check(f"{label}低于根目标列为待迁移", "系统文档待迁移规范" in titles(c, "WARNING"))

    # 10.x 式数值比较：2.10 高于 2.9，不得按字符串比较
    files = valid_files()
    files[ARCH] = files[ARCH].replace(row, "| 规范版本 | 1.10 |\n")
    files["ued/README.md"] = files["ued/README.md"].replace(
        f"| 规范版本目标 | {inst} |", "| 规范版本目标 | 1.9 |")
    c = case("arch-spec-numeric", files)
    check("数值比较：1.10 不低于目标 1.9", "系统文档待迁移规范" not in titles(c))

    # 根 README 缺目标时不判待迁移（只有缺目标告警）
    files = valid_files()
    files[ARCH] = files[ARCH].replace(row, "| 规范版本 | 1.0 |\n")
    files["ued/README.md"] = files["ued/README.md"].replace(f"| 规范版本目标 | {inst} |\n", "")
    c = case("arch-spec-no-target", files)
    check("根目标缺失时不判待迁移",
          "系统文档待迁移规范" not in titles(c) and "系统 README 缺规范版本目标" in titles(c))

    # 发布清单与注册表不逐篇记录：release yaml 无 规范版本 也不得报
    c = case("release-no-spec", valid_files())
    check("发布清单无规范版本不告警",
          not any("发布" in t and "规范版本" in t for t in titles(c)))

    print(f"\n{PASS} passed, {FAIL} failed")
    return 1 if FAIL else 0


def re_match_h1(line: str) -> bool:
    return bool(re.match(r"^\s{0,3}#\s+", line))


if __name__ == "__main__":
    sys.exit(main())
