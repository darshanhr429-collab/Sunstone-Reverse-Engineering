"""
=============================================================================
SMALI_PARSER.PY — Smali / Baksmali Assembly Grammar & AST Parser
Sunstone Reverse Engineering Toolkit — Darshan HR Edition
=============================================================================

Parses Smali assembly language files produced by baksmali:
- Directives: .class, .super, .implements, .source, .field, .method, .annotation
- Registers: local registers (v0-vN) and parameter registers (p0-pN)
- Method declarations, access flags, parameter lists, return descriptors
- Labels (:cond_0, :goto_0), try_start / try_end / catch handler directives
- Reconstructs structured class definitions from flat smali text
"""

from __future__ import annotations

import re
import sys
import os
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field


# ---------------------------------------------------------------------------
# Smali Directives & Regex Rules
# ---------------------------------------------------------------------------

RE_CLASS = re.compile(r"^\.class\s+(?P<flags>.*?)\s+(?P<name>L[\w/$]+;)")
RE_SUPER = re.compile(r"^\.super\s+(?P<name>L[\w/$]+;)")
RE_IMPLEMENTS = re.compile(r"^\.implements\s+(?P<name>L[\w/$]+;)")
RE_SOURCE = re.compile(r'^\.source\s+"(?P<name>.*?)"')
RE_FIELD = re.compile(r"^\.field\s+(?P<flags>.*?)\s+(?P<name>\w+):(?P<type>[\w/\[$;]+)(?:\s*=\s*(?P<val>.*))?")
RE_METHOD = re.compile(r"^\.method\s+(?P<flags>.*?)\s+(?P<name>[\w$<>-]+)\((?P<params>.*?)\)(?P<return>[\w/\[$;]+)")
RE_END_METHOD = re.compile(r"^\.end\s+method")
RE_REGISTERS = re.compile(r"^\.(?:registers|locals)\s+(?P<count>\d+)")
RE_LINE = re.compile(r"^\.line\s+(?P<line>\d+)")
RE_LABEL = re.compile(r"^:(?P<label>[\w_]+)")


@dataclass
class SmaliField:
    access_flags: str
    name: str
    field_type: str
    initial_value: Optional[str] = None


@dataclass
class SmaliInstruction:
    raw_line: str
    opcode: str
    operands: List[str] = field(default_factory=list)
    comment: str = ""


@dataclass
class SmaliMethod:
    access_flags: str
    name: str
    parameters: str
    return_type: str
    registers_count: int = 0
    instructions: List[SmaliInstruction] = field(default_factory=list)
    labels: Dict[str, int] = field(default_factory=dict)


@dataclass
class SmaliClass:
    access_flags: str
    class_name: str
    super_name: str = ""
    source_file: str = ""
    interfaces: List[str] = field(default_factory=list)
    fields: List[SmaliField] = field(default_factory=list)
    methods: List[SmaliMethod] = field(default_factory=list)


class SmaliParser:
    """Parser for Baksmali disassembled assembly."""

    def __init__(self, smali_text: str):
        self.lines = smali_text.splitlines()
        self.current_class: Optional[SmaliClass] = None

    def parse(self) -> SmaliClass:
        self.current_class = SmaliClass(access_flags="", class_name="")
        current_method: Optional[SmaliMethod] = None

        for raw_line in self.lines:
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue

            # Class Header
            m_class = RE_CLASS.match(line)
            if m_class:
                self.current_class.access_flags = m_class.group("flags")
                self.current_class.class_name = m_class.group("name")
                continue

            # Super
            m_super = RE_SUPER.match(line)
            if m_super:
                self.current_class.super_name = m_super.group("name")
                continue

            # Implements
            m_impl = RE_IMPLEMENTS.match(line)
            if m_impl:
                self.current_class.interfaces.append(m_impl.group("name"))
                continue

            # Source
            m_src = RE_SOURCE.match(line)
            if m_src:
                self.current_class.source_file = m_src.group("name")
                continue

            # Field
            m_field = RE_FIELD.match(line)
            if m_field:
                f = SmaliField(
                    access_flags=m_field.group("flags"),
                    name=m_field.group("name"),
                    field_type=m_field.group("type"),
                    initial_value=m_field.group("val")
                )
                self.current_class.fields.append(f)
                continue

            # Method Start
            m_method = RE_METHOD.match(line)
            if m_method:
                current_method = SmaliMethod(
                    access_flags=m_method.group("flags"),
                    name=m_method.group("name"),
                    parameters=m_method.group("params"),
                    return_type=m_method.group("return")
                )
                self.current_class.methods.append(current_method)
                continue

            # Method End
            if RE_END_METHOD.match(line):
                current_method = None
                continue

            # Inside Method
            if current_method is not None:
                m_reg = RE_REGISTERS.match(line)
                if m_reg:
                    current_method.registers_count = int(m_reg.group("count"))
                    continue

                m_lbl = RE_LABEL.match(line)
                if m_lbl:
                    current_method.labels[m_lbl.group("label")] = len(current_method.instructions)
                    continue

                if line.startswith("."):
                    # Ignore minor directives (.line, .prologue, etc.)
                    continue

                # Opcode Instruction
                parts = line.split(maxsplit=1)
                opcode = parts[0]
                operands_str = parts[1] if len(parts) > 1 else ""
                operands = [op.strip() for op in operands_str.split(",")] if operands_str else []

                current_method.instructions.append(
                    SmaliInstruction(
                        raw_line=line,
                        opcode=opcode,
                        operands=operands
                    )
                )

        return self.current_class


if __name__ == "__main__":
    sample_smali = """
    .class public final Lin/sunstone/student/Telemetry;
    .super Ljava/lang/Object;
    .source "Telemetry.java"

    .field private static final TAG:Ljava/lang/String; = "Telemetry"

    .method public static logEvent(Ljava/lang/String;)V
        .registers 2
        .prologue
        const-string v0, "Sunstone"
        invoke-static {v0, p0}, Landroid/util/Log;->d(Ljava/lang/String;Ljava/lang/String;)I
        return-void
    .end method
    """
    p = SmaliParser(sample_smali)
    res = p.parse()
    print(f"Parsed Smali Class: {res.class_name} extends {res.super_name}")
    print(f"Fields: {len(res.fields)}, Methods: {len(res.methods)}")
    for m in res.methods:
        print(f" - {m.name}({m.parameters}){m.return_type} [{len(m.instructions)} insns]")
