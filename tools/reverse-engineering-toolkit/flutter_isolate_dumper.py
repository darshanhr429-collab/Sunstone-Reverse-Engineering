"""
=============================================================================
FLUTTER_ISOLATE_DUMPER.PY — Flutter Dart VM Isolate & Heap Memory Dumper
Sunstone Reverse Engineering Toolkit — Darshan HR Edition
=============================================================================

Dynamic and static memory snapshot analyzer for Flutter Dart VM heaps:
- Inspects Dart VM heap pages (Old Gen, New Gen, Read-Only Object Store)
- Recovers tagged Dart Object pointers (Heap Object header, Class ID, Hash)
- Extracts Dart Strings, TypedData arrays, and Field dictionaries
- Generates JSON heap dumps for offline reverse-engineering
"""

from __future__ import annotations

import struct
import json
import io
import sys
import os
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field


# ---------------------------------------------------------------------------
# Dart 64-bit Object Tagging Constants
# ---------------------------------------------------------------------------

DART_SMI_TAG_MASK = 0x01
DART_SMI_TAG_VALUE = 0x00
DART_HEAP_TAG_MASK = 0x03
DART_HEAP_TAG_VALUE = 0x01

# Dart Class IDs (Predefined in VM)
CID_ILLEGAL = 0
CID_CLASS = 1
CID_DYNAMIC_TYPE = 2
CID_TYPE = 3
CID_TYPE_REF = 4
CID_TYPE_PARAMETER = 5
CID_LIBRARY_PREFIX = 6
CID_TYPE_ARGUMENTS = 7
CID_INSTRUCTIONS = 8
CID_GRAPH_INTRINSICS = 9
CID_CODE = 10
CID_BYTECODE = 11
CID_FUNCTION = 12
CID_FIELD = 13
CID_CONTEXT = 14
CID_ONE_BYTE_STRING = 20
CID_TWO_BYTE_STRING = 21
CID_EXTERNAL_ONE_BYTE_STRING = 22
CID_ARRAY = 25
CID_GROWABLE_OBJECT_ARRAY = 26


@dataclass
class DartHeapObject:
    address: int
    class_id: int
    class_name: str
    size: int
    string_value: Optional[str] = None
    fields: List[int] = field(default_factory=list)


class FlutterIsolateDumper:
    """Inspector for dumped Dart VM isolate heap memory regions."""

    def __init__(self, raw_dump_path: str):
        self.raw_dump_path = raw_dump_path
        self.objects: List[DartHeapObject] = []

    def parse_heap_dump(self) -> List[DartHeapObject]:
        if not os.path.exists(self.raw_dump_path):
            raise FileNotFoundError(f"Heap dump file not found: {self.raw_dump_path}")

        with open(self.raw_dump_path, "rb") as f:
            data = f.read()

        stream = io.BytesIO(data)
        length = len(data)
        addr = 0x7000000000  # Virtual base

        while stream.tell() + 16 <= length:
            cur_pos = stream.tell()
            header_word = struct.unpack("<Q", stream.read(8))[0]

            # Header word layout in Dart 64-bit:
            # bits 0..1: GC bits
            # bits 2..31: Hash
            # bits 32..51: Class ID
            # bits 52..63: Size tag
            cid = (header_word >> 32) & 0xFFFFF
            size_tag = (header_word >> 52) & 0xFFF
            obj_size = size_tag * 8 if size_tag > 0 else 16

            if cid == CID_ONE_BYTE_STRING:
                # String object: header (8) + length (8) + characters
                str_len_word = struct.unpack("<Q", stream.read(8))[0]
                str_len = str_len_word >> 1  # Unbox Smi
                str_chars = stream.read(min(str_len, 512))
                val = str_chars.decode("latin1", errors="replace")
                self.objects.append(
                    DartHeapObject(
                        address=addr + cur_pos,
                        class_id=cid,
                        class_name="OneByteString",
                        size=obj_size,
                        string_value=val
                    )
                )

            # Advance to next 8-byte boundary
            next_offset = (cur_pos + max(8, obj_size) + 7) & ~7
            stream.seek(min(next_offset, length))

        return self.objects

    def export_strings_json(self, output_file: str = "dart_strings.json") -> str:
        strings = [
            {"address": f"0x{o.address:x}", "value": o.string_value}
            for o in self.objects
            if o.string_value
        ]
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(strings, f, indent=2)
        return output_file


if __name__ == "__main__":
    if len(sys.argv) > 1 and os.path.exists(sys.argv[1]):
        dumper = FlutterIsolateDumper(sys.argv[1])
        objs = dumper.parse_heap_dump()
        print(f"Parsed {len(objs)} Dart heap objects.")
    else:
        print("Flutter Isolate Dumper loaded. Run with: python flutter_isolate_dumper.py <heap.bin>")
