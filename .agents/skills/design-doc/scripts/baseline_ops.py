"""产品基线快照（baselines/vX.Y.yaml）的读写、差分与升版/补丁。

规则本体见 references/product-version.md；本模块只执行，不另定语义。
"""
from __future__ import annotations

import re
from copy import deepcopy
from datetime import date
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Set, Tuple

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None  # type: ignore

# 两段式：文件名 / README / product_version
VERSION_RE = re.compile(r"^v\d+\.\d+$")
# 完整 SemVer tip：full_version / prev
FULL_VERSION_RE = re.compile(r"^v(\d+)\.(\d+)\.(\d+)$")
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
_LINEAGE_AFTER = ("最后修订日期", "创建日期", "修订版本号", "细项状态")


def version_key(ver: str) -> Tuple[int, int]:
    xy = xy_of(ver)
    m = VERSION_RE.match(xy or "")
    if not m:
        return (-1, -1)
    a, b = xy[1:].split(".", 1)
    return int(a), int(b)


def xy_of(ver: str) -> str:
    """`v5.26.2` / `v5.26` → `v5.26`；无法识别则空串。"""
    ver = (ver or "").strip()
    m = FULL_VERSION_RE.match(ver)
    if m:
        return f"v{m.group(1)}.{m.group(2)}"
    if VERSION_RE.match(ver):
        return ver
    return ""


def full_version_key(ver: str) -> Tuple[int, int, int]:
    m = FULL_VERSION_RE.match((ver or "").strip())
    if not m:
        return (-1, -1, -1)
    return int(m.group(1)), int(m.group(2)), int(m.group(3))


def initial_full(xy: str) -> str:
    xy = xy_of(xy) or "v1.0"
    return f"{xy}.0"


def bump_full_patch(full: str) -> str:
    m = FULL_VERSION_RE.match((full or "").strip())
    if not m:
        return initial_full(full)
    return f"v{m.group(1)}.{m.group(2)}.{int(m.group(3)) + 1}"


def next_version(ver: str, major: bool = False) -> str:
    a, b = version_key(ver)
    if a < 0:
        return "v1.0"
    if major:
        return f"v{a + 1}.0"
    return f"v{a}.{b + 1}"


def effective_full_version(data: Dict[str, Any]) -> str:
    """读取 tip；存量缺字段时回落为 `{product_version}.0`。"""
    fv = str(data.get("full_version") or "").strip()
    if FULL_VERSION_RE.match(fv):
        return fv
    pv = str(data.get("product_version") or "").strip()
    return initial_full(pv) if VERSION_RE.match(pv) else ""


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
    lines: List[str] = []
    lines.append(f"product_version: {data['product_version']}")
    fv = data.get("full_version") or initial_full(data["product_version"])
    lines.append(f"full_version: {fv}")
    created = data.get("created") or data.get("date") or date.today().isoformat()
    updated = data.get("updated") or created
    lines.append(f"created: {created}")
    lines.append(f"updated: {updated}")
    prev = data.get("prev")
    if prev:
        lines.append(f"prev: {prev}")
    else:
        lines.append("prev: null")
    log = data.get("patch_log")
    if log is None and data.get("note"):
        log = [{"full_version": fv, "date": updated,
                "note": str(data.get("note") or "")}]
    if log:
        lines.append("patch_log:")
        for entry in log:
            lines.append(f"  - full_version: {entry.get('full_version')}")
            lines.append(f"    date: {entry.get('date')}")
            note = str(entry.get("note") or "").replace('"', '\\"')
            lines.append(f'    note: "{note}"')
    else:
        lines.append("patch_log: []")
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
    idx = max(0, item_line - 1)
    for i in range(idx, -1, -1):
        m = HEADING_TITLE.match(lines[i])
        if m:
            return m.group(1).strip()
        if re.match(r"^\s{0,3}#{1,6}\s+", lines[i]) and i < idx:
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


def resolve_prev_path(bdir: Path, prev: Any) -> Optional[Path]:
    """`prev` 为 tip SemVer 或两段式时，解析到 `baselines/vX.Y.yaml`。"""
    if prev in (None, "null", ""):
        return None
    xy = xy_of(str(prev))
    if not xy:
        return None
    path = bdir / f"{xy}.yaml"
    return path if path.is_file() else path  # 返回期望路径，由调用方判 exists


def build_snapshot(
    product_version: str,
    curr_items: List[Dict[str, Any]],
    prev_data: Optional[Dict[str, Any]] = None,
    note: str = "",
    when: Optional[str] = None,
    full_version: str = "",
    prev_tip: Any = None,
    created: str = "",
    patch_log: Optional[List[Dict[str, str]]] = None,
) -> Dict[str, Any]:
    prev_items = list((prev_data or {}).get("items") or [])
    added, removed, changed = compute_delta(prev_items, curr_items)
    if not prev_data:
        # 首份基线没有前驱：增量字段表示版本间差异，不记开发期操作历史。
        added, removed, changed = [], [], []
        tip_prev = None
    else:
        tip_prev = prev_tip
        if tip_prev is None:
            tip_prev = effective_full_version(prev_data)
    today = when or date.today().isoformat()
    fv = full_version or initial_full(product_version)
    created_s = created or today
    log = list(patch_log or [])
    if not any(str(e.get("full_version")) == fv for e in log):
        log.append({"full_version": fv, "date": today, "note": note or ""})
    return {
        "product_version": product_version,
        "full_version": fv,
        "created": created_s,
        "updated": today,
        "prev": tip_prev,
        "patch_log": log,
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
    idx = max(0, item_line - 1)
    j = idx + 1
    while j < len(lines) and not lines[j].strip():
        j += 1
    start = j
    while j < len(lines) and lines[j].strip() and ATTR_FIELD.match(lines[j]):
        j += 1
    return start, j


def set_item_attr(lines: List[str], item_line: int, field: str, value: str) -> bool:
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


def _item_locations(docs) -> Dict[str, Tuple[Path, int, str]]:
    """编码 → (文件, 行号, 细项状态)；供谱系回写与清理共用。"""
    out: Dict[str, Tuple[Path, int, str]] = {}
    for doc in docs:
        path = Path(getattr(doc, "path", "") or "")
        if not path:
            continue
        for item in getattr(doc, "items", []) or []:
            if not getattr(item, "defined", True):
                continue
            code = getattr(item, "code", "") or ""
            line = getattr(item, "line", 0) or 0
            status = (getattr(item, "item_status", "")
                      or getattr(item, "def_status", "")).strip()
            if code and line:
                out[code] = (path, line, status)
    return out


def stamp_lineage_cache(
    docs,
    added,
    removed,
    version: str = "",
) -> List[Path]:
    """立新基线时回写 `引入版本` / `退出版本`（值为两段 `vX.Y`）。

    条目可写编码或 `(编码, 版本)`；冻结时用后者把工作期内的成员进出
    归属到其实际所在的产品版本。`退出版本` 只写给当前已 `废弃` 的条目。
    """
    from collections import defaultdict

    def _pairs(entries) -> List[Tuple[str, str]]:
        out: List[Tuple[str, str]] = []
        for entry in entries or []:
            if isinstance(entry, (tuple, list)) and len(entry) == 2:
                out.append((str(entry[0]), str(entry[1])))
            else:
                out.append((str(entry), version))
        return out

    code_loc = _item_locations(docs)

    jobs: Dict[Path, List[Tuple[int, str, str]]] = defaultdict(list)
    for code, ver in _pairs(added):
        if code in code_loc and ver:
            path, line, _ = code_loc[code]
            jobs[path].append((line, "引入版本", ver))
    for code, ver in _pairs(removed):
        if code in code_loc and ver:
            path, line, status = code_loc[code]
            if status == "废弃":
                jobs[path].append((line, "退出版本", ver))

    changed: List[Path] = []
    for path, ops in jobs.items():
        if not path.is_file():
            continue
        raw = path.read_text(encoding="utf-8")
        lines = raw.splitlines()
        dirty = False
        for item_line, field, ver in sorted(ops, key=lambda t: t[0], reverse=True):
            if set_item_attr(lines, item_line, field, ver):
                dirty = True
        if dirty:
            ending = "\n" if raw.endswith("\n") else ""
            path.write_text("\n".join(lines) + ending, encoding="utf-8")
            changed.append(path)
    return changed


def prune_lineage_cache(
    docs,
    version: str,
    keep_codes: Set[str],
    fields: Tuple[str, ...] = ("引入版本", "退出版本"),
) -> List[Path]:
    """清除与最终冻结集合冲突的自动谱系缓存。

    仅删除值等于 `version` 且编码不在 `keep_codes` 的字段；其他版本与其他
    元数据原样保留。
    """
    if not version:
        return []
    from collections import defaultdict

    code_loc = _item_locations(docs)
    jobs: Dict[Path, List[Tuple[int, str, str]]] = defaultdict(list)
    for code, (path, line, _) in code_loc.items():
        if code in keep_codes:
            continue
        for field in fields:
            jobs[path].append((line, field, version))

    changed: List[Path] = []
    for path, ops in jobs.items():
        if not path.is_file():
            continue
        raw = path.read_text(encoding="utf-8")
        lines = raw.splitlines()
        dirty = False
        for item_line, field, ver in sorted(ops, key=lambda t: t[0], reverse=True):
            start, end = _attr_group_range(lines, item_line)
            for i in range(start, end):
                m = ATTR_FIELD.match(lines[i])
                if m and m.group(2) == field and m.group(3).strip() == ver:
                    del lines[i]
                    dirty = True
                    break
        if dirty:
            ending = "\n" if raw.endswith("\n") else ""
            path.write_text("\n".join(lines) + ending, encoding="utf-8")
            changed.append(path)
    return changed
