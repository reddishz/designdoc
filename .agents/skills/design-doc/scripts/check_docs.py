#!/usr/bin/env python3
"""
DesignDoc 文档检查工具

对 `ued/` 下的设计文档做静态校验：

- 文档编码 / 细项编码格式、唯一性、引用是否存在
- 状态字段：文档 `状态`、细项 `细项状态` 统一取标准四态；L6 追溯矩阵 `追溯状态`
- 旧状态值（`草稿` / `提议` / `采纳` / `登记中` / `使用中` / `验证状态` 等）的迁移提示
- 正文定义 / 本文档清单 / 作用域 README 全局索引三方的编码与状态一致
- 锁定矩阵：标题与引用处的一致性（`--refs CODE` 可反查某编码的全部出现位置）
- 版本号递增时机（仅 `正式→草案` 解冻时递增）、回退记录完整性、版本号不复用
- 废弃流程字段（含 `建议归档日期`）、`替代方案` 值形态与活跃引用
- REF 时效字段齐备性与复查周期（超期提示复核）
- PLN 闭环：`落实情况` 与 `落实记录` 一致、已落实者被目标细项 `来源` 回指；未落实者的 `建议复审日期`（到期提示）
- README 全局索引升序、编码缺口、计数器一致性
- 零章节编号引用门禁、文件名与结构合规
- 定义块形态：禁粗体式定义位、锚点行齐备且与编码一致、属性行形态、三部分连续
- 属性行组三段：治理段（`细项状态` / `修订版本号` / `最后修订日期`）齐备且居首、追溯段（`出处` → `来源`）居末且值形态互斥
- 修订号不变式：`初稿` → rev = 1、`草案` → rev ≥ 2、`最后修订日期` 不晚于本文档 `变更记录` 最新日期
- 层级门控：解冻自顶向下（细项 `草案` 而文档 `正式` = 结构违规）、定稿自底向上（文档 `正式` 而有未定稿细项 → 提示确认）
- 锚点可达性：链接的 `#fragment` 在目标文档的锚点集合（显式 id ∪ 标题 slug）中存在
- ADR / REF 的必备小节；`DEC` 落在 L2/L3 时的量级提示（升格为 ADR）
- `初稿` / `草案` 对象的定稿提醒（不阻断）
- `--check-templates`：`assets/templates/` 的哨兵房规（成对、唯一 H1、无残留外层围栏）
- `--instantiate TPL`：剥除哨兵输出模板实例化后的正文，供预览评估

规则本体的唯一完整表述在 `references/` 专项文件内，本脚本只执行校验、不重复定义
规则；类型码清单优先从 `references/coding-system.md` 的类型码表读取，读取失败时
回退到内置快照。
"""

import os
import re
import sys
import calendar
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Set, Tuple

SKILL_ROOT = Path(__file__).resolve().parents[1]
CODING_SYSTEM_MD = SKILL_ROOT / "references" / "coding-system.md"

# 回退快照：与 references/coding-system.md 的类型码表保持一致
FALLBACK_TYPE_CODES = {
    "GOL", "STK", "SCN", "FR", "NFR", "UC", "PRN", "DEC", "CMP", "IF", "FLW",
    "ALG", "DOM", "ASM", "RSK", "MET", "TC", "AC", "CON", "RUL", "ACT", "PLN",
    "REF",
}
DOC_CODE_PREFIXES = {"L0", "L1", "L2", "L3", "L4", "L5", "L6", "ADR", "REF"}
LEGACY_TYPE_CODES = {"API", "FLD", "DICT", "README", "CHANGELOG"}

# 标准四态：唯一生命周期状态集合（L0-L6 / ADR / REF / PLN 共用，不设专属枚举）
DOC_STATUSES = ["初稿", "正式", "草案", "废弃"]
DEFAULT_DOC_STATUS = "初稿"
ITEM_STATUSES = DOC_STATUSES
TRACE_STATUSES = ["未追溯", "已追溯", "不适用"]

# 旧状态值 → 标准四态的迁移兼容层；命中即报 INFO 提示改写，不直接判为无效值。
# `草稿` 无固定映射（值 None）：按 `变更记录` 判定——有定稿条目 → `草案`，
# 从未定稿 → `初稿`，无法判定 → `草案`（保守侧）。
LEGACY_STATUS_MAP: Dict[str, Optional[str]] = {
    "草稿": None,
    "提议": "初稿", "采纳": "正式", "拒绝": "废弃", "取代": "废弃",
    "登记中": "初稿", "有效": "正式",
    "使用中": "正式", "已停用": "废弃",
    "已废弃": "废弃", "已正式": "正式", "已完成定稿": "正式",
    "已采纳": "正式", "已被取代": "废弃",
}
LEGACY_TRACE_MAP = {"待验证": "未追溯", "已验证": "已追溯", "失败": ""}
# PLN 旧的第二套枚举（`规划状态`）与 L6 旧的追溯列名，只用于迁移提示
LEGACY_PLAN_MAP = {
    "待考虑": "初稿", "已纳入规划": "正式",
    "已落实": "正式", "不再考虑": "废弃",
}
LEGACY_TRACE_COLUMN = "验证状态"
TRACE_COLUMN = "追溯状态"

FINALIZE_KW = re.compile(
    r"定稿|转为正式|升为正式|评审通过|正式发布|(?:草稿|初稿|草案)\s*(?:→|->)\s*正式")
UNFREEZE_KW = re.compile(r"解冻|正式\s*(?:→|->)\s*(?:草稿|草案)|转(?:草稿|草案)")
ROLLBACK_KW = re.compile(r"回退|放弃本轮修订|放弃修订|撤回修订")
INIT_KW = re.compile(r"初始|新建|创建|初稿")

CODE_TOKEN = re.compile(
    r"(?<![A-Za-z0-9_-])((?:[A-Z]{2,4}-)?([A-Z]{1,5}[0-9]?)-(\d{2,4}))(?![0-9A-Za-z])"
)
ITEM_BOLD_DEF = re.compile(r"^\s*[-*+]\s+\*\*((?:[A-Z]{2,4}-)?[A-Z]{1,5}[0-9]?-\d{2,4})\*\*\s*[:：]")
FENCE = re.compile(r"^\s*(`{3,}|~{3,})")
FENCE_CLOSE = re.compile(r"^\s*(`{3,}|~{3,})\s*$")
SEP_CELL = re.compile(r"^:?-{2,}:?$")
VERSION_RE = re.compile(r"^v\d+\.\d+$")
CODE_CELL = re.compile(r"(?:[A-Z]{2,4}-)?([A-Z]{1,5}[0-9]?)-(\d{2,4})(?=$|[ \uff1a:\uff08(\-\u2014\u3001,])")
BOLD_ATTR = re.compile(r"^\s*(?:[-*+]\s*)?\*\*(细项状态|状态)\*\*\s*[:\uff1a]\s*(.*)$")
TITLE_LINK = re.compile(
    r"\[((?:[A-Z]{2,4}-)?[A-Z]{1,5}[0-9]?-\d{2,4})\uff08([^\uff09]+)\uff09\]")
REF_TIME_FIELDS = ("来源版本", "获取日期", "最近核验日期", "复查周期", "失效风险")
REF_FIELD = re.compile(
    r"^\s*(?:[-*+]\s*)?\*\*(" + "|".join(REF_TIME_FIELDS) + r")\*\*\s*[:\uff1a]\s*(.*)$")
STATUS_NOTE_SUFFIX = re.compile(r"[\uff08(][^\uff09)]*[\uff09)]\s*$")
PLN_RECORD_FIELDS = ("建议复审日期", "落实情况", "落实记录", "废弃原因")
# `落实情况` 的封闭值域（房规：coding-system.md ·《PLN 治理规则》第 10 条）
PLN_LANDING_VALUES = ("未落实", "已落实")
# 属性行允许在 `**字段名**` 与冒号之间带一段括号说明，如 `**落实记录**（记录型字段）：`
PLN_FIELD = re.compile(
    r"^\s*(?:[-*+]\s*)?\*\*(" + "|".join(PLN_RECORD_FIELDS) + r")\*\*"
    r"(?:\uff08[^\uff09)]*\uff09|\([^)]*\))?\s*[:\uff1a]\s*(.*)$")
BOLD_ATTR_ANY = re.compile(
    r"^\s*(?:[-*+]\s*)?\*\*[^*\n]{1,24}\*\*"
    r"(?:\uff08[^\uff09)]*\uff09|\([^)]*\))?\s*[:\uff1a]")
EMPTY_MARKS = ("无", "暂无", "-", "—", "n/a")

# ---- 定义块形态与锚点（房规：coding-system.md ·《细项定义块形态》《锚点定义位》）----
ANCHOR_TAG = re.compile(r"""^\s*<a\s+(?:id|name)\s*=\s*["']([^"']+)["']""", re.IGNORECASE)
HEADING_LINE = re.compile(r"^\s{0,3}(#{1,6})\s+(.*)$")
# 合规属性行：列表项 + 要素名加粗（允许字段名后带括号说明）
ATTR_LINE_OK = re.compile(
    r"^\s*[-*+]\s+\*\*[^*\n]{1,24}\*\*"
    r"(?:\uff08[^\uff09)]*\uff09|\([^)]*\))?\s*[:\uff1a]")
# 禁止形态一：裸段落（有加粗、无列表符）
ATTR_LINE_NO_BULLET = re.compile(
    r"^\s{0,3}\*\*[^*\n]{1,24}\*\*"
    r"(?:\uff08[^\uff09)]*\uff09|\([^)]*\))?\s*[:\uff1a]")
# 禁止形态二：列表项但要素名未加粗
ATTR_LINE_NO_BOLD = re.compile(r"^\s*[-*+]\s+([^*\n\[\]#]{1,16})\s*[:\uff1a]")
# 禁止形态三：裸段落且要素名未加粗（如 `所属组件：…`）。限定短要素名、
# 不以数字开头（避开 `1. 想法内容：` 类续行）、不含句读（避开散文段落）。
ATTR_LINE_BARE_PLAIN = re.compile(
    r"^\s{0,3}([^*\s>#\-|{\d][^*\n|]{0,11})\s*[:\uff1a]\s*\S")
ATTR_NAME_PROSE = re.compile(r"[\u3002\uff0c\uff1b\uff1f\uff01,;?!]")
MD_LINK = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")
INLINE_CODE = re.compile(r"`[^`]*`")
# 属性行拆分：与 ATTR_LINE_OK 同口径，另捕获要素名与值（供三段校验取用）
ATTR_NAME_VALUE = re.compile(
    r"^\s*[-*+]\s+\*\*([^*\n]{1,24})\*\*"
    r"(?:\uff08[^\uff09)]*\uff09|\([^)]*\))?\s*[:\uff1a]\s*(.*)$")
# 属性行组三段（房规：coding-system.md ·《细项定义块形态》）
GOV_SEGMENT = ("细项状态", "修订版本号", "最后修订日期")
TRACE_SEGMENT = ("出处", "来源")          # 追溯段固定序：`出处` 在 `来源` 之前
REV_VALUE = re.compile(r"^\d+$")
DATE_VALUE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
DATE_IN_TEXT = re.compile(r"\d{4}-\d{2}-\d{2}")   # 表格单元格内提取日期（可带后缀说明）

CHANGELOG_HEADINGS = ("变更记录", "变更历史", "版本历史", "修订记录")
ITEM_LIST_HEADINGS = ("细项编码清单", "细项清单", "全局编码索引", "编码索引")

# 模板哨兵：`assets/templates/` 用 HTML 注释界定「待复制正文」，取代 ```markdown
# 外层围栏（围栏会使正文不可渲染，且与正文内 ```mermaid 等嵌套围栏相互破坏）。
# 房规本体单点承载于 assets/templates/index.md · 模板边界（哨兵）。
TEMPLATE_DIR = SKILL_ROOT / "assets" / "templates"
TPL_BEGIN = re.compile(r"^<!--\s*TEMPLATE:BEGIN(?:\s+(.*?))?\s*-->$")
TPL_END = re.compile(r"^<!--\s*TEMPLATE:END\s*-->$")
TPL_LABEL = re.compile(r"^>\s+\*\*(.+?)\*\*\s*$")
TPL_FENCE_WRAP = re.compile(r"^\s*(?:`{3,}|~{3,})\s*markdown\s*$")
TPL_USAGE_HEAD = re.compile(r"^#{1,6}\s+使用说明\s*$")
# 片段型模板：正文是嵌入宿主文档的片段，容器保留自身标题结构
TPL_FRAGMENT_FILES = {"project-registry.md"}
# 目录内的索引文件，不是模板，不含哨兵
TPL_NON_FILES = {"index.md"}


def load_type_codes() -> Set[str]:
    """从规范文件读取类型码表首列；失败时回退内置快照。"""
    try:
        text = CODING_SYSTEM_MD.read_text(encoding="utf-8")
    except OSError:
        return set(FALLBACK_TYPE_CODES)
    lines = text.splitlines()
    codes: Set[str] = set()
    in_table = False
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("### "):
            in_table = stripped.startswith("### 类型码表")
            continue
        if not in_table:
            continue
        if not stripped.startswith("|"):
            if codes and stripped:
                break
            continue
        cells = split_row(line)
        if not cells:
            continue
        head = cells[0].replace("*", "")
        if head in ("类型码", "") or SEP_CELL.match(head):
            continue
        if re.fullmatch(r"[A-Z]{1,5}[0-9]?", head):
            codes.add(head)
    return codes or set(FALLBACK_TYPE_CODES)


def split_row(line: str) -> List[str]:
    """把 Markdown 表格行拆成去空白单元格列表；非表格行返回 []。"""
    stripped = line.strip()
    if not stripped.startswith("|"):
        return []
    body = stripped.strip("|")
    return [c.strip() for c in body.split("|")]


def is_sep_row(cells: List[str]) -> bool:
    return bool(cells) and all(SEP_CELL.match(c) for c in cells if c != "") and \
        any(SEP_CELL.match(c) for c in cells)


def mask_fences(text: str) -> List[str]:
    """返回把代码围栏内容清空后的行列表（围栏行本身也清空）。"""
    out: List[str] = []
    fence_char = ""
    fence_len = 0
    for line in text.splitlines():
        opener = FENCE.match(line)
        closer = FENCE_CLOSE.match(line)
        if fence_char:
            out.append("")
            if closer and closer.group(1)[0] == fence_char and len(closer.group(1)) >= fence_len:
                fence_char, fence_len = "", 0
            continue
        if opener:
            fence_char, fence_len = opener.group(1)[0], len(opener.group(1))
            out.append("")
            continue
        out.append(line)
    return out


def heading_slug(text: str) -> str:
    """按 GitHub / cmark-gfm 规则把标题文本转为自动 slug（仅用于锚点可达性判定）。

    小写 → 去行内标记与标点（保留字母数字、下划线、连字符、中日韩文字）
    → 空格转连字符。如《ADR 与 DEC 的定位》→ `adr-与-dec-的定位`。

    细项锚点 MUST NOT 依赖本 slug（会随标题改动而失效，房规见《锚点定义位》）；
    本函数只用于判定小节链接能不能跳得过去。
    """
    s = re.sub(r"<[^>]*>", "", text.strip().lower())
    s = s.replace("`", "").replace("*", "")
    s = re.sub(r"[^\w\u4e00-\u9fff\- ]", "", s)
    return s.replace(" ", "-")


def template_segments(lines: List[str]) -> Tuple[List[Dict], List[str]]:
    """切出模板哨兵段，返回 (段列表, 配对错误描述)。

    段结构 `{name, begin, end, body}`，`begin` / `end` 为哨兵行号（1 起）；
    未闭合的段 `end` 为 0。哨兵 MUST 成对、不嵌套、各自独占一行。
    """
    segs: List[Dict] = []
    errs: List[str] = []
    cur: Optional[Dict] = None
    for n, line in enumerate(lines, 1):
        begin, end = TPL_BEGIN.match(line), TPL_END.match(line)
        if begin:
            if cur is not None:
                errs.append(f"{n}: `TEMPLATE:BEGIN` 未闭合即再次开启（哨兵 MUST NOT 嵌套）")
                segs.append(cur)
            cur = {"name": (begin.group(1) or "").strip(), "begin": n, "end": 0, "body": []}
        elif end:
            if cur is None:
                errs.append(f"{n}: 孤立的 `TEMPLATE:END`（无配对 `TEMPLATE:BEGIN`）")
                continue
            cur["end"] = n
            segs.append(cur)
            cur = None
        elif cur is not None:
            cur["body"].append(line)
    if cur is not None:
        errs.append(f"{cur['begin']}: `TEMPLATE:BEGIN` 直到文件结束仍未闭合")
        segs.append(cur)
    return segs, errs


def instantiate_template(text: str) -> List[Tuple[str, str]]:
    """把模板还原为「实例化后的文档」：[(段名, 正文)]。

    只保留哨兵之间的内容并删除两行哨兵，等价于 AI 实例化的产物；
    哨兵外的模板名、元信息与使用说明一律不进入结果。
    """
    segs, _errs = template_segments(text.splitlines())
    return [(s["name"], "\n".join(s["body"]).strip("\n") + "\n")
            for s in segs if s["end"]]


def norm(value: str) -> str:
    """去掉单元格里的 markdown 修饰，便于比对。"""
    v = value.replace("*", "").replace("`", "").strip()
    return re.sub(r"\s+", " ", v)


def parse_review_period(text: str) -> Optional[int]:
    """把 REF 的 `复查周期` 文本解析为月数；无法解析返回 None。"""
    t = norm(text)
    if not t or "{" in t or "/" in t:
        return None
    m = re.search(r"(\d+)\s*个?\s*月", t)
    if m:
        return int(m.group(1))
    m = re.search(r"(\d+)\s*年", t)
    if m:
        return int(m.group(1)) * 12
    if "半年" in t:
        return 6
    m = re.search(r"(\d+)\s*(?:天|日)", t)
    if m:
        return max(1, int(m.group(1)) // 30)
    return None


def add_months(base, months: int):
    """日期加月数（溢出则取当月最后一天）。"""
    total = base.month - 1 + months
    year = base.year + total // 12
    month = total % 12 + 1
    day = min(base.day, calendar.monthrange(year, month)[1])
    return base.replace(year=year, month=month, day=day)


def iter_tables(lines: List[str]) -> Iterable[Tuple[int, List[str], List[Tuple[int, List[str]]]]]:
    """遍历表格：产出 (表头行号, 表头单元格, [(行号, 单元格)])。"""
    i = 0
    n = len(lines)
    while i < n:
        head = split_row(lines[i])
        if head and i + 1 < n and is_sep_row(split_row(lines[i + 1])):
            rows: List[Tuple[int, List[str]]] = []
            j = i + 2
            while j < n:
                cells = split_row(lines[j])
                if not cells:
                    break
                rows.append((j, cells))
                j += 1
            yield i, head, rows
            i = j
            continue
        i += 1


def col_index(header: List[str], *names: str) -> Optional[int]:
    clean = [norm(h) for h in header]
    for name in names:
        if name in clean:
            return clean.index(name)
    for idx, cell in enumerate(clean):
        for name in names:
            if name in cell:
                return idx
    return None


@dataclass
class ItemInfo:
    code: str
    type_code: str
    number: int
    path: str
    line: int
    item_status: str = ""
    raw_status: str = ""          # 清单/索引行状态单元格原文，供旧值按所属文档重判
    def_status: str = ""          # 定义块内粗体属性行 `**细项状态**：X` 的值
    defined: bool = False
    listed: bool = False


@dataclass
class DocInfo:
    """文档信息"""
    path: str
    doc_code: str = ""
    doc_type: str = "UNKNOWN"
    layer: str = ""
    status: str = ""
    status_present: bool = False
    status_category: str = ""
    version: str = ""
    content: str = ""
    is_index: bool = False          # README.md 等作用域索引文件
    lines: List[str] = field(default_factory=list)        # 已屏蔽代码围栏
    raw_lines: List[str] = field(default_factory=list)
    meta: Dict[str, str] = field(default_factory=dict)
    items: List[ItemInfo] = field(default_factory=list)
    code_sections: List[Tuple[str, List[Tuple[int, str, int]]]] = field(default_factory=list)
    counters: List[Tuple[str, str]] = field(default_factory=list)

    @property
    def archived(self) -> bool:
        return "/deprecated/" in self.path.replace(os.sep, "/")


class DesignDocChecker:
    """设计文档检查器"""

    def __init__(self, ued_path: str = "./ued"):
        self.ued_path = Path(ued_path)
        self.type_codes = load_type_codes()
        self.known_types = self.type_codes | DOC_CODE_PREFIXES | LEGACY_TYPE_CODES
        self.docs: List[DocInfo] = []
        self.codes: Set[str] = set()
        self.code_to_doc: Dict[str, DocInfo] = {}
        self.item_def_doc: Dict[str, DocInfo] = {}   # 细项编码 → 定义所在文档
        self.doc_by_path: Dict[str, DocInfo] = {}    # 归一化路径 → 文档（跨文档锚点解析用）
        self.anchor_cache: Dict[str, Set[str]] = {}  # 路径 → 可达锚点集合
        self.chg_date_cache: Dict[str, str] = {}     # 路径 → 变更记录最新日期
        self.issues: List[Dict] = []
        self.legacy_hits: Set[Tuple[str, str]] = set()   # (文件, 旧值 → 新值)

    # ------------------------------------------------------------------ 扫描

    def scan_docs(self) -> None:
        """扫描所有文档"""
        if not self.ued_path.exists():
            self.add_issue("CRITICAL", "UED目录不存在", f"未找到 {self.ued_path} 目录")
            return

        for md_file in sorted(self.ued_path.rglob("*.md")):
            try:
                content = md_file.read_text(encoding="utf-8")
            except Exception as exc:  # noqa: BLE001
                self.add_issue("ERROR", "读取文档失败", f"{md_file}: {exc}")
                continue
            self.docs.append(self.parse_doc_info(str(md_file), content))
        self._build_code_maps()

    def _build_code_maps(self) -> None:
        """建立编码 → 文档映射，并重判索引 / 清单行里的旧值 `草稿`。"""
        for doc in self.docs:
            self.doc_by_path[os.path.normpath(doc.path)] = doc
            if doc.doc_code:
                self.codes.add(doc.doc_code)
                self.code_to_doc.setdefault(doc.doc_code, doc)
            for item in doc.items:
                if item.defined:
                    self.item_def_doc.setdefault(item.code, doc)
        self._resolve_legacy_status()

    def _resolve_legacy_status(self) -> None:
        """按被登记编码所属文档重判旧值 `草稿`，消除索引行与源文件的结论分歧。

        索引 / 清单行自身没有 `变更记录`；若不重判，同一编码会在源文件得到
        `初稿`、在索引行得到保守侧 `草案`，进而误报「同一编码状态不一致」。
        """
        for doc in self.docs:
            for item in doc.items:
                if item.raw_status not in LEGACY_STATUS_MAP:
                    continue
                if LEGACY_STATUS_MAP[item.raw_status] is not None:
                    continue          # 有固定映射的旧值与判定文件无关
                ctx = self._status_ctx(item.code, doc)
                if ctx is doc:
                    continue
                stale = f"{item.raw_status} → {item.item_status}"
                fixed = self._norm_status(item.raw_status, doc, ctx)
                if not fixed or fixed == item.item_status:
                    continue
                self.legacy_hits.discard((doc.path, stale))
                item.item_status = fixed

    def parse_doc_info(self, path: str, content: str) -> DocInfo:
        """解析文档信息：元信息表、细项定义、细项清单/索引表、计数器表。"""
        raw_lines = content.splitlines()
        lines = mask_fences(content)
        doc = DocInfo(
            path=path,
            content=content,
            lines=lines,
            raw_lines=raw_lines,
            is_index=Path(path).name.upper() == "README.MD",
        )

        doc.meta = self._parse_meta_table(lines)
        if doc.meta.get("文档编号") and not doc.meta.get("文档编码"):
            doc.meta["文档编码"] = doc.meta["文档编号"]
        doc.doc_code = doc.meta.get("文档编码") or ""
        doc.status_present = bool(doc.meta.get("状态") or doc.meta.get("文档状态"))
        doc.status = self._norm_status(doc.meta.get("状态") or doc.meta.get("文档状态") or "", doc)
        doc.version = doc.meta.get("版本") or doc.meta.get("文档版本") or ""
        if "文档编号" in doc.meta:
            self.add_issue("WARNING", "元信息字段名不规范",
                           f"{path}: 字段 `文档编号` 应用 `文档编码`（与索引表列名、编码体系术语一致）")

        if doc.doc_code:
            first = doc.doc_code.split("-")[0]
            if first in DOC_CODE_PREFIXES:
                doc.status_category = first
                doc.layer = first if first.startswith("L") else ""
                doc.doc_type = first
            else:
                doc.doc_type = f"UNKNOWN-{first}"

        self._parse_items(doc)
        return doc

    def _parse_meta_table(self, lines: List[str]) -> Dict[str, str]:
        """取第一张「属性 | 值」两列表格作为文档元信息。"""
        meta: Dict[str, str] = {}
        for _idx, header, rows in iter_tables(lines):
            if len(header) != 2:
                continue
            if norm(header[0]) not in ("属性", "字段"):
                continue
            for _row_idx, cells in rows:
                if len(cells) < 2:
                    continue
                key = norm(cells[0])
                if key and key not in meta:
                    meta[key] = norm(cells[1])
            break
        return meta

    def _norm_status(self, value: str, doc: Optional[DocInfo] = None,
                     ctx: Optional[DocInfo] = None) -> str:
        """归一状态值：去注记后缀、兼容旧值；占位写法视为未填写。

        `doc` 是命中文件（决定报告归属），`ctx` 是判定文件（其 `变更记录` 决定旧值
        `草稿` 的迁移目标）；索引 / 清单行描述的是被登记的编码，二者可以不同。
        """
        v = norm(value)
        if not v:
            return ""
        # 去掉 `（默认）` 等注记后缀，模板与存量文档可能带此写法
        v = STATUS_NOTE_SUFFIX.sub("", v).strip()
        # 占位写法（枚举、模板变量）视为未填写
        if "{" in v or "}" in v or "/" in v or "、" in v:
            return ""
        if v in LEGACY_STATUS_MAP:
            target = LEGACY_STATUS_MAP[v] or self._legacy_draft_target(ctx or doc)
            if doc is not None:
                self.legacy_hits.add((doc.path, f"{v} → {target}"))
            return target
        return v

    def _status_ctx(self, code: str, doc: DocInfo) -> DocInfo:
        """索引 / 清单行的状态判定文件：取该编码所属文档，取不到则用当前文件。

        README 等索引文件自身没有 `变更记录`，若拿当前文件判定，同一个对象的旧值
        `草稿` 会在源文件与索引行得出不同的迁移目标。
        """
        if not code:
            return doc
        return self.code_to_doc.get(code) or self.item_def_doc.get(code) or doc

    def _legacy_draft_target(self, doc: Optional[DocInfo]) -> str:
        """旧值 `草稿` 的迁移目标：按 `变更记录` 判定，无法判定取保守侧 `草案`。"""
        if doc is None:
            return "草案"
        rows = self._changelog_rows(doc)
        if not rows:
            return "草案"
        for _ver, desc in rows:
            if FINALIZE_KW.search(desc):
                return "草案"
        return "初稿"

    def _block_status_attr(self, doc: DocInfo, idx: int) -> str:
        """取定义块内粗体属性行 `**细项状态**：X` 的值（PLN 等以属性块定义细项）。"""
        lines = doc.lines
        hm = re.match(r"^\s{0,3}(#{1,6})\s+", lines[idx])
        level = len(hm.group(1)) if hm else 0
        for j in range(idx + 1, len(lines)):
            line = lines[j]
            nm = re.match(r"^\s{0,3}(#{1,6})\s+", line)
            if nm:
                if level and len(nm.group(1)) <= level:
                    break
                continue
            if level == 0 and self._heading_code(line):
                break
            m = BOLD_ATTR.match(line)
            if m:
                return self._norm_status(m.group(2), doc)
        return ""

    def _parse_items(self, doc: DocInfo) -> None:
        """收集细项：定义位（标题/粗体项）与登记位（含 `细项状态` 列的表格）。"""
        seen: Dict[str, ItemInfo] = {}

        def touch(code: str, type_code: str, number: int, line: int) -> ItemInfo:
            key = f"{code}@{doc.path}"
            item = seen.get(key)
            if item is None:
                item = ItemInfo(code=code, type_code=type_code, number=number,
                                path=doc.path, line=line)
                seen[key] = item
                doc.items.append(item)
            return item

        for i, line in enumerate(doc.lines):
            code = self._heading_code(line)
            if not code:
                continue
            code, t, num = self._split_code(code)
            if not code or t not in self.type_codes:
                continue
            item = touch(code, t, num, i + 1)
            item.defined = True
            if not item.def_status:
                item.def_status = self._block_status_attr(doc, i)

        for head_idx, header, rows in iter_tables(doc.lines):
            status_col = col_index(header, "细项状态")
            plan_col = col_index(header, "规划状态")
            heading = self._nearest_heading(doc.lines, head_idx)
            is_item_list = any(k in heading for k in ITEM_LIST_HEADINGS)
            if status_col is None and plan_col is None and not is_item_list:
                continue
            code_col = col_index(header, "编码")
            if code_col is None:
                continue
            section = heading or "表格"
            for row_idx, cells in rows:
                if code_col >= len(cells):
                    continue
                code, t, num = self._split_code(norm(cells[code_col]))
                if not code or t not in self.known_types:
                    continue
                item = touch(code, t, num, row_idx + 1)
                item.listed = True
                if status_col is not None and status_col < len(cells):
                    item.raw_status = STATUS_NOTE_SUFFIX.sub(
                        "", norm(cells[status_col])).strip()
                    item.item_status = self._norm_status(cells[status_col], doc)
            entries: List[Tuple[int, str, int]] = []
            for r, cells in rows:
                code, _t, num = self._split_code(cells[code_col]) if code_col < len(cells) else ("", "", 0)
                if code:
                    entries.append((r, code, num))
            if entries:
                doc.code_sections.append((section, entries))

        # 定义块的粗体属性行与清单列共用 `item_status`：清单未填时回退到定义位
        for item in doc.items:
            if not item.item_status and item.def_status:
                item.item_status = item.def_status

    def _doc_items(self, doc: DocInfo) -> List[ItemInfo]:
        """本文档的细项，排除与**文档自身编码**同名的那一项。

        `REF-{三位序号}` 既是文档编码格式、`REF` 又是类型码（编码空间重叠），
        因此 REF 文档的 H1 会被解析成一个与 `doc_code` 同名的细项。但文档标题
        不是细项：它不进本文档细项编码清单、不适用定义块形态与锚点房规（引用
        ADR / REF 等整份文档用文档链接、不带锚点）。L0-L6 / ADR 的前缀不是类型码，
        本过滤对它们是空操作。
        """
        if not doc.doc_code:
            return doc.items
        return [it for it in doc.items if it.code != doc.doc_code]

    def _heading_code(self, line: str) -> str:
        """取定义位开头的编码；允许行首带 `~~已废弃~~` 等修饰。"""
        hm = re.match(r"^\s{0,3}#{1,6}\s+(.*)$", line)
        if hm:
            head = re.sub(r"^(?:~~[^~]*~~|（[^）]*）|\[[^\]]*\]\s*)+", "", hm.group(1)).strip()
        else:
            bm = ITEM_BOLD_DEF.match(line)
            if not bm:
                return ""
            head = bm.group(1)
        m = re.match(r"((?:[A-Z]{2,4}-)?[A-Z]{1,5}[0-9]?-\d{2,4})(?![0-9A-Za-z])", head)
        if not m:
            return ""
        code = m.group(1)
        _full, t, _num = self._split_code(code)
        return code if t in self.known_types else ""

    def _split_code(self, text: str) -> Tuple[str, str, int]:
        """把表格单元格解析为 (完整编码, 类型码, 序号)；不是编码开头则返回空。"""
        m = CODE_CELL.match(norm(text))
        if not m:
            return "", "", 0
        return norm(text)[:m.end()], m.group(1), int(m.group(2))


    def _nearest_heading(self, lines: List[str], idx: int) -> str:
        for j in range(idx, -1, -1):
            m = re.match(r"^\s{0,3}#{1,6}\s+(.*)$", lines[j])
            if m:
                return norm(m.group(1))
        return ""

    # -------------------------------------------------------------- 通用工具

    def add_issue(self, level: str, title: str, description: str) -> None:
        """添加问题"""
        self.issues.append({"level": level, "title": title, "description": description})

    def _all_codes(self) -> Dict[str, List[ItemInfo]]:
        by_code: Dict[str, List[ItemInfo]] = defaultdict(list)
        for doc in self.docs:
            for item in doc.items:
                by_code[item.code].append(item)
        return by_code

    def _known_item_codes(self) -> Set[str]:
        known = set(self.code_to_doc)
        for doc in self.docs:
            for item in doc.items:
                known.add(item.code)
        return known

    # -------------------------------------------------------------- 检查规则

    def check_doc_meta(self) -> None:
        """文件名、文档编码、文档 `状态`、版本号格式。"""
        for doc in self.docs:
            name = Path(doc.path).name
            if re.search(r"[\u3400-\u9fff]", name):
                self.add_issue("ERROR", "文件名含中文",
                               f"{doc.path}: 文件名 MUST NOT 使用中文（描述用小写英文/拼音、短横线分隔）")
            if doc.is_index:
                continue
            if not doc.doc_code:
                self.add_issue("INFO", "无文档编码",
                               f"{doc.path}: 未找到元信息表 `文档编码`；"
                               "若属词汇表等辅助文件可忽略")
                continue
            if not re.fullmatch(r"(?:L[0-6]|ADR|REF)-\d{3}", doc.doc_code):
                self.add_issue("ERROR", "文档编码格式错误",
                               f"{doc.path}: {doc.doc_code}（应为 L{{层级}}-三位序号 / ADR-三位序号 / REF-三位序号）")
            if not name.startswith(doc.doc_code + "-"):
                self.add_issue("WARNING", "文件名与文档编码不一致",
                               f"{doc.path}: 文件名应以 `{doc.doc_code}-` 开头")

            category = doc.status_category
            if not category:
                continue
            if not doc.status_present:
                fallback = self._legacy_draft_target(doc)
                self.add_issue("INFO", "文档状态字段缺失",
                               f"{doc.path}: 元信息缺 `状态`，按 `变更记录` 判定为 `{fallback}`"
                               "（无法判定取 `草案`）；请确认后补齐（历史文档常见）")
            elif not doc.status:
                self.add_issue("WARNING", "文档状态未填写",
                               f"{doc.path}: `状态` 仍是占位写法，应填 "
                               f"{'/'.join(DOC_STATUSES)} 之一")
            elif doc.status not in DOC_STATUSES:
                self.add_issue("WARNING", "无效状态值",
                               f"{doc.path}: 状态 '{doc.status}' 不在标准四态内 "
                               f"{'/'.join(DOC_STATUSES)}（L0-L6 / ADR / REF / PLN 共用同一枚举）")
            if doc.version and not VERSION_RE.match(doc.version):
                self.add_issue("WARNING", "版本号格式错误",
                               f"{doc.path}: 版本 '{doc.version}' 应为 v主.次（如 v1.0）")

    def check_duplicate_codes(self) -> None:
        """检查重复编码（文档编码与细项编码）"""
        code_count: Dict[str, List[str]] = defaultdict(list)
        for doc in self.docs:
            if doc.doc_code:
                code_count[doc.doc_code].append(doc.path)
        for code, paths in code_count.items():
            if len(paths) > 1:
                self.add_issue("ERROR", "重复文档编码", f"{code} 出现在多个文件: {', '.join(paths)}")

        item_count: Dict[str, List[str]] = defaultdict(list)
        for doc in self.docs:
            for item in doc.items:
                if item.defined:
                    item_count[item.code].append(f"{doc.path}:{item.line}")
        for code, sites in item_count.items():
            if len(sites) > 1:
                self.add_issue("ERROR", "重复细项编码",
                               f"{code} 在多处定义: {', '.join(sorted(set(sites)))}")

    def check_references(self) -> None:
        """引用存在性：正文出现的编码须在包内有定义或登记。"""
        known = self._known_item_codes()
        for doc in self.docs:
            if doc.archived:
                continue
            reported: Set[str] = set()
            for lineno, line in enumerate(doc.lines, 1):
                for m in CODE_TOKEN.finditer(line):
                    full, type_code = m.group(1), m.group(2)
                    if type_code not in self.known_types or full in reported:
                        continue
                    if full in known:
                        continue
                    # 项目前缀未启用时可能写成 {项目编码}-FR-001 之类占位，跳过含花括号的片段
                    start = max(0, m.start() - 2)
                    if "{" in line[start:m.end() + 1]:
                        continue
                    reported.add(full)
                    self.add_issue("WARNING", "引用悬空",
                                   f"{doc.path}:{lineno} 引用了未定义/未登记的编码 {full}")

    def check_item_status(self) -> None:
        """细项状态、追溯状态取值，第二套枚举迁移提示，以及清单/索引列名合规。"""
        for doc in self.docs:
            reported_plan = False
            for _idx, header, rows in iter_tables(doc.lines):
                plan_col = col_index(header, "规划状态")
                if plan_col is not None:
                    if not reported_plan:
                        reported_plan = True
                        self.add_issue("WARNING", "存在第二套状态枚举",
                                       f"{doc.path}: 表头 {header} 含 `规划状态`；PLN 只用标准四态"
                                       " `细项状态` 表达生命周期，是否已展开改用记录型字段"
                                       " `落实情况` / `落实记录` 承载")
                    for _r, cells in rows:
                        if plan_col < len(cells):
                            v = norm(cells[plan_col])
                            if v in LEGACY_PLAN_MAP:
                                self.legacy_hits.add(
                                    (doc.path,
                                     f"规划状态 {v} → {LEGACY_PLAN_MAP[v]}"
                                     f" + 落实情况 {'已落实' if v == '已落实' else '未落实'}"))
                    continue
                status_col = col_index(header, "状态")
                code_col = col_index(header, "编码")
                if status_col is None or code_col is None:
                    continue
                if col_index(header, "细项状态") is not None:
                    continue
                # 仅当该列承载的确实是细项状态枚举时才要求改名：
                # 文档索引表的 `状态` 指文档状态、应用注册表的 `状态` 列、
                # 追溯矩阵的 `追溯状态`，均合规
                carries_item_code = False
                values: Set[str] = set()
                for _r, cells in rows:
                    row_code = ""
                    if code_col < len(cells):
                        row_code, t, _n = self._split_code(cells[code_col])
                        if t and t not in DOC_CODE_PREFIXES:
                            carries_item_code = True
                    if status_col < len(cells):
                        # 行内状态描述的是 `row_code`，不是当前文件
                        v = self._norm_status(cells[status_col], doc,
                                              self._status_ctx(row_code, doc))
                        if v:
                            values.add(v)
                if carries_item_code and values and values <= set(ITEM_STATUSES):
                    self.add_issue("WARNING", "索引/清单列名不规范",
                                   f"{doc.path}: 表头 {header} 承载细项状态的列应为 `细项状态`"
                                   "（`状态` 专用于文档元信息与应用注册表）")
            for item in doc.items:
                if item.item_status and item.item_status not in ITEM_STATUSES:
                    self.add_issue("WARNING", "细项状态值无效",
                                   f"{doc.path}: {item.code} 的 `细项状态` '{item.item_status}' "
                                   f"应为 {'/'.join(ITEM_STATUSES)}")
                elif item.listed and not item.item_status:
                    self.add_issue("INFO", "细项状态待确认",
                                   f"{doc.path}: {item.code} 未填 `细项状态`，按 `变更记录` 判定"
                                   "（有定稿条目 → `草案`，从未定稿 → `初稿`，无法判定 → `草案`）")
                if item.def_status and item.item_status and item.def_status != item.item_status:
                    self.add_issue("WARNING", "定义位与清单状态不一致",
                                   f"{doc.path}:{item.line} {item.code} 定义块 `**细项状态**` 为 "
                                   f"'{item.def_status}'，清单/索引列为 '{item.item_status}'")

            for _idx, header, rows in iter_tables(doc.lines):
                trace_col = col_index(header, TRACE_COLUMN, LEGACY_TRACE_COLUMN)
                if trace_col is None:
                    continue
                if norm(header[trace_col]) == LEGACY_TRACE_COLUMN:
                    self.add_issue("WARNING", "追溯列名待迁移",
                                   f"{doc.path}: `{LEGACY_TRACE_COLUMN}` 应改为 `{TRACE_COLUMN}`，"
                                   "取值 未追溯/已追溯/不适用（L6 只记追溯覆盖关系，"
                                   "**不记测试执行结果**）")
                for _r, cells in rows:
                    if trace_col >= len(cells):
                        continue
                    raw = norm(cells[trace_col])
                    if not raw or "{" in raw or "/" in raw:
                        continue
                    if raw in LEGACY_TRACE_MAP:
                        mapped = LEGACY_TRACE_MAP[raw]
                        self.legacy_hits.add(
                            (doc.path,
                             f"{raw} → {mapped or '（无对应值：执行结果改记于测试管理系统；已有验证链接者应记 `已追溯`）'}"))
                        continue
                    if raw not in TRACE_STATUSES:
                        self.add_issue("WARNING", "追溯状态值无效",
                                       f"{doc.path}: `{header[trace_col]}` '{raw}' "
                                       f"应为 {'/'.join(TRACE_STATUSES)}")

    def check_legacy_statuses(self) -> None:
        """旧状态值迁移提示（INFO，不阻断）：命中兼容层即提示改写为标准四态。"""
        by_path: Dict[str, Set[str]] = defaultdict(set)
        for path, hit in self.legacy_hits:
            by_path[path].add(hit)
        for path, hits in sorted(by_path.items()):
            self.add_issue("INFO", "状态值待迁移",
                           f"{path}: 使用了旧状态值 {'；'.join(sorted(hits))}；"
                           f"标准四态为 {'/'.join(DOC_STATUSES)}"
                           "（映射表见 references/status-definitions.md · 存量文档迁移）")

    def check_registration_consistency(self) -> None:
        """正文定义、本文档清单、全局索引三方的编码与状态一致。"""
        for doc in self.docs:
            if doc.is_index:
                continue
            for item in self._doc_items(doc):
                if item.defined and not item.listed:
                    self.add_issue("WARNING", "细项未登记入清单",
                                   f"{doc.path}:{item.line} {item.code} 在正文定义，但未出现在"
                                   "带 `细项状态` 列的清单/索引表中")
                elif item.listed and not item.defined:
                    self.add_issue("INFO", "清单条目缺正文定义",
                                   f"{doc.path}:{item.line} {item.code} 已登记但未在本文找到定义位")

        by_code = self._all_codes()
        for code, entries in sorted(by_code.items()):
            statuses = {i.item_status for i in entries if i.item_status}
            if len(statuses) > 1:
                sites = ", ".join(f"{i.path}:{i.line}={i.item_status}" for i in entries)
                self.add_issue("WARNING", "同一编码状态不一致",
                               f"{code}: 正文/清单/索引取值不一 ({sites})")

        index_by_scope: Dict[str, Set[str]] = defaultdict(set)
        for doc in self.docs:
            if doc.is_index:
                index_by_scope[self._scope_of(doc.path)] |= {i.code for i in doc.items if i.listed}
        for doc in self.docs:
            if doc.is_index:
                continue
            registered = index_by_scope.get(self._scope_of(doc.path))
            if registered is None:
                continue
            for item in self._doc_items(doc):
                if item.defined and item.type_code in self.type_codes and item.code not in registered:
                    self.add_issue("WARNING", "细项未登记入全局索引",
                                   f"{doc.path}:{item.line} {item.code} 未出现在作用域 README 的"
                                   "全局编码索引中")

    def check_index_order_and_gaps(self) -> None:
        """编码升序与缺口：清单/索引表内同类型码必须升序；`正式` 基线序列不得有缺口。"""
        for doc in self.docs:
            for section, entries in doc.code_sections:
                by_type: Dict[str, List[Tuple[int, int, str]]] = defaultdict(list)
                for lineno, code, num in entries:
                    m = CODE_TOKEN.match(code)
                    if not m:
                        continue
                    by_type[m.group(2)].append((lineno, num, code))
                for type_code, rows in sorted(by_type.items()):
                    nums = [r[1] for r in rows]
                    if any(b < a for a, b in zip(nums, nums[1:])):
                        detail = ", ".join(c for _, _, c in rows)
                        self.add_issue("WARNING", "编码未按升序排列",
                                       f"{doc.path}（{section}）: {type_code} 序列乱序 -> {detail}")
                    dup = sorted({c for _, _, c in rows if [c2 for _, _, c2 in rows].count(c) > 1})
                    if dup:
                        self.add_issue("WARNING", "清单内重复编码",
                                       f"{doc.path}（{section}）: {', '.join(dup)}")

        scope_codes: Dict[str, Dict[str, Set[int]]] = defaultdict(lambda: defaultdict(set))
        for doc in self.docs:
            scope = self._scope_of(doc.path)
            for item in doc.items:
                scope_codes[scope][item.type_code].add(item.number)
        for scope, by_type in sorted(scope_codes.items()):
            for type_code, filled in sorted(by_type.items()):
                if type_code in DOC_CODE_PREFIXES or not filled:
                    continue
                upper = max(filled)
                missing = [n for n in range(1, upper + 1) if n not in filled]
                if missing:
                    shown = ", ".join(f"{type_code}-{n:03d}" for n in missing[:12])
                    self.add_issue("INFO", "编码序列存在缺口",
                                   f"{scope or '.'}: {type_code} 缺少 {shown}"
                                   "（若为 `初稿` 期删除后可回收编号则无需处理，否则须补索引或废弃记录）")

    def _scope_of(self, path: str) -> str:
        """作用域 = `ued/` 下的顶层目录；多应用模式为应用目录，单应用模式归并为根（`""`）。"""
        try:
            rel = Path(path).resolve().relative_to(self.ued_path.resolve())
        except ValueError:
            return ""
        parents = rel.parts[:-1]
        if not parents:
            return ""
        top = parents[0]
        return "" if re.fullmatch(r"L[0-6](-.*)?", top) else top

    def check_counters(self) -> None:
        """README 编码计数器与已用编号的一致性。"""
        for doc in self.docs:
            for _idx, header, rows in iter_tables(doc.lines):
                type_col = col_index(header, "类型码")
                next_col = col_index(header, "下一可用编号")
                if type_col is None or next_col is None:
                    continue
                scope = self._scope_of(doc.path)
                max_used: Dict[str, int] = defaultdict(int)
                for other in self.docs:
                    if self._scope_of(other.path) != scope:
                        continue
                    for item in other.items:
                        if item.type_code in self.type_codes:
                            max_used[item.type_code] = max(max_used[item.type_code], item.number)
                for _row_idx, cells in rows:
                    if max(type_col, next_col) >= len(cells):
                        continue
                    type_code = norm(cells[type_col])
                    raw = norm(cells[next_col])
                    if type_code not in self.type_codes:
                        continue
                    if "{" in raw or not raw.isdigit():
                        self.add_issue("INFO", "计数器未填写",
                                       f"{doc.path}: {type_code} 的 `下一可用编号` 为 '{raw}'")
                        continue
                    counter = int(raw)
                    top = max_used.get(type_code, 0)
                    if top and counter <= top:
                        self.add_issue("WARNING", "计数器落后于实际编号",
                                       f"{doc.path}: {type_code} 下一可用编号 {raw} <= 已用最大编号 {top:03d}")
                    elif top and counter > top + 1:
                        self.add_issue("INFO", "计数器提示存在缺口",
                                       f"{doc.path}: {type_code} 下一可用编号 {raw} > 已用最大编号 {top:03d} + 1")

    def _changelog_start(self, doc: DocInfo) -> Optional[int]:
        """定位 `变更记录` 小节标题行下标，无则返回 None。

        取**最后一个**匹配标题：同一文档可能出现多个含「变更记录」字样的标题
        （如正文散文引用），真正的小节在后。
        """
        heading_at = {i: norm(m.group(1)) for i, line in enumerate(doc.lines)
                      if (m := re.match(r"^\s{0,3}#{1,6}\s+(.*)$", line))}
        start = None
        for i in range(len(doc.lines)):
            text = heading_at.get(i, "")
            if text and any(k in text for k in CHANGELOG_HEADINGS):
                start = i
        return start

    def _changelog_rows(self, doc: DocInfo) -> List[Tuple[str, str]]:
        """取变更记录表，返回 [(版本号, 变更说明)]，按文件中的顺序（应为倒序）。"""
        start = self._changelog_start(doc)
        if start is None:
            return []
        for idx, header, rows in iter_tables(doc.lines):
            if idx <= start:
                continue
            ver_col = col_index(header, "版本")
            desc_col = col_index(header, "变更说明", "说明", "内容")
            if ver_col is None:
                return []
            out: List[Tuple[str, str]] = []
            for _r, cells in rows:
                ver = norm(cells[ver_col]) if ver_col < len(cells) else ""
                desc = norm(cells[desc_col]) if desc_col is not None and desc_col < len(cells) else ""
                if ver:
                    out.append((ver, desc))
            return out
        return []

    def _changelog_latest_date(self, doc: DocInfo) -> str:
        """取 `变更记录` 表的最新日期（`YYYY-MM-DD`），无则返回空串。

        扫全部日期单元格取**最大值**而不取首行：表 MUST 倒序，但存量文档存在
        乱序与日期缺失，取最大值对两种情形都稳。供「`最后修订日期` MUST NOT 晚于
        本文档 `变更记录` 最新日期」不变式使用（房规见
        `references/status-definitions.md` ·《细项修订版本号》）。

        按文档缓存：本方法由治理段校验逐细项调用，而结果是文档级不变量。
        """
        if doc.path in self.chg_date_cache:
            return self.chg_date_cache[doc.path]
        latest = self._scan_changelog_latest_date(doc)
        self.chg_date_cache[doc.path] = latest
        return latest

    def _scan_changelog_latest_date(self, doc: DocInfo) -> str:
        start = self._changelog_start(doc)
        if start is None:
            return ""
        for idx, header, rows in iter_tables(doc.lines):
            if idx <= start:
                continue
            date_col = col_index(header, "日期", "变更日期", "时间")
            if date_col is None:
                return ""
            dates = []
            for _r, cells in rows:
                if date_col < len(cells):
                    m = DATE_IN_TEXT.search(norm(cells[date_col]))
                    if m:
                        dates.append(m.group(0))
            return max(dates) if dates else ""
        return ""

    def check_version_flow(self) -> None:
        """版本机制：起始 v1.0、初稿期与定稿不变号、解冻才递增且基于历史最大号、
        回退记录完整、版本号不复用、变更记录倒序。"""

        def key(ver: str) -> Optional[Tuple[int, int]]:
            m = re.fullmatch(r"v(\d+)\.(\d+)", ver)
            return (int(m.group(1)), int(m.group(2))) if m else None

        for doc in self.docs:
            rows = self._changelog_rows(doc)
            if not rows:
                continue
            versions = [key(v) for v, _d in rows]
            if doc.version:
                cur = key(doc.version)
                if cur and versions[0] and cur != versions[0]:
                    self.add_issue("WARNING", "文档版本与变更记录不一致",
                                   f"{doc.path}: 元信息 `版本` {doc.version} != 变更记录最新行 {rows[0][0]}")

            # 版本号不复用：不得出现“解冻递增到不大于历史最大号”的情形（定稿不变号、
            # 回退回到旧号均为合法重复，具体校验见下方逐行判定）
            prev = None
            for idx, ver in enumerate(versions):
                if ver is None:
                    if not rows[idx][0].startswith("{"):
                        self.add_issue("WARNING", "版本号格式错误",
                                       f"{doc.path}: 变更记录版本 '{rows[idx][0]}' 应为 v主.次")
                    continue
                # 回退行的版本号合法地低于其下方被弃行，不参与倒序校验
                if ROLLBACK_KW.search(rows[idx][1]):
                    continue
                if prev and ver > prev:
                    self.add_issue("WARNING", "变更记录未按版本倒序",
                                   f"{doc.path}: {rows[idx][0]} 晚于其上一行，最新记录应置顶")
                prev = ver

            for idx in range(len(rows)):
                ver, desc = rows[idx]
                older = rows[idx + 1] if idx + 1 < len(rows) else None
                if older is None:
                    if INIT_KW.search(desc) and ver and not ver.startswith("v1.0"):
                        self.add_issue("INFO", "起始版本非 v1.0",
                                       f"{doc.path}: 历史起始版本 {ver}（新建文档应从 v1.0 + `初稿` 起）")
                    continue
                cur_key, old_key = key(ver), key(older[0])
                history_max = max((k for k in versions[idx + 1:] if k), default=None)
                if ROLLBACK_KW.search(desc):
                    # 回退：版本号与内容回到上一 `正式` 基线，被弃号条目 MUST 完整保留
                    if cur_key and history_max and cur_key >= history_max:
                        self.add_issue("WARNING", "回退记录不完整",
                                       f"{doc.path}: '{desc[:28]}' 声明回退，但变更记录中没有高于"
                                       "当前版本号的被弃条目（被回退弃用的版本号 MUST 保留且不复用）")
                    continue
                if FINALIZE_KW.search(desc) and cur_key and old_key and cur_key != old_key:
                    self.add_issue("WARNING", "定稿时递增了版本号",
                                   f"{doc.path}: '{desc[:28]}' 定稿不应变号"
                                   "（{old} -> {new}）".replace("{old}", older[0]).replace("{new}", ver))
                if UNFREEZE_KW.search(desc) and cur_key and old_key:
                    if cur_key == old_key:
                        self.add_issue("WARNING", "解冻未递增版本号",
                                       f"{doc.path}: `正式→草案` 解冻是版本号唯一正规递增时机，"
                                       f"应保持 {ver} 递增一版")
                    elif history_max and cur_key <= history_max:
                        self.add_issue("WARNING", "递增未基于历史最大版本号",
                                       f"{doc.path}: 解冻递增到 {ver}，但历史已出现过不低于它的版本号；"
                                       "递增基准 = 该对象历史上出现过的最大版本号（含被回退弃用的号）")

    CHAPTER_REF_PATTERNS = [
        (re.compile(r"§\s*\d"), "§ 编号引用"),
        (re.compile(r"第\s*[0-9一二三四五六七八九十百]+\s*(?:章|节|小节|条|款)"), "章节编号引用"),
        (re.compile(r"(?:见|参见|详见)\s*[0-9]+(?:\.[0-9]+)+"), "编号式引用"),
        (re.compile(r"[0-9]+(?:\.[0-9]+)+\s*(?:节|小节|章)"), "编号式引用"),
        (re.compile(r"(?:见|参见|详见)\s*(?:上文|下文|前文|后文|上述|前述|上表|下表|上图|下图|上节|下节)"),
         "位置式引用"),
    ]

    def check_chapter_references(self) -> None:
        """零章节编号引用门禁（命中即不通过）。"""
        for doc in self.docs:
            if doc.archived:
                continue
            for lineno, line in enumerate(doc.lines, 1):
                if any(k in line for k in ("禁止", "MUST NOT", "不得", "示例：")):
                    continue
                for pat, kind in self.CHAPTER_REF_PATTERNS:
                    m = pat.search(line)
                    if m:
                        self.add_issue("ERROR", "章节编号引用",
                                       f"{doc.path}:{lineno} 命中{kind} '{m.group(0)}'；"
                                       "引用一律改用细项编码/文档编码")
                        break

    def check_structure(self) -> None:
        """结构完整性：必备小节、细项清单存在。

        key 优先用层级（`L0`-`L6`）；ADR / REF 的文档编码不含层级（`doc.layer`
        为空），回退到 `doc.doc_type`，否则两类文档的结构校验会整体静默失效。

        同一层级 MAY 有**多种文档形态**（与 `assets/templates/` 的官方模板一一对应：
        L0 分产品战略 / 产品路线图，L1 分利益相关者需求 / 产品规划总览），命中任一
        形态的完整小节集即视为合规；MUST NOT 拿单一形态的小节集去要求另一种形态。
        均未命中时，按缺失最少（最接近）的形态报缺。
        """
        required: Dict[str, List[Tuple[str, List[Tuple[str, ...]]]]] = {
            "L0": [("产品战略", [("愿景",), ("目标", "成功标准")]),
                   ("产品路线图", [("阶段", "主题"), ("时间线", "演进")])],
            "L1": [("利益相关者需求", [("利益相关者",), ("场景",)]),
                   ("产品规划总览", [("登记口径", "落实"), ("统计", "分布")])],
            "L2": [("系统/产品需求", [("功能需求",), ("非功能需求",)])],
            "L3": [("概念架构", [("架构",), ("组件", "子系统")])],
            "L4": [("逻辑/系统设计", [("模块", "设计概述"), ("数据", "接口")])],
            "L5": [("详细设计", [("算法", "流程"), ("约束", "配置")])],
            "L6": [("验证与确认", [("测试",), ("追溯",)])],
            # ADR 的论证负担：完整记录背景、备选方案、选择理由、后果
            # （房规见 coding-system.md ·《ADR 与 DEC 的定位》）
            "ADR": [("架构决策记录",
                     [("背景",), ("备选方案",), ("决策",), ("理由",), ("后果",)])],
            "REF": [("外部参考资料", [("来源信息",)])],
        }
        for doc in self.docs:
            if doc.is_index or not doc.doc_code:
                continue
            headings = [norm(m.group(1)) for line in doc.lines
                        if (m := re.match(r"^\s{0,3}#{1,6}\s+(.*)$", line))]
            if not any(any(k in h for k in CHANGELOG_HEADINGS) for h in headings):
                self.add_issue("WARNING", "缺少变更记录",
                               f"{doc.path}: 未找到 `变更记录`/`版本历史` 小节")
            if self._doc_items(doc) and not any(any(k in h for k in ITEM_LIST_HEADINGS) for h in headings):
                self.add_issue("WARNING", "缺少细项编码清单",
                               f"{doc.path}: 本文档定义/登记了细项，但文末无 `本文档细项编码清单` 小节")
            key = doc.layer or doc.doc_type
            variants = required.get(key)
            if not variants:
                continue
            best: Optional[Tuple[str, List[Tuple[str, ...]]]] = None
            for form, groups in variants:
                missing = [g for g in groups
                           if not any(any(k in h for k in g) for h in headings)]
                if not missing:
                    best = None
                    break
                if best is None or len(missing) < len(best[1]):
                    best = (form, missing)
            if best:
                form, missing = best
                for group in missing:
                    self.add_issue("WARNING", "缺少必需章节",
                                   f"{doc.path}: {key}「{form}」形态文档未找到含 "
                                   f"{'/'.join(group)} 的小节")

    # ------------------------------------------------- 定义块形态与锚点

    def check_def_blocks(self) -> None:
        """定义块形态：禁粗体式定义位、锚点行齐备且与编码一致、属性行形态。

        房规单点承载于 `references/coding-system.md` ·《细项定义块形态》与
        《锚点定义位》；本方法只执行校验。仅针对**定义位**（`item.defined`），
        登记表 / 索引行不适用定义块形态。

        文档自身的 H1 跳过（见 `_doc_items`）：`REF-{三位序号}` 既是文档编码格式、
        `REF` 又是类型码（编码空间重叠），因此 REF 文档的 H1 会被当成定义位；但
        引用 REF / ADR 等**整份文档**时用文档链接、**不带锚点**，文档标题不适用
        细项锚点房规。
        """
        for doc in self.docs:
            if doc.archived:
                continue
            lines = doc.lines
            for item in self._doc_items(doc):
                if not item.defined or item.path != doc.path:
                    continue
                idx = item.line - 1
                if not (0 <= idx < len(lines)):
                    continue
                if ITEM_BOLD_DEF.match(lines[idx]):
                    self.add_issue(
                        "ERROR", "细项定义块形态不合规",
                        f"{doc.path}:{item.line} `{item.code}`: 以 `- **{item.code}**：…` "
                        "粗体列表项充当定义位——编码不进文档大纲、无具名属性行可承载五要素、"
                        "不产生任何锚点；MUST 改为「`<a id>` 锚点行 + 标题行（`{编码}：{标题}`，"
                        "全角冒号）+ `- **{要素名}**：{值}` 属性行」")
                    continue        # 形态整体不合规，锚点与属性行不再重复报
                self._check_def_anchor(doc, item, idx)
                self._check_attr_lines(doc, item, idx)
                self._check_attr_segments(doc, item, idx)
                self._check_block_contiguity(doc, item, idx)

    def _check_def_anchor(self, doc: DocInfo, item: ItemInfo, idx: int) -> None:
        """定义位标题行上方 MUST 有 `<a id="{编码全小写}">`，且锚点值与编码一致。"""
        lines = doc.lines
        want = item.code.lower()
        j = idx - 1
        while j >= 0 and not lines[j].strip():
            j -= 1                  # 允许锚点行与标题行之间有空行
        m = ANCHOR_TAG.match(lines[j]) if j >= 0 else None
        found = m.group(1).strip().lower() if m else ""
        if found == want:
            return
        if found:
            self.add_issue("ERROR", "定义位锚点与编码不符",
                           f"{doc.path}:{item.line} `{item.code}`: 标题行上方的锚点为 "
                           f"`<a id=\"{found}\">`，MUST 为 `<a id=\"{want}\">`（锚点值与编码"
                           "一一对应，MUST NOT 随标题改动而变动）")
        else:
            self.add_issue("ERROR", "定义位缺锚点",
                           f"{doc.path}:{item.line} `{item.code}`: 标题行上方 MUST 有 "
                           f"`<a id=\"{want}\"></a>`；MUST NOT 依赖标题自动 slug（含标题文本，"
                           "改标题即失效），也 MUST NOT 用 `{#编码小写}` 属性语法（在 GitHub 等 "
                           "cmark-gfm 渲染器下不生效）")

    def _check_attr_lines(self, doc: DocInfo, item: ItemInfo, idx: int) -> None:
        """属性行形态：MUST 为 `- **{要素名}**：{值}`；禁裸段落、禁要素名未加粗。

        只判定标题行下方**紧邻的连续非空行**（即属性行组）；组内缩进更深的行是
        多条目值的续行（如 `落实记录` / `业务流程` 的分条），不属属性行，跳过。
        """
        lines = doc.lines
        j = idx + 1
        while j < len(lines) and not lines[j].strip():
            j += 1
        group: List[int] = []
        while j < len(lines) and lines[j].strip():
            group.append(j)
            j += 1
        if not group:
            return
        base = len(lines[group[0]]) - len(lines[group[0]].lstrip())
        # 只有组内确实存在合规属性行时，才把同行的裸段落当属性行判定；
        # 否则该组可能整段是叙述文字，不属属性行语义。
        has_ok = any(ATTR_LINE_OK.match(lines[k]) for k in group)
        for k in group:
            line = lines[k]
            if len(line) - len(line.lstrip()) > base:
                continue            # 续行（多条目值），不是属性行
            if ATTR_LINE_OK.match(line):
                continue
            if ATTR_LINE_NO_BULLET.match(line):
                self.add_issue("ERROR", "属性行写成裸段落",
                               f"{doc.path}:{k + 1} `{item.code}` 定义块的属性行 "
                               f"`{line.strip()[:40]}` 缺列表符；MUST 为列表项 "
                               "`- **{要素名}**：{值}`（一个要素独占一行）")
                continue
            m = ATTR_LINE_NO_BOLD.match(line)
            if m and "{" not in m.group(1):
                self.add_issue("WARNING", "属性行要素名未加粗",
                               f"{doc.path}:{k + 1} `{item.code}` 定义块的属性行 "
                               f"`{line.strip()[:40]}` 要素名未加粗；MUST 写成 "
                               f"`- **{m.group(1).strip()}**：…`")
                continue
            bm = ATTR_LINE_BARE_PLAIN.match(line)
            if (has_ok and bm and "{" not in bm.group(1)
                    and not ATTR_NAME_PROSE.search(bm.group(1))):
                self.add_issue("ERROR", "属性行写成裸段落",
                               f"{doc.path}:{k + 1} `{item.code}` 定义块的属性行 "
                               f"`{line.strip()[:40]}` 既无列表符也无粗体；MUST 写成 "
                               f"`- **{bm.group(1).strip()}**：…`")

    def _attr_group(self, doc: DocInfo, idx: int) -> List[Tuple[str, str, int]]:
        """取标题行下方属性行组的 `(要素名, 值, 行号)`。

        与 `_check_attr_lines` 同口径：组 = 标题行下方紧邻的连续非空行，缩进更深
        者是多条目值的续行（如 `落实记录` 的分条），不计入属性行。
        """
        lines = doc.lines
        j = idx + 1
        while j < len(lines) and not lines[j].strip():
            j += 1
        group: List[int] = []
        while j < len(lines) and lines[j].strip():
            group.append(j)
            j += 1
        if not group:
            return []
        base = len(lines[group[0]]) - len(lines[group[0]].lstrip())
        out: List[Tuple[str, str, int]] = []
        for k in group:
            if len(lines[k]) - len(lines[k].lstrip()) > base:
                continue                # 续行（多条目值）
            m = ATTR_NAME_VALUE.match(lines[k])
            if m:
                out.append((m.group(1).strip(), m.group(2).strip(), k + 1))
        return out

    def _check_attr_segments(self, doc: DocInfo, item: ItemInfo, idx: int) -> None:
        """属性行组三段校验：治理段齐备且居首、追溯段居末且值形态互斥。

        房规单点承载于 `references/coding-system.md` ·《细项定义块形态》与
        《追溯类属性行命名》；本方法只执行校验。废弃登记字段的值形态一并在此判，
        因为它同样落在属性行组内（紧随治理段）。
        """
        attrs = self._attr_group(doc, idx)
        if not attrs:
            return                      # 整组缺失属「缺属性行」，不在本方法职责内
        self._check_gov_segment(doc, item, attrs)
        self._check_trace_segment(doc, item, attrs)
        self._check_replacement_value(doc, item, attrs)

    def _check_gov_segment(self, doc: DocInfo, item: ItemInfo,
                           attrs: List[Tuple[str, str, int]]) -> None:
        """治理段：`细项状态` / `修订版本号` / `最后修订日期` MUST 齐备、按序居首。

        `细项状态` 缺失或不在首行报 ERROR（它同时受 `references/status-definitions.md`
        ·《状态即基线》的「承载位 MUST 两处」约束）；`修订版本号` / `最后修订日期`
        是新增治理字段，缺失按《存量文档迁移》回填，故报 WARNING 不阻断。
        """
        names = [n for n, _v, _l in attrs]
        pos: Dict[str, int] = {}
        for i, n in enumerate(names):
            pos.setdefault(n, i)
        if "细项状态" not in pos:
            self.add_issue("ERROR", "定义块缺细项状态属性行",
                           f"{doc.path}:{item.line} `{item.code}`: 属性行组 MUST 以 "
                           "`- **细项状态**：{值}` 开头——它与清单 / 索引表的状态列同为"
                           "必备承载位，缺任一处即违规")
            return
        anchored = pos["细项状态"] == 0
        if not anchored:
            self.add_issue("ERROR", "细项状态未位于属性行组首行",
                           f"{doc.path}:{attrs[pos['细项状态']][2]} `{item.code}`: "
                           f"`细项状态` 排在第 {pos['细项状态'] + 1} 行（首行是 "
                           f"`{names[0]}`）；治理段 MUST 按 {' / '.join(GOV_SEGMENT)} "
                           "之序位于属性行组最前")
        for want, slot in (("修订版本号", 1), ("最后修订日期", 2)):
            if want not in pos:
                self.add_issue("WARNING", "治理段缺行",
                               f"{doc.path}:{item.line} `{item.code}`: 属性行组缺 "
                               f"`- **{want}**：…`；治理段三行 MUST 齐备并按序居首，"
                               "存量文档按《存量文档迁移》回填")
            elif not anchored:
                # 首行错位时槽位判定无意义：把 `细项状态` 移回首位，其余两行自然归槽。
                # 连带报「顺序错乱」会把 1 处笔误放大成 3 条 ERROR，且后两条不可独立处置。
                continue
            elif pos[want] != slot:
                self.add_issue("ERROR", "治理段顺序错乱",
                               f"{doc.path}:{attrs[pos[want]][2]} `{item.code}`: "
                               f"`{want}` 排在第 {pos[want] + 1} 行，MUST 排在第 "
                               f"{slot + 1} 行（治理段固定序：{' / '.join(GOV_SEGMENT)}）")
        for field, pat, msg in (("修订版本号", REV_VALUE,
                                 "MUST 是单个正整数（新建为 1、每轮解冻 +1、单调不回退）"),
                                ("最后修订日期", DATE_VALUE,
                                 "MUST 为 YYYY-MM-DD")):
            if field not in pos:
                continue
            val, lineno = attrs[pos[field]][1], attrs[pos[field]][2]
            if val and "{" not in val and val.lower() not in EMPTY_MARKS \
                    and not pat.match(val):
                self.add_issue("WARNING", f"{field}取值非法",
                               f"{doc.path}:{lineno} `{item.code}`: `{field}` "
                               f"'{val[:24]}' {msg}")
        self._check_rev_invariants(doc, item, attrs, pos)

    def _check_rev_invariants(self, doc: DocInfo, item: ItemInfo,
                              attrs: List[Tuple[str, str, int]],
                              pos: Dict[str, int]) -> None:
        """`修订版本号` / `最后修订日期` 与状态、变更记录的一致性不变式。

        房规见 `references/status-definitions.md` ·《细项修订版本号》「状态与修订号
        的一致性（可机检）」：`初稿` → rev **MUST** = 1；`草案` → **MUST** ≥ 2；
        `最后修订日期` **MUST NOT** 晚于本文档 `变更记录` 的最新日期（细项修订必然
        落在某个文档变更轮次内）。

        取值非单一规范形态时跳过（模板占位符、`初稿 / 正式 / 草案 / 废弃` 一类枚举
        示例、非数字 rev）——形态问题已由「取值非法」与状态值校验覆盖，本方法只判
        语义一致性。报 WARNING 不阻断：两个字段本轮新增，存量文档待回填。
        """
        status = attrs[pos["细项状态"]][1].strip()
        if "修订版本号" in pos:
            val, lineno = attrs[pos["修订版本号"]][1].strip(), attrs[pos["修订版本号"]][2]
            if val.isdigit():
                rev = int(val)
                if status == "初稿" and rev != 1:
                    self.add_issue("WARNING", "修订版本号与状态不一致",
                                   f"{doc.path}:{lineno} `{item.code}`: `细项状态` 为 "
                                   f"`初稿` 而 `修订版本号` 为 {rev}；`初稿` = 从未解冻，"
                                   "rev MUST 为 1（递增唯一时机是 `正式→草案` 解冻）")
                elif status == "草案" and rev < 2:
                    self.add_issue("WARNING", "修订版本号与状态不一致",
                                   f"{doc.path}:{lineno} `{item.code}`: `细项状态` 为 "
                                   f"`草案` 而 `修订版本号` 为 {rev}；`草案` 必经一轮解冻，"
                                   "rev MUST ≥ 2（解冻时 +1）")
        if "最后修订日期" in pos:
            val, lineno = attrs[pos["最后修订日期"]][1].strip(), attrs[pos["最后修订日期"]][2]
            m = DATE_IN_TEXT.search(val)
            latest = self._changelog_latest_date(doc) if m else ""
            if m and latest and m.group(0) > latest:
                self.add_issue("WARNING", "最后修订日期晚于变更记录",
                               f"{doc.path}:{lineno} `{item.code}`: `最后修订日期` "
                               f"{m.group(0)} 晚于本文档 `变更记录` 最新日期 {latest}；"
                               "细项修订必然落在某个文档变更轮次内，MUST 补登变更记录"
                               "或修正日期")

    def _check_trace_segment(self, doc: DocInfo, item: ItemInfo,
                             attrs: List[Tuple[str, str, int]]) -> None:
        """追溯段：`出处` → `来源` MUST 居属性行组末尾，且值形态互斥。

        `来源` 的值 MUST 含标准链接，`出处` 的值 MUST NOT 含链接——值形态是二者的
        判别依据。追溯段本身非强制（Trace 要素为 SHOULD），故仅当出现时校验。
        """
        names = [n for n, _v, _l in attrs]
        hits = [(i, n) for i, n in enumerate(names) if n in TRACE_SEGMENT]
        if not hits:
            return
        tail = len(names) - len(hits)   # 追溯段应有的起始下标
        for k, (i, n) in enumerate(hits):
            if i != tail + k:
                self.add_issue("ERROR", "追溯段未位于属性行组末尾",
                               f"{doc.path}:{attrs[i][2]} `{item.code}`: `{n}` 排在第 "
                               f"{i + 1} 行、其后还有 {len(names) - i - 1} 行（如 "
                               f"`{names[i + 1]}`）；追溯段 MUST 置于属性行组末尾，"
                               "MUST NOT 夹在内容段中间")
                break
        order = [n for _i, n in hits]
        expect = [n for n in TRACE_SEGMENT if n in order]
        if order != expect:
            self.add_issue("ERROR", "追溯段顺序错乱",
                           f"{doc.path}:{attrs[hits[0][0]][2]} `{item.code}`: 追溯段为 "
                           f"{' → '.join(order)}，MUST 为 {' → '.join(expect)}"
                           "（`出处` 写自然语言、在 `来源` 之前）")
        for i, n in hits:
            val, lineno = attrs[i][1], attrs[i][2]
            blank = (not val) or "{" in val or val.lower() in EMPTY_MARKS
            if n == "来源" and not blank and not MD_LINK.search(val):
                self.add_issue("ERROR", "来源值缺链接",
                               f"{doc.path}:{lineno} `{item.code}`: `来源` 的值 "
                               f"'{val[:30]}' MUST 含标准链接；编码依据用 `来源`、"
                               "自然语言依据用 `出处`，MUST NOT 互换")
            if n == "出处" and val and MD_LINK.search(val):
                self.add_issue("ERROR", "出处值含链接",
                               f"{doc.path}:{lineno} `{item.code}`: `出处` 的值 MUST NOT "
                               "含链接——编码链接 MUST 由 `来源` 承载，`出处` 只写自然语言")

    def _check_replacement_value(self, doc: DocInfo, item: ItemInfo,
                                 attrs: List[Tuple[str, str, int]]) -> None:
        """废弃登记字段 `替代方案` 的值 MUST 为标准链接或「无」。

        房规见 `references/item-deprecation.md` ·《标准标记格式》。只写裸编码会让
        引用方跳不到替代细项的定义位，写散文则侵占了 `废弃原因` 的职责——两者都使
        该字段不可机检跟随，故与 `来源` 同族按值形态判定。字段缺失已由「废弃细项
        缺少必需字段」报，本方法只在字段存在时判形态；非废弃细项误写该字段同样校验
        （值形态与状态无关）。
        """
        for name, val, lineno in attrs:
            if name != "替代方案":
                continue
            val = val.strip()
            if (not val) or "{" in val or val.lower() in EMPTY_MARKS:
                return                  # 模板占位符与「无」均合规
            if not MD_LINK.search(val):
                self.add_issue("ERROR", "替代方案值缺链接",
                               f"{doc.path}:{lineno} `{item.code}`: `替代方案` 的值 "
                               f"'{val[:30]}' MUST 为指向替代细项定义位的标准链接"
                               "（带 `#{编码全小写}` 锚点），无替代时填「无」；MUST NOT "
                               "只写裸编码，也 MUST NOT 写替代思路一类的散文（思路归 "
                               "`废弃原因`）")
            return

    def _check_block_contiguity(self, doc: DocInfo, item: ItemInfo, idx: int) -> None:
        """定义块三部分 MUST 连续：标题行与属性行组之间不得插入其他内容。

        房规见 `references/coding-system.md` ·《细项定义块形态》。MUST 读
        `raw_lines`——`doc.lines` 已把围栏抹成空行，插在标题与属性行之间的
        mermaid 图会被静默放过。自行跟踪围栏状态，避免把围栏内的行当成标题或
        属性行。

        仅当**属性行组确实排在插入内容之后**时才报（顺序被打断）；若整块根本没有
        属性行组，属「缺属性行」而非顺序问题，不在本方法职责内。
        """
        raw = doc.raw_lines
        hm = HEADING_LINE.match(raw[idx]) if idx < len(raw) else None
        level = len(hm.group(1)) if hm else 0
        fence_char = ""
        fence_len = 0
        insert_kind = ""        # 插入内容的类型（标题行下首个非属性行）
        insert_at = 0
        j = idx + 1
        while j < len(raw):
            line = raw[j]
            if fence_char:      # 围栏内：只找闭合，不参与任何判定
                closer = FENCE_CLOSE.match(line)
                if (closer and closer.group(1)[0] == fence_char
                        and len(closer.group(1)) >= fence_len):
                    fence_char, fence_len = "", 0
                j += 1
                continue
            opener = FENCE.match(line)
            if opener:
                fence_char = opener.group(1)[0]
                fence_len = len(opener.group(1))
                if not insert_kind:
                    insert_kind, insert_at = "图表 / 代码围栏", j + 1
                j += 1
                continue
            if not line.strip():
                j += 1
                continue
            if ATTR_LINE_OK.match(line):
                if insert_kind:
                    self.add_issue(
                        "ERROR", "定义块顺序被打断",
                        f"{doc.path}:{item.line} `{item.code}`: 标题行与属性行组之间插入了"
                        f"{insert_kind}（第 {insert_at} 行起）；定义块三部分 MUST 连续，其间"
                        "只允许空行——图表、表格、子标题与散文段落无具名要素可承载，夹在"
                        "中间会使五要素不可机检。MUST 把叙述与图示移到属性行组之后，或作为"
                        "某个属性行的值")
                return
            sub = HEADING_LINE.match(line)
            if ANCHOR_TAG.match(line) or (sub and level and len(sub.group(1)) <= level):
                return          # 已到下一个定义位 / 同级小节：本块无属性行组，不在此报
            if not insert_kind:
                if sub:
                    insert_kind = "子标题"
                elif line.lstrip().startswith("|"):
                    insert_kind = "表格"
                else:
                    insert_kind = "散文段落"
                insert_at = j + 1
            j += 1

    def _doc_anchors(self, doc: DocInfo) -> Set[str]:
        """文档的可达锚点集合：显式 `<a id>` / `<a name>` ∪ 标题自动 slug。"""
        key = os.path.normpath(doc.path)
        cached = self.anchor_cache.get(key)
        if cached is not None:
            return cached
        out: Set[str] = set()
        for line in doc.lines:      # doc.lines 已屏蔽围栏，围栏内锚点自然不计
            for m in ANCHOR_TAG.finditer(line):
                out.add(m.group(1).strip().lower())
            hm = HEADING_LINE.match(line)
            if hm:
                out.add(heading_slug(hm.group(2)))
        self.anchor_cache[key] = out
        return out

    def check_anchor_reachability(self) -> None:
        """锚点可达性：链接的 `#fragment` MUST 在目标文档的锚点集合中存在。

        只判定**可解析**的目标：同文档锚点，或相对路径能落到本次扫描范围内文档的
        跨文档锚点；含 `{占位符}` 的模板链接、外部 URL、目标不在扫描范围内的链接
        一律跳过（不误报）。`doc.lines` 已屏蔽围栏，行内代码另行剔除，因此示例
        片段不会被当成真链接。
        """
        for doc in self.docs:
            for idx, line in enumerate(doc.lines):
                for m in MD_LINK.finditer(INLINE_CODE.sub("", line)):
                    target = m.group(1)
                    if target.startswith(("http://", "https://", "mailto:", "//")):
                        continue
                    if "{" in target or "}" in target:
                        continue            # 模板占位符，实例化后才成真链接
                    path_part, _, frag = target.partition("#")
                    if not frag:
                        continue            # 无锚点；文件存在性不属本检查
                    if path_part:
                        tgt_path = os.path.normpath(
                            os.path.join(os.path.dirname(doc.path), path_part))
                        tgt = self.doc_by_path.get(tgt_path)
                        if tgt is None:
                            continue        # 目标不在本次扫描范围
                    else:
                        tgt = doc
                    if frag.lower() in self._doc_anchors(tgt):
                        continue
                    self.add_issue(
                        "WARNING", "锚点不可达",
                        f"{doc.path}:{idx + 1}: 链接 `{target}` 的锚点 `#{frag}` 在 "
                        f"{tgt.path} 中无对应目标（既无 `<a id=\"{frag.lower()}\">`，"
                        "也无同名标题 slug）；细项锚点 MUST 由定义块的锚点行提供")

    def check_dec_layer(self) -> None:
        """`DEC` 量级提示：定义位落在 L2/L3 文档时提示评估是否升格为 ADR。

        仅 INFO、**不报违规**：`DEC` MAY 被任何层级文档收录（类型码表的「典型层级」
        是语义归属建议、不是物理存放限制）。ADR 文档自身豁免：ADR 就是「已升格」
        的形态，其《决策》小节收录 DEC 是房规明确允许的做法。
        """
        for doc in self.docs:
            if doc.archived or doc.doc_type == "ADR" or doc.layer not in ("L2", "L3"):
                continue
            for item in self._doc_items(doc):
                if item.type_code != "DEC" or not item.defined or item.path != doc.path:
                    continue
                self.add_issue(
                    "INFO", "DEC 量级可能偏大",
                    f"{doc.path}:{item.line} `{item.code}`: `DEC` 的典型层级为 L4/L5，"
                    f"本定义位落在 {doc.layer} 文档；若该决策属技术栈选型、子系统划分、"
                    "数据一致性策略等宏观架构级，SHOULD 评估升格为 ADR 文档（一事一档）")

    def _item_block(self, doc: DocInfo, code: str) -> str:
        return "\n".join(doc.lines[i - 1] for i in self._own_lines(doc, code, block=True))

    def _own_lines(self, doc: DocInfo, code: str, block: bool = False) -> Set[int]:
        """返回该编码在本文内“属于自己”的行号（1-based）：定义位及其正文块、
        以及表格中以该编码为首列的登记行；用于区分“引用”与“自身定义/登记”。"""
        out: Set[int] = set()
        lines = doc.lines
        for i, line in enumerate(lines):
            if block and self._heading_code(line) == code:
                level = len(line) - len(line.lstrip("#"))
                out.add(i + 1)
                for j in range(i + 1, len(lines)):
                    nm = re.match(r"^\s{0,3}(#{1,6})\s+", lines[j])
                    if nm and len(nm.group(1)) <= level:
                        break
                    out.add(j + 1)
                continue
            if line.lstrip().startswith("|"):
                cells = split_row(line)
                for cell in cells[:2]:
                    if self._split_code(cell)[0] == code:
                        out.add(i + 1)
                        break
        return out

    def check_deprecation(self) -> None:
        """废弃处理规范性：细项废弃（原地）与文档废弃（两阶段）。"""
        deprecated_doc_codes: Set[str] = set()
        deprecated_item_codes: Set[str] = set()

        for doc in self.docs:
            # ---- 文档级废弃（状态精确等于 废弃）----
            if doc.status == "废弃":
                if doc.doc_code:
                    deprecated_doc_codes.add(doc.doc_code)
                text = "\n".join(doc.lines)
                missing_doc_fields: List[str] = [f for f in ("废弃时间", "废弃原因") if f not in text]
                archive_field = "建议归档日期" if "建议归档日期" in text else (
                    "建议移除日期" if "建议移除日期" in text else "")
                if not doc.archived and not archive_field:
                    missing_doc_fields.append("建议归档日期")
                if archive_field == "建议移除日期":
                    self.add_issue("INFO", "废弃字段名待迁移",
                                   f"{doc.path}: `建议移除日期` 应改名为 `建议归档日期`"
                                   "（到期只归档入 deprecated/，不删除）")
                if missing_doc_fields:
                    self.add_issue("ERROR", "废弃文档缺少必需字段",
                                   f"{doc.path}: 缺少 {'、'.join(missing_doc_fields)}")
                m = re.search(r"建议(?:归档|移除)日期[^0-9]*(\d{4}-\d{2}-\d{2})", text)
                if m and not doc.archived:
                    try:
                        d = datetime.strptime(m.group(1), "%Y-%m-%d").date()
                        if d < datetime.now().date():
                            self.add_issue("INFO", "废弃文档可归档",
                                           f"{doc.path}: 已过建议归档日期 {m.group(1)}，"
                                           "可归档入本作用域 deprecated/（只归档不删除）")
                    except ValueError:
                        self.add_issue("WARNING", "建议归档日期格式错误",
                                       f"{doc.path}: '{m.group(1)}' 非 YYYY-MM-DD")

            # ---- 细项级废弃 ----
            for i, line in enumerate(doc.lines):
                if line.lstrip().startswith("#") and "~~已废弃~~" in line:
                    code = self._heading_code(line)
                    block = self._item_block(doc, code) if code else line
                    missing = [f for f in ("细项状态", "废弃时间", "废弃原因", "替代方案")
                               if f not in block]
                    if missing:
                        self.add_issue("ERROR", "废弃细项缺少必需字段",
                                       f"{doc.path}:{i + 1} {code or '未知编码'} 缺少 "
                                       f"{'、'.join(missing)}")
                    if code:
                        deprecated_item_codes.add(code)

            for item in doc.items:
                if item.item_status == "废弃":
                    deprecated_item_codes.add(item.code)
                    if not item.defined:
                        continue
                    block = self._item_block(doc, item.code)
                    if not block:
                        continue
                    missing = [f for f in ("废弃时间", "废弃原因", "替代方案") if f not in block]
                    if missing:
                        self.add_issue("ERROR", "废弃细项缺少必需字段",
                                       f"{doc.path}:{item.line} {item.code} 缺少 "
                                       f"{'、'.join(missing)}")
                if item.item_status and item.item_status != "废弃":
                    for i, line in enumerate(doc.lines):
                        if line.lstrip().startswith("#") and item.code in line and "~~已废弃~~" in line:
                            self.add_issue("WARNING", "细项废弃标记与状态不一致",
                                           f"{doc.path}: {item.code} 标题带 `~~已废弃~~` "
                                           f"但 `细项状态` 为 '{item.item_status}'")
                            break

        # 引用完整性：活跃文档引用已废弃对象却未标注
        targets = deprecated_doc_codes | deprecated_item_codes
        patterns = {code: re.compile(re.escape(code) + r"(?![0-9A-Za-z-])") for code in targets}
        for doc in self.docs:
            if doc.archived or doc.status == "废弃":
                continue
            reported: Set[str] = set()
            own = {code: self._own_lines(doc, code, block=True) for code in patterns}
            for lineno, line in enumerate(doc.lines, 1):
                for code, pat in sorted(patterns.items()):
                    if code == doc.doc_code or code in reported or not pat.search(line):
                        continue
                    if lineno in own[code] or "~~" in line or "废弃" in line:
                        continue
                    reported.add(code)
                    self.add_issue("WARNING", "活跃文档引用已废弃对象",
                                   f"{doc.path}:{lineno} 引用了已废弃的 {code}，"
                                   "应改指替代细项或同步标注废弃")

    def check_draft_finalization(self) -> None:
        """状态即基线：仍为 `初稿` / `草案` 的文档与细项给出定稿提醒（INFO，不阻断）。"""
        for doc in self.docs:
            if doc.archived:
                continue
            if doc.status == "初稿":
                self.add_issue("INFO", "文档待定稿",
                               f"{doc.path}: 状态为 '初稿'，稳定后请经确认定稿"
                               "（初稿→正式，不递增版本号）")
            elif doc.status == "草案":
                self.add_issue("INFO", "草案待定稿",
                               f"{doc.path}: 状态为 '草案'（已从 `正式` 解冻），修订完成后请定稿"
                               "（草案→正式，沿用当前版本号）；放弃本轮修订可回退，"
                               "变更记录 MUST 完整保留被弃版本号条目")
            pending = sorted({item.code for item in doc.items
                              if item.item_status in ("", "初稿", "草案")})
            if pending:
                shown = ", ".join(pending[:30]) + (" ..." if len(pending) > 30 else "")
                self.add_issue("INFO", "细项待定稿",
                               f"{doc.path}: 仍为 '初稿'/'草案' 的细项（缺字段按 `变更记录` 判定）：{shown}")

    def check_status_gating(self) -> None:
        """层级门控：解冻自顶向下、定稿自底向上。

        房规见 `references/status-definitions.md` ·《层级门控》：
        - 解冻方向：细项解冻（`正式→草案`）MUST 先解冻所在文档，故「细项 `草案`
          而文档 `正式`」是结构违规（ERROR）。
        - 定稿方向：文档定稿 MUST 以「全部细项 ∈ {`正式`, `废弃`}」为前置，未满足时
          MUST 列出并提示用户确认（WARNING，人可确认后放行）。

        只针对**定义位**（`item.defined`）：登记视图 / 索引行不承载定义，重复计会
        造成同一细项多次报告。缺 `细项状态` 者不参与判定（已由治理段校验报缺行）。
        """
        for doc in self.docs:
            if doc.archived or doc.status != "正式":
                continue
            own = [it for it in self._doc_items(doc)
                   if it.defined and it.path == doc.path]
            drafts = sorted({it.code for it in own if it.item_status == "草案"})
            if drafts:
                shown = ", ".join(drafts[:20]) + (" ..." if len(drafts) > 20 else "")
                self.add_issue("ERROR", "细项草案而文档正式",
                               f"{doc.path}: 文档状态为 `正式`，但细项 {shown} 为 `草案`；"
                               "解冻 MUST 自顶向下——细项 `正式→草案` 前 MUST 先解冻所在"
                               "文档（文档版本号在此递增），或把细项回退 / 定稿")
            pending = sorted({it.code for it in own
                              if it.item_status in ("初稿", "草案")})
            if pending:
                shown = ", ".join(pending[:20]) + (" ..." if len(pending) > 20 else "")
                self.add_issue("WARNING", "文档定稿前置未满足",
                               f"{doc.path}: 文档状态为 `正式`，但仍有细项未定稿：{shown}；"
                               "定稿 MUST 自底向上——文档 `→正式` MUST 以全部细项 "
                               "`细项状态` ∈ {正式, 废弃} 为前置；向已 `正式` 的文档新增细项"
                               "同受门控，MUST 先解冻文档")

    def check_layer_references(self) -> None:
        """层级引用关系：下层文档应引用上层文档编码。"""
        layer_order = ["L0", "L1", "L2", "L3", "L4", "L5", "L6"]
        for doc in self.docs:
            if not doc.layer or doc.layer == "L0" or doc.archived:
                continue
            expected_parents = layer_order[:layer_order.index(doc.layer)]
            text = "\n".join(doc.lines)
            if not any(re.search(rf"{p}-\d{{3}}", text) for p in expected_parents):
                self.add_issue("INFO", "缺少上级引用",
                               f"{doc.path} 未引用任何上层文档编码（{'/'.join(expected_parents)}）")

    # ------------------------------------------------- 锁定矩阵与 REF 时效

    def _def_title(self, doc: DocInfo, code: str) -> str:
        """取该编码在本文定义位的标题文本（标题锁定校验用）。"""
        for i, line in enumerate(doc.lines):
            if self._heading_code(line) != code:
                continue
            hm = re.match(r"^\s{0,3}#{1,6}\s+(.*)$", line)
            if hm:
                text = re.sub(r"^(?:~~[^~]*~~|\[[^\]]*\]\s*)+", "", hm.group(1)).strip()
            else:
                bm = ITEM_BOLD_DEF.match(line)
                text = line[bm.end():] if bm else ""
            text = re.sub(r"^(?:[A-Z]{2,4}-)?[A-Z]{1,5}[0-9]?-\d{2,4}\s*[:\uff1a\-\u2014]?\s*", "", text)
            return norm(text)
        return ""

    def check_title_lock(self) -> None:
        """锁定矩阵·标题：引用处标题 MUST 与定义位一致。

        `初稿` 期改标题 MUST 先扫描全部引用处并同步（`--refs CODE` 可反查）；
        `正式` / `草案` 期标题锁定，不一致即意味着发生了未经废弃流程的标题漂移。
        """
        titles: Dict[str, Tuple[str, str]] = {}
        for doc in self.docs:
            for item in doc.items:
                if not item.defined or item.code in titles:
                    continue
                title = self._def_title(doc, item.code)
                if title and "{" not in title:
                    titles[item.code] = (title, f"{doc.path}:{item.line}")
        if not titles:
            return
        for doc in self.docs:
            if doc.archived:
                continue
            reported: Set[Tuple[str, str]] = set()
            for lineno, line in enumerate(doc.lines, 1):
                for m in TITLE_LINK.finditer(line):
                    code, raw_title = m.group(1), norm(m.group(2))
                    if code not in titles or not raw_title or "{" in raw_title:
                        continue
                    expect, site = titles[code]
                    if raw_title == expect or (code, raw_title) in reported:
                        continue
                    reported.add((code, raw_title))
                    self.add_issue("WARNING", "引用标题与定义标题不一致",
                                   f"{doc.path}:{lineno} 引用 {code} 写作「{raw_title}」，"
                                   f"定义位为「{expect}」（{site}）；`初稿` 期改标题 MUST 同步"
                                   "全部引用处，`正式` / `草案` 期标题锁定不得修改")

    def check_ref_freshness(self) -> None:
        """REF 时效字段齐备性与复查周期：超期未核验提示复核（WARNING，不阻断）。"""
        required = ("来源版本", "获取日期", "最近核验日期", "复查周期")
        for doc in self.docs:
            if not doc.doc_code.startswith("REF-") or doc.archived or doc.status == "废弃":
                continue
            fields: Dict[str, str] = {}
            for line in doc.lines:
                m = REF_FIELD.match(line)
                if m and m.group(1) not in fields:
                    fields[m.group(1)] = norm(m.group(2))
            missing = [f for f in required if not fields.get(f) or "{" in fields.get(f, "")]
            if missing:
                self.add_issue("WARNING", "REF 时效字段缺失",
                               f"{doc.path}: 缺少 {'、'.join(missing)}"
                               "（记录型字段，用于评估资料是否过期；不参与冻结）")
            last = fields.get("最近核验日期", "")
            months = parse_review_period(fields.get("复查周期", ""))
            m = re.search(r"(\d{4}-\d{2}-\d{2})", last)
            if not m or months is None:
                continue
            try:
                base = datetime.strptime(m.group(1), "%Y-%m-%d").date()
            except ValueError:
                self.add_issue("WARNING", "REF 日期格式错误",
                               f"{doc.path}: `最近核验日期` '{last}' 非 YYYY-MM-DD")
                continue
            due = add_months(base, months)
            if due < datetime.now().date():
                self.add_issue("WARNING", "REF 需复核",
                               f"{doc.path}: 最近核验 {m.group(1)} + 复查周期 "
                               f"'{fields.get('复查周期')}' 已于 {due.isoformat()} 到期，"
                               "请核验来源是否仍有效并更新 `最近核验日期`")

    # ------------------------------------------------------------- PLN 闭环

    def _codes_in(self, text: str) -> List[str]:
        """从一段文本里取出全部已知的**细项**编码（不含文档编码）。"""
        out: List[str] = []
        for m in re.finditer(
                r"((?:[A-Z]{2,4}-)?[A-Z]{1,5}[0-9]?-\d{2,4})(?![0-9A-Za-z])", text):
            code, t, _n = self._split_code(m.group(1))
            if code and t in self.type_codes and code not in out:
                out.append(code)
        return out

    def _pln_field(self, code: str, field: str) -> str:
        """跨文档取 PLN 的记录型字段值：定义块属性行优先，其次登记表同名列。

        PLN 的定义块在所属层级文档（默认 L2），而 `建议复审日期` 也可能只填在
        规划总览的登记表里，因此两边都要看。
        """
        fallback = ""
        for doc in self.docs:
            for i in sorted(self._own_lines(doc, code, block=True)):
                m = PLN_FIELD.match(doc.lines[i - 1])
                if m and m.group(1) == field and norm(m.group(2)):
                    return norm(m.group(2))
            for _h, header, rows in iter_tables(doc.lines):
                c_code = col_index(header, "编码", "PLN 编码")
                c_field = col_index(header, field)
                if c_code is None or c_field is None:
                    continue
                for _r, cells in rows:
                    if (c_code < len(cells) and c_field < len(cells)
                            and self._split_code(cells[c_code])[0] == code
                            and norm(cells[c_field]) and not fallback):
                        fallback = norm(cells[c_field])
        return fallback

    def _pln_targets(self, code: str) -> List[str]:
        """取 PLN 的落实目标编码：`落实记录` 段内的编码 + 登记表同名列（含「落实为」）。"""
        out: List[str] = []
        for doc in self.docs:
            lines = doc.lines
            armed = False
            for i in sorted(self._own_lines(doc, code, block=True)):
                line = lines[i - 1]
                m = PLN_FIELD.match(line)
                if m and m.group(1) == "落实记录":
                    armed = True
                    out += self._codes_in(m.group(2))
                    continue
                if armed:
                    if (BOLD_ATTR_ANY.match(line) or line.lstrip().startswith("|")
                            or re.match(r"^\s{0,3}#{1,6}\s+", line)):
                        armed = False
                    else:
                        out += self._codes_in(line)
            for _h, header, rows in iter_tables(lines):
                c_code = col_index(header, "编码", "PLN 编码")
                c_land = col_index(header, "落实记录", "落实为")
                if c_code is None or c_land is None:
                    continue
                for _r, cells in rows:
                    if (c_code < len(cells) and c_land < len(cells)
                            and self._split_code(cells[c_code])[0] == code):
                        out += self._codes_in(cells[c_land])
        uniq: List[str] = []
        for c in out:
            if not c.startswith("PLN-") and c not in uniq:
                uniq.append(c)
        return uniq

    def check_pln_closure(self) -> None:
        """PLN 闭环：`落实情况` 与 `落实记录` 一致，未落实者有复审兜底，已落实者被回指。

        `细项状态` 与 `落实情况` **正交**：状态只表达想法记录自身的生命周期
        （定论即 `正式`，与是否已展开无关），是否已展开由 `落实情况` 表达。
        房规见 `references/coding-system.md` ·《规划项生命周期》。
        """
        done: Set[str] = set()
        for doc in self.docs:
            if doc.archived:
                continue
            for item in doc.items:
                if item.type_code != "PLN" or item.code in done:
                    continue
                owner = self.item_def_doc.get(item.code)
                if owner is not None and owner is not doc:
                    continue        # 只在定义位判定，避免登记视图重复报告
                done.add(item.code)
                if self._pln_landed(doc, item):
                    self._check_pln_landing(doc, item)
                elif item.item_status != "废弃":
                    self._check_pln_review(doc, item)

    def _pln_landed(self, doc: DocInfo, item: ItemInfo) -> bool:
        """判定 PLN 是否已落实。

        `落实情况` 是显式判据（封闭值域 `未落实` / `已落实`）。缺字段、占位符或
        值非法时退回按 `落实记录` 是否指向目标细项推断，并提示补齐——存量文档
        迁移期不阻断。
        """
        where = f"{doc.path}:{item.line} `{item.code}`"
        val = self._pln_field(item.code, "落实情况") or ""
        if val.startswith("已落实"):
            return True
        if val.startswith("未落实"):
            return False
        targets = self._pln_targets(item.code)
        inferred = "已落实" if targets else "未落实"
        if not val or "{" in val or val.strip().lower() in EMPTY_MARKS:
            self.add_issue("INFO", "PLN 缺落实情况",
                           f"{where}: MUST 补 `落实情况`（`未落实` / `已落实`）——它是「想法是否"
                           "已全部展开」的显式终局判据，与 `细项状态` 正交；本轮暂按 `落实记录` "
                           f"推断为「{inferred}」")
        else:
            self.add_issue("WARNING", "PLN 落实情况取值非法",
                           f"{where}: `落实情况` '{val}' 不在封闭值域 "
                           f"{' / '.join(PLN_LANDING_VALUES)} 内；本轮暂按 `落实记录` "
                           f"推断为「{inferred}」")
        return bool(targets)

    def _check_pln_review(self, doc: DocInfo, item: ItemInfo) -> None:
        """未落实的 PLN：`建议复审日期` 必填；已到期则提示重新评估（INFO，不阻断）。"""
        where = f"{doc.path}:{item.line} `{item.code}`"
        raw = self._pln_field(item.code, "建议复审日期")
        if not raw or "{" in raw or raw.strip().lower() in EMPTY_MARKS:
            self.add_issue("INFO", "PLN 缺建议复审日期",
                           f"{where}: `落实情况` 为 `未落实` 且 `细项状态` 非 `废弃`，"
                           "MUST 填 `建议复审日期` 作为复审兜底")
            return
        m = re.search(r"(\d{4}-\d{2}-\d{2})", raw)
        if not m:
            self.add_issue("INFO", "PLN 建议复审日期格式",
                           f"{where}: `建议复审日期` '{raw}' 非 YYYY-MM-DD")
            return
        try:
            due = datetime.strptime(m.group(1), "%Y-%m-%d").date()
        except ValueError:
            self.add_issue("INFO", "PLN 建议复审日期格式",
                           f"{where}: `建议复审日期` '{m.group(1)}' 不是有效日期")
            return
        if due < datetime.now().date():
            self.add_issue("INFO", "PLN 待复审",
                           f"{where}: 建议复审日期 {m.group(1)} 已过，请重新评估——"
                           "展开为具体细项（置 `落实情况：已落实` 并写 `落实记录`）、"
                           "延后（更新日期）或 `废弃`")

    def _check_pln_landing(self, doc: DocInfo, item: ItemInfo) -> None:
        """`已落实` 的 PLN：`落实记录` 非空，且每个目标细项的定义块回指本 PLN。"""
        where = f"{doc.path}:{item.line} `{item.code}`"
        targets = self._pln_targets(item.code)
        if not targets:
            self.add_issue("ERROR", "已落实但无落实记录",
                           f"{where}: `落实情况` 为 `已落实`，但 `落实记录` 未指向任何目标"
                           "细项——`已落实` MUST 有非空 `落实记录`；尚在分批展开者应为"
                           " `未落实`（`落实记录` MAY 先记过程条目）")
            return
        for t in targets:
            tdoc = self.item_def_doc.get(t)
            if tdoc is None:
                continue            # 目标不在本次扫描范围，不误报
            if item.code not in self._item_block(tdoc, t):
                self.add_issue("WARNING", "落实目标未回指 PLN",
                               f"{tdoc.path}: `{t}` 的定义块缺 `来源` 回指 "
                               f"`{item.code}`，双向追溯断裂")

    # ------------------------------------------------------------- 引用反查

    def find_references(self, code: str) -> List[Tuple[str, int, str, str]]:
        """反查某编码的全部出现位置：[(文件, 行号, 定义/登记|引用, 原文)]。

        改标题与 `初稿` 期删除前 MUST 先执行本反查，并一并修改全部引用处。
        """
        pat = re.compile(r"(?<![0-9A-Za-z_-])" + re.escape(code) + r"(?![0-9A-Za-z])")
        out: List[Tuple[str, int, str, str]] = []
        for doc in self.docs:
            own = self._own_lines(doc, code, block=True)
            for lineno, line in enumerate(doc.raw_lines, 1):
                if pat.search(line):
                    if lineno not in own:
                        kind = "引用"
                    else:
                        kind = "登记" if line.lstrip().startswith("|") else "定义"
                    out.append((doc.path, lineno, kind, line.strip()))
        return out

    # ------------------------------------------------------------------ 执行

    def run_checks(self) -> List[Dict]:
        """运行所有检查"""
        print("🔍 开始扫描文档...")
        self.scan_docs()
        print(f"📄 找到 {len(self.docs)} 个文档")

        print("🔧 运行检查规则...")
        self.check_doc_meta()
        self.check_duplicate_codes()
        self.check_item_status()
        self.check_registration_consistency()
        self.check_references()
        self.check_index_order_and_gaps()
        self.check_counters()
        self.check_version_flow()
        self.check_chapter_references()
        self.check_structure()
        self.check_def_blocks()
        self.check_anchor_reachability()
        self.check_dec_layer()
        self.check_deprecation()
        self.check_draft_finalization()
        self.check_status_gating()
        self.check_layer_references()
        self.check_legacy_statuses()
        self.check_title_lock()
        self.check_ref_freshness()
        self.check_pln_closure()
        return self.issues

    # ------------------------------------------------------------------ 输出

    LEVELS = ("CRITICAL", "ERROR", "WARNING", "INFO")

    def level_count(self) -> Dict[str, int]:
        counts: Dict[str, int] = defaultdict(int)
        for issue in self.issues:
            counts[issue["level"]] += 1
        return counts

    def generate_report(self) -> str:
        """生成检查报告（纯文本，可直接落盘）。"""
        items_total = sum(len(d.items) for d in self.docs)
        defined_total = sum(len([i for i in d.items if i.defined]) for d in self.docs)
        archived_total = len([d for d in self.docs if d.archived])
        index_total = len([d for d in self.docs if d.is_index])
        counts = self.level_count()

        report: List[str] = []
        report.append("=" * 80)
        report.append("DesignDoc 文档检查报告")
        report.append("=" * 80)
        report.append("")
        report.append(f"检查目录: {self.ued_path}")
        report.append(f"检查时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")

        report.append("📊 文档统计:")
        report.append(f"  文档总数: {len(self.docs)}（索引 {index_total}、归档 {archived_total}）")
        report.append(f"  文档编码数: {len(self.codes)}")
        report.append(f"  细项编码数: {items_total}（正文定义 {defined_total}）")
        report.append(f"  问题总数: {len(self.issues)}")
        report.append("")

        doc_type_count: Dict[str, int] = defaultdict(int)
        for doc in self.docs:
            doc_type_count["README/索引" if doc.is_index else doc.doc_type] += 1
        report.append("📑 文档类型分布:")
        for doc_type, count in sorted(doc_type_count.items()):
            report.append(f"  {doc_type}: {count}")
        report.append("")

        report.append("⚠️ 问题统计:")
        for level in self.LEVELS:
            if counts[level]:
                report.append(f"  {level}: {counts[level]}")
        report.append("")

        if self.issues:
            report.append("🔍 问题详情:")
            report.append("")
            for level in self.LEVELS:
                level_issues = [i for i in self.issues if i["level"] == level]
                if not level_issues:
                    continue
                report.append(f"### {level}（{len(level_issues)}）")
                for n, issue in enumerate(level_issues, 1):
                    report.append(f"{n}. {issue['title']}")
                    report.append(f"   {issue['description']}")
                report.append("")

            by_title: Dict[str, int] = defaultdict(int)
            for issue in self.issues:
                by_title[issue["title"]] += 1
            report.append("📌 按检查项汇总:")
            for title, count in sorted(by_title.items(), key=lambda kv: (-kv[1], kv[0])):
                report.append(f"  {title}: {count}")
            report.append("")

        if not self.issues:
            report.append("✅ 未发现问题，文档规范良好。")
        elif counts["CRITICAL"] or counts["ERROR"]:
            report.append("❌ 存在严重问题（CRITICAL/ERROR），修复后方可定稿。")
        else:
            report.append("⚠️ 存在 WARNING/INFO 项，建议在本轮内一并处理。")
        report.append("")
        report.append("=" * 80)
        return "\n".join(report)

    def print_summary(self) -> int:
        """打印摘要并返回退出码（CRITICAL/ERROR 存在时为 1）。"""
        counts = self.level_count()
        print(f"\n📊 检查完成: {len(self.docs)} 个文档, {len(self.issues)} 个问题")
        for level in self.LEVELS:
            if counts[level]:
                icon = "🔴" if level in ("CRITICAL", "ERROR") else "🟡" if level == "WARNING" else "🔵"
                print(f"  {icon} {level}: {counts[level]}")

        if counts["CRITICAL"] or counts["ERROR"]:
            print("\n❌ 存在严重问题，请查看详细报告（-v 或 -o）")
            return 1
        if counts["WARNING"]:
            print("\n⚠️ 存在警告，建议修复")
        else:
            print("\n✅ 文档检查通过")
        return 0


class TemplateChecker:
    """`assets/templates/` 哨兵房规校验。

    只执行校验、不重复定义规则；规则本体见
    `assets/templates/index.md · 模板边界（哨兵）`。
    """

    LEVELS = ("CRITICAL", "ERROR", "WARNING", "INFO")

    def __init__(self, tpl_dir: Optional[Path] = None):
        self.tpl_dir = Path(tpl_dir) if tpl_dir else TEMPLATE_DIR
        self.issues: List[Dict] = []
        self.checked = 0

    def add_issue(self, level: str, title: str, description: str) -> None:
        self.issues.append({"level": level, "title": title, "description": description})

    def run(self) -> List[Dict]:
        if not self.tpl_dir.exists():
            self.add_issue("CRITICAL", "模板目录不存在", f"未找到 {self.tpl_dir}")
            return self.issues
        for path in sorted(self.tpl_dir.glob("*.md")):
            if path.name in TPL_NON_FILES:
                continue
            self.checked += 1
            try:
                self._check_one(path, path.read_text(encoding="utf-8"))
            except Exception as exc:  # noqa: BLE001
                self.add_issue("ERROR", "读取模板失败", f"{path.name}: {exc}")
        return self.issues

    def _check_one(self, path: Path, text: str) -> None:
        name = path.name
        lines = text.splitlines()
        segs, errs = template_segments(lines)
        for err in errs:
            self.add_issue("ERROR", "模板哨兵不配对", f"{name}: {err}")
        if not segs and not errs:
            self.add_issue("ERROR", "模板缺哨兵",
                           f"{name}: 未见 `TEMPLATE:BEGIN` / `TEMPLATE:END`，待复制正文无边界")
            return
        fragment = name in TPL_FRAGMENT_FILES
        inside: Set[int] = set()
        for seg in segs:
            if seg["end"]:
                inside.update(range(seg["begin"], seg["end"] + 1))

        for n, line in enumerate(lines, 1):
            if n in inside:
                continue
            if TPL_FENCE_WRAP.match(line):
                self.add_issue("ERROR", "模板残留外层围栏",
                               f"{name}:{n}: 哨兵外仍有 ```markdown 围栏——正文 MUST 由哨兵界定，"
                               "不再用围栏包裹（围栏会使正文不可渲染）")
            if not fragment and line.startswith("# "):
                self.add_issue("ERROR", "整篇型模板容器自带 H1",
                               f"{name}:{n}: 整篇型模板 MUST NOT 自带 H1；唯一 H1 应在哨兵内"
                               "（即目标文档的标题）")

        for seg in segs:
            if not seg["end"]:
                continue
            body = seg["body"]
            where = f"{name}:{seg['begin']}"
            h1 = [ln for ln in body if ln.startswith("# ")]
            if not fragment and len(h1) != 1:
                self.add_issue("ERROR", "哨兵段 H1 数不合规",
                               f"{where}: 整篇型模板每段 MUST 恰有一个 H1，实得 {len(h1)}")
            for off, ln in enumerate(body, seg["begin"] + 1):
                if TPL_USAGE_HEAD.match(ln):
                    self.add_issue("ERROR", "使用说明混入待复制正文",
                                   f"{name}:{off}: `使用说明` MUST 置于哨兵之外（前置），"
                                   "否则会被复制进目标文档")
            if len(segs) > 1 and seg["name"]:
                label = self._label_above(lines, seg["begin"])
                if label and label.replace("`", "") != seg["name"]:
                    self.add_issue("WARNING", "哨兵段名与可见标签不一致",
                                   f"{where}: 哨兵参数「{seg['name']}」与上方标签「{label}」不符")

        if "正文边界" not in text:
            self.add_issue("WARNING", "模板缺正文边界指针",
                           f"{name}: 未见「正文边界」说明行，AI 可能连带复制哨兵外的元信息")

    @staticmethod
    def _label_above(lines: List[str], begin: int) -> str:
        """取哨兵上方最近的 `> **{段名}**` 可见标签；无则返回空串。"""
        for i in range(begin - 2, max(-1, begin - 6), -1):
            match = TPL_LABEL.match(lines[i])
            if match:
                return match.group(1).strip()
            if lines[i].strip() and not lines[i].startswith(">"):
                break
        return ""

    def print_summary(self) -> int:
        """打印模板校验结果并返回退出码（CRITICAL/ERROR 存在时为 1）。"""
        if not self.issues:
            print(f"✅ 模板哨兵校验通过：{self.checked} 个模板（{self.tpl_dir}）")
            return 0
        order = {level: n for n, level in enumerate(self.LEVELS)}
        for issue in sorted(self.issues, key=lambda x: order.get(x["level"], 9)):
            print(f"[{issue['level']}] {issue['title']}")
            print(f"    {issue['description']}")
        bad = any(i["level"] in ("CRITICAL", "ERROR") for i in self.issues)
        print(f"\n{'❌' if bad else '⚠️'} {self.checked} 个模板共 {len(self.issues)} 个问题")
        return 1 if bad else 0


def _print_instantiated(tpl: str, segment: Optional[str]) -> int:
    """把模板剥除哨兵后输出，供渲染预览与实例化效果评估。"""
    path = Path(tpl)
    if not path.exists():
        path = TEMPLATE_DIR / tpl
    if not path.exists():
        print(f"未找到模板: {tpl}（已尝试 {TEMPLATE_DIR / tpl}）")
        return 1
    segs = instantiate_template(path.read_text(encoding="utf-8"))
    if segment:
        segs = [s for s in segs if s[0] == segment]
    if not segs:
        print(f"{path.name}: 无匹配哨兵段（--segment 需与哨兵参数完全一致）")
        return 1
    for name, body in segs:
        if len(segs) > 1:
            print(f"===== 段：{name or '(未命名)'} =====")
        sys.stdout.write(body)
    return 0


def main() -> int:
    """命令行入口。"""
    import argparse

    parser = argparse.ArgumentParser(description="DesignDoc 文档检查工具")
    parser.add_argument("-p", "--path", default="./ued",
                        help="UED 目录路径 (默认: ./ued)")
    parser.add_argument("-o", "--output", help="输出报告到文件")
    parser.add_argument("-v", "--verbose", action="store_true", help="显示详细信息")
    parser.add_argument("--refs", metavar="CODE",
                        help="反查指定编码的全部出现位置（改标题 / `初稿` 期删除前 MUST 先执行）")
    parser.add_argument("--check-templates", action="store_true",
                        help="校验 assets/templates/ 的哨兵房规（成对、唯一 H1、无残留外层围栏）")
    parser.add_argument("--instantiate", metavar="TPL",
                        help="剥除哨兵输出模板实例化后的正文（文件名或路径），供预览评估")
    parser.add_argument("--segment", metavar="NAME",
                        help="配合 --instantiate：只输出指定段名的那一段")
    args = parser.parse_args()

    if args.check_templates:
        tpl_checker = TemplateChecker()
        tpl_checker.run()
        return tpl_checker.print_summary()

    if args.instantiate:
        return _print_instantiated(args.instantiate, args.segment)

    checker = DesignDocChecker(args.path)

    if args.refs:
        checker.scan_docs()
        hits = checker.find_references(args.refs)
        if not hits:
            print(f"未找到编码 {args.refs} 的任何出现位置（请确认编码与 --path 范围）")
            return 1
        print(f"🔎 {args.refs} 共出现 {len(hits)} 处（改标题 / 删除前需一并处理）：")
        for path, lineno, kind, text in hits:
            print(f"  [{kind}] {path}:{lineno}  {text[:120]}")
        return 0

    checker.run_checks()
    report = checker.generate_report()

    if args.output:
        Path(args.output).write_text(report + "\n", encoding="utf-8")
        print(f"📄 报告已保存到: {args.output}")
    if args.verbose or not args.output:
        print("\n" + report)

    return checker.print_summary()


if __name__ == "__main__":
    sys.exit(main())
