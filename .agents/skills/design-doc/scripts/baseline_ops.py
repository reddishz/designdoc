"""产品基线快照（baselines/vX.Y.yaml）的读写、差分与升版。

规则本体见 references/product-version.md；本模块只执行，不另定语义。
"""
from __future__ import annotations

import re
from copy import deepcopy
from datetime import date
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None  # type: ignore

VERSION_RE = re.compile(r"^v\d+\.\d+$")
HEADING_TITLE = re.compile(
    r"^\s{0,3}#{1,6}\s+"
    r"(?:[A-Z][A-Z0-9]{1,4}-)?[A-Z]{1,5}[0-9]?-\d{2,4}\s*[:：]\s*(.+?)\s*$"
)
ATTR_REV = re.compile(
    r"^\s*[-*+]\s+\*\*修订版本号\*\*\s*[:：]\s*(\d+)\s*$"
)
ATTR_FIELD = re.compile(
    r"^(\s*[-*+]\s+\*\*(.+?)\*\*\s*[:：]\s*)(.*)$"
)
# 谱系缓存插入点：紧随治理段末行 `最后修订日期`（见 coding-system 段位）
_LINEAGE_AFTER = ("最后修订日期", "创建日期", "修订版本号", "细项状态")


def version_key(ver: str) -> Tuple[int, int]:
    m = VERSION_RE.match(ver or "")
    if not m:
        return (-1, -1)
    a, b = ver[1:].split(".", 1)
    return int(a), int(b)


def next_version(ver: str, major: bool = False) -> str:
    a, b = version_key(ver)
    if a < 0:
        return "v1.0"
    if major:
        return f"v{a + 1}.0"
    return f"v{a}.{b + 1}"


def load_baseline(path: Path) -> Dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    if yaml is None:
        raise RuntimeError("需要 PyYAML 以读写 baselines/*.yaml")
    data = yaml.safe_load(text)
    if not isinstance(data, dict):
        raise ValueError(f"{path}: 根节点须为 mapping")
    return data


def dump_baseline(data: Dict[str, Any]) -> str:
    if yaml is None:
        raise RuntimeError("需要 PyYAML 以读写 baselines/*.yaml")
    # 稳定键序：手工拼装，避免 sort_keys 打乱 items 内字段观感
    lines: List[str] = []
    lines.append(f"product_version: {data['product_version']}")
    lines.append(f"date: {data['date']}")
    if data.get("note"):
        note = str(data["note"]).replace('"', '\\"')
        lines.append(f'note: "{note}"')
    prev = data.get("prev")
    if prev:
        lines.append(f"prev: {prev}")
    else:
        lines.append("prev: null")
    lines.append("")
    for key in ("added", "removed", "changed"):
        vals = data.get(key) or []
        if not vals:
            lines.append(f"{key}: []")
        else:
            lines.append(f"{key}:")
            for c in vals:
                lines.append(f"  - {c}")
    lines.append("")
    lines.append("items:")
    for it in data.get("items") or []:
        lines.append(f"  - code: {it['code']}")
        lines.append(f"    type: {it['type']}")
        title = str(it.get("title") or "").replace('"', '\\"')
        lines.append(f'    title: "{title}"')
        lines.append(f"    revision: {int(it['revision'])}")
        lines.append(f"    doc: {it['doc']}")
    lines.append("")
    return "\n".join(lines)


def items_by_code(items: Iterable[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    out: Dict[str, Dict[str, Any]] = {}
    for it in items or []:
        code = str(it.get("code") or "").strip()
        if code:
            out[code] = it
    return out


def compute_delta(
    prev_items: List[Dict[str, Any]],
    curr_items: List[Dict[str, Any]],
) -> Tuple[List[str], List[str], List[str]]:
    prev = items_by_code(prev_items)
    curr = items_by_code(curr_items)
    added = sorted(set(curr) - set(prev))
    removed = sorted(set(prev) - set(curr))
    changed = sorted(
        c for c in set(curr) & set(prev)
        if int(curr[c].get("revision") or 0) > int(prev[c].get("revision") or 0)
    )
    return added, removed, changed


def extract_item_title(lines: List[str], item_line: int) -> str:
    """item_line 为 1-based；标题取定义块最近上方含编码的标题行。"""
    idx = max(0, item_line - 1)
    for i in range(idx, -1, -1):
        m = HEADING_TITLE.match(lines[i])
        if m:
            return m.group(1).strip()
        if re.match(r"^\s{0,3}#{1,6}\s+", lines[i]) and i < idx:
            # 其它标题：尝试「编码：标题」已失败则截掉编码前缀
            body = re.sub(r"^\s{0,3}#{1,6}\s+", "", lines[i]).strip()
            body = re.sub(
                r"^(?:[A-Z][A-Z0-9]{1,4}-)?[A-Z]{1,5}[0-9]?-\d{2,4}\s*",
                "",
                body,
            ).strip(" ：:")
            return body
    return ""


def extract_item_revision(lines: List[str], item_line: int) -> int:
    idx = max(0, item_line - 1)
    # 属性行组在标题下方
    j = idx + 1
    while j < len(lines) and not lines[j].strip():
        j += 1
    while j < len(lines) and lines[j].strip():
        m = ATTR_REV.match(lines[j])
        if m:
            return int(m.group(1))
        j += 1
    return 1


def collect_formal_items(docs) -> List[Dict[str, Any]]:
    """从已扫描 DocInfo 列表收集全部正式细项。"""
    rows: List[Dict[str, Any]] = []
    seen = set()
    for doc in docs:
        if getattr(doc, "is_index", False) or getattr(doc, "archived", False):
            continue
        doc_code = doc.doc_code or Path(doc.path).stem
        for item in doc.items:
            if not item.defined:
                continue
            st = item.item_status or item.def_status
            if st != "正式":
                continue
            if item.code in seen:
                continue
            seen.add(item.code)
            rev = extract_item_revision(doc.lines, item.line)
            title = extract_item_title(doc.lines, item.line)
            rows.append({
                "code": item.code,
                "type": item.type_code,
                "title": title,
                "revision": rev,
                "doc": doc_code,
            })
    rows.sort(key=lambda r: r["code"])
    return rows


def build_snapshot(
    product_version: str,
    curr_items: List[Dict[str, Any]],
    prev_data: Optional[Dict[str, Any]] = None,
    note: str = "",
    when: Optional[str] = None,
) -> Dict[str, Any]:
    prev_items = list((prev_data or {}).get("items") or [])
    prev_ver = (prev_data or {}).get("product_version")
    added, removed, changed = compute_delta(prev_items, curr_items)
    if not prev_data:
        added = [it["code"] for it in curr_items]
        removed, changed = [], []
        prev_ver = None
    return {
        "product_version": product_version,
        "date": when or date.today().isoformat(),
        "note": note or "",
        "prev": prev_ver,
        "added": added,
        "removed": removed,
        "changed": changed,
        "items": deepcopy(curr_items),
    }


def find_baseline_dir(scope_dir: Path) -> Path:
    return scope_dir / "baselines"


def list_baseline_files(scope_dir: Path) -> List[Path]:
    bdir = find_baseline_dir(scope_dir)
    if not bdir.is_dir():
        return []
    files = [p for p in bdir.glob("v*.yaml") if VERSION_RE.match(p.stem)]
    return sorted(files, key=lambda p: version_key(p.stem))


def latest_baseline(scope_dir: Path) -> Optional[Path]:
    files = list_baseline_files(scope_dir)
    return files[-1] if files else None


def _attr_group_range(lines: List[str], item_line: int) -> Tuple[int, int]:
    """属性行组在标题行（1-based）下方的 [start, end) 下标。"""
    idx = max(0, item_line - 1)
    j = idx + 1
    while j < len(lines) and not lines[j].strip():
        j += 1
    start = j
    while j < len(lines) and lines[j].strip() and ATTR_FIELD.match(lines[j]):
        j += 1
    return start, j


def set_item_attr(lines: List[str], item_line: int, field: str, value: str) -> bool:
    """在定义块属性行组内写入 `field`；已存在则改值，否则按段位插入。返回是否改动。"""
    start, end = _attr_group_range(lines, item_line)
    if start >= end:
        return False
    indent = re.match(r"^(\s*)", lines[start]).group(1) if start < len(lines) else ""
    bullet = f"{indent}- **{field}**：{value}"
    for i in range(start, end):
        m = ATTR_FIELD.match(lines[i])
        if m and m.group(2) == field:
            if m.group(3).strip() == value:
                return False
            lines[i] = f"{m.group(1)}{value}"
            return True
    # 插入：引入版本紧随治理段；退出版本紧随引入版本（若有）否则同引入
    names = []
    for i in range(start, end):
        m = ATTR_FIELD.match(lines[i])
        names.append(m.group(2) if m else "")
    if field == "退出版本" and "引入版本" in names:
        insert_at = start + names.index("引入版本") + 1
    else:
        insert_at = start + 1
        for anchor in _LINEAGE_AFTER:
            if anchor in names:
                insert_at = start + names.index(anchor) + 1
                break
    lines.insert(insert_at, bullet)
    return True


def stamp_lineage_cache(
    docs,
    added: List[str],
    removed: List[str],
    version: str,
) -> List[Path]:
    """升版回写 `引入版本` / `退出版本`。返回改过的文件路径。

    真源仍是 baselines/；本函数只维护对象上的便查阅缓存。
    """
    from collections import defaultdict

    code_loc: Dict[str, Tuple[Path, int]] = {}
    for doc in docs:
        path = Path(getattr(doc, "path", "") or "")
        if not path:
            continue
        for item in getattr(doc, "items", []) or []:
            if not getattr(item, "defined", True):
                continue
            code = getattr(item, "code", "") or ""
            line = getattr(item, "line", 0) or 0
            if code and line:
                code_loc[code] = (path, line)

    jobs: Dict[Path, List[Tuple[int, str, str]]] = defaultdict(list)
    for code in added or []:
        if code in code_loc:
            path, line = code_loc[code]
            jobs[path].append((line, "引入版本", version))
    for code in removed or []:
        if code in code_loc:
            path, line = code_loc[code]
            jobs[path].append((line, "退出版本", version))

    changed: List[Path] = []
    for path, ops in jobs.items():
        if not path.is_file():
            continue
        raw = path.read_text(encoding="utf-8")
        lines = raw.splitlines()
        dirty = False
        # 同文件多细项：按行号降序改，避免插入打乱后续下标
        for item_line, field, ver in sorted(ops, key=lambda t: t[0], reverse=True):
            if set_item_attr(lines, item_line, field, ver):
                dirty = True
        if dirty:
            ending = "\n" if raw.endswith("\n") else ""
            path.write_text("\n".join(lines) + ending, encoding="utf-8")
            changed.append(path)
    return changed
