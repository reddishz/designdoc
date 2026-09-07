#!/usr/bin/env python3
"""
DesignDoc 文档检查工具

用于检查产品设计文档的规范性、完整性和一致性。
"""

import os
import re
import sys
import json
from pathlib import Path
from datetime import date, datetime
from typing import Dict, List, Set, Tuple
from dataclasses import dataclass
from collections import defaultdict


@dataclass
class DocInfo:
    """文档信息"""
    path: str
    doc_code: str
    doc_type: str
    layer: str = ""
    status: str = ""
    status_category: str = ""
    content: str = ""


class DesignDocChecker:
    """设计文档检查器"""

    def __init__(self, ued_path: str = "./ued"):
        self.ued_path = Path(ued_path)
        self.docs: List[DocInfo] = []
        self.codes: Set[str] = set()
        self.code_to_doc: Dict[str, DocInfo] = {}
        self.issues: List[Dict] = []

    def scan_docs(self) -> None:
        """扫描所有文档"""
        if not self.ued_path.exists():
            self.add_issue("CRITICAL", "UED目录不存在", f"未找到 {self.ued_path} 目录")
            return

        # 扫描所有 .md 文件
        for md_file in self.ued_path.rglob("*.md"):
            if md_file.name in [".doc-config.json"]:
                continue

            try:
                content = md_file.read_text(encoding='utf-8')
                doc_info = self.parse_doc_info(str(md_file), content)
                if doc_info:
                    self.docs.append(doc_info)
                    if doc_info.doc_code:
                        self.codes.add(doc_info.doc_code)
                        self.code_to_doc[doc_info.doc_code] = doc_info
            except Exception as e:
                self.add_issue("ERROR", "读取文档失败", f"{md_file}: {str(e)}")

    def parse_doc_info(self, path: str, content: str) -> DocInfo:
        """解析文档信息"""
        doc_info = DocInfo(path=path, content=content, doc_code="", doc_type="UNKNOWN")

        # 提取文档编码
        code_match = re.search(r'文档编号\s*\|\s*([A-Z0-9-]+)', content)
        if code_match:
            doc_info.doc_code = code_match.group(1)

        # 提取文档类型
        if doc_info.doc_code:
            if doc_info.doc_code.startswith("L0"):
                doc_info.doc_type = "L0-战略与愿景"
                doc_info.layer = "L0"
            elif doc_info.doc_code.startswith("L1"):
                doc_info.doc_type = "L1-利益相关者需求"
                doc_info.layer = "L1"
            elif doc_info.doc_code.startswith("L2"):
                doc_info.doc_type = "L2-系统/产品需求"
                doc_info.layer = "L2"
            elif doc_info.doc_code.startswith("L3"):
                doc_info.doc_type = "L3-概念架构"
                doc_info.layer = "L3"
            elif doc_info.doc_code.startswith("L4"):
                doc_info.doc_type = "L4-逻辑/系统设计"
                doc_info.layer = "L4"
            elif doc_info.doc_code.startswith("L5"):
                doc_info.doc_type = "L5-详细设计"
                doc_info.layer = "L5"
            elif doc_info.doc_code.startswith("L6"):
                doc_info.doc_type = "L6-验证与确认"
                doc_info.layer = "L6"
            elif doc_info.doc_code.startswith("ADR"):
                doc_info.doc_type = "ADR-架构决策记录"
            elif doc_info.doc_code.startswith("REF"):
                doc_info.doc_type = "REF-外部参考"
            elif doc_info.doc_code.startswith("PLN"):
                doc_info.doc_type = "PLN-规划项"
            elif doc_info.doc_code.startswith("API"):
                doc_info.doc_type = "API-接口文档"
            elif doc_info.doc_code.startswith("FLD"):
                doc_info.doc_type = "FLD-字段定义"
            elif doc_info.doc_code.startswith("DICT"):
                doc_info.doc_type = "DICT-数据字典"
            else:
                doc_info.doc_type = f"UNKNOWN-{doc_info.doc_code.split('-')[0]}"

        # 提取状态
        status_match = re.search(r'状态\s*\|\s*(\S+)', content)
        if status_match:
            doc_info.status = status_match.group(1)

        # 派生状态类别（用于状态值校验）：L0-L6 取层码，ADR/REF 取类型码
        if doc_info.doc_code:
            first = doc_info.doc_code.split('-')[0]
            if first in ("L0", "L1", "L2", "L3", "L4", "L5", "L6", "ADR", "REF"):
                doc_info.status_category = first

        return doc_info

    def check_code_format(self) -> None:
        """检查编码格式"""
        valid_prefixes = [
            "L0", "L1", "L2", "L3", "L4", "L5", "L6",
            "ADR", "REF", "PLN", "API", "FLD", "DICT",
            "CHANGELOG", "README", "PLANNING"
        ]

        for doc in self.docs:
            if not doc.doc_code:
                self.add_issue("WARNING", "缺少文档编码", doc.path)
                continue

            # 检查编码格式
            if not re.match(r'^[A-Z0-9-]+$', doc.doc_code):
                self.add_issue("ERROR", "编码格式错误", f"{doc.path}: {doc.doc_code}")
                continue

            # 检查前缀
            prefix = doc.doc_code.split('-')[0]
            if prefix not in valid_prefixes:
                self.add_issue("WARNING", "未知编码前缀", f"{doc.path}: {doc.doc_code}")

    def check_duplicate_codes(self) -> None:
        """检查重复编码"""
        code_count = defaultdict(list)
        for doc in self.docs:
            if doc.doc_code:
                code_count[doc.doc_code].append(doc.path)

        for code, paths in code_count.items():
            if len(paths) > 1:
                self.add_issue("ERROR", "重复文档编码", f"{code} 出现在多个文件: {', '.join(paths)}")

    def check_code_consistency(self) -> None:
        """检查编码一致性"""
        # 检查文档中的编码引用是否存在
        for doc in self.docs:
            if not doc.content:
                continue

            # 查找所有编码引用（格式：{编号} 或具体编码）
            references = re.findall(r'[A-Z]{2,4}-\d{3,}', doc.content)
            for ref in references:
                if ref not in self.code_to_doc:
                    self.add_issue("INFO", "未找到引用的编码", f"{doc.path} 引用了不存在的编码 {ref}")

    def check_doc_structure(self) -> None:
        """检查文档结构"""
        required_sections = {
            "L0": ["1. 愿景描述", "2. 目标市场", "3. 成功标准"],
            "L1": ["1. 利益相关者", "2. 场景需求", "3. 业务目标"],
            "L2": ["1. 功能需求", "2. 非功能需求", "3. 业务规则"],
            "L3": ["1. 架构原则", "2. 组件设计", "3. 技术选型"],
            "L4": ["1. 设计概述", "2. 模块设计", "3. 数据设计"],
            "L5": ["1. 详细设计", "2. 流程逻辑", "3. 状态转换"],
            "L6": ["1. 验证策略", "2. 需求追溯", "3. 验收标准"],
        }

        for doc in self.docs:
            if doc.layer in required_sections:
                for section in required_sections[doc.layer]:
                    if section not in doc.content:
                        self.add_issue("WARNING", "缺少必需章节", f"{doc.path}: 缺少章节 '{section}'")

    def check_status_validity(self) -> None:
        """检查状态有效性"""
        valid_statuses = {
            "L0": ["草稿", "正式", "废弃"],
            "L1": ["草稿", "正式", "废弃"],
            "L2": ["草稿", "正式", "废弃"],
            "L3": ["草稿", "正式", "废弃"],
            "L4": ["草稿", "正式", "废弃"],
            "L5": ["草稿", "正式", "废弃"],
            "L6": ["草稿", "正式", "废弃"],
            "ADR": ["提议", "采纳", "拒绝", "废弃", "取代"],
            "REF": ["有效", "废弃"],
        }

        for doc in self.docs:
            if doc.status and doc.status_category in valid_statuses:
                if doc.status not in valid_statuses[doc.status_category]:
                    self.add_issue("WARNING", "无效状态值",
                                   f"{doc.path}: 状态 '{doc.status}' 不在 {doc.status_category} 允许范围内")

    def check_layer_references(self) -> None:
        """检查层级引用关系"""
        # 下层文档应该引用上层文档
        layer_order = ["L0", "L1", "L2", "L3", "L4", "L5", "L6"]

        for doc in self.docs:
            if not doc.layer or doc.layer == "L0":
                continue

            current_layer_index = layer_order.index(doc.layer)
            expected_parent_layers = layer_order[:current_layer_index]

            has_parent_reference = False
            for parent_layer in expected_parent_layers:
                if re.search(rf'{parent_layer}-\d{{3,}}', doc.content):
                    has_parent_reference = True
                    break

            if not has_parent_reference:
                self.add_issue("INFO", "缺少上级引用", f"{doc.path} 未引用上层文档")

    def _is_archived(self, doc: "DocInfo") -> bool:
        """文档是否已移入某作用域的 deprecated/ 目录（归档态）"""
        norm = doc.path.replace(os.sep, "/")
        return "/deprecated/" in norm

    def _extract_heading_block(self, lines: List[str], idx: int) -> str:
        """从标题行 idx 起，截取到下一个同级或更高级标题之前的正文块"""
        cur_level = len(lines[idx]) - len(lines[idx].lstrip("#")) if lines[idx].lstrip().startswith("#") else 0
        collected = [lines[idx]]
        for line in lines[idx + 1:]:
            stripped = line.lstrip()
            if stripped.startswith("#"):
                level = len(line) - len(line.lstrip("#"))
                if level <= cur_level:
                    break
            collected.append(line)
        return "\n".join(collected)

    def check_deprecation(self) -> None:
        """检查废弃处理规范性：细项废弃（原地）与文档废弃（两阶段）"""
        item_heading_re = re.compile(r'^#{2,4}\s+([A-Z][A-Z0-9]*(?:-[A-Z0-9]+)+)\b')
        deprecated_doc_codes: Set[str] = set()
        deprecated_item_codes: Set[str] = set()

        # 第一遍：字段完整性、状态值归一、到期提醒
        for doc in self.docs:
            if not doc.content:
                continue
            archived = self._is_archived(doc)

            # ---- 文档级废弃 ----
            if doc.status and "废弃" in doc.status:
                if doc.status.strip() == "已废弃":
                    self.add_issue("WARNING", "文档状态值不规范",
                                   f"{doc.path}: 状态值应统一为 '废弃'，而非 '已废弃'")
                required = ["废弃时间", "废弃原因"]
                if not archived:
                    required.append("建议移除日期")
                for field in required:
                    if field not in doc.content:
                        self.add_issue("ERROR", "废弃文档缺少必需字段",
                                       f"{doc.path}: 缺少 '{field}'")
                m = re.search(r'建议移除日期[^0-9]*(\d{4}-\d{2}-\d{2})', doc.content)
                if m and not archived:
                    try:
                        d = datetime.strptime(m.group(1), "%Y-%m-%d").date()
                        if d < date.today():
                            self.add_issue("INFO", "废弃文档可移除",
                                           f"{doc.path}: 已过建议移除日期 {m.group(1)}，可移除入 deprecated/")
                    except ValueError:
                        self.add_issue("WARNING", "建议移除日期格式错误",
                                       f"{doc.path}: '{m.group(1)}' 非 YYYY-MM-DD")
                if doc.doc_code:
                    deprecated_doc_codes.add(doc.doc_code)

            # ---- 细项级废弃（标题含 ~~已废弃~~）----
            lines = doc.content.splitlines()
            for i, line in enumerate(lines):
                if line.lstrip().startswith("#") and "~~已废弃~~" in line:
                    mh = item_heading_re.match(line.strip())
                    code = mh.group(1) if mh else None
                    block = self._extract_heading_block(lines, i)
                    for field in ["细项状态", "废弃时间", "废弃原因", "替代方案"]:
                        if field not in block:
                            self.add_issue("ERROR", "废弃细项缺少必需字段",
                                           f"{doc.path}: {code or '未知编码'} 缺少 '{field}'")
                    if re.search(r'细项状态\*{0,2}\s*[：:]\s*已废弃', block):
                        self.add_issue("WARNING", "细项状态值不规范",
                                       f"{doc.path}: {code or ''} '细项状态' 应统一为 '废弃'")
                    if code:
                        deprecated_item_codes.add(code)

        # 第二遍：引用完整性（活跃文档引用已废弃对象却未标注）
        for doc in self.docs:
            if not doc.content or self._is_archived(doc):
                continue
            if doc.status and "废弃" in doc.status:
                continue  # 自身已废弃，跳过
            seen: Set[str] = set()
            for line in doc.content.splitlines():
                for code in (deprecated_doc_codes | deprecated_item_codes):
                    if code in line and code != doc.doc_code:
                        # 该行未做任何废弃/删除线标注，视为对已废弃对象的有效引用
                        if "~~" not in line and "废弃" not in line:
                            key = f"{doc.path}::{code}"
                            if key not in seen:
                                seen.add(key)
                                self.add_issue("WARNING", "活跃文档引用已废弃对象",
                                               f"{doc.path}: 引用了已废弃的 {code}，但未标注其废弃或改指替代")

    def add_issue(self, level: str, title: str, description: str) -> None:
        """添加问题"""
        self.issues.append({
            "level": level,
            "title": title,
            "description": description
        })

    def run_checks(self) -> List[Dict]:
        """运行所有检查"""
        print("🔍 开始扫描文档...")
        self.scan_docs()

        print(f"📄 找到 {len(self.docs)} 个文档")

        print("🔧 运行检查规则...")
        self.check_code_format()
        self.check_duplicate_codes()
        self.check_code_consistency()
        self.check_doc_structure()
        self.check_status_validity()
        self.check_layer_references()
        self.check_deprecation()

        return self.issues

    def generate_report(self) -> str:
        """生成检查报告"""
        report = []
        report.append("=" * 80)
        report.append("DesignDoc 文档检查报告")
        report.append("=" * 80)
        report.append("")

        # 统计信息
        report.append("📊 文档统计:")
        report.append(f"  文档总数: {len(self.docs)}")
        report.append(f" 编码总数: {len(self.codes)}")
        report.append(f" 问题总数: {len(self.issues)}")
        report.append("")

        # 按类型统计文档
        doc_type_count = defaultdict(int)
        for doc in self.docs:
            doc_type_count[doc.doc_type] += 1

        report.append("📑 文档类型分布:")
        for doc_type, count in sorted(doc_type_count.items()):
            report.append(f"  {doc_type}: {count}")
        report.append("")

        # 按级别统计问题
        level_count = defaultdict(int)
        for issue in self.issues:
            level_count[issue["level"]] += 1

        report.append("⚠️ 问题统计:")
        for level in ["CRITICAL", "ERROR", "WARNING", "INFO"]:
            if level_count[level] > 0:
                report.append(f"  {level}: {level_count[level]}")
        report.append("")

        # 详细问题列表
        if self.issues:
            report.append("🔍 问题详情:")
            report.append("")

            # 按级别分组
            for level in ["CRITICAL", "ERROR", "WARNING", "INFO"]:
                level_issues = [i for i in self.issues if i["level"] == level]
                if level_issues:
                    report.append(f"### {level}")
                    for i, issue in enumerate(level_issues, 1):
                        report.append(f"{i}. {issue['title']}")
                        report.append(f"   {issue['description']}")
                    report.append("")

        # 建议
        if not self.issues:
            report.append("✅ 恭喜！未发现问题，文档规范良好。")
        else:
            critical_count = level_count["CRITICAL"]
            error_count = level_count["ERROR"]
            if critical_count > 0 or error_count > 0:
                report.append("❌ 发现严重问题，请立即修复。")
            else:
                report.append("⚠️ 发现一些问题，建议修复以提升文档质量。")

        report.append("")
        report.append("=" * 80)

        return "\n".join(report)

    def print_summary(self) -> None:
        """打印摘要信息"""
        level_count = defaultdict(int)
        for issue in self.issues:
            level_count[issue["level"]] += 1

        print(f"\n📊 检查完成: {len(self.docs)} 个文档, {len(self.issues)} 个问题")
        for level in ["CRITICAL", "ERROR", "WARNING", "INFO"]:
            if level_count[level] > 0:
                icon = "🔴" if level in ["CRITICAL", "ERROR"] else "🟡"
                print(f"  {icon} {level}: {level_count[level]}")

        if level_count["CRITICAL"] > 0 or level_count["ERROR"] > 0:
            print("\n❌ 存在严重问题，请查看详细报告")
            return 1
        elif level_count["WARNING"] > 0:
            print("\n⚠️ 存在警告，建议修复")
            return 0
        else:
            print("\n✅ 文档检查通过")
            return 0


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="DesignDoc 文档检查工具")
    parser.add_argument(
        "-p", "--path",
        default="./ued",
        help="UED 目录路径 (默认: ./ued)"
    )
    parser.add_argument(
        "-o", "--output",
        help="输出报告到文件"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="显示详细信息"
    )

    args = parser.parse_args()

    # 创建检查器
    checker = DesignDocChecker(args.path)

    # 运行检查
    issues = checker.run_checks()

    # 生成报告
    report = checker.generate_report()

    # 输出报告
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"📄 报告已保存到: {args.output}")
    else:
        if args.verbose:
            print("\n" + report)

    # 打印摘要并返回状态码
    return checker.print_summary()


if __name__ == "__main__":
    sys.exit(main())
