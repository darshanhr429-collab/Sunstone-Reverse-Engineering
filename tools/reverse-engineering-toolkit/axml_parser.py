"""
=============================================================================
AXML_PARSER.PY — Android Binary XML (AXML) Manifest Parser
Sunstone Reverse Engineering Toolkit — Darshan HR Edition
=============================================================================

Parses binary AndroidManifest.xml files extracted from Android APKs.
Recovers the human-readable XML tree including:
- Package name, versionCode, versionName
- Permissions requested (uses-permission, permission)
- Components (Activities, Services, BroadcastReceivers, ContentProviders)
- Intent filters (actions, categories, data schemes, mimeTypes)
- Custom Application meta-data and hardware feature requirements
"""

from __future__ import annotations

import struct
import io
import sys
import os
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field


# ---------------------------------------------------------------------------
# Chunk Types in Android Binary XML
# ---------------------------------------------------------------------------

RES_NULL_TYPE = 0x0000
RES_STRING_POOL_TYPE = 0x0001
RES_TABLE_TYPE = 0x0002
RES_XML_TYPE = 0x0003
RES_XML_FIRST_CHUNK_TYPE = 0x0100
RES_XML_START_NAMESPACE_TYPE = 0x0100
RES_XML_END_NAMESPACE_TYPE = 0x0101
RES_XML_START_ELEMENT_TYPE = 0x0102
RES_XML_END_ELEMENT_TYPE = 0x0103
RES_XML_CDATA_TYPE = 0x0104
RES_XML_RESOURCE_MAP_TYPE = 0x0180


@dataclass
class ResStringPool:
    string_count: int
    style_count: int
    flags: int
    strings_start: int
    styles_start: int
    strings: List[str] = field(default_factory=list)


@dataclass
class XmlAttribute:
    ns_idx: int
    name_idx: int
    raw_val_idx: int
    type: int
    data: int
    ns: str = ""
    name: str = ""
    value: str = ""


@dataclass
class XmlNode:
    tag: str
    ns: str = ""
    attributes: List[XmlAttribute] = field(default_factory=list)
    children: List[XmlNode] = field(default_factory=list)
    text: str = ""


class AxmlParser:
    """Complete Android Binary XML Parser."""
    def __init__(self, data: bytes):
        self.raw_data = data
        self.stream = io.BytesIO(data)
        self.string_pool: Optional[ResStringPool] = None
        self.resource_map: List[int] = []
        self.root_node: Optional[XmlNode] = None

    def read_u16(self) -> int:
        return struct.unpack("<H", self.stream.read(2))[0]

    def read_u32(self) -> int:
        return struct.unpack("<I", self.stream.read(4))[0]

    def parse(self) -> XmlNode:
        """Parse binary AXML and construct DOM tree."""
        file_type = self.read_u16()
        header_size = self.read_u16()
        file_size = self.read_u32()

        if file_type != RES_XML_TYPE:
            raise ValueError(f"Not a valid AXML file (type: 0x{file_type:04x})")

        node_stack: List[XmlNode] = []

        while self.stream.tell() < file_size:
            chunk_start = self.stream.tell()
            chunk_type = self.read_u16()
            chunk_header_size = self.read_u16()
            chunk_size = self.read_u32()

            if chunk_type == RES_STRING_POOL_TYPE:
                self._parse_string_pool(chunk_start, chunk_size)
            elif chunk_type == RES_XML_RESOURCE_MAP_TYPE:
                self._parse_resource_map(chunk_start, chunk_size)
            elif chunk_type == RES_XML_START_ELEMENT_TYPE:
                node = self._parse_start_element()
                if node_stack:
                    node_stack[-1].children.append(node)
                else:
                    self.root_node = node
                node_stack.append(node)
            elif chunk_type == RES_XML_END_ELEMENT_TYPE:
                self.stream.seek(chunk_start + chunk_size)
                if node_stack:
                    node_stack.pop()
            elif chunk_type in (RES_XML_START_NAMESPACE_TYPE, RES_XML_END_NAMESPACE_TYPE):
                self.stream.seek(chunk_start + chunk_size)
            else:
                self.stream.seek(chunk_start + chunk_size)

        return self.root_node

    def _parse_string_pool(self, chunk_start: int, chunk_size: int) -> None:
        string_count = self.read_u32()
        style_count = self.read_u32()
        flags = self.read_u32()
        strings_start = self.read_u32()
        styles_start = self.read_u32()

        pool = ResStringPool(
            string_count=string_count,
            style_count=style_count,
            flags=flags,
            strings_start=strings_start,
            styles_start=styles_start,
        )

        offsets = [self.read_u32() for _ in range(string_count)]
        strings_data_start = chunk_start + strings_start

        is_utf8 = (flags & (1 << 8)) != 0

        for off in offsets:
            self.stream.seek(strings_data_start + off)
            if is_utf8:
                # UTF-8
                _ = self.stream.read(1)  # Length
                u8_len = self.stream.read(1)[0]
                s = self.stream.read(u8_len).decode("utf-8", errors="replace")
            else:
                # UTF-16
                u16_len = self.read_u16()
                s = self.stream.read(u16_len * 2).decode("utf-16le", errors="replace")
            pool.strings.append(s)

        self.string_pool = pool
        self.stream.seek(chunk_start + chunk_size)

    def _parse_resource_map(self, chunk_start: int, chunk_size: int) -> None:
        count = (chunk_size - 8) // 4
        self.resource_map = [self.read_u32() for _ in range(count)]
        self.stream.seek(chunk_start + chunk_size)

    def _parse_start_element(self) -> XmlNode:
        _line_number = self.read_u32()
        _comment_idx = self.read_u32()
        ns_idx = self.read_u32()
        name_idx = self.read_u32()
        _attr_start = self.read_u16()
        _attr_size = self.read_u16()
        attr_count = self.read_u16()
        _id_idx = self.read_u16()
        _class_idx = self.read_u16()
        _style_idx = self.read_u16()

        tag = self.get_string(name_idx)
        ns = self.get_string(ns_idx)

        node = XmlNode(tag=tag, ns=ns)

        for _ in range(attr_count):
            a_ns_idx = self.read_u32()
            a_name_idx = self.read_u32()
            a_raw_val_idx = self.read_u32()
            a_type = self.read_u32() >> 24
            a_data = self.read_u32()

            attr = XmlAttribute(
                ns_idx=a_ns_idx,
                name_idx=a_name_idx,
                raw_val_idx=a_raw_val_idx,
                type=a_type,
                data=a_data,
                ns=self.get_string(a_ns_idx),
                name=self.get_string(a_name_idx),
                value=self.get_string(a_raw_val_idx) if a_raw_val_idx != 0xFFFFFFFF else str(a_data)
            )
            node.attributes.append(attr)

        return node

    def get_string(self, idx: int) -> str:
        if self.string_pool and 0 <= idx < len(self.string_pool.strings):
            return self.string_pool.strings[idx]
        return ""

    def to_xml_string(self, node: Optional[XmlNode] = None, indent: int = 0) -> str:
        """Convert AST back into human-readable formatted XML."""
        if node is None:
            node = self.root_node
        if not node:
            return ""

        pad = "  " * indent
        attrs = []
        for a in node.attributes:
            name = a.name
            attrs.append(f'{name}="{a.value}"')

        attr_str = (" " + " ".join(attrs)) if attrs else ""

        if not node.children:
            return f"{pad}<{node.tag}{attr_str} />\n"

        out = f"{pad}<{node.tag}{attr_str}>\n"
        for child in node.children:
            out += self.to_xml_string(child, indent + 1)
        out += f"{pad}</{node.tag}>\n"
        return out


if __name__ == "__main__":
    if len(sys.argv) > 1 and os.path.exists(sys.argv[1]):
        with open(sys.argv[1], "rb") as f:
            p = AxmlParser(f.read())
            p.parse()
            print(p.to_xml_string())
    else:
        print("AXML Parser loaded. Run with: python axml_parser.py <AndroidManifest.xml>")
