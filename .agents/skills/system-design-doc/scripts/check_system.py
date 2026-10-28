#!/usr/bin/env python3
"""系统 / 子系统结构检查器（system-design-doc）。

只检查系统级编排，不检查子系统文档内部规则：

- 系统根 README：子系统注册表、当前结构、发布索引；根上不得有产品版本 / 基线 / 设计索引
- 注册表：键、目录、前缀、角色文档、状态、唯一性与 README 一致性
- 子系统目录：单层、已登记、有 README；无嵌套作用域
- 子系统基线扩展字段：depends_on / external_deps 的目标、版本与闭合
- 系统发布清单：发布项有效性、基线存在、patch_log、依赖闭合、外部依赖冲突
- 跨子系统：完整编码唯一定义、前缀归属、跨作用域引用、全局术语表

文档内部规则（编码、状态、定义块、单作用域产品基线等）由 design-doc 的
check_docs.py 负责；两者互不导入。
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Set, Tuple

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None  # type: ignore

VERSION_RE = re.compile(r"^v(\d+)\.(\d+)$")
FULL_VERSION_RE = re.compile(r"^v(\d+)\.(\d+)\.(\d+)$")
KEY_RE = re.compile(r"^[a-z][a-z0-9-]*$")
PREFIX_RE = re.compile(r"^[A-Z][A-Z0-9]{1,4}$")
ROLE_RE = re.compile(r"^(?:[A-Z][A-Z0-9]{1,4}-)?CMP-\d{2,4}$")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
RELEASE_FILE_RE = re.compile(r"^sys-v(\d+)\.(\d+)\.yaml$")
RESERVED_DIRS = {"releases", "references", "assets", "deprecated", "baselines"}
LAYER_DIR_RE = re.compile(r"^L[0-6]-")
PLACEHOLDER_RE = re.compile(r"\{[^}]*\}")

# design-doc 的类型码快照；仅用于识别「细项定义标题」，不承担类型规则
TYPE_CODES = {
    "GOL", "STK", "SCN", "FR", "NFR", "UC", "PRN", "DEC", "CMP", "IF", "FLW",
    "ALG", "DOM", "ASM", "RSK", "MET", "TC", "AC", "CON", "RUL", "ACT", "PLN",
    "REF",
}
DOC_CODE_RE = re.compile(r"^(?:[A-Z][A-Z0-9]{1,4}-)?(?:L[0-6]|ADR|EVAL|REF)-\d{2,4}$")
ITEM_CODE_RE = re.compile(r"^(?:([A-Z][A-Z0-9]{1,4})-)?([A-Z]{1,5}[0-9]?)-\d{2,4}$")
HEADING_CODE_RE = re.compile(
    r"^\s{0,3}#{1,6}\s+((?:[A-Z][A-Z0-9]{1,4}-)?([A-Z]{1,5}[0-9]?)-\d{2,4})\b")
REF_CODE_RE = re.compile(r"\b(([A-Z][A-Z0-9]{1,4})-[A-Z]{1,5}[0-9]?-\d{2,4})\b")
# 无前缀简写：只从链接文字与表格行识别为引用，正文散文里的裸编码不在此校验。
BARE_CODE_RE = re.compile(
    r"(?<![A-Za-z0-9_/-])([A-Z]{1,5}[0-9]?-\d{2,4})(?![0-9A-Za-z.])")
MD_LINK_TEXT_RE = re.compile(r"\[([^\]]+)\]\([^)]*\)")
INLINE_CODE_RE = re.compile(r"`[^`]*`")
DOC_META_CODE_RE = re.compile(r"^(?:[A-Z][A-Z0-9]{1,4}-)?(?:L[0-6]|ADR|EVAL|REF)-\d{2,4}$")
TERM_HEADING_RE = re.compile(r"^###\s+(.+?)\s*$")
ATTR_RE = re.compile(r"^-\s+\*\*(.+?)\*\*\s*[:：]\s*(.*)$")


@dataclass
class Subsystem:
    key: str
    name: str
    directory: str
    prefix: str
    role_doc: str
    status: str
    line: int = 0

    @property
    def dir_path(self) -> Path:
        return Path(self.directory)


@dataclass
class Issue:
    level: str
    title: str
    detail: str


def norm(value: str) -> str:
    value = (value or "").strip()
    value = value.replace("`", "").strip()
    value = re.sub(r"^\*\*(.+?)\*\*$", r"\1", value).strip()
    return value


def split_row(line: str) -> List[str]:
    s = line.strip()
    if s.startswith("|"):
        s = s[1:]
    if s.endswith("|"):
        s = s[:-1]
    return [norm(c) for c in s.split("|")]


def is_separator(line: str) -> bool:
    if "|" not in line:
        return False
    cells = split_row(line)
    return bool(cells) and all(re.fullmatch(r":?-{3,}:?", c) for c in cells)


def mask_fences(text: str) -> List[str]:
    lines = text.splitlines()
    out: List[str] = []
    fence = False
    for line in lines:
        if re.match(r"^\s*(```|~~~)", line):
            fence = not fence
            out.append("")
            continue
        out.append("" if fence else line)
    return out


def iter_tables(lines: Sequence[str]) -> Iterable[Tuple[int, List[str], List[Tuple[int, List[str]]]]]:
    """产出 (表头行号, 表头, [(行号, 单元格)])；跳过围栏代码。"""
    i = 0
    while i < len(lines) - 1:
        if "|" in lines[i] and is_separator(lines[i + 1]):
            header = split_row(lines[i])
            rows: List[Tuple[int, List[str]]] = []
            j = i + 2
            while j < len(lines) and "|" in lines[j] and lines[j].strip():
                if is_separator(lines[j]):
                    j += 1
                    continue
                rows.append((j, split_row(lines[j])))
                j += 1
            yield i, header, rows
            i = j
        else:
            i += 1


def parse_meta(lines: Sequence[str]) -> Dict[str, str]:
    meta: Dict[str, str] = {}
    for _idx, header, rows in iter_tables(lines):
        heads = [norm(h) for h in header]
        if len(heads) < 2 or heads[0] not in ("字段", "属性"):
            continue
        if heads[1] not in ("值", "内容"):
            continue
        for _ln, cells in rows:
            if len(cells) < 2:
                continue
            key = norm(cells[0])
            if key:
                meta[key] = norm(cells[1])
    return meta


def link_target(cell: str) -> str:
    m = re.search(r"\]\(([^)]+)\)", cell or "")
    return m.group(1).strip() if m else ""


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError as exc:
        raise RuntimeError(f"读取失败 {path}: {exc}") from exc


def load_yaml(path: Path) -> Dict:
    if yaml is None:
        raise RuntimeError("需要 PyYAML 以读取 baselines/ 与 releases/")
    data = yaml.safe_load(read_text(path))
    if data is None:
        return {}
    if not isinstance(data, dict):
        raise ValueError("根节点须为 mapping")
    return data


def xy_of(version: str) -> str:
    version = (version or "").strip()
    m = FULL_VERSION_RE.match(version)
    if m:
        return f"v{m.group(1)}.{m.group(2)}"
    if VERSION_RE.match(version):
        return version
    return ""


class SystemChecker:
    LEVELS = ("CRITICAL", "ERROR", "WARNING", "INFO")

    def __init__(self, ued_path: str = "./ued"):
        self.ued_path = Path(ued_path)
        self.issues: List[Issue] = []
        self.readme: Optional[Path] = None
        self.readme_lines: List[str] = []
        self.meta: Dict[str, str] = {}
        self.registry_header: List[str] = []
        self.registry_rows: List[Tuple[int, List[str]]] = []
        self.is_system = False
        self.subsystems: List[Subsystem] = []
        self.by_key: Dict[str, Subsystem] = {}
        self.by_dir: Dict[str, Subsystem] = {}
        self.prefix_owner: Dict[str, Subsystem] = {}
        self.deps: Dict[str, Dict[str, str]] = {}       # key -> {target: vX.Y}
        self.exts: Dict[str, Dict[str, str]] = {}       # key -> {external: vX.Y}
        self.baselines: Dict[Tuple[str, str], Dict] = {}
        self.releases: List[Dict] = []
        self.release_index: List[str] = []
        self.glossary_rows: List[Dict[str, str]] = []
        self.doc_code_map: Dict[str, List[Path]] = defaultdict(list)
        self.definitions: Dict[str, List[Tuple[str, Path, int]]] = defaultdict(list)

    # ---------------------------------------------------------------- 记录

    def add(self, level: str, title: str, detail: str) -> None:
        self.issues.append(Issue(level, title, detail))

    def rel(self, path: Path) -> str:
        try:
            return str(path.relative_to(self.ued_path))
        except ValueError:
            return str(path)

    # ---------------------------------------------------------------- 加载

    def load(self) -> None:
        if not self.ued_path.is_dir():
            self.add("CRITICAL", "UED 目录不存在", f"未找到 {self.ued_path}")
            return
        self.readme = self.ued_path / "README.md"
        if not self.readme.is_file():
            self.add("CRITICAL", "系统根 README 缺失", f"{self.ued_path}/README.md 不存在")
            return
        text = read_text(self.readme)
        self.readme_lines = mask_fences(text)
        self.meta = parse_meta(self.readme_lines)
        self._find_registry()
        self._parse_subsystems()
        self._scan_doc_codes()

    def _find_registry(self) -> None:
        for _idx, header, rows in iter_tables(self.readme_lines):
            heads = [norm(h) for h in header]
            if "subsystem_key" in heads and "目录" in heads and "状态" in heads:
                self.registry_header = heads
                self.registry_rows = rows
                self.is_system = True
                return

    def _parse_subsystems(self) -> None:
        if not self.is_system:
            return
        col = {name: i for i, name in enumerate(self.registry_header)}
        required = ["subsystem_key", "子系统名称", "目录", "编码前缀", "角色文档", "状态"]
        missing = [name for name in required if name not in col]
        if missing:
            self.add("ERROR", "注册表缺列",
                     f"{self.rel(self.readme)}: 缺 {'、'.join(missing)}；"
                     "固定六列 MUST 齐备")
            return
        for lineno, cells in self.registry_rows:
            if not any(cells):
                continue
            def cell(name: str) -> str:
                idx = col[name]
                return cells[idx] if idx < len(cells) else ""
            sub = Subsystem(
                key=cell("subsystem_key"),
                name=cell("子系统名称"),
                directory=cell("目录"),
                prefix=cell("编码前缀"),
                role_doc=cell("角色文档"),
                status=cell("状态"),
                line=lineno + 1,
            )
            self.subsystems.append(sub)
        for sub in self.subsystems:
            if sub.key:
                self.by_key.setdefault(sub.key, sub)
            if sub.directory:
                self.by_dir.setdefault(sub.directory.rstrip("/"), sub)
            if sub.prefix:
                self.prefix_owner.setdefault(sub.prefix, sub)

    def _scan_doc_codes(self) -> None:
        if not self.ued_path.is_dir():
            return
        for path in sorted(self.ued_path.rglob("*.md")):
            if self._is_reserved_path(path):
                continue
            try:
                text = read_text(path)
            except RuntimeError:
                continue
            lines = mask_fences(text)
            meta = parse_meta(lines)
            code = norm(meta.get("文档编码") or "")
            if not code:
                name = path.name
                for prefix in ("L0-", "L1-", "L2-", "L3-", "L4-", "L5-", "L6-",
                               "ADR-", "EVAL-", "REF-"):
                    if name.startswith(prefix):
                        m = re.match(r"^((?:[A-Z][A-Z0-9]{1,4}-)?(?:L[0-6]|ADR|EVAL|REF)-\d{2,4})",
                                     name)
                        if m:
                            code = m.group(1)
                        break
            if code and DOC_CODE_RE.match(code):
                self.doc_code_map[code].append(path)
            for i, line in enumerate(lines):
                m = HEADING_CODE_RE.match(line)
                if not m:
                    continue
                full, typ = m.group(1), m.group(2)
                if typ in TYPE_CODES:
                    self.definitions[full].append((self._scope_of(path), path, i + 1))

    def _is_reserved_path(self, path: Path) -> bool:
        try:
            rel = path.relative_to(self.ued_path)
        except ValueError:
            return False
        return bool(rel.parts) and rel.parts[0] in {"releases", "references", "assets", "deprecated"}

    def _scope_of(self, path: Path) -> str:
        try:
            rel = path.relative_to(self.ued_path)
        except ValueError:
            return ""
        return rel.parts[0] if len(rel.parts) > 1 else ""

    # ---------------------------------------------------------------- 结构

    def check_structure(self) -> None:
        if not self.ued_path.is_dir():
            return
        if self.meta.get("doc_mode"):
            self.add("ERROR", "系统根不得有 doc_mode",
                     f"{self.rel(self.readme)}: `doc_mode` 已移除；结构由注册表判定")
        if not self.is_system:
            self._check_non_system()
            return
        if self.meta.get("产品版本"):
            self.add("ERROR", "系统根不得有产品版本",
                     f"{self.rel(self.readme)}: 系统根 MUST NOT 有 `产品版本`；"
                     "系统版本写在 releases/sys-vX.Y.yaml")
        if (self.ued_path / "baselines").is_dir():
            self.add("ERROR", "系统根不得有 baselines",
                     f"{self.rel(self.ued_path / 'baselines')}: 系统根 MUST NOT 有产品基线；"
                     "基线属于子系统")
        for child in sorted(self.ued_path.iterdir()):
            if child.is_dir() and LAYER_DIR_RE.match(child.name):
                self.add("ERROR", "系统根不得有层级目录",
                         f"{self.rel(child)}: 系统根 MUST NOT 作为设计文档作用域；"
                         "L0–L6 属于子系统")
        for line_no, line in enumerate(self.readme_lines, 1):
            if re.match(r"^\s{0,3}##\s+(文档索引|编码计数器|全局编码索引)\s*$", line):
                self.add("ERROR", "系统根不得有设计索引",
                         f"{self.rel(self.readme)}:{line_no} `{line.strip('# ').strip()}` "
                         "属于子系统；系统根只维护注册表与发布索引")
        if not self.subsystems:
            self.add("ERROR", "子系统注册表为空",
                     f"{self.rel(self.readme)}: 系统 MUST 至少登记一个子系统")
        self._check_nested_scopes()

    def _check_non_system(self) -> None:
        nested = []
        for child in sorted(self.ued_path.iterdir()):
            if not child.is_dir() or child.name in {"releases", "references", "assets", "deprecated"}:
                continue
            readme = child / "README.md"
            if not readme.is_file():
                continue
            meta = parse_meta(mask_fences(read_text(readme)))
            if meta.get("产品版本") or (child / "baselines").is_dir():
                nested.append(child)
        if nested:
            self.add("ERROR", "结构不一致：子系统目录缺注册表",
                     "发现子系统作用域 " + "、".join(self.rel(p) for p in nested)
                     + "，但系统根 README 没有子系统注册表；"
                     "请补注册表，或改用 design-doc 校验单个作用域")
        else:
            self.add("INFO", "非系统结构",
                     f"{self.rel(self.ued_path)}: 未检测到子系统注册表；"
                     "这是单系统，请使用 design-doc 的 check_docs.py")

    def _check_nested_scopes(self) -> None:
        for child in sorted(self.ued_path.iterdir()):
            if not child.is_dir() or child.name in RESERVED_DIRS:
                continue
            if LAYER_DIR_RE.match(child.name):
                continue
            readme = child / "README.md"
            if not readme.is_file():
                continue
            meta = parse_meta(mask_fences(read_text(readme)))
            if meta.get("产品版本") or (child / "baselines").is_dir():
                if child.name not in self.by_dir:
                    self.add("ERROR", "未登记子系统目录",
                             f"{self.rel(child)}: 含 design-doc 作用域但未在注册表登记")
            for grand in sorted(child.iterdir()):
                if not grand.is_dir() or grand.name in RESERVED_DIRS:
                    continue
                greadme = grand / "README.md"
                if not greadme.is_file():
                    continue
                gmeta = parse_meta(mask_fences(read_text(greadme)))
                if gmeta.get("产品版本") or (grand / "baselines").is_dir():
                    self.add("ERROR", "子系统嵌套作用域",
                             f"{self.rel(grand)}: 子系统 MUST NOT 再嵌套子系统作用域")

    # ---------------------------------------------------------------- 注册表

    def check_registry(self) -> None:
        if not self.is_system:
            return
        if not self.registry_rows:
            self.add("ERROR", "注册表无数据行", f"{self.rel(self.readme)}: 子系统注册表为空")
            return
        seen_key: Dict[str, int] = {}
        seen_dir: Dict[str, int] = {}
        seen_prefix: Dict[str, int] = {}
        for sub in self.subsystems:
            loc = f"{self.rel(self.readme)}:{sub.line}"
            if not sub.key:
                self.add("ERROR", "注册表缺 subsystem_key", f"{loc}: `subsystem_key` MUST 非空")
                continue
            if PLACEHOLDER_RE.search(sub.key) or PLACEHOLDER_RE.search(sub.directory):
                self.add("ERROR", "注册表含占位符", f"{loc}: 子系统仍含 `{...}` 占位符")
                continue
            if not KEY_RE.match(sub.key):
                self.add("ERROR", "subsystem_key 格式错误",
                         f"{loc}: `{sub.key}` MUST 匹配 [a-z][a-z0-9-]*")
            if sub.key.lower() in RESERVED_DIRS or re.match(r"^l[0-6]", sub.key.lower()):
                self.add("ERROR", "subsystem_key 使用保留名",
                         f"{loc}: `{sub.key}` 与系统保留目录 / 层级前缀冲突")
            if sub.key in seen_key:
                self.add("ERROR", "subsystem_key 重复",
                         f"{loc}: `{sub.key}` 与第 {seen_key[sub.key]} 行重复")
            else:
                seen_key[sub.key] = sub.line
            if not sub.name:
                self.add("ERROR", "子系统名称缺失", f"{loc}: `子系统名称` MUST 非空")
            status = sub.status
            if status not in ("初稿", "正式", "废弃"):
                self.add("ERROR", "子系统状态非法",
                         f"{loc}: `{status}` 只允许 初稿 / 正式 / 废弃；`草案` 不适用")
            self._check_directory(sub, loc, seen_dir)
            self._check_prefix(sub, loc, seen_prefix)
            self._check_role_doc(sub, loc)
            self._check_active_requirements(sub, loc)

    def _check_directory(self, sub: Subsystem, loc: str, seen: Dict[str, int]) -> None:
        raw = (sub.directory or "").strip().strip("/")
        if not raw:
            self.add("ERROR", "子系统目录缺失", f"{loc}: `目录` MUST 非空")
            return
        if "/" in raw or "\\" in raw or raw in (".", ".."):
            self.add("ERROR", "子系统目录非单层",
                     f"{loc}: `{sub.directory}` MUST 是 ued/ 的直接子目录")
            return
        if raw in RESERVED_DIRS or LAYER_DIR_RE.match(raw):
            self.add("ERROR", "子系统目录使用保留名",
                     f"{loc}: `{raw}/` 是系统保留目录 / 层级目录，不能登记为子系统")
        if raw in seen:
            self.add("ERROR", "子系统目录重复",
                     f"{loc}: `{raw}/` 与第 {seen[raw]} 行重复")
        else:
            seen[raw] = sub.line
        path = self.ued_path / raw
        if not path.is_dir():
            self.add("ERROR", "子系统目录不存在", f"{loc}: 未找到 {self.rel(path)}")
            return
        if not (path / "README.md").is_file():
            self.add("ERROR", "子系统缺 README", f"{loc}: {self.rel(path)}/README.md 不存在")

    def _check_prefix(self, sub: Subsystem, loc: str, seen: Dict[str, int]) -> None:
        prefix = (sub.prefix or "").strip()
        readme = self.ued_path / sub.directory.strip("/") / "README.md"
        meta = parse_meta(mask_fences(read_text(readme))) if readme.is_file() else {}
        declared = norm(meta.get("project_code") or "")
        if prefix:
            if not PREFIX_RE.match(prefix):
                self.add("ERROR", "编码前缀格式错误",
                         f"{loc}: `{prefix}` MUST 匹配 [A-Z][A-Z0-9]{1,4}")
            if prefix in seen:
                self.add("ERROR", "编码前缀重复",
                         f"{loc}: `{prefix}` 与第 {seen[prefix]} 行重复")
            else:
                seen[prefix] = sub.line
            if not declared:
                self.add("ERROR", "前缀未在子系统 README 声明",
                         f"{loc}: 注册表前缀 `{prefix}`，但 {self.rel(readme)} 缺 `project_code`")
            elif declared != prefix:
                self.add("ERROR", "前缀与 project_code 不一致",
                         f"{loc}: 注册表 `{prefix}` ≠ README `project_code` `{declared}`")
        else:
            if declared:
                self.add("ERROR", "project_code 未登记",
                         f"{loc}: {self.rel(readme)} 声明 `project_code={declared}`，"
                         "但注册表编码前缀为空")

    def _check_role_doc(self, sub: Subsystem, loc: str) -> None:
        role = (sub.role_doc or "").strip()
        if not role:
            if sub.status == "正式":
                self.add("ERROR", "正式子系统缺角色文档",
                         f"{loc}: `{sub.key}` 为 `正式`，`角色文档` MUST 指向一个 `CMP` 细项")
            elif sub.status == "初稿":
                self.add("WARNING", "初稿子系统未登记角色文档",
                         f"{loc}: `{sub.key}` 尚无 `角色文档`；激活前 MUST 补齐")
            return
        if not ROLE_RE.match(role):
            self.add("ERROR", "角色文档编码非法",
                     f"{loc}: `{role}` MUST 为 `CMP-{序号}` 或 `{前缀}-CMP-{序号}`")
            return
        root = self.ued_path / sub.directory.strip("/")
        found = self._find_item_status(root, role)
        if found is None:
            self.add("ERROR", "角色文档不存在",
                     f"{loc}: 在 {self.rel(root)} 内未找到 `{role}` 的定义标题")
            return
        status, path, line_no = found
        if sub.status == "正式" and status != "正式":
            self.add("ERROR", "角色文档非正式",
                     f"{self.rel(path)}:{line_no}: `{role}` 的细项状态为 "
                     f"`{status or '（空）'}`；正式子系统 MUST 使用正式角色文档")
        elif sub.status == "初稿" and status != "正式":
            self.add("WARNING", "角色文档尚未正式",
                     f"{self.rel(path)}:{line_no}: `{role}` 尚未 `正式`；激活前 MUST 补齐")

    def _find_item_status(self, root: Path, code: str) -> Optional[Tuple[str, Path, int]]:
        if not root.is_dir():
            return None
        pattern = re.compile(r"^\s{0,3}#{1,6}\s+" + re.escape(code) + r"\b")
        for path in sorted(root.rglob("*.md")):
            if "deprecated" in path.parts:
                continue
            try:
                lines = mask_fences(read_text(path))
            except RuntimeError:
                continue
            for i, line in enumerate(lines):
                if not pattern.match(line):
                    continue
                status = ""
                for j in range(i + 1, min(len(lines), i + 40)):
                    m = ATTR_RE.match(lines[j])
                    if m and norm(m.group(1)) == "细项状态":
                        status = norm(m.group(2))
                        break
                return status, path, i + 1
        return None

    def _check_active_requirements(self, sub: Subsystem, loc: str) -> None:
        root = self.ued_path / sub.directory.strip("/")
        if not root.is_dir():
            return
        readme = root / "README.md"
        meta = parse_meta(mask_fences(read_text(readme))) if readme.is_file() else {}
        pv = norm(meta.get("产品版本") or "")
        if sub.status == "正式":
            if not pv:
                self.add("ERROR", "正式子系统缺产品版本",
                         f"{loc}: {self.rel(readme)} 缺 `产品版本`")
                return
            if not VERSION_RE.match(pv):
                self.add("ERROR", "子系统产品版本格式错误",
                         f"{loc}: `{pv}` MUST 为 v主.次")
                return
            base = root / "baselines" / f"{pv}.yaml"
            if not base.is_file():
                self.add("ERROR", "正式子系统缺基线",
                         f"{loc}: 缺 {self.rel(base)}；正式子系统 MUST 有当前基线")
        elif sub.status == "初稿" and pv and not VERSION_RE.match(pv):
            self.add("WARNING", "子系统产品版本格式错误",
                     f"{loc}: `{pv}` MUST 为 v主.次")

    def check_subsystem_dirs(self) -> None:
        if not self.is_system:
            return
        for sub in self.subsystems:
            if not sub.key or not sub.directory:
                continue
            root = self.ued_path / sub.directory.strip("/")
            if not root.is_dir():
                continue
            docs = [p for p in root.rglob("*.md")
                    if "deprecated" not in p.parts
                    and (p.name.startswith("L")
                         or p.name.startswith(("ADR-", "EVAL-", "REF-")))]
            if not docs:
                self.add("WARNING", "子系统无设计文档",
                         f"{self.rel(root)}: 未找到 L*/ADR/EVAL/REF 文档；"
                         "子系统至少应有承载职责的设计文档")
            if (root / "glossary.md").is_file():
                self.add("ERROR", "子系统不得自建术语表",
                         f"{self.rel(root / 'glossary.md')}: 全局术语表固定 ued/glossary.md，"
                         "子系统 MUST NOT 另建")
        # 未登记目录
        for child in sorted(self.ued_path.iterdir()):
            if not child.is_dir() or child.name in RESERVED_DIRS or LAYER_DIR_RE.match(child.name):
                continue
            if child.name in self.by_dir:
                continue
            has_md = any(child.rglob("*.md"))
            if has_md:
                self.add("ERROR", "未登记目录含文档",
                         f"{self.rel(child)}: 目录含 Markdown 但未登记为子系统；"
                         "请登记，或移入 references/assets")
        for reserved in ("references", "assets", "releases", "deprecated"):
            root = self.ued_path / reserved
            if not root.is_dir():
                continue
            for path in root.rglob("*.md"):
                if DOC_META_CODE_RE.match(path.name):
                    self.add("WARNING", "系统根含设计文档",
                             f"{self.rel(path)}: 系统根 {reserved}/ 只放原始资料；"
                             "L*/ADR/EVAL/REF 文档属于子系统")

    # ---------------------------------------------------------------- 依赖

    def check_dependencies(self) -> None:
        if not self.is_system:
            return
        for sub in self.subsystems:
            if sub.status != "正式" or not sub.key or not sub.directory:
                continue
            root = self.ued_path / sub.directory.strip("/")
            readme = root / "README.md"
            meta = parse_meta(mask_fences(read_text(readme))) if readme.is_file() else {}
            pv = norm(meta.get("产品版本") or "")
            if not VERSION_RE.match(pv):
                continue
            base = root / "baselines" / f"{pv}.yaml"
            if not base.is_file():
                continue
            try:
                data = load_yaml(base)
            except Exception as exc:  # noqa: BLE001
                self.add("ERROR", "子系统基线无法解析", f"{self.rel(base)}: {exc}")
                continue
            self.baselines[(sub.key, pv)] = data
            self._check_depends_on(sub, base, data)
            self._check_external_deps(sub, base, data)
        self._check_cycles()

    def _check_depends_on(self, sub: Subsystem, base: Path, data: Dict) -> None:
        loc = self.rel(base)
        raw = data.get("depends_on")
        if raw is None:
            self.add("WARNING", "基线缺 depends_on",
                     f"{loc}: 建议显式写 `depends_on: []`（确无依赖时）")
            raw = []
        if not isinstance(raw, list):
            self.add("ERROR", "depends_on 形态错误", f"{loc}: 须为列表")
            return
        seen: Set[str] = set()
        deps: Dict[str, str] = {}
        for i, item in enumerate(raw):
            if not isinstance(item, dict):
                self.add("ERROR", "depends_on 项形态错误", f"{loc}: [{i}] 须为 mapping")
                continue
            target = norm(str(item.get("subsystem") or ""))
            version = norm(str(item.get("product_version") or ""))
            if not target:
                self.add("ERROR", "depends_on 缺 subsystem", f"{loc}: [{i}]")
                continue
            if target in seen:
                self.add("ERROR", "depends_on 重复", f"{loc}: `{target}` 出现多次")
                continue
            seen.add(target)
            if target == sub.key:
                self.add("ERROR", "子系统自依赖", f"{loc}: `{sub.key}` 依赖自身")
                continue
            if not KEY_RE.match(target):
                self.add("ERROR", "depends_on 目标格式错误",
                         f"{loc}: `{target}` 不是合法 subsystem_key")
                continue
            if not VERSION_RE.match(version):
                self.add("ERROR", "depends_on 版本格式错误",
                         f"{loc}: `{target}` 的 `{version}` MUST 为 v主.次")
                continue
            target_sub = self.by_key.get(target)
            if target_sub is None:
                self.add("ERROR", "depends_on 目标未登记",
                         f"{loc}: `{target}` 不在子系统注册表")
                continue
            if target_sub.status != "正式":
                self.add("ERROR", "depends_on 目标未启用",
                         f"{loc}: `{target}` 状态为 `{target_sub.status}`；MUST 依赖正式子系统")
                continue
            target_base = self.ued_path / target_sub.directory.strip("/") / "baselines" / f"{version}.yaml"
            if not target_base.is_file():
                self.add("ERROR", "depends_on 目标基线不存在",
                         f"{loc}: `{target}` 不存在 {self.rel(target_base)}")
                continue
            deps[target] = version
        self.deps[sub.key] = deps

    def _check_external_deps(self, sub: Subsystem, base: Path, data: Dict) -> None:
        loc = self.rel(base)
        raw = data.get("external_deps")
        if raw is None:
            self.add("WARNING", "基线缺 external_deps",
                     f"{loc}: 建议显式写 `external_deps: []`（确无外部依赖时）")
            raw = []
        if not isinstance(raw, list):
            self.add("ERROR", "external_deps 形态错误", f"{loc}: 须为列表")
            return
        seen: Set[str] = set()
        exts: Dict[str, str] = {}
        for i, item in enumerate(raw):
            if not isinstance(item, dict):
                self.add("ERROR", "external_deps 项形态错误", f"{loc}: [{i}] 须为 mapping")
                continue
            name = norm(str(item.get("name") or ""))
            version = norm(str(item.get("product_version") or ""))
            if not name:
                self.add("ERROR", "external_deps 缺 name", f"{loc}: [{i}]")
                continue
            if not KEY_RE.match(name):
                self.add("ERROR", "external_deps 名称格式错误",
                         f"{loc}: `{name}` MUST 匹配 [a-z][a-z0-9-]*")
            if name in seen:
                self.add("ERROR", "external_deps 重复", f"{loc}: `{name}` 出现多次")
                continue
            seen.add(name)
            if name in self.by_key:
                self.add("ERROR", "外部依赖误写为外部",
                         f"{loc}: `{name}` 是已登记子系统；MUST 用 depends_on")
            if not VERSION_RE.match(version):
                self.add("ERROR", "external_deps 版本格式错误",
                         f"{loc}: `{name}` 的 `{version}` MUST 为 v主.次")
                continue
            exts[name] = version
        self.exts[sub.key] = exts

    def _check_cycles(self) -> None:
        graph = {k: list(v.keys()) for k, v in self.deps.items()}
        visiting: Set[str] = set()
        visited: Set[str] = set()
        reported: Set[Tuple[str, ...]] = set()

        def dfs(node: str, stack: List[str]) -> None:
            if node in visiting:
                idx = stack.index(node) if node in stack else 0
                cycle = tuple(stack[idx:] + [node])
                key = tuple(sorted(set(cycle)))
                if key not in reported:
                    reported.add(key)
                    self.add("WARNING", "子系统依赖环",
                             " → ".join(cycle) + "：SHOULD 消除循环依赖")
                return
            if node in visited:
                return
            visiting.add(node)
            stack.append(node)
            for nxt in graph.get(node, []):
                if nxt in graph:
                    dfs(nxt, stack)
            stack.pop()
            visiting.discard(node)
            visited.add(node)

        for node in sorted(graph):
            dfs(node, [])

    # ---------------------------------------------------------------- 发布

    def check_releases(self) -> None:
        if not self.is_system:
            return
        releases_dir = self.ued_path / "releases"
        self._parse_release_index()
        files = sorted(releases_dir.glob("*.yaml")) if releases_dir.is_dir() else []
        if not files:
            if self.release_index:
                self.add("ERROR", "发布索引指向不存在的目录",
                         f"{self.rel(self.readme)}: 有发布索引但缺 releases/")
            return
        seen_release: Set[str] = set()
        file_names: Set[str] = set()
        for path in files:
            if not RELEASE_FILE_RE.match(path.name):
                self.add("ERROR", "发布文件名非法",
                         f"{self.rel(path)}: MUST 为 sys-vX.Y.yaml")
                continue
            try:
                data = load_yaml(path)
            except Exception as exc:  # noqa: BLE001
                self.add("ERROR", "发布清单无法解析", f"{self.rel(path)}: {exc}")
                continue
            stem = path.stem
            file_names.add(stem)
            release = norm(str(data.get("release") or ""))
            if release != stem:
                self.add("ERROR", "发布清单版本不一致",
                         f"{self.rel(path)}: `release` 为 `{release}`，文件名要求 `{stem}`")
            if release in seen_release:
                self.add("ERROR", "发布版本重复", f"{self.rel(path)}: `{release}` 重复")
            seen_release.add(release)
            created = norm(str(data.get("created") or ""))
            if not DATE_RE.match(created):
                self.add("ERROR", "发布清单 created 非法",
                         f"{self.rel(path)}: `{created}` MUST 为 YYYY-MM-DD")
            self._check_release_pins(path, data)
        for name in self.release_index:
            if name and name not in file_names:
                self.add("ERROR", "发布索引悬空",
                         f"{self.rel(self.readme)}: 索引 `{name}` 无对应 releases/{name}.yaml")
        for name in sorted(file_names - set(self.release_index)):
            self.add("WARNING", "发布未登记索引",
                     f"{self.rel(self.readme)}: releases/{name}.yaml 未出现在发布索引")

    def _parse_release_index(self) -> None:
        for _idx, header, rows in iter_tables(self.readme_lines):
            heads = [norm(h) for h in header]
            if "发布" not in heads or "清单" not in heads:
                continue
            i_release = heads.index("发布")
            i_link = heads.index("清单")
            for _ln, cells in rows:
                name = cells[i_release] if i_release < len(cells) else ""
                if name:
                    self.release_index.append(norm(name))
                link = link_target(cells[i_link] if i_link < len(cells) else "")
                if link and not link.endswith(f"{name}.yaml"):
                    self.add("WARNING", "发布索引链接不一致",
                             f"{self.rel(self.readme)}: `{name}` 的清单链接为 `{link}`")
            return

    def _check_release_pins(self, path: Path, data: Dict) -> None:
        loc = self.rel(path)
        raw = data.get("subsystems")
        if not isinstance(raw, list) or not raw:
            self.add("ERROR", "发布清单缺 subsystems", f"{loc}: 须为非空列表")
            return
        pins: Dict[str, str] = {}
        for i, item in enumerate(raw):
            if not isinstance(item, dict):
                self.add("ERROR", "发布项形态错误", f"{loc}: subsystems[{i}] 须为 mapping")
                continue
            key = norm(str(item.get("subsystem") or ""))
            pv = norm(str(item.get("product_version") or ""))
            fv = norm(str(item.get("full_version") or ""))
            if not key:
                self.add("ERROR", "发布项缺 subsystem", f"{loc}: [{i}]")
                continue
            if key in pins:
                self.add("ERROR", "发布项重复", f"{loc}: `{key}` 出现多次")
                continue
            sub = self.by_key.get(key)
            if sub is None:
                self.add("ERROR", "发布项未登记", f"{loc}: `{key}` 不在子系统注册表")
                continue
            if sub.status == "初稿":
                self.add("ERROR", "发布包含初稿子系统",
                         f"{loc}: `{key}` 状态为 `初稿`；未启用子系统 MUST NOT 进入发布")
            elif sub.status == "废弃":
                self.add("WARNING", "发布含已废弃子系统",
                         f"{loc}: `{key}` 当前为 `废弃`；历史清单可保留，"
                         "新发布 MUST 移除该成员")
            if not VERSION_RE.match(pv):
                self.add("ERROR", "发布项产品版本格式错误",
                         f"{loc}: `{key}` 的 `{pv}` MUST 为 v主.次")
                continue
            pins[key] = pv
            if not FULL_VERSION_RE.match(fv) or xy_of(fv) != pv:
                self.add("ERROR", "发布项 full_version 非法",
                         f"{loc}: `{key}` 的 `{fv}` 须为 {pv}.Z")
            base = self.ued_path / sub.directory.strip("/") / "baselines" / f"{pv}.yaml"
            if not base.is_file():
                self.add("ERROR", "发布项基线不存在",
                         f"{loc}: `{key}` 缺 {self.rel(base)}")
                continue
            try:
                bdata = self.baselines.get((key, pv)) or load_yaml(base)
            except Exception as exc:  # noqa: BLE001
                self.add("ERROR", "发布项基线无法解析", f"{self.rel(base)}: {exc}")
                continue
            self.baselines[(key, pv)] = bdata
            log = bdata.get("patch_log") or []
            if not isinstance(log, list) or not any(
                    norm(str(e.get("full_version") or "")) == fv
                    for e in log if isinstance(e, dict)):
                self.add("ERROR", "发布项 tip 不在 patch_log",
                         f"{loc}: `{key}` 的 `{fv}` 未出现在 "
                         f"{self.rel(base)} 的 patch_log")
        self._check_release_closure(path, pins, data)

    def _check_release_closure(self, path: Path, pins: Dict[str, str], data: Dict) -> None:
        loc = self.rel(path)
        ext_raw = data.get("external_deps")
        ext_pins: Dict[str, str] = {}
        if ext_raw is None:
            ext_raw = []
        if not isinstance(ext_raw, list):
            self.add("ERROR", "发布清单 external_deps 形态错误", f"{loc}: 须为列表")
            ext_raw = []
        for i, item in enumerate(ext_raw):
            if not isinstance(item, dict):
                self.add("ERROR", "发布外部依赖项形态错误", f"{loc}: [{i}] 须为 mapping")
                continue
            name = norm(str(item.get("name") or ""))
            version = norm(str(item.get("product_version") or ""))
            if not name:
                self.add("ERROR", "发布外部依赖缺 name", f"{loc}: [{i}]")
                continue
            if name in ext_pins:
                self.add("ERROR", "发布外部依赖重复", f"{loc}: `{name}` 出现多次")
                continue
            if not VERSION_RE.match(version):
                self.add("ERROR", "发布外部依赖版本格式错误",
                         f"{loc}: `{name}` 的 `{version}` MUST 为 v主.次")
                continue
            ext_pins[name] = version

        for key, pv in pins.items():
            sub = self.by_key.get(key)
            if sub is None:
                continue
            base = self.ued_path / sub.directory.strip("/") / "baselines" / f"{pv}.yaml"
            bdata = self.baselines.get((key, pv))
            if bdata is None and base.is_file():
                try:
                    bdata = load_yaml(base)
                    self.baselines[(key, pv)] = bdata
                except Exception:  # noqa: BLE001
                    continue
            if bdata is None:
                continue
            deps = bdata.get("depends_on") or []
            if isinstance(deps, list):
                for item in deps:
                    if not isinstance(item, dict):
                        continue
                    target = norm(str(item.get("subsystem") or ""))
                    version = norm(str(item.get("product_version") or ""))
                    if not target or not version:
                        continue
                    if target not in pins:
                        self.add("ERROR", "发布依赖未闭合",
                                 f"{loc}: `{key}` 依赖 `{target}`，但发布清单未包含")
                    elif pins[target] != version:
                        self.add("ERROR", "发布依赖版本不一致",
                                 f"{loc}: `{key}` 钉住 `{target} {version}`，"
                                 f"发布清单为 `{pins[target]}`")
            exts = bdata.get("external_deps") or []
            if isinstance(exts, list):
                for item in exts:
                    if not isinstance(item, dict):
                        continue
                    name = norm(str(item.get("name") or ""))
                    version = norm(str(item.get("product_version") or ""))
                    if not name or not version:
                        continue
                    if name not in ext_pins:
                        self.add("ERROR", "发布外部依赖未覆盖",
                                 f"{loc}: `{key}` 需要 `{name} {version}`，清单未钉住")
                    elif ext_pins[name] != version:
                        self.add("ERROR", "发布外部依赖版本冲突",
                                 f"{loc}: `{key}` 需要 `{name} {version}`，"
                                 f"清单为 `{ext_pins[name]}`；先调整子系统基线")
        used = set()
        for key, pv in pins.items():
            bdata = self.baselines.get((key, pv)) or {}
            for item in bdata.get("external_deps") or []:
                if isinstance(item, dict):
                    used.add(norm(str(item.get("name") or "")))
        for name in sorted(set(ext_pins) - used):
            self.add("WARNING", "发布外部依赖未被使用",
                     f"{loc}: `{name}` 未被子系统 external_deps 声明")

    # ---------------------------------------------------------------- 跨作用域

    @staticmethod
    def _item_key(code: str) -> Tuple[str, int]:
        """细项编码的解析键 `(类型码, 序号)`：忽略项目前缀与前导零。"""
        m = re.match(r"^(?:[A-Z][A-Z0-9]{1,4}-)?([A-Z]{1,5}[0-9]?)-(\d{2,4})$", code)
        return (m.group(1), int(m.group(2))) if m else ("", 0)

    @staticmethod
    def _reference_texts(line: str) -> List[str]:
        """引用上下文：Markdown 链接文字与表格行；正文散文不参与简写识别。"""
        texts = [m.group(1) for m in MD_LINK_TEXT_RE.finditer(line)]
        if line.lstrip().startswith("|"):
            texts.append(INLINE_CODE_RE.sub("", line))
        return texts

    def check_cross_scope(self) -> None:
        """跨子系统编码归属与引用。

        子系统内部的定义/引用前缀由 design-doc 的 `check_docs.py` 按
        `project_code` 校验；本方法只处理跨子系统：重复定义、定义占用他子系统
        前缀、跨子系统引用悬空/归属不符、跨作用域简写。
        """
        if not self.is_system:
            return
        for code, sites in self.definitions.items():
            if len(sites) <= 1:
                continue
            scopes = {s[0] for s in sites}
            if len(scopes) > 1:
                self.add("ERROR", "跨子系统重复定义编码",
                         f"`{code}` 在多个子系统定义："
                         + " / ".join(f"{p}:{ln}" for _s, p, ln in sites))
        global_keys = {self._item_key(code) for code in self.definitions}
        global_keys.discard(("", 0))
        for sub in self.subsystems:
            if not sub.key or not sub.directory:
                continue
            root = self.ued_path / sub.directory.strip("/")
            if not root.is_dir():
                continue
            sub_dir = sub.directory.strip("/")
            local_keys = {
                self._item_key(code)
                for code, sites in self.definitions.items()
                if any(scope == sub_dir for scope, _p, _l in sites)
            }
            local_keys.discard(("", 0))
            for path in sorted(root.rglob("*.md")):
                if "deprecated" in path.parts:
                    continue
                try:
                    lines = mask_fences(read_text(path))
                except RuntimeError:
                    continue
                reported: Set[str] = set()
                reported_bare: Set[str] = set()
                for i, line in enumerate(lines):
                    # 定义行由下方「定义前缀」规则处理，不当作引用
                    if not HEADING_CODE_RE.match(line):
                        self._check_cross_refs(path, i, line, sub, reported)
                    for text in self._reference_texts(line):
                        for m in BARE_CODE_RE.finditer(text):
                            bare = m.group(1)
                            key = self._item_key(bare)
                            if not key[0] or key in local_keys:
                                continue        # 本子系统简写，交给 check_docs.py
                            if key not in global_keys or bare in reported_bare:
                                continue        # 无同键定义 → 悬空，由 check_docs.py 报
                            reported_bare.add(bare)
                            self.add("ERROR", "跨作用域简写",
                                     f"{self.rel(path)}:{i + 1}: `{bare}` 在本子系统"
                                     "无定义，其他子系统有同键编码；跨子系统引用 MUST "
                                     "写全量编码")
                for i, line in enumerate(lines):
                    m = HEADING_CODE_RE.match(line)
                    if not m:
                        continue
                    full, typ = m.group(1), m.group(2)
                    if typ not in TYPE_CODES:
                        continue
                    cm = ITEM_CODE_RE.match(full)
                    if not cm:
                        continue
                    prefix = cm.group(1) or ""
                    if prefix == sub.prefix:
                        continue
                    if prefix and prefix in self.prefix_owner:
                        self.add("ERROR", "定义了他子系统前缀",
                                 f"{self.rel(path)}:{i + 1}: `{full}` 使用前缀 `{prefix}`，"
                                 f"属于 {self.prefix_owner[prefix].key}；本子系统前缀为 `{sub.prefix}`")
                    else:
                        self.add("ERROR", "定义前缀与子系统不符",
                                 f"{self.rel(path)}:{i + 1}: `{full}` 的前缀 `{prefix or '（空）'}` "
                                 f"与本子系统登记前缀 `{sub.prefix or '（空）'}` 不符")
        self._check_glossary()

    def _check_cross_refs(self, path: Path, i: int, line: str, sub: Subsystem,
                          reported: Set[str]) -> None:
        """跨子系统全量引用：目标须存在，且归属被引用前缀的子系统。"""
        for m in REF_CODE_RE.finditer(line):
            code, prefix = m.group(1), m.group(2)
            if prefix == sub.prefix or prefix not in self.prefix_owner:
                continue
            if code in reported:
                continue
            reported.add(code)
            owner = self.prefix_owner[prefix]
            item_sites = self.definitions.get(code, [])
            doc_paths = self.doc_code_map.get(code, [])
            loc = f"{self.rel(path)}:{i + 1}: `{code}`"
            if not item_sites and not doc_paths:
                self.add("WARNING", "跨子系统引用悬空",
                         f"{loc} 在 {owner.key} 内无定义")
                continue
            owner_dir = owner.directory.strip("/")
            scopes = {s for s, _p, _l in item_sites}
            scopes |= {self._scope_of(p) for p in doc_paths}
            if owner_dir not in scopes:
                self.add("ERROR", "跨子系统引用前缀与定义不符",
                         f"{loc} 使用前缀 `{prefix}`，但定义不在 {owner.key} 子系统内")

    def _check_glossary(self) -> None:
        glos = self.ued_path / "glossary.md"
        if not glos.is_file():
            if any((self.ued_path / s.directory.strip("/") / "glossary.md").is_file()
                   for s in self.subsystems if s.directory):
                self.add("ERROR", "缺全局术语表",
                         "子系统存在 glossary.md，但系统根缺 ued/glossary.md")
            return
        text = read_text(glos)
        if not re.search(r"\]\([^)]*glossary\.md(?:[#)])", read_text(self.readme)):
            self.add("WARNING", "系统 README 未登记术语表",
                     f"{self.rel(self.readme)}: 存在全局术语表，但 README 未链接 glossary.md")
        rows = self._parse_glossary_table(mask_fences(text))
        if rows is None:
            self.add("ERROR", "术语表缺少固定四列表",
                     f"{self.rel(glos)}: 未找到含 中文名称 / 英文名称 / 定义 / 定义位置 的表格")
            return
        seen_zh: Dict[str, int] = {}
        seen_en: Dict[str, int] = {}
        for line_no, row in rows:
            zh, en, loc = row["zh"], row["en"], row["loc"]
            if zh:
                if zh in seen_zh:
                    self.add("ERROR", "术语名称重复",
                             f"{self.rel(glos)}:{line_no}: 中文名称「{zh}」重复")
                else:
                    seen_zh[zh] = line_no
            if en:
                key = en.casefold()
                if key in seen_en:
                    self.add("ERROR", "术语名称重复",
                             f"{self.rel(glos)}:{line_no}: 英文名称「{en}」重复")
                else:
                    seen_en[key] = line_no
            if loc:
                if not DOC_META_CODE_RE.match(loc):
                    self.add("ERROR", "术语定义位置非法",
                             f"{self.rel(glos)}:{line_no}: `{loc}` MUST 为完整文档编码")
                    continue
                targets = self.doc_code_map.get(loc, [])
                if not targets:
                    self.add("ERROR", "术语定义位置不存在",
                             f"{self.rel(glos)}:{line_no}: `{loc}` 在系统内无对应文档")
                elif len(targets) > 1:
                    self.add("ERROR", "术语定义位置不唯一",
                             f"{self.rel(glos)}:{line_no}: `{loc}` 对应多个文件："
                             + " / ".join(self.rel(p) for p in targets))
        self._check_terms_registered(rows)

    def _parse_glossary_table(self, lines: Sequence[str]) -> Optional[List[Tuple[int, Dict[str, str]]]]:
        for _idx, header, rows in iter_tables(lines):
            heads = [norm(h) for h in header]
            if not all(name in heads for name in ("中文名称", "英文名称", "定义", "定义位置")):
                continue
            idx = {name: heads.index(name) for name in ("中文名称", "英文名称", "定义", "定义位置")}
            out: List[Tuple[int, Dict[str, str]]] = []
            for ln, cells in rows:
                def cell(name: str) -> str:
                    i = idx[name]
                    return norm(cells[i]) if i < len(cells) else ""
                row = {"zh": cell("中文名称"), "en": cell("英文名称"),
                       "loc": cell("定义位置")}
                if any(row.values()):
                    out.append((ln + 1, row))
            return out
        return None

    def _check_terms_registered(self, glos_rows: List[Tuple[int, Dict[str, str]]]) -> None:
        registered = {(r["zh"], r["en"].casefold()) for _ln, r in glos_rows if r["zh"] and r["en"]}
        by_zh = {r["zh"] for _ln, r in glos_rows if r["zh"]}
        by_en = {r["en"].casefold() for _ln, r in glos_rows if r["en"]}
        for sub in self.subsystems:
            if not sub.directory:
                continue
            root = self.ued_path / sub.directory.strip("/")
            if not root.is_dir():
                continue
            for path in sorted(root.rglob("*.md")):
                if "deprecated" in path.parts:
                    continue
                try:
                    lines = mask_fences(read_text(path))
                except RuntimeError:
                    continue
                in_terms = False
                current = ""
                for i, line in enumerate(lines):
                    if re.match(r"^\s{0,3}##\s+术语和概念\s*$", line):
                        in_terms = True
                        current = ""
                        continue
                    if in_terms and re.match(r"^\s{0,3}##\s+", line):
                        in_terms = False
                    if not in_terms:
                        continue
                    hm = TERM_HEADING_RE.match(line)
                    if hm:
                        current = norm(hm.group(1))
                        continue
                    m = ATTR_RE.match(line)
                    if not m:
                        continue
                    name = norm(m.group(1))
                    value = norm(m.group(2))
                    if name in ("中文名称", "英文名称") and current:
                        # 简化：以术语小节标题作为中文名，检查是否登记
                        if current not in by_zh and current.casefold() not in by_en:
                            self.add("ERROR", "术语未登记到全局表",
                                     f"{self.rel(path)}:{i + 1}: 术语「{current}」"
                                     "未出现在 ued/glossary.md")
                        break

    # ---------------------------------------------------------------- README 结构

    def check_readme_sections(self) -> None:
        if not self.is_system:
            return
        text = "\n".join(self.readme_lines)
        if not re.search(r"系统\s*[+＋与和]\s*子系统|系统级|子系统级", text):
            self.add("WARNING", "系统 README 缺结构说明",
                     f"{self.rel(self.readme)}: SHOULD 有「当前结构」说明，"
                     "明确这是系统 + 子系统")
        for field in ("project_name", "scope", "author", "last_updated"):
            if not self.meta.get(field):
                self.add("WARNING", "系统 README 缺元信息",
                         f"{self.rel(self.readme)}: 缺 `{field}`")
        if "系统" not in (self.meta.get("scope") or ""):
            self.add("WARNING", "系统 README scope 未说明系统",
                     f"{self.rel(self.readme)}: `scope` SHOULD 说明为系统（含子系统）")

    # ---------------------------------------------------------------- 报告

    def level_count(self) -> Dict[str, int]:
        counts: Dict[str, int] = defaultdict(int)
        for issue in self.issues:
            counts[issue.level] += 1
        return counts

    def generate_report(self) -> str:
        counts = self.level_count()
        lines = [
            "=" * 80,
            "SystemDesignDoc 系统检查报告",
            "=" * 80,
            "",
            f"检查目录: {self.ued_path}",
            f"检查时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"结构判定: {'系统 + 子系统' if self.is_system else '非系统 / 单系统'}",
            f"子系统数: {len(self.subsystems)}",
            f"系统发布数: {len(self.releases) if self.releases else len(list((self.ued_path / 'releases').glob('*.yaml')) if (self.ued_path / 'releases').is_dir() else [])}",
            "",
            "问题统计:",
            f"  CRITICAL: {counts.get('CRITICAL', 0)}",
            f"  ERROR:    {counts.get('ERROR', 0)}",
            f"  WARNING:  {counts.get('WARNING', 0)}",
            f"  INFO:     {counts.get('INFO', 0)}",
            "",
        ]
        if not self.issues:
            lines.append("✅ 未发现问题")
        for level in self.LEVELS:
            group = [i for i in self.issues if i.level == level]
            if not group:
                continue
            icon = {"CRITICAL": "❌", "ERROR": "❌", "WARNING": "⚠️", "INFO": "ℹ️"}[level]
            lines.append(f"{icon} {level} ({len(group)})")
            lines.append("-" * 80)
            for issue in group:
                lines.append(f"[{issue.title}] {issue.detail}")
            lines.append("")
        return "\n".join(lines)

    def print_summary(self) -> int:
        counts = self.level_count()
        print("\n" + "=" * 80)
        print("检查完成："
              f"CRITICAL {counts.get('CRITICAL', 0)} / "
              f"ERROR {counts.get('ERROR', 0)} / "
              f"WARNING {counts.get('WARNING', 0)} / "
              f"INFO {counts.get('INFO', 0)}")
        if counts.get("CRITICAL", 0) or counts.get("ERROR", 0):
            print("❌ 存在阻断问题")
            return 1
        print("✅ 通过")
        return 0

    def member_commands(self) -> List[str]:
        cmds = []
        for sub in self.subsystems:
            if not sub.directory:
                continue
            cmds.append(
                "python3 .agents/skills/design-doc/scripts/check_docs.py "
                f"-p {self.ued_path / sub.directory.strip('/')} --glossary {self.ued_path / 'glossary.md'}"
            )
        return cmds


def main() -> int:
    parser = argparse.ArgumentParser(description="SystemDesignDoc 系统检查工具")
    parser.add_argument("-p", "--path", default="./ued", help="系统根 ued/ 路径")
    parser.add_argument("-o", "--output", help="输出报告到文件")
    parser.add_argument("-v", "--verbose", action="store_true", help="显示详细信息")
    parser.add_argument("--print-member-commands", action="store_true",
                        help="打印每个子系统的 design-doc 校验命令")
    args = parser.parse_args()

    checker = SystemChecker(args.path)
    checker.load()
    if args.print_member_commands:
        if not checker.is_system:
            print("未检测到子系统注册表；单系统请直接使用 design-doc。")
            return 0
        for cmd in checker.member_commands():
            print(cmd)
        return 0

    checker.check_structure()
    if checker.is_system:
        checker.check_registry()
        checker.check_subsystem_dirs()
        checker.check_dependencies()
        checker.check_releases()
        checker.check_cross_scope()
        checker.check_readme_sections()

    report = checker.generate_report()
    if args.output:
        Path(args.output).write_text(report + "\n", encoding="utf-8")
        print(f"📄 报告已保存到: {args.output}")
    if args.verbose or not args.output:
        print("\n" + report)
    return checker.print_summary()


if __name__ == "__main__":
    sys.exit(main())
