#!/usr/bin/env python3
"""`check_docs.py` 的规则回归集跑台。

`fixtures/` 下每条夹具是一个最小 L2 文档，刻意触发（或刻意不触发）某一条校验
规则。改动 `check_docs.py` 后跑一遍，可确认既有规则没有静默退化。

跑台只断言**目标问题名**（见 `EXPECT`），忽略夹具因极简结构必然产生的结构性
噪声（见 `NOISE`）——夹具只为验证单条规则，不追求自身是一份合规文档。

用法：
    python3 scripts/tests/run_fixtures.py       # 全量
    python3 scripts/tests/run_fixtures.py -v    # 附带每条夹具的命中详情
"""
import re
import sys
import subprocess
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
FIXTURES = ROOT / "fixtures"
CHECKER = ROOT.parent / "check_docs.py"

SECTION = re.compile(r"^###\s+(?:ERROR|WARNING|INFO)")
ITEM = re.compile(r"^\d+\.\s+(.+?)\s*$")
# 夹具名 MAY 带项目编码前缀（如 `W3T-L2-929-prefix-digit.md`），前缀字符集与
# check_docs.py 的 PROJECT_PREFIX 同口径。
FIXTURE = re.compile(r"((?:[A-Z][A-Z0-9]{1,4}-)?L\d+-\d+-[a-z0-9\-]+)\.md")

# 夹具极简（无变更记录表、无清单表、无完整章节、编码从 9xx 起跳）必然触发的
# 结构性问题，与本回归集要验证的规则无关，一律不计入断言。
NOISE = {
    "缺少变更记录", "缺少细项编码清单", "缺少必需章节", "引用悬空",
    "细项未登记入清单", "编码序列存在缺口", "细项待定稿", "文档待定稿",
}

# 夹具 → 期望命中的目标问题名（空集 = 该规则的正例，MUST 零命中）。
# 夹具名即规则语义，改检查器的问题名时 MUST 同步此表。
EXPECT = {
    # —— 治理段（属性行组首三行） ——
    "L2-902-no-status":           {"定义块缺细项状态属性行"},
    "L2-903-status-not-first":    {"细项状态未位于属性行组首行"},
    "L2-904-gov-order":           {"治理段顺序错乱"},
    "L2-905-gov-missing":         {"治理段缺行"},
    "L2-906-gov-badval":          {"修订版本号取值非法", "最后修订日期取值非法"},
    # —— 追溯段（属性行组末尾，出处 → 来源） ——
    "L2-907-trace-mid":           {"追溯段未位于属性行组末尾"},
    "L2-908-trace-order":         {"追溯段顺序错乱"},
    "L2-909-src-nolink":          {"来源值缺链接"},
    "L2-910-origin-link":         {"出处值含链接"},
    # `来源` MAY 多行（每行一个来源对象），同名多行 MUST NOT 被判为顺序错乱
    "L2-928-trace-multi-source":  set(),
    # —— 层级门控（解冻自顶向下、定稿自底向上） ——
    "L2-915-gate-draft-item":     {"细项草案而文档正式", "文档定稿前置未满足"},
    "L2-916-gate-new-item":       {"文档定稿前置未满足"},
    "L2-917-gate-ok-draftdoc":    set(),
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


def main():
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
    return 1 if (fails or orphan or stale) else 0


if __name__ == "__main__":
    sys.exit(main())
