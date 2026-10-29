#!/usr/bin/env python3
"""`check_docs.py` 的规则回归集跑台。

`fixtures/` 下每条夹具是一份最小设计文档（多为 L2，亦含 EVAL 等文档型），刻意触发
（或刻意不触发）某一条校验规则。`glossary_fixtures/` 是自成一体的 `ued/` 场景目录，
验证术语表 / 术语块规则；`skill_link_fixtures/` 验证技能包内部 `#锚点` 可达性。
跑台末尾对本包执行 `--check-templates` 冒烟，并跑哨兵内写作约束 / 技能包路径的正反例。改动 `check_docs.py` 后跑一遍，可确认
既有规则没有静默退化。

跑台只断言**目标问题名**（见 `EXPECT`），忽略夹具因极简结构必然产生的结构性
噪声（见 `NOISE`）——夹具只为验证单条规则，不追求自身是一份合规文档。

用法：
    python3 scripts/tests/run_fixtures.py       # 全量
    python3 scripts/tests/run_fixtures.py -v    # 附带每条夹具的命中详情

测试环境依赖（仅本跑台，非正式规范）：须能 `import yaml`（PyYAML），否则含基线
成员状态等夹具会被检查器跳过而假漏报；缺依赖时本脚本以环境错误退出。
"""
import contextlib
import io
import re
import sys
import subprocess
from collections import defaultdict
from pathlib import Path


def require_test_deps() -> None:
    """跑台前置：基线类夹具依赖 PyYAML；缺则不得伪装成规则回归失败。"""
    try:
        import yaml  # noqa: F401
    except ImportError:
        print(
            "ERROR: 测试环境缺少 PyYAML（`pip install pyyaml`）。\n"
            "基线相关夹具在无 yaml 时会被 check_docs 跳过，不能当作规则漏报。\n"
            "此依赖仅约束 scripts/tests/run_fixtures.py，不改变正式检查规则。",
            file=sys.stderr,
        )
        sys.exit(2)

ROOT = Path(__file__).resolve().parent
FIXTURES = ROOT / "fixtures"
LINK_FIXTURES = ROOT / "skill_link_fixtures"
CHECKER = ROOT.parent / "check_docs.py"

SECTION = re.compile(r"^###\s+(?:ERROR|WARNING|INFO)")
ITEM = re.compile(r"^\d+\.\s+(.+?)\s*$")
# 夹具名 MAY 带项目编码前缀（如 `W3T-L2-929-prefix-digit.md`），前缀字符集与
# check_docs.py 的 PROJECT_PREFIX 同口径。
# 夹具名：层文档 L{n}-…，或文档型 ADR/EVAL/REF-…；MAY 带项目编码前缀。
FIXTURE = re.compile(
    r"((?:[A-Z][A-Z0-9]{1,4}-)?(?:L\d+|ADR|EVAL|REF)-\d+-[a-z0-9\-]+)\.md"
)
LINK_FILE = re.compile(r"([^/\\]+\.md):")

# 技能包锚点夹具 → 期望命中的目标问题名（空集 = 正例，MUST 零命中）。
LINK_EXPECT = {
    "ok-link.md": set(),
    "target.md": set(),
    "broken-link.md": {"技能包锚点不可达", "技能包链目标不存在"},
}

# 夹具极简（无变更记录表、无清单表、无完整章节、编码从 9xx 起跳）必然触发的
# 结构性问题，与本回归集要验证的规则无关，一律不计入断言。
NOISE = {
    "缺少变更记录", "缺少细项编码清单", "缺少必需章节", "引用悬空",
    "细项未登记入清单", "编码序列存在缺口", "细项待定稿", "文档待定稿",
    "草案待定稿",
}

# 夹具 → 期望命中的目标问题名（空集 = 该规则的正例，MUST 零命中）。
# 夹具名即规则语义，改检查器的问题名时 MUST 同步此表。
EXPECT = {
    # —— 治理段（属性行组首四行） ——
    "L2-902-no-status":           {"定义块缺细项状态属性行"},
    "L2-903-status-not-first":    {"细项状态未位于属性行组首行"},
    "L2-904-gov-order":           {"治理段顺序错乱"},
    "L2-905-gov-missing":         {"治理段缺行"},
    "L2-906-gov-badval":          {"修订版本号取值非法", "创建日期取值非法",
                                   "最后修订日期取值非法"},
    # —— 追溯段（属性行组末尾，出处 → 来源 → 依赖） ——
    "L2-907-trace-mid":           {"追溯段未位于属性行组末尾"},
    "L2-908-trace-order":         {"追溯段顺序错乱"},
    "L2-909-src-nolink":          {"来源值缺链接"},
    "L2-910-origin-link":         {"出处值含链接"},
    # `来源` MAY 多行（每行一个来源对象），同名多行 MUST NOT 被判为顺序错乱
    "L2-928-trace-multi-source":  set(),
    "L2-934-dep-ok-multi":        set(),
    "L2-935-dep-before-src":      {"追溯段顺序错乱"},
    "L2-936-dep-nolink":          {"依赖值缺链接"},
    "L2-937-dep-on-chugao":       {"依赖指向初稿"},
    "L2-938-dep-same-source":     {"依赖与来源指向同一对象"},
    "L2-939-nfr-cat-ok":          set(),
    "L2-940-nfr-cat-bad":         {"类别取值非法"},
    "L2-941-formal-no-verify":    {"正式需求缺验证方式"},
    "L2-942-formal-tbd":          {"正式文档含待定"},
    "L2-943-chugao-tbd-ok":       set(),
    # —— 层级门控（解冻自顶向下、定稿与整份废止自底向上） ——
    "L2-915-gate-draft-item":     {"细项草案而文档正式", "文档定稿前置未满足"},
    "L2-916-gate-new-item":       {"文档定稿前置未满足"},
    "L2-917-gate-ok-draftdoc":    set(),
    # 整份废弃：文档 `废弃` 而仍有未废弃细项 → ERROR；全部已废弃或无细项 → 不报该问题
    "L2-944-docvoid-live-item":   {"废弃文档仍含未废弃细项"},
    "L2-945-docvoid-all-void-ok": set(),
    "L2-946-docvoid-empty-ok":    set(),
    # 依据方向：`正式` / `草案` 细项 MUST NOT 依据 `初稿` 细项；`出处` / `来源` / `落实记录` 豁免，`依赖` 不豁免
    # （932 里 `PLN 落实记录 → FR` 与 `FR 来源 → PLN` 互相回指，若同受约束则两项谁都定不了稿；
    #  933 锁死豁免的**边界**——追溯段固定在属性行组末尾、正文段在其后，豁免若按「段」放行
    #  会把正文段整段吞掉，使带 `来源` 的常态定义块完全不受检）
    "L2-931-dep-on-chugao":       {"正式或草案细项依据初稿细项"},
    "L2-932-dep-trace-exempt":    set(),
    "L2-933-dep-prose-after-trace": {"正式或草案细项依据初稿细项"},
    # —— 修订版本号 / 最后修订日期 的不变式 ——
    "L2-918-rev-draft-one":       {"修订版本号与状态不一致"},
    "L2-919-rev-chugao-two":      {"修订版本号与状态不一致"},
    "L2-920-date-late":           {"最后修订日期晚于变更记录"},
    "L2-921-date-ok":             set(),
    # —— PLN：落实情况与细项状态正交 ——
    "L2-911-pln-landed-norecord": {"已落实但无落实记录"},
    "L2-912-pln-nofield":         {"PLN 缺落实情况"},
    "L2-913-pln-badval":          {"PLN 落实情况取值非法"},
    "L2-914-pln-ok-landed":       set(),
    # —— 废弃登记字段 `替代方案` 的值形态（链接 / 「无」） ——
    "L2-922-dep-bare-code":       {"替代方案值缺链接"},
    "L2-923-dep-link-ok":         set(),
    # —— 初稿期作废：与 `正式→废弃` 走同一条流程，编号原地保留、`修订版本号` 保持 1 ——
    # 作废项状态为 `废弃`，因此所在文档仍可定稿（不触发「文档定稿前置未满足」）
    "L2-930-chugao-void-ok":      set(),
    # —— 属性名白名单（《属性行定义集（封闭）》）——
    # 反例覆盖三类野属性名：散文槽位、规范关键字 / 写作提要词、跨类型码误用
    "L2-926-attr-wild":           {"属性名未在定义集内"},
    "L2-927-attr-prose-ok":       set(),
    # —— 项目编码前缀（字符集见 coding-system.md ·《项目编码规则》）——
    # 带前缀时：文档编码的层级段 MUST 取自序号前一段，细项编码 MUST 切为
    # 项目编码 + 类型码（前缀含数字时不得被当成类型码的一部分）
    "W3T-L2-929-prefix-digit":    set(),
    # —— 全合规正例：仅余「目标细项未回指 PLN」，因夹具内 FR 刻意不回指 ——
    "L2-901-ok-full":             {"落实目标未回指 PLN"},
    # —— 文档修订号 / 发版谱系 ——
    "L2-947-legacy-docver":       {"文档元信息仍用版本字段"},
    "L2-948-lineage-chugao":      {"初稿带发版谱系"},
    "L2-949-lineage-exit":        {"退出版本须已废弃"},
    "L2-950-unfreeze-noinc":      {"解冻未递增修订号"},
    "L2-951-void-lineage":        {"初稿期作废带发版谱系"},
    # —— 产品基线 baselines/vX.Y.yaml ——
    "L2-952-baseline-ok":         set(),
    "L2-953-baseline-informal":   {"产品基线成员非正式"},
    # —— 本文引用钉住表 / 简写解析 ——
    # 同一作用域内简写（可跨文档）不报；歧义与缺钉住行必报
    "W3T-L2-959-prefix-target":   set(),
    "L2-960-pin-missing":         {"缺本文引用钉住行"},
    "L2-961-pin-ok":              set(),
    "L2-962-shorthand-cross":     set(),
    "L2-980-shorthand-ambiguous": {"简写编码歧义"},
    # 序号位宽：2–4 位均可解析（写入默认三位补零，超过 999 自然四位）
    "L2-963-width-ok":            set(),
    # —— 废弃类别 / 原因与废弃后受控复活 ——
    "L2-964-void-bad-category":   {"废弃类别非法"},
    "L2-965-void-empty-reason":   {"废弃原因为空"},
    "L2-966-revive-ok":           set(),
    "L2-967-revive-banner":       {"细项废弃标记与状态不一致"},
    "L2-968-revive-early":        {"复活时间早于废弃时间"},
    "L2-969-doc-revive-banner":   {"复活后仍保留废弃横幅"},
    "L2-970-doc-revive-ok":       set(),
    # —— 维护性变更：`变更记录` 维护行 ——
    # 维护行沿用当前修订号（全角括号、无空格），位于同号语义行之上；说明为一个或
    # 多个批次片段（`；` 连接、最新在前、末尾一次 `；语义不变`）；同号后续维护
    # 追加片段而非新起一行（存量多行保留、不追溯）
    "L2-971-maint-row-ok":        set(),
    "L2-972-maint-row-misplaced": {"维护行未置于同号语义行之上"},
    "L2-973-maint-row-ghost":     {"维护行引用的修订号不存在"},
    "L2-974-maint-row-badmark":   {"维护行标记格式错误"},
    "L2-975-maint-row-desc":      {"维护行说明格式错误"},
    # 旧称不再有专用属性：写进定义块即按自造属性名报错
    "L2-976-oldname-field":       {"属性名未在定义集内"},
    # 同号多批次合并为一行（最新在前）；片段乱序必报
    "L2-981-maint-merge-ok":      set(),
    "L2-979-maint-order-bad":     {"维护片段未按批次日期倒序"},
    # 存量同号多行保留不迁移，不新增告警
    "L2-982-maint-legacy-dup-ok": set(),
    # 语义行里的「解冻」指向细项 / 上游文档时，不触发本文档递增判定
    "L2-983-item-unfreeze-ok":    set(),
    "L2-984-upstream-unfreeze-ok": set(),
    # —— EVAL 文档级基线评估报告 ——
    "EVAL-901-ok":                set(),
    "EVAL-902-no-scope":          {"EVAL缺少必需章节"},
    "EVAL-903-bad-meta":          {"EVAL对照版本格式错误", "EVAL评估日期格式错误",
                                   "EVAL评估类型非法"},
    "EVAL-904-preamble-leak":     {"疑似模板前置泄漏"},
}

# 术语表夹具是自成一体的 `ued/` 场景目录（各含 README、可选 glossary.md 与
# L2 文档）。它们不能放进 `fixtures/`：只要目录里出现 glossary.md，检查器就会
# 对**所有**夹具启用术语校验，污染既有断言。
GLOSSARY_FIXTURES = ROOT / "glossary_fixtures"

GLOSSARY_TITLES = {
    "术语章节重复", "术语章节层级错误", "术语章节标题待迁移", "术语章节位置靠后",
    "术语章节使用表格", "术语定义缺失", "术语标题与名称不一致", "术语重复定义",
    "缺少全局术语表", "术语表位置非法", "术语表元信息缺失", "术语表修订号非法",
    "术语表日期格式错误", "术语表含编码或状态字段", "术语表缺变更记录",
    "术语表缺少固定四列表", "术语表列不合规", "术语表字段缺失", "术语名称重复",
    "术语定义位置非法", "术语定义位置错误", "术语定义未找到", "术语未登记",
    "所用术语含链接或编码", "所用术语无法解析", "所用术语重复本文定义",
    "README未登记术语表", "文档修订号与变更记录不一致",
}

# 场景目录名 → 期望命中的问题名（空集 = 正例，MUST 零命中）。
GLOSSARY_EXPECT = {
    "ok":                        set(),
    "ok-empty":                  set(),
    "duplicate-definition":      {"术语重复定义"},
    "duplicate-name":            {"术语名称重复"},
    "missing-registration":      {"术语未登记"},
    "bad-location":              {"术语定义位置非法"},
    "shorthand-location":        {"术语定义位置非法"},
    "wrong-doc-location":        {"术语定义位置错误"},
    "term-not-found":            {"术语定义未找到"},
    "used-term-missing":         {"所用术语无法解析"},
    "used-term-link":            {"所用术语含链接或编码", "所用术语无法解析"},
    "used-term-own":             {"所用术语重复本文定义"},
    "no-glossary":               {"缺少全局术语表"},
    "no-glossary-used":          {"缺少全局术语表"},
    "missing-english":           {"术语定义缺失"},
    "heading-mismatch":          {"术语标题与名称不一致"},
    "extra-column":              {"术语表列不合规"},
    "missing-column":            {"术语表缺少固定四列表"},
    "glossary-field-missing":    {"术语表字段缺失"},
    "glossary-bad-date":         {"术语表日期格式错误"},
    "glossary-state-field":      {"术语表含编码或状态字段"},
    "table-in-doc-term-section": {"术语章节使用表格"},
    "term-section-nested":       {"术语章节层级错误", "术语章节标题待迁移"},
    "term-section-late":         {"术语章节位置靠后"},
    "term-section-duplicate":    {"术语章节重复"},
    "glossary-meta":             {"术语表修订号非法", "术语表元信息缺失",
                                  "术语表缺变更记录"},
    "rev-mismatch":              {"文档修订号与变更记录不一致"},
    "readme-no-link":            {"README未登记术语表"},
    "app-glossary":              {"术语表位置非法"},
    "maint-ok":                  set(),
}


def parse(report):
    """把检查报告解析为 {夹具名: {问题名, ...}}。

    报告排版为 `### ERROR（N）` 分节 → `N. 问题名` → 缩进详情行（含夹具路径）。
    同一问题名可挂多条详情行；归属同一夹具时只记一次（断言看的是"有没有命中"，
    不是"命中几次"）。
    """
    got = defaultdict(set)
    cur = None
    for line in report.split("\n"):
        if SECTION.match(line):
            cur = None                      # 跨分节不复用问题名
            continue
        m = ITEM.match(line)
        if m:
            cur = m.group(1).strip()
            continue
        if cur:
            f = FIXTURE.search(line)
            if f:
                got[f.group(1)].add(cur)
    return {k: v - NOISE for k, v in got.items()}


def _load_checker():
    import importlib.util
    spec = importlib.util.spec_from_file_location("check_docs", CHECKER)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def parse_skill_links(issues):
    """把技能包锚点问题归到夹具文件名。"""
    got = defaultdict(set)
    for issue in issues:
        m = LINK_FILE.search(issue["description"])
        if m:
            got[m.group(1)].add(issue["title"])
    return dict(got)


def run_skill_link_fixtures(verbose):
    """正反夹具：ok-link 零命中；broken-link 必报不可达与缺文件。"""
    check_docs = _load_checker()
    issues = []
    check_docs.check_package_internal_links(
        LINK_FIXTURES, lambda lv, title, desc: issues.append(
            {"level": lv, "title": title, "description": desc}),
        exclude_tests=False)
    got = parse_skill_links(issues)
    on_disk = {p.name for p in LINK_FIXTURES.glob("*.md")}
    fails = []
    for name in sorted(LINK_EXPECT):
        want, have = LINK_EXPECT[name], got.get(name, set())
        missing, unexpected = want - have, have - want
        if missing or unexpected:
            fails.append((name, missing, unexpected))
        if verbose:
            mark = "FAIL" if (missing or unexpected) else "ok  "
            print(f"  [{mark}] {name}")
    orphan = sorted(on_disk - set(LINK_EXPECT))
    stale = sorted(set(LINK_EXPECT) - on_disk)
    print(f"技能包锚点夹具 {len(LINK_EXPECT)} 条，通过 "
          f"{len(LINK_EXPECT) - len(fails)} 条")
    for name, missing, unexpected in fails:
        print(f"  FAIL {name}")
        if missing:
            print(f"       漏报：{'、'.join(sorted(missing))}")
        if unexpected:
            print(f"       误报：{'、'.join(sorted(unexpected))}")
    for name in orphan:
        print(f"  FAIL {name}：夹具存在但未在 LINK_EXPECT 登记期望")
        fails.append((name, set(), set()))
    for name in stale:
        print(f"  FAIL {name}：LINK_EXPECT 登记的夹具已不在 skill_link_fixtures/")
        fails.append((name, set(), set()))
    return 1 if (fails or orphan or stale) else 0


def run_glossary_fixtures(verbose):
    """术语表 / 术语块场景：逐目录跑完整检查，只断言术语相关的问题名。"""
    check_docs = _load_checker()
    scenarios = sorted(p for p in GLOSSARY_FIXTURES.iterdir() if p.is_dir())
    got = {}
    for scenario in scenarios:
        checker = check_docs.DesignDocChecker(str(scenario))
        with contextlib.redirect_stdout(io.StringIO()):
            checker.run_checks()
        got[scenario.name] = {i["title"] for i in checker.issues
                              if i["title"] in GLOSSARY_TITLES}

    on_disk = {p.name for p in scenarios}
    fails = []
    for name in sorted(GLOSSARY_EXPECT):
        want, have = GLOSSARY_EXPECT[name], got.get(name, set())
        missing, unexpected = want - have, have - want
        if missing or unexpected:
            fails.append((name, missing, unexpected))
        if verbose:
            mark = "FAIL" if (missing or unexpected) else "ok  "
            print(f"  [{mark}] {name}")
    orphan = sorted(on_disk - set(GLOSSARY_EXPECT))
    stale = sorted(set(GLOSSARY_EXPECT) - on_disk)
    total = len(GLOSSARY_EXPECT)
    print(f"术语表场景 {total} 条，通过 {total - len(fails)} 条")
    for name, missing, unexpected in fails:
        print(f"  FAIL {name}")
        if missing:
            print(f"       漏报：{'、'.join(sorted(missing))}")
        if unexpected:
            print(f"       误报：{'、'.join(sorted(unexpected))}")
    for name in orphan:
        print(f"  FAIL {name}：场景存在但未在 GLOSSARY_EXPECT 登记期望")
    for name in stale:
        print(f"  FAIL {name}：GLOSSARY_EXPECT 登记的场景已不在 glossary_fixtures/")
    return 1 if (fails or orphan or stale) else 0


def run_baseline_bump_cases():
    """产品基线动作：首份基线 PATCH 可增删成员且增量恒空；非首份成员变化须立
    新基线；首份创建不写谱系，冻结时按最终 items 归属，并清掉开发期残留。"""
    import tempfile
    import yaml

    check_docs = _load_checker()
    readme_text = """# 基线测试

## 项目元信息

| 字段 | 值 |
|------|----|
| project_name | 基线测试 |
| project_code | BASE |
| 产品版本 | v1.0 |

## 发版记录

| 产品版本 | 日期 | 说明 |
|----------|------|------|
"""

    def doc_text(code, num, title, status):
        return f"""# L2-{num:03d}-bump

## 文档信息

| 属性 | 值 |
| ---- | -- |
| 文档编码 | L2-{num:03d} |
| 层级 | L2 - 系统需求 |
| 修订版本号 | 1 |
| 状态 | 初稿 |
| 作者 | 测试 |
| 创建日期 | 2026-01-15 |
| 最后更新 | 2026-01-15 |

## 需求定义

<a id="{code.lower()}"></a>
### {code}：{title}

- **细项状态**：{status}
- **修订版本号**：1
- **创建日期**：2026-01-15
- **最后修订日期**：2026-01-15
- **优先级**：P1
- **验证方式**：单元测试
"""

    fails = []

    def check(name, cond):
        if not cond:
            fails.append(name)

    def load(root, pv):
        return yaml.safe_load((root / "baselines" / f"{pv}.yaml").read_text(
            encoding="utf-8"))

    def bump(root, **kw):
        checker = check_docs.DesignDocChecker(str(root))
        with contextlib.redirect_stdout(io.StringIO()):
            checker.bump_product_version(**kw)

    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        (root / "README.md").write_text(readme_text, encoding="utf-8")
        a = root / "L2-901-bump.md"
        b = root / "L2-902-bump.md"
        c = root / "L2-903-bump.md"
        d = root / "L2-904-bump.md"
        a.write_text(doc_text("FR-901", 901, "甲", "正式"), encoding="utf-8")
        b.write_text(doc_text("FR-902", 902, "乙", "草案"), encoding="utf-8")
        c.write_text(doc_text("FR-903", 903, "丙", "草案"), encoding="utf-8")
        d.write_text(doc_text("FR-904", 904, "丁", "正式"), encoding="utf-8")

        bump(root, note="首份")
        v10 = load(root, "v1.0")
        check("首份 items",
              [i["code"] for i in v10["items"]] == ["FR-901", "FR-904"])
        check("首份 prev", v10.get("prev") in (None, "null"))
        check("首份增量恒空",
              v10["added"] == [] and v10["removed"] == [] and v10["changed"] == [])
        check("首份创建不写谱系",
              "**引入版本**" not in a.read_text(encoding="utf-8")
              and "**退出版本**" not in a.read_text(encoding="utf-8")
              and "**引入版本**" not in d.read_text(encoding="utf-8")
              and "**退出版本**" not in d.read_text(encoding="utf-8"))

        b.write_text(b.read_text(encoding="utf-8").replace(
            "**细项状态**：草案", "**细项状态**：正式"), encoding="utf-8")
        bump(root, patch=True, note="首份纳入 FR-902")
        v10 = load(root, "v1.0")
        check("首份 PATCH 纳入 items",
              [i["code"] for i in v10["items"]] == ["FR-901", "FR-902", "FR-904"])
        check("首份 PATCH 纳入不记增量",
              v10["added"] == [] and v10["removed"] == [] and v10["changed"] == [])
        check("首份 PATCH 升 tip", v10["full_version"] == "v1.0.1")
        check("首份 PATCH 不回写谱系",
              "**引入版本**" not in b.read_text(encoding="utf-8"))
        check("PATCH 不改 README 两段号",
              "| 产品版本 | v1.0 |" in (root / "README.md").read_text(encoding="utf-8"))

        c.write_text(c.read_text(encoding="utf-8").replace(
            "**细项状态**：草案", "**细项状态**：正式"), encoding="utf-8")
        bump(root, patch=True, note="首份再纳入 FR-903")
        v10 = load(root, "v1.0")
        check("首份 PATCH 再次纳入",
              [i["code"] for i in v10["items"]]
              == ["FR-901", "FR-902", "FR-903", "FR-904"])
        check("首份 PATCH 累计不记增量",
              v10["added"] == [] and v10["removed"] == [] and v10["changed"] == [])
        check("首份 PATCH 再升 tip", v10["full_version"] == "v1.0.2")

        c.write_text(c.read_text(encoding="utf-8").replace(
            "**细项状态**：正式", "**细项状态**：废弃"), encoding="utf-8")
        bump(root, patch=True, note="首份退出 FR-903")
        v10 = load(root, "v1.0")
        check("首份 PATCH 退出 items",
              [i["code"] for i in v10["items"]] == ["FR-901", "FR-902", "FR-904"])
        check("首份 PATCH 退出不记增量",
              v10["added"] == [] and v10["removed"] == [] and v10["changed"] == [])
        check("首份 PATCH 退出升 tip", v10["full_version"] == "v1.0.3")
        check("首份 PATCH 未写谱系",
              "**引入版本**" not in c.read_text(encoding="utf-8")
              and "**退出版本**" not in c.read_text(encoding="utf-8"))

        d.write_text(d.read_text(encoding="utf-8").replace(
            "**细项状态**：正式", "**细项状态**：废弃"), encoding="utf-8")
        bump(root, patch=True, note="首份退出 FR-904")
        v10 = load(root, "v1.0")
        check("首份 PATCH 再退出 items",
              [i["code"] for i in v10["items"]] == ["FR-901", "FR-902"])
        check("首份 PATCH 再退出不记增量",
              v10["added"] == [] and v10["removed"] == [] and v10["changed"] == [])
        check("首份 PATCH 再退出升 tip", v10["full_version"] == "v1.0.4")

        d.write_text(d.read_text(encoding="utf-8").replace(
            "- **最后修订日期**：2026-01-15\n- **优先级**：P1",
            "- **最后修订日期**：2026-01-15\n- **引入版本**：v1.0\n"
            "- **退出版本**：v1.0\n- **优先级**：P1"), encoding="utf-8")
        check("注入残留谱系",
              "**引入版本**：v1.0" in d.read_text(encoding="utf-8")
              and "**退出版本**：v1.0" in d.read_text(encoding="utf-8"))

        bump(root, note="冻结 v1.0")
        v11 = load(root, "v1.1")
        check("v1.1 prev", str(v11.get("prev")) == "v1.0.4")
        check("v1.1 无增量",
              v11["added"] == [] and v11["removed"] == [] and v11["changed"] == [])
        check("冻结按最终 items 回写首份成员",
              "**引入版本**：v1.0" in a.read_text(encoding="utf-8")
              and "**引入版本**：v1.0" in b.read_text(encoding="utf-8"))
        check("冻结清除初始成员残留谱系",
              "**引入版本**" not in d.read_text(encoding="utf-8")
              and "**退出版本**" not in d.read_text(encoding="utf-8"))
        check("冻结不为已退出成员写谱系",
              "**引入版本**" not in c.read_text(encoding="utf-8")
              and "**退出版本**" not in c.read_text(encoding="utf-8"))

        c.write_text(c.read_text(encoding="utf-8").replace(
            "**细项状态**：废弃", "**细项状态**：正式"), encoding="utf-8")
        try:
            bump(root, patch=True, note="非首份纳入 FR-903")
            check("非首份拒绝新增成员 PATCH", False)
        except RuntimeError as exc:
            check("非首份拒绝新增成员 PATCH", "成员进出不能 PATCH" in str(exc))
        c.write_text(c.read_text(encoding="utf-8").replace(
            "**细项状态**：正式", "**细项状态**：废弃"), encoding="utf-8")

        a.write_text(a.read_text(encoding="utf-8").replace(
            "**细项状态**：正式", "**细项状态**：废弃"), encoding="utf-8")
        try:
            bump(root, patch=True, note="非首份退出 FR-901")
            check("非首份拒绝删除成员 PATCH", False)
        except RuntimeError as exc:
            check("非首份拒绝删除成员 PATCH", "成员进出不能 PATCH" in str(exc))
        a.write_text(a.read_text(encoding="utf-8").replace(
            "**细项状态**：废弃", "**细项状态**：正式"), encoding="utf-8")

        b.write_text(
            b.read_text(encoding="utf-8")
            .replace("- **修订版本号**：1", "- **修订版本号**：2")
            .replace("- **最后修订日期**：2026-01-15", "- **最后修订日期**：2026-02-01"),
            encoding="utf-8")
        bump(root, patch=True, note="同步 revision")
        v11 = load(root, "v1.1")
        check("非首份 PATCH revision items",
              [i["code"] for i in v11["items"]] == ["FR-901", "FR-902"])
        check("非首份 PATCH revision 增量",
              v11["added"] == [] and v11["removed"] == [] and v11["changed"] == ["FR-902"])
        check("非首份 PATCH 升 tip", v11["full_version"] == "v1.1.1")

        a.write_text(a.read_text(encoding="utf-8").replace(
            "**细项状态**：正式", "**细项状态**：废弃"), encoding="utf-8")
        bump(root, note="冻结 v1.1")
        v12 = load(root, "v1.2")
        check("v1.2 items", [i["code"] for i in v12["items"]] == ["FR-902"])
        check("v1.2 净差异",
              v12["added"] == [] and v12["removed"] == ["FR-901"]
              and v12["changed"] == [])
        check("冻结回写漂移退出",
              "**退出版本**：v1.2" in a.read_text(encoding="utf-8")
              and "**引入版本**：v1.0" in a.read_text(encoding="utf-8"))
        check("非首份不重复归属引入版本",
              "**引入版本**：v1.0" in b.read_text(encoding="utf-8")
              and "**引入版本**：v1.1" not in b.read_text(encoding="utf-8"))
        check("v1.0 历史快照保持",
              [i["code"] for i in load(root, "v1.0")["items"]] == ["FR-901", "FR-902"])
        v11_hist = load(root, "v1.1")
        check("v1.1 历史增量保留",
              v11_hist["added"] == [] and v11_hist["removed"] == []
              and v11_hist["changed"] == ["FR-902"])

        checker = check_docs.DesignDocChecker(str(root))
        with contextlib.redirect_stdout(io.StringIO()):
            checker.run_checks()
        baseline_noise = [
            i for i in checker.issues
            if any(k in i["title"] for k in ("基线", "谱系", "产品版本"))
        ]
        check("冻结结果通过基线校验", not baseline_noise)

        readme = root / "README.md"
        readme.write_text(readme.read_text(encoding="utf-8").replace(
            "| 产品版本 | v1.2 |", "| 产品版本 | v1.1 |"), encoding="utf-8")
        try:
            bump(root, patch=True, note="越权")
            check("历史基线拒绝 PATCH", False)
        except RuntimeError as exc:
            check("历史基线拒绝 PATCH", "历史基线只读" in str(exc))

    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        (root / "README.md").write_text(readme_text, encoding="utf-8")
        (root / "L2-904-bump.md").write_text(
            doc_text("FR-904", 904, "丁", "正式"), encoding="utf-8")
        (root / "baselines").mkdir()
        (root / "baselines" / "v1.0.yaml").write_text(yaml.safe_dump({
            "product_version": "v1.0",
            "full_version": "v1.0.0",
            "created": "2026-01-15",
            "updated": "2026-01-15",
            "prev": None,
            "patch_log": [{"full_version": "v1.0.0", "date": "2026-01-15",
                           "note": "首份"}],
            "added": ["FR-904"],
            "removed": [],
            "changed": [],
            "items": [{"code": "FR-904", "type": "FR", "title": "丁",
                       "revision": 1, "doc": "L2-904"}],
        }, allow_unicode=True), encoding="utf-8")
        checker = check_docs.DesignDocChecker(str(root))
        with contextlib.redirect_stdout(io.StringIO()):
            checker.run_checks()
        check("首份非空增量被拒绝",
              any(i["title"] == "产品基线增量不一致"
                  and "首份基线无前驱" in i["description"]
                  for i in checker.issues))

    if fails:
        print("FAIL 产品基线 PATCH/冻结用例未通过")
        for name in fails:
            print(f"     未通过：{name}")
        return 1
    print("产品基线 PATCH/冻结用例通过")
    return 0


def run_single_scope_and_extension_cases():
    """单一作用域守卫、外部术语表、基线扩展字段保留。"""
    import tempfile
    import yaml

    check_docs = _load_checker()
    fails = []

    def check(name, cond):
        if not cond:
            fails.append(name)

    readme = """# 作用域

| 字段 | 值 |
|------|----|
| project_name | 作用域 |
| project_code | SCP |
| 产品版本 | v1.0 |

## 发版记录

| 产品版本 | 日期 | 说明 |
|----------|------|------|
"""

    doc = """# SCP-L2-001-示例

| 属性 | 值 |
|------|----|
| 文档编码 | SCP-L2-001 |
| 层级 | L2 - 系统/产品需求 |
| 修订版本号 | 1 |
| 状态 | 初稿 |
| 作者 | tester |
| 创建日期 | 2026-01-01 |
| 最后更新 | 2026-01-01 |

## 术语和概念

### 订单

- **中文名称**：订单
- **英文名称**：Order

**定义**：客户提交的购买请求。

## 需求定义

<a id="scp-fr-001"></a>
### SCP-FR-001：下单

- **细项状态**：正式
- **修订版本号**：1
- **创建日期**：2026-01-01
- **最后修订日期**：2026-01-01
- **优先级**：P1
- **验证方式**：单元测试

## 变更记录

| 修订版本号 | 日期 | 作者 | 变更说明 |
|------------|------|------|----------|
| 1 | 2026-01-01 | tester | 初稿创建 |
"""

    glossary = """# 全局术语表

| 属性 | 值 |
|------|----|
| 修订版本号 | 1 |
| 作者 | tester |
| 创建日期 | 2026-01-01 |
| 最后更新 | 2026-01-01 |

## 术语

| 中文名称 | 英文名称 | 定义 | 定义位置 |
|----------|----------|------|----------|
| 订单 | Order | 客户提交的购买请求。 | SCP-L2-001 |

## 变更记录

| 修订版本号 | 日期 | 作者 | 变更说明 |
|------------|------|------|----------|
| 1 | 2026-01-01 | tester | 初稿创建 |
"""

    with tempfile.TemporaryDirectory() as td:
        root = Path(td) / "ued"
        root.mkdir()
        (root / "README.md").write_text(
            "# 系统\n\n## 子系统注册表\n\n"
            "| subsystem_key | 子系统名称 | 目录 | 编码前缀 | 角色文档 | 状态 |\n"
            "|---------------|------------|------|----------|----------|------|\n"
            "| crm | CRM | `crm/` | CRM | CMP-01 | 正式 |\n",
            encoding="utf-8")
        crm = root / "crm"
        crm.mkdir()
        (crm / "README.md").write_text(readme, encoding="utf-8")
        (crm / "SCP-L2-001-sample.md").write_text(doc, encoding="utf-8")
        (root / "glossary.md").write_text(glossary, encoding="utf-8")

        checker = check_docs.DesignDocChecker(str(root))
        with contextlib.redirect_stdout(io.StringIO()):
            checker.run_checks()
        check("系统根被拒",
              any(i["title"] == "系统根需由 system-design-doc 校验"
                  for i in checker.issues))

        checker = check_docs.DesignDocChecker(
            str(crm), glossary_path=str(root / "glossary.md"))
        with contextlib.redirect_stdout(io.StringIO()):
            checker.run_checks()
        glossary_errors = [i for i in checker.issues
                           if i["title"] in GLOSSARY_TITLES and i["level"] == "ERROR"]
        check("外部术语表可用", not glossary_errors)
        check("带前缀定义通过",
              not any(i["title"] in ("定义编码前缀不符", "文档编码前缀不符")
                      for i in checker.issues))

        bad = doc.replace("SCP-FR-001", "FR-001").replace(
            "scp-fr-001", "fr-001").replace("SCP-L2-001", "SCP-L2-002")
        (crm / "SCP-L2-002-bad.md").write_text(bad, encoding="utf-8")
        checker = check_docs.DesignDocChecker(
            str(crm), glossary_path=str(root / "glossary.md"))
        with contextlib.redirect_stdout(io.StringIO()):
            checker.run_checks()
        check("定义使用简写报错",
              any(i["title"] == "定义编码前缀不符" and i["level"] == "ERROR"
                  for i in checker.issues))
        (crm / "SCP-L2-002-bad.md").unlink()

        sample = crm / "SCP-L2-001-sample.md"
        original = sample.read_text(encoding="utf-8")
        sample.write_text(original + "\n跨子系统引用 `OTH-FR-001`。\n", encoding="utf-8")
        checker = check_docs.DesignDocChecker(
            str(crm), glossary_path=str(root / "glossary.md"))
        with contextlib.redirect_stdout(io.StringIO()):
            checker.run_checks()
        check("他作用域前缀引用不判悬空",
              not any(i["title"] == "引用悬空" and "OTH-FR-001" in i["description"]
                      for i in checker.issues))
        sample.write_text(original, encoding="utf-8")

        (crm / "glossary.md").write_text(glossary, encoding="utf-8")
        checker = check_docs.DesignDocChecker(
            str(crm), glossary_path=str(root / "glossary.md"))
        with contextlib.redirect_stdout(io.StringIO()):
            checker.run_checks()
        check("子系统内术语表非法",
              any(i["title"] == "术语表位置非法" for i in checker.issues))

    with tempfile.TemporaryDirectory() as td:
        root = Path(td) / "ued"
        root.mkdir()
        (root / "README.md").write_text(
            "# 旧结构\n\n| 字段 | 值 |\n|------|----|\n| doc_mode | multi_app |\n\n"
            "## 应用注册表\n\n| app_key | 应用名称 | 目录 |\n"
            "|---------|----------|------|\n| crm | CRM | crm/ |\n",
            encoding="utf-8")
        checker = check_docs.DesignDocChecker(str(root))
        with contextlib.redirect_stdout(io.StringIO()):
            checker.run_checks()
        check("旧多应用结构被拒",
              any(i["title"] == "旧多应用结构需迁移" for i in checker.issues))

    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        (root / "README.md").write_text(readme, encoding="utf-8")
        (root / "SCP-L2-001-sample.md").write_text(doc, encoding="utf-8")

        def bump(**kw):
            checker = check_docs.DesignDocChecker(str(root))
            with contextlib.redirect_stdout(io.StringIO()):
                checker.bump_product_version(**kw)

        def load(pv):
            return yaml.safe_load((root / "baselines" / f"{pv}.yaml").read_text(
                encoding="utf-8"))

        bump(note="首份")
        first = load("v1.0")
        first["depends_on"] = [{"subsystem": "oms", "product_version": "v2.5"}]
        first["external_deps"] = [{"name": "identity-provider",
                                   "product_version": "v4.0"}]
        (root / "baselines" / "v1.0.yaml").write_text(
            yaml.safe_dump(first, allow_unicode=True, sort_keys=False),
            encoding="utf-8")

        bump(patch=True, note="PATCH 保留扩展")
        check("PATCH 保留 depends_on",
              load("v1.0").get("depends_on") == first["depends_on"])
        check("PATCH 保留 external_deps",
              load("v1.0").get("external_deps") == first["external_deps"])

        bump(note="MINOR 继承扩展")
        v11 = load("v1.1")
        check("MINOR 继承 depends_on", v11.get("depends_on") == first["depends_on"])
        check("MINOR 继承 external_deps",
              v11.get("external_deps") == first["external_deps"])

    if fails:
        print("FAIL 单一作用域 / 扩展字段用例未通过")
        for name in fails:
            print(f"     未通过：{name}")
        return 1
    print("单一作用域 / 扩展字段用例通过")
    return 0


def run_cross_scope_glossary_cases():
    """系统根术语表的跨子系统 `定义位置`：只读辅助作用域的启停与隔离边界。"""
    import tempfile

    check_docs = _load_checker()
    fails = []

    def check(name, cond):
        if not cond:
            fails.append(name)

    def scope_doc(code, prefix, zh, en, definition, terms=True, changelog=True,
                  status="正式"):
        term_block = (
            "## 术语和概念\n\n"
            f"### {zh}\n\n"
            f"- **中文名称**：{zh}\n"
            f"- **英文名称**：{en}\n\n"
            f"**定义**：{definition}\n\n"
        ) if terms else ""
        changelog_block = (
            "## 变更记录\n\n"
            "| 修订版本号 | 日期 | 作者 | 变更说明 |\n"
            "|------------|------|------|----------|\n"
            "| 1 | 2026-01-01 | tester | 初稿创建 |\n"
        ) if changelog else ""
        return (
            f"# {code}-示例\n\n"
            "| 属性 | 值 |\n|------|----|\n"
            f"| 文档编码 | {code} |\n"
            "| 层级 | L2 - 系统/产品需求 |\n"
            "| 修订版本号 | 1 |\n"
            f"| 状态 | {status} |\n"
            "| 作者 | tester |\n"
            "| 创建日期 | 2026-01-01 |\n"
            "| 最后更新 | 2026-01-01 |\n\n"
            f"{term_block}"
            "## 需求定义\n\n"
            f'<a id="{prefix.lower()}-fr-001"></a>\n'
            f"### {prefix}-FR-001：示例\n\n"
            "- **细项状态**：正式\n"
            "- **修订版本号**：1\n"
            "- **创建日期**：2026-01-01\n"
            "- **最后修订日期**：2026-01-01\n\n"
            f"{changelog_block}"
        )

    def build(root, *, registry=True, scope_registered=True,
              oms_status="正式", oms_terms=True, oms_loc="OMS-L2-001",
              oms_deprecated_dir=False, oms_changelog=True,
              oms_doc_status="正式"):
        root.mkdir(parents=True, exist_ok=True)
        if registry:
            rows = []
            if scope_registered:
                rows.append("| crm | CRM | `crm/` | CRM | CMP-01 | 正式 |")
            if oms_status:
                rows.append(f"| oms | OMS | `oms/` | OMS | CMP-02 | {oms_status} |")
            (root / "README.md").write_text(
                "# 系统\n\n## 子系统注册表\n\n"
                "| subsystem_key | 子系统名称 | 目录 | 编码前缀 | 角色文档 | 状态 |\n"
                "|---------------|------------|------|----------|----------|------|\n"
                + "\n".join(rows) + "\n",
                encoding="utf-8")
        else:
            (root / "README.md").write_text(
                "# 单系统\n\n[全局术语表](glossary.md)\n", encoding="utf-8")

        crm = root / "crm"
        crm.mkdir()
        (crm / "README.md").write_text(
            "# CRM\n\n[全局术语表](../glossary.md)\n", encoding="utf-8")
        (crm / "CRM-L2-001-order.md").write_text(
            scope_doc("CRM-L2-001", "CRM", "订单", "Order", "客户提交的购买请求。"),
            encoding="utf-8")

        oms_dir = root / "oms" / ("deprecated" if oms_deprecated_dir else "")
        oms_dir.mkdir(parents=True)
        (oms_dir / "OMS-L2-001-waybill.md").write_text(
            scope_doc("OMS-L2-001", "OMS", "运单", "Waybill", "物流运输单据。",
                      terms=oms_terms, changelog=oms_changelog,
                      status=oms_doc_status),
            encoding="utf-8")

        rows = ["| 订单 | Order | 客户提交的购买请求。 | CRM-L2-001 |"]
        if oms_loc:
            rows.append(f"| 运单 | Waybill | 物流运输单据。 | {oms_loc} |")
        (root / "glossary.md").write_text(
            "# 全局术语表\n\n"
            "| 属性 | 值 |\n|------|----|\n"
            "| 修订版本号 | 1 |\n| 作者 | tester |\n"
            "| 创建日期 | 2026-01-01 |\n| 最后更新 | 2026-01-01 |\n\n"
            "## 术语\n\n"
            "| 中文名称 | 英文名称 | 定义 | 定义位置 |\n"
            "|----------|----------|------|----------|\n"
            + "\n".join(rows) + "\n\n"
            "## 变更记录\n\n"
            "| 修订版本号 | 日期 | 作者 | 变更说明 |\n"
            "|------------|------|------|----------|\n"
            "| 1 | 2026-01-01 | tester | 初稿创建 |\n",
            encoding="utf-8")

    @contextlib.contextmanager
    def scenario(**opts):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td) / "ued"
            build(root, **opts)
            checker = check_docs.DesignDocChecker(
                str(root / "crm"), glossary_path=str(root / "glossary.md"))
            with contextlib.redirect_stdout(io.StringIO()):
                checker.run_checks()
            yield checker, root

    def errors(checker):
        return {i["title"] for i in checker.issues
                if i["title"] in GLOSSARY_TITLES and i["level"] == "ERROR"}

    with scenario(oms_changelog=False, oms_doc_status="草稿") as (checker, root):
        oms_dir = str(root / "oms")
        check("跨子系统定义位置可解析", not errors(checker))
        check("辅助文档不进入当前作用域",
              all(oms_dir not in d.path for d in checker.docs))
        check("辅助文档缺陷不混入报告",
              not any(oms_dir in i["description"] for i in checker.issues))

    with scenario(oms_terms=False) as (checker, _root):
        check("辅助文档缺术语报未找到", "术语定义未找到" in errors(checker))

    with scenario(oms_loc="OMS-L2-999") as (checker, _root):
        check("辅助作用域不存在的编码报非法", "术语定义位置非法" in errors(checker))

    with scenario(oms_status="废弃") as (checker, _root):
        check("废弃子系统不参与解析", "术语定义位置非法" in errors(checker))

    with scenario(scope_registered=False) as (checker, _root):
        check("未登记作用域不启用辅助解析", "术语定义位置非法" in errors(checker))

    with scenario(oms_deprecated_dir=True) as (checker, _root):
        check("归档目录不参与解析", "术语定义位置非法" in errors(checker))

    with scenario(registry=False, oms_loc="") as (checker, _root):
        check("无系统注册表时单系统行为不变", not errors(checker))

    if fails:
        print("FAIL 跨子系统术语表用例未通过")
        for name in fails:
            print(f"     未通过：{name}")
        return 1
    print("跨子系统术语表用例通过")
    return 0


def run_pin_scope_and_history_cases():
    """本文引用作用域、钉住代际对象与历史内容豁免的正反例。"""
    import tempfile

    check_docs = _load_checker()
    fails = []

    def check(name, cond):
        if not cond:
            fails.append(name)

    def doc(code, layer, rev, body, changelog):
        return (
            f"# {code}-示例\n\n"
            "| 属性 | 值 |\n|------|----|\n"
            f"| 文档编码 | {code} |\n"
            f"| 层级 | {layer} |\n"
            f"| 修订版本号 | {rev} |\n"
            "| 状态 | 正式 |\n"
            "| 作者 | tester |\n"
            "| 创建日期 | 2026-01-01 |\n"
            "| 最后更新 | 2026-01-05 |\n\n"
            f"{body}\n\n"
            "## 变更记录\n\n"
            "| 修订版本号 | 日期 | 作者 | 变更说明 |\n"
            "|------------|------|------|----------|\n"
            f"{changelog}\n")

    def item(code, title, status, rev, extra=""):
        suffix = " ~~已废弃~~" if status == "废弃" else ""
        return (
            f'<a id="{code.lower()}"></a>\n'
            f"### {code}：{title}{suffix}\n\n"
            f"- **细项状态**：{status}\n"
            f"- **修订版本号**：{rev}\n"
            "- **创建日期**：2026-01-01\n"
            "- **最后修订日期**：2026-01-01\n"
            f"{extra}\n")

    def scenario(files):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td) / "ued"
            root.mkdir()
            for name, text in files.items():
                (root / name).write_text(text, encoding="utf-8")
            checker = check_docs.DesignDocChecker(str(root))
            with contextlib.redirect_stdout(io.StringIO()):
                checker.run_checks()
            return checker

    def hits(checker, title):
        return [i for i in checker.issues if i["title"] == title]

    def desc_has(checker, title, needle):
        return any(needle in i["description"] for i in hits(checker, title))

    deprecated_fields = (
        "- **废弃时间**：2026-01-02\n"
        "- **废弃类别**：被替代\n"
        "- **废弃原因**：已被替代\n"
        "- **替代方案**：无\n")

    l2_body = (
        "## 需求\n\n"
        + item("CRM-FR-001", "登录", "正式", 3)
        + item("CRM-FR-002", "注册", "废弃", 2, deprecated_fields)
        + item("CRM-FR-003", "约束", "正式", 7)
        + item("CRM-FR-007", "临时标注 ~~待删~~", "正式", 1)
        + item("CRM-FR-006", "坏登记", "废弃", 1,
               "- **废弃时间**：2026-01-02\n"
               "- **废弃类别**：被替代\n"
               "- **替代方案**：无\n"))

    l2_changelog = (
        "| 5 | 2026-01-05 | tester | 现行 |\n"
        "| 4 | 2026-01-04 | tester | 历史引用 L5-002 与 "
        "[CRM-FR-002（历史旧称）](./CRM-L2-001-requirements.md#crm-fr-002) |\n")

    l4_body = (
        "## 本文引用\n\n"
        "| 引用对象 | 类型 | 所在文档 | 钉住代际 | 钉住日期 |\n"
        "|----------|------|----------|----------|----------|\n"
        "| CRM-FR-001 | 细项 | CRM-L2-001 | 4 | 2026-01-01 |\n"
        "| CRM-FR-002 | 细项 | CRM-L2-001 | 2 | 2026-01-01 |\n"
        "| CRM-FR-003 | 细项 | CRM-L2-001 | 6 | 2026-01-01 |\n"
        "| CRM-L2-001 | 文档 | — | 6 | 2026-01-01 |\n"
        "| CRM-L2-002 | 文档 | — | 2 | 2026-01-01 |\n"
        "| OMS-L2-001 | 细项 | OMS-L2-001 | 99 | 2026-1-1 |\n"
        "| OMS-FR-009 | 文档 | — | 99 | 2026-1-1 |\n"
        "| OMS-FR-003 | 细项 | OMS-L2-001 | 1 | 2026-01-01 |\n"
        "| CRM-FR-007 | 细项 | CRM-L2-001 | 1 | 2026-01-01 |\n\n"
        "## 动作\n\n"
        '<a id="crm-act-001"></a>\n'
        "### CRM-ACT-001：旧动作 ~~已废弃~~\n\n"
        "- **细项状态**：废弃\n"
        "- **修订版本号**：1\n"
        "- **创建日期**：2026-01-01\n"
        "- **最后修订日期**：2026-01-01\n"
        "- **废弃时间**：2026-01-02\n"
        "- **废弃类别**：被替代\n"
        "- **废弃原因**：动作退场\n"
        "- **替代方案**：无\n"
        "- **来源**：[CRM-FR-001（登录）](./CRM-L2-001-requirements.md#crm-fr-001)\n"
        "- **依赖**：[CRM-FR-002（废弃旧称）](./CRM-L2-001-requirements.md#crm-fr-002)\n"
        "- **依赖**：[CRM-FR-005（补充）](./CRM-L2-002-extra.md#crm-fr-005)\n\n"
        "参见 [CRM-FR-002（废弃旧称）](./CRM-L2-001-requirements.md#crm-fr-002)。\n\n"
        '<a id="crm-act-002"></a>\n'
        "### CRM-ACT-002：新动作\n\n"
        "- **细项状态**：正式\n"
        "- **修订版本号**：1\n"
        "- **创建日期**：2026-01-01\n"
        "- **最后修订日期**：2026-01-01\n"
        "- **来源**：[OMS-FR-003（订单）](../oms/OMS-L2-001-order.md#oms-fr-003)\n"
        "- **来源**：[CRM-FR-005（补充）](./CRM-L2-002-extra.md#crm-fr-005)\n\n"
        "参见 [CRM-FR-002（过期旧称）](./CRM-L2-001-requirements.md#crm-fr-002)。\n"
        "外部契约见 [OMS-L2-001（订单）](../oms/OMS-L2-001-order.md) 与 OMS-FR-001。\n"
        "标题核对 [CRM-FR-007（临时标注）](./CRM-L2-001-requirements.md#crm-fr-007)。\n"
        "另见 [OMS-FR-004（订单行）](../oms/OMS-L2-001-order.md#oms-fr-004)。\n"
        "另见 CRM-FR-999。\n")

    files = {
        "README.md": (
            "# CRM 设计文档索引\n\n"
            "| 属性 | 值 |\n|------|----|\n"
            "| project_code | CRM |\n| 产品版本 | v1.0 |\n"),
        "CRM-L2-001-requirements.md": doc(
            "CRM-L2-001", "L2", 5, l2_body, l2_changelog),
        "CRM-L2-002-extra.md": doc(
            "CRM-L2-002", "L2", 2,
            "## 需求\n\n" + item("CRM-FR-005", "补充", "正式", 1),
            "| 2 | 2026-01-02 | tester | 现行 |\n"
            "| 1 | 2026-01-01 | tester | 初建 |\n"),
        "CRM-L4-001-system.md": doc(
            "CRM-L4-001", "L4", 5, l4_body,
            "| 5 | 2026-01-05 | tester | 现行 |\n"
            "| 4 | 2026-01-04 | tester | 历史 [CRM-FR-002（变更旧称）]"
            "(./CRM-L2-001-requirements.md#crm-fr-002) |\n"),
    }
    checker = scenario(files)

    # 跨作用域引用：存在性 / 归属由 check_system.py 负责，本检查器不重复报
    check("跨作用域钉住行不报对象不存在", not hits(checker, "本文引用对象不存在"))
    check("跨作用域正文引用不报悬空", not desc_has(checker, "引用悬空", "OMS-"))
    missing_pins = hits(checker, "缺本文引用钉住行")
    check("跨作用域已钉引用不报缺行",
          not any("OMS-FR-003" in i["description"] for i in missing_pins))
    check("跨作用域未钉引用仍报缺行",
          any("OMS-FR-004" in i["description"] for i in missing_pins))
    check("跨作用域钉住行不做类型校验", not hits(checker, "本文引用类型不符"))
    check("跨作用域钉住行不做所在文档校验",
          not hits(checker, "文档型引用所在文档应为 —")
          and not hits(checker, "本文引用所在文档不符"))
    check("跨作用域钉住行不做日期校验", not hits(checker, "钉住日期格式错误"))

    # 本地无效引用仍须报错
    check("本地无效引用仍报悬空", desc_has(checker, "引用悬空", "CRM-FR-999"))

    # 钉住代际：文档比较文档修订号，细项比较目标细项修订号
    supers = hits(checker, "钉住代际超前")
    check("细项钉住代际用细项修订号",
          any("`CRM-FR-001`" in i["description"] for i in supers))
    check("细项钉住代际不误用文档修订号",
          not any("`CRM-FR-003`" in i["description"] for i in supers))
    check("文档钉住代际用文档修订号",
          any("`CRM-L2-001`" in i["description"] for i in supers))
    check("文档钉住代际不超前时不报",
          not any("`CRM-L2-002`" in i["description"] for i in supers))
    check("跨作用域钉住代际不比较",
          not any("`OMS-" in i["description"] for i in supers))

    # 历史内容：不随后续改名 / 废弃而要求改写
    check("变更记录历史引用不报悬空",
          not desc_has(checker, "引用悬空", "L5-002"))
    check("变更记录历史标题不强制改写",
          not desc_has(checker, "引用标题与定义标题不一致", "变更旧称"))
    check("废弃细项历史标题不强制改写",
          not desc_has(checker, "引用标题与定义标题不一致", "废弃旧称"))
    check("废弃细项历史依赖不报收口",
          not hits(checker, "依赖指向废弃细项"))
    check("废弃细项历史属性不要求补钉",
          not any("CRM-ACT-001" in i["description"] and "CRM-FR-005" in i["description"]
                  for i in missing_pins))
    check("活跃细项缺钉仍报",
          any("CRM-ACT-002" in i["description"] and "CRM-FR-005" in i["description"]
              for i in missing_pins))

    # 活跃内容仍须报错
    active = hits(checker, "活跃文档引用已废弃对象")
    l4_lines = files["CRM-L4-001-system.md"].splitlines()
    active_line = next(i for i, line in enumerate(l4_lines, 1) if "过期旧称" in line)
    check("活跃正文引用废弃对象仍告警",
          any(f":{active_line} 引用了已废弃的" in i["description"] for i in active))
    check("活跃正文标题不一致仍告警",
          desc_has(checker, "引用标题与定义标题不一致", "过期旧称"))
    check("一般删除线不从标题剥离",
          desc_has(checker, "引用标题与定义标题不一致", "临时标注"))
    l4_doc = next(d for d in checker.docs if d.doc_code == "CRM-L4-001")
    check("废弃标记仍从标题剥离",
          checker._def_title(l4_doc, "CRM-ACT-001") == "旧动作")

    # 废弃登记的结构检查不被历史豁免吞掉
    check("废弃登记缺字段仍报错", hits(checker, "废弃细项缺少必需字段"))

    if fails:
        print("FAIL 本文引用作用域 / 钉住代际 / 历史豁免用例未通过")
        for name in fails:
            print(f"     未通过：{name}")
        return 1
    print("本文引用作用域 / 钉住代际 / 历史豁免用例通过")
    return 0


def run_dep_graph_cases():
    """细项 `依赖`：外部编码原义、成环口径（活跃 ERROR / 整环废弃豁免）、
    系统根只读跨作用域检查。"""
    import tempfile

    check_docs = _load_checker()
    fails = []

    def check(name, cond):
        if not cond:
            fails.append(name)

    def scope_readme(code, name):
        return (
            "# 作用域\n\n"
            "| 字段 | 值 |\n|------|----|\n"
            f"| project_name | {name} |\n"
            f"| project_code | {code} |\n"
            "| 产品版本 | v1.0 |\n\n"
            "## 发版记录\n\n"
            "| 产品版本 | 日期 | 说明 |\n"
            "|----------|------|------|\n"
            "| v1.0 | 2026-01-01 | 初建 |\n")

    def item(code, title, status, deps=(), deprecated=False):
        suffix = " ~~已废弃~~" if deprecated else ""
        lines = [
            f'<a id="{code.lower()}"></a>',
            f"### {code}：{title}{suffix}",
            "",
            f"- **细项状态**：{status}",
            "- **修订版本号**：1",
            "- **创建日期**：2026-01-01",
            "- **最后修订日期**：2026-01-01",
        ]
        if deprecated:
            lines += [
                "- **废弃时间**：2026-01-02",
                "- **废弃类别**：被替代",
                "- **废弃原因**：测试存量环",
                "- **替代方案**：无",
            ]
        else:
            lines += ["- **优先级**：P1", "- **验证方式**：单元测试"]
        for target, target_title, url in deps:
            lines.append(f"- **依赖**：[{target}（{target_title}）]({url})")
        return "\n".join(lines) + "\n"

    def doc(code, layer, body):
        return (
            f"# {code}-示例\n\n"
            "| 属性 | 值 |\n|------|----|\n"
            f"| 文档编码 | {code} |\n"
            f"| 层级 | {layer} |\n"
            "| 修订版本号 | 1 |\n"
            "| 状态 | 初稿 |\n"
            "| 作者 | tester |\n"
            "| 创建日期 | 2026-01-01 |\n"
            "| 最后更新 | 2026-01-01 |\n\n"
            f"## 需求\n\n{body}\n"
            "## 变更记录\n\n"
            "| 修订版本号 | 日期 | 作者 | 变更说明 |\n"
            "|------------|------|------|----------|\n"
            "| 1 | 2026-01-01 | tester | 初建 |\n")

    def run_scope(root):
        checker = check_docs.DesignDocChecker(str(root))
        with contextlib.redirect_stdout(io.StringIO()):
            checker.run_checks()
        return checker

    def hits(checker, title):
        return [i for i in checker.issues if i["title"] == title]

    # —— 跨作用域编码原义：外部全量编码不得按 (类型码, 序号) 重映射 ——
    with tempfile.TemporaryDirectory() as td:
        beta = Path(td) / "beta"
        beta.mkdir()
        (beta / "README.md").write_text(scope_readme("BET", "乙"), encoding="utf-8")
        (beta / "BET-L2-001.md").write_text(doc("BET-L2-001", "L2", (
            item("BET-DOM-001", "本地领域", "正式")
            + item("BET-ACT-001", "动作甲", "正式", [
                ("ALP-DOM-001", "外部领域",
                 "../alpha/ALP-L2-001.md#alp-dom-001")])
            + item("BET-ACT-002", "动作乙", "正式", [
                ("DOM-001", "本地领域", "#bet-dom-001")]))),
            encoding="utf-8")
        checker = run_scope(beta)
        check("外部编码不重映射",
              checker.resolve_code("ALP-DOM-001") == "ALP-DOM-001")
        check("外部依赖边保留原义",
              checker.dep_forward.get("BET-ACT-001") == ["ALP-DOM-001"])
        check("外部依赖不报目标不存在",
              not any("ALP-DOM-001" in i["description"]
                      for i in hits(checker, "依赖目标不存在")))
        check("同作用域简写照旧解析",
              checker.dep_forward.get("BET-ACT-002") == ["BET-DOM-001"])

    # —— 依赖成环：活跃 ERROR；整环 `废弃` 属历史存量，不报 ——
    with tempfile.TemporaryDirectory() as td:
        cyc = Path(td) / "cyc"
        cyc.mkdir()
        (cyc / "README.md").write_text(scope_readme("CYC", "环"), encoding="utf-8")
        (cyc / "CYC-L2-001.md").write_text(doc("CYC-L2-001", "L2", (
            item("CYC-FR-001", "甲", "正式", [
                ("CYC-FR-002", "乙", "#cyc-fr-002")])
            + item("CYC-FR-002", "乙", "正式", [
                ("CYC-FR-001", "甲", "#cyc-fr-001")])
            + item("CYC-FR-003", "丙", "废弃", [
                ("CYC-FR-004", "丁", "#cyc-fr-004")], deprecated=True)
            + item("CYC-FR-004", "丁", "废弃", [
                ("CYC-FR-003", "丙", "#cyc-fr-003")], deprecated=True))),
            encoding="utf-8")
        checker = run_scope(cyc)
        live = hits(checker, "依赖成环")
        check("活跃依赖环报 ERROR",
              any(i["level"] == "ERROR" and "CYC-FR-001" in i["description"]
                  for i in live))
        check("整环废弃不报依赖成环",
              not any("CYC-FR-003" in i["description"] for i in live))

    # —— 系统根只读跨作用域检查 ——
    registry = (
        "# 系统\n\n"
        "## 子系统注册表\n\n"
        "| subsystem_key | 子系统名称 | 目录 | 编码前缀 | 角色文档 | 状态 |\n"
        "|---------------|------------|------|----------|----------|------|\n"
        "| alpha | 甲 | `alpha/` | ALP | ALP-CMP-001 | 初稿 |\n"
        "| beta | 乙 | `beta/` | BET | BET-CMP-001 | 初稿 |\n")

    with tempfile.TemporaryDirectory() as td:
        root = Path(td) / "ued"
        (root / "alpha").mkdir(parents=True)
        (root / "beta").mkdir()
        (root / "README.md").write_text(registry, encoding="utf-8")
        (root / "alpha" / "README.md").write_text(
            scope_readme("ALP", "甲"), encoding="utf-8")
        (root / "beta" / "README.md").write_text(
            scope_readme("BET", "乙"), encoding="utf-8")
        alpha_doc = root / "alpha" / "ALP-L2-001.md"
        beta_doc = root / "beta" / "BET-L2-001.md"

        alpha_doc.write_text(doc("ALP-L2-001", "L2", (
            item("ALP-FR-001", "甲需求", "初稿")
            + item("ALP-FR-002", "甲目标", "正式"))), encoding="utf-8")
        beta_doc.write_text(doc("BET-L2-001", "L2", (
            item("BET-FR-001", "乙需求", "草案", [
                ("ALP-FR-001", "甲需求",
                 "../alpha/ALP-L2-001.md#alp-fr-001")])
            + item("BET-FR-002", "乙目标", "正式", [
                ("ALP-FR-002", "甲目标",
                 "../alpha/ALP-L2-001.md#alp-fr-002")]))), encoding="utf-8")

        checker = check_docs.DesignDocChecker(str(root))
        with contextlib.redirect_stdout(io.StringIO()):
            checker.run_cross_scope_deps()
        check("跨作用域依赖指向初稿",
              any("BET-FR-001" in i["description"] and "ALP-FR-001" in i["description"]
                  for i in hits(checker, "跨作用域依赖指向初稿")))
        check("跨作用域依赖图按原义记录",
              "ALP-FR-001" in checker.dep_forward.get("BET-FR-001", []))

        alpha_doc.write_text(doc("ALP-L2-001", "L2", (
            item("ALP-FR-001", "甲需求", "正式")
            + item("ALP-FR-002", "甲目标", "正式", [
                ("BET-FR-002", "乙目标",
                 "../beta/BET-L2-001.md#bet-fr-002")]))), encoding="utf-8")
        checker = check_docs.DesignDocChecker(str(root))
        with contextlib.redirect_stdout(io.StringIO()):
            checker.run_cross_scope_deps()
        check("跨子系统依赖环报 ERROR",
              any(i["level"] == "ERROR" and "ALP-FR-002" in i["description"]
                  for i in hits(checker, "依赖成环")))

        checker = check_docs.DesignDocChecker(str(root / "beta"))
        with contextlib.redirect_stdout(io.StringIO()):
            checker.run_cross_scope_deps()
        check("非系统根拒绝跨作用域检查",
              hits(checker, "跨作用域依赖检查未在系统根运行"))

    if fails:
        print("FAIL 细项依赖图用例未通过")
        for name in fails:
            print(f"     未通过：{name}")
        return 1
    print("细项依赖图用例通过")
    return 0


def run_template_body_hygiene_cases():
    """哨兵内写作约束 / 技能包路径 MUST 报；干净正文 MUST 不报。"""
    import importlib.util

    spec = importlib.util.spec_from_file_location("check_docs", CHECKER)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    cases = [
        ("leak-label", """> **模板：x**
>
> **正文边界**：TEMPLATE:BEGIN

<!-- TEMPLATE:BEGIN -->
# L2-001-x

> **编码形式**：默认使用简洁编码（{类型码}-{三位序号}）
<!-- TEMPLATE:END -->
""", {"写作约束混入待复制正文"}),
        ("leak-path", """> **模板：x**
>
> **正文边界**：TEMPLATE:BEGIN

<!-- TEMPLATE:BEGIN -->
# L2-001-x

口径见 references/coding-system.md
<!-- TEMPLATE:END -->
""", {"技能包路径混入待复制正文"}),
        ("ok-body", """> **模板：x**
>
> **正文边界**：TEMPLATE:BEGIN

<!-- TEMPLATE:BEGIN -->
# L2-001-x

见 {文档相对路径}
<!-- TEMPLATE:END -->
""", set()),
    ]
    fails = []
    for name, text, want in cases:
        checker = mod.TemplateChecker()
        checker._check_one(Path(f"{name}.md"), text)
        have = {i["title"] for i in checker.issues}
        missing = want - have
        unexpected = (have & {"写作约束混入待复制正文", "技能包路径混入待复制正文",
                              "使用说明混入待复制正文"}) - want
        if missing or unexpected:
            fails.append((name, missing, unexpected, have))
            print(f"  FAIL {name}")
            if missing:
                print(f"       漏报：{'、'.join(sorted(missing))}")
            if unexpected:
                print(f"       误报：{'、'.join(sorted(unexpected))}")
    if fails:
        print("FAIL 模板正文禁区正反例未通过")
        return 1
    print("模板正文禁区正反例通过")
    return 0


def run_check_templates_smoke():
    """本包 `--check-templates` 必须通过（哨兵 + 技能包内部锚点）。"""
    proc = subprocess.run(
        [sys.executable, str(CHECKER), "--check-templates"],
        capture_output=True, text=True, timeout=120)
    if proc.returncode != 0:
        sys.stdout.write(proc.stdout)
        sys.stderr.write(proc.stderr)
        print("FAIL --check-templates 冒烟未通过")
        return 1
    print("--check-templates 冒烟通过")
    return 0


def main():
    require_test_deps()
    verbose = "-v" in sys.argv or "--verbose" in sys.argv
    proc = subprocess.run(
        [sys.executable, str(CHECKER), "-p", str(FIXTURES)],
        capture_output=True, text=True, timeout=600)
    got = parse(proc.stdout + "\n" + proc.stderr)

    on_disk = {p.stem for p in FIXTURES.glob("*.md")}
    orphan = sorted(on_disk - set(EXPECT))      # 新增夹具未登记期望
    stale = sorted(set(EXPECT) - on_disk)       # 期望表里的夹具已不存在

    fails = []
    for stem in sorted(EXPECT):
        want, have = EXPECT[stem], got.get(stem, set())
        missing, unexpected = want - have, have - want
        if missing or unexpected:
            fails.append((stem, missing, unexpected))
        if verbose:
            mark = "FAIL" if (missing or unexpected) else "ok  "
            print(f"  [{mark}] {stem}")
            if missing:
                print(f"           漏报：{'、'.join(sorted(missing))}")
            if unexpected:
                print(f"           误报：{'、'.join(sorted(unexpected))}")

    total = len(EXPECT)
    print(f"\n夹具 {total} 条，通过 {total - len(fails)} 条")
    if not verbose:
        for stem, missing, unexpected in fails:
            print(f"  FAIL {stem}")
            if missing:
                print(f"       漏报：{'、'.join(sorted(missing))}")
            if unexpected:
                print(f"       误报：{'、'.join(sorted(unexpected))}")
    for stem in orphan:
        print(f"  FAIL {stem}：夹具存在但未在 EXPECT 登记期望")
    for stem in stale:
        print(f"  FAIL {stem}：EXPECT 登记的夹具已不在 fixtures/")
    rc = 1 if (fails or orphan or stale) else 0
    rc |= run_glossary_fixtures(verbose)
    rc |= run_skill_link_fixtures(verbose)
    rc |= run_baseline_bump_cases()
    rc |= run_single_scope_and_extension_cases()
    rc |= run_cross_scope_glossary_cases()
    rc |= run_pin_scope_and_history_cases()
    rc |= run_dep_graph_cases()
    rc |= run_template_body_hygiene_cases()
    rc |= run_check_templates_smoke()
    return 1 if rc else 0


if __name__ == "__main__":
    sys.exit(main())
