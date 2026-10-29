#!/usr/bin/env python3
"""system-design-doc 夹具测试。

每个用例在临时目录中构造一个 ued/ 树，运行 check_system.py 的检查方法，
断言预期问题标题出现 / 不出现。只覆盖系统级规则；文档内部规则由
design-doc 的测试覆盖。
"""
from __future__ import annotations

import re
import sys
import tempfile
from pathlib import Path
from typing import Dict

import yaml

ROOT = Path(__file__).resolve().parent
SKILL = ROOT.parents[1]
sys.path.insert(0, str(SKILL / "scripts"))

from check_system import SystemChecker  # noqa: E402

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
           glossary: bool = True) -> str:
    structure_block = (
        "## 当前结构\n\n本仓库为系统 + 子系统结构；系统级与子系统级职责分离。\n\n"
        if structure else ""
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
{extra_meta}
{structure_block}## 子系统注册表

| subsystem_key | 子系统名称 | 目录 | 编码前缀 | 角色文档 | 状态 |
|---------------|------------|------|----------|----------|------|
{rows}

{release_block}{glossary_block}## 子系统导航

| 子系统 | 入口 | 说明 |
|--------|------|------|
| CRM | [crm/README.md](crm/README.md) | 客户 |
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


def role_doc(prefix: str, body: str = "角色、边界与交互") -> str:
    code = f"{prefix}-CMP-001" if prefix else "CMP-001"
    return f"""# {code}-子系统职责

- **细项状态**：正式
- **修订版本号**：1
- **创建日期**：2026-01-01
- **最后修订日期**：2026-01-01
- **满足需求**：无

## 职责

{body}
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


def release_text(subs, exts=None) -> str:
    data = {
        "release": "sys-v1.0",
        "created": "2026-01-02",
        "note": "首个产品集发布",
        "subsystems": subs,
        "external_deps": exts if exts is not None else [],
    }
    return yaml.safe_dump(data, allow_unicode=True, sort_keys=False)


def valid_files(include_shared: bool = False) -> Dict[str, str]:
    rows = [
        "| crm | 客户关系 | crm/ | CRM | CRM-CMP-001 | 正式 |",
        "| oms | 订单中心 | oms/ | OMS | OMS-CMP-001 | 正式 |",
    ]
    subs = [
        {"subsystem": "crm", "product_version": "v1.0", "full_version": "v1.0.0"},
        {"subsystem": "oms", "product_version": "v2.5", "full_version": "v2.5.0"},
    ]
    if include_shared:
        rows.append("| shared-lib | 公共库 | shared-lib/ | LIB | LIB-CMP-001 | 正式 |")
        subs.append({"subsystem": "shared-lib", "product_version": "v1.0",
                     "full_version": "v1.0.0"})
    files = {
        "ued/README.md": readme(
            "\n".join(rows),
            "| sys-v1.0 | 2026-01-02 | 首个产品集发布 | [清单](releases/sys-v1.0.yaml) |",
        ),
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
        "ued/crm/L3-001-arch.md": role_doc("CRM"),
        "ued/crm/baselines/v1.0.yaml": baseline(
            "v1.0", "v1.0.0",
            deps=[{"subsystem": "oms", "product_version": "v2.5"}],
            exts=[{"name": "identity-provider", "product_version": "v4.0"}]),
        "ued/oms/README.md": sub_readme("订单中心", "OMS", "v2.5"),
        "ued/oms/L2-001-req.md": l2_doc("OMS"),
        "ued/oms/L3-001-arch.md": role_doc("OMS"),
        "ued/oms/baselines/v2.5.yaml": baseline(
            "v2.5", "v2.5.0", deps=[],
            exts=[{"name": "identity-provider", "product_version": "v4.0"}]),
    }
    if include_shared:
        files.update({
            "ued/shared-lib/README.md": sub_readme("公共库", "LIB", "v1.0"),
            "ued/shared-lib/L2-001-req.md": l2_doc("LIB"),
            "ued/shared-lib/L3-001-arch.md": role_doc("LIB"),
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
    print("system-design-doc fixtures")

    c = case("valid", valid_files())
    check("有效系统无 ERROR", no_errors(c))
    check("有效系统识别为系统", c.is_system)

    c = case("shared-as-subsystem", valid_files(include_shared=True))
    check("共享库作为普通子系统通过", no_errors(c))
    check("共享库被识别", "shared-lib" in [s.key for s in c.subsystems])

    files = valid_files()
    files["ued/README.md"] = readme(
        "| crm | 客户关系 | crm/ | CRM | CRM-CMP-001 | 正式 |",
        "| sys-v1.0 | 2026-01-02 | 首个产品集发布 | [清单](releases/sys-v1.0.yaml) |",
    )
    c = case("missing-ledger-row", files)
    check("未登记 oms 目录报错", has(c, "未登记子系统目录"))

    files = valid_files()
    files["ued/README.md"] = readme(
        "| crm | 客户关系 | crm/ | CRM | CRM-CMP-001 | 正式 |\n"
        "| oms | 订单中心 | oms/ | OMS | OMS-CMP-001 | 正式 |",
        release_rows="",)
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
| project_code | SYS |
| scope | 单系统 |
| author | tester |
| last_updated | 2026-01-01 |
| 产品版本 | v1.0 |

## 文档索引

| 文档编码 | 文档标题 | 状态 |
|----------|----------|------|
| L2-001 | 需求 | 正式 |
""",
        "ued/L2-001-req.md": l2_doc("SYS"),
        "ued/baselines/v1.0.yaml": baseline("v1.0", "v1.0.0"),
    }
    c = case("single-system", single)
    check("单系统不误报 ERROR", no_errors(c))
    check("单系统给出指引", has(c, "非系统结构"))

    files = valid_files()
    files["ued/README.md"] = files["ued/README.md"].replace(
        "| crm | 客户关系 | crm/ | CRM | CRM-CMP-001 | 正式 |\n"
        "| oms | 订单中心 | oms/ | OMS | OMS-CMP-001 | 正式 |",
        "| crm | 客户关系 | crm/ | CRM | CRM-CMP-001 | 正式 |\n"
        "| crm | 客户关系副本 | oms/ | OMS | OMS-CMP-001 | 正式 |")
    c = case("duplicate-key", files)
    check("subsystem_key 重复报错", has(c, "subsystem_key 重复"))

    files = valid_files()
    files["ued/README.md"] = files["ued/README.md"].replace(
        "| oms | 订单中心 | oms/ | OMS | OMS-CMP-001 | 正式 |",
        "| oms | 订单中心 | crm/ | OMS | OMS-CMP-001 | 正式 |")
    c = case("duplicate-dir", files)
    check("子系统目录重复报错", has(c, "子系统目录重复"))

    files = valid_files()
    files["ued/README.md"] = files["ued/README.md"].replace(
        "| oms | 订单中心 | oms/ | OMS | OMS-CMP-001 | 正式 |",
        "| oms | 订单中心 | oms/ | CRM | OMS-CMP-001 | 正式 |")
    c = case("duplicate-prefix", files)
    check("编码前缀重复报错", has(c, "编码前缀重复"))

    files = valid_files()
    files["ued/README.md"] = files["ued/README.md"].replace(
        "| oms | 订单中心 | oms/ | OMS | OMS-CMP-001 | 正式 |",
        "| oms | 订单中心 | nope/ | OMS | OMS-CMP-001 | 正式 |")
    c = case("missing-dir", files)
    check("子系统目录不存在报错", has(c, "子系统目录不存在"))

    files = valid_files()
    files["ued/README.md"] = files["ued/README.md"].replace(
        "| oms | 订单中心 | oms/ | OMS | OMS-CMP-001 | 正式 |",
        "| oms | 订单中心 | oms/ | OMS | OMS-CMP-001 | 草案 |")
    c = case("invalid-status", files)
    check("草案状态报错", has(c, "子系统状态非法"))

    files = valid_files()
    files["ued/README.md"] = files["ued/README.md"].replace(
        "| crm | 客户关系 | crm/ | CRM | CRM-CMP-001 | 正式 |",
        "| crm | 客户关系 | crm/ | CRM | | 正式 |")
    c = case("active-no-role", files)
    check("正式子系统缺角色文档报错", has(c, "正式子系统缺角色文档"))

    files = valid_files()
    del files["ued/crm/baselines/v1.0.yaml"]
    c = case("active-no-baseline", files)
    check("正式子系统缺基线报错", has(c, "正式子系统缺基线"))

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
        "| oms | 订单中心 | oms/ | OMS | OMS-CMP-001 | 正式 |",
        "| oms | 订单中心 | oms/ | OMS | OMS-CMP-001 | 初稿 |")
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
        "| oms | 订单中心 | oms/ | OMS | OMS-CMP-001 | 正式 |",
        "| oms | 订单中心 | oms/ | OMS | OMS-CMP-001 | 初稿 |")
    c = case("release-draft-member", files)
    check("发布包含初稿子系统报错", has(c, "发布包含初稿子系统"))

    files = valid_files(include_shared=True)
    files["ued/README.md"] = files["ued/README.md"].replace(
        "| shared-lib | 公共库 | shared-lib/ | LIB | LIB-CMP-001 | 正式 |",
        "| shared-lib | 公共库 | shared-lib/ | LIB | LIB-CMP-001 | 废弃 |")
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
        "\n- **依赖**：[CRM-CMP-001（客户关系）](./L3-001-arch.md#crm-cmp-001)\n")
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
        "\n见 [CMP-001（客户关系）](./L3-001-arch.md#crm-cmp-001)。\n")
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

    # 模板哨兵 smoke
    tpl_dir = SKILL / "assets" / "templates"
    for path in sorted(tpl_dir.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        begin = text.count("TEMPLATE:BEGIN")
        end = text.count("TEMPLATE:END")
        h1 = sum(1 for line in text.splitlines()
                 if re_match_h1(line))
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
    check("发布模板 YAML 可解析",
          isinstance(parsed, dict) and parsed.get("release") == "sys-v1.0")

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

    print(f"\n{PASS} passed, {FAIL} failed")
    return 1 if FAIL else 0


def re_match_h1(line: str) -> bool:
    import re
    return bool(re.match(r"^\s{0,3}#\s+", line))


if __name__ == "__main__":
    sys.exit(main())
