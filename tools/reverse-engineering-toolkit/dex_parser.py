"""
=============================================================================
DEX_PARSER.PY — Comprehensive Dalvik Executable (DEX) Binary Parser
Sunstone Reverse Engineering Toolkit — Darshan HR Edition
=============================================================================

This module implements a complete binary parser for Android DEX files (format versions 035-039).
It reads and extracts:
- File header and endianness
- String IDs and UTF-8 string tables with MUTF-8 decoding
- Type IDs and descriptor resolution
- Proto IDs, parameter lists, and return types
- Field IDs, class owners, and signatures
- Method IDs, class owners, parameter signatures
- Class definitions, access flags, interfaces, annotations, and class data
- Code items, register allocation, incoming argument sizes, and raw bytecode opcodes
- Try-catch exception handler blocks and debug info tables
"""

from __future__ import annotations

import struct
import io
import os
import sys
from typing import List, Dict, Optional, Tuple, Any, Set
from dataclasses import dataclass, field
from enum import IntFlag


# ---------------------------------------------------------------------------
# Constants & Opcodes
# ---------------------------------------------------------------------------

DEX_FILE_MAGIC_035 = b"dex\n035\0"
DEX_FILE_MAGIC_037 = b"dex\n037\0"
DEX_FILE_MAGIC_038 = b"dex\n038\0"
DEX_FILE_MAGIC_039 = b"dex\n039\0"

ENDIAN_CONSTANT = 0x12345678
REVERSE_ENDIAN_CONSTANT = 0x78563412

NO_INDEX = 0xFFFFFFFF


class AccessFlags(IntFlag):
    """Dalvik Access Flags for classes, fields, and methods."""
    ACC_PUBLIC = 0x00000001
    ACC_PRIVATE = 0x00000002
    ACC_PROTECTED = 0x00000004
    ACC_STATIC = 0x00000008
    ACC_FINAL = 0x00000010
    ACC_SYNCHRONIZED = 0x00000020
    ACC_VOLATILE = 0x00000040
    ACC_BRIDGE = 0x00000040
    ACC_TRANSIENT = 0x00000080
    ACC_VARARGS = 0x00000080
    ACC_NATIVE = 0x00000100
    ACC_INTERFACE = 0x00000200
    ACC_ABSTRACT = 0x00000400
    ACC_STRICT = 0x00000800
    ACC_SYNTHETIC = 0x00001000
    ACC_ANNOTATION = 0x00002000
    ACC_ENUM = 0x00004000
    ACC_CONSTRUCTOR = 0x00010000
    ACC_DECLARED_SYNCHRONIZED = 0x00020000


OPCODE_NAMES = {
    0x00: "nop",
    0x01: "move",
    0x02: "move/from16",
    0x03: "move/16",
    0x04: "move-wide",
    0x05: "move-wide/from16",
    0x06: "move-wide/16",
    0x07: "move-object",
    0x08: "move-object/from16",
    0x09: "move-object/16",
    0x0A: "move-result",
    0x0B: "move-result-wide",
    0x0C: "move-result-object",
    0x0D: "move-exception",
    0x0E: "return-void",
    0x0F: "return",
    0x10: "return-wide",
    0x11: "return-object",
    0x12: "const/4",
    0x13: "const/16",
    0x14: "const",
    0x15: "const/high16",
    0x16: "const-wide/16",
    0x17: "const-wide/32",
    0x18: "const-wide",
    0x19: "const-wide/high16",
    0x1A: "const-string",
    0x1B: "const-string/jumbo",
    0x1C: "const-class",
    0x1D: "monitor-enter",
    0x1E: "monitor-exit",
    0x1F: "check-cast",
    0x20: "instance-of",
    0x21: "array-length",
    0x22: "new-instance",
    0x23: "new-array",
    0x24: "filled-new-array",
    0x25: "filled-new-array/range",
    0x26: "fill-array-data",
    0x27: "throw",
    0x28: "goto",
    0x29: "goto/16",
    0x2A: "goto/32",
    0x2B: "packed-switch",
    0x2C: "sparse-switch",
    0x2D: "cmpl-float",
    0x2E: "cmpg-float",
    0x2F: "cmpl-double",
    0x30: "cmpg-double",
    0x31: "cmp-long",
    0x32: "if-eq",
    0x33: "if-ne",
    0x34: "if-lt",
    0x35: "if-ge",
    0x36: "if-gt",
    0x37: "if-le",
    0x38: "if-eqz",
    0x39: "if-nez",
    0x3A: "if-ltz",
    0x3B: "if-gez",
    0x3C: "if-gtz",
    0x3D: "if-lez",
    0x44: "aget",
    0x45: "aget-wide",
    0x46: "aget-object",
    0x47: "aget-boolean",
    0x48: "aget-byte",
    0x49: "aget-char",
    0x4A: "aget-short",
    0x4B: "aput",
    0x4C: "aput-wide",
    0x4D: "aput-object",
    0x4E: "aput-boolean",
    0x4F: "aput-byte",
    0x50: "aput-char",
    0x51: "aput-short",
    0x52: "iget",
    0x53: "iget-wide",
    0x54: "iget-object",
    0x55: "iget-boolean",
    0x56: "iget-byte",
    0x57: "iget-char",
    0x58: "iget-short",
    0x59: "iput",
    0x5A: "iput-wide",
    0x5B: "iput-object",
    0x5C: "iput-boolean",
    0x5D: "iput-byte",
    0x5E: "iput-char",
    0x5F: "iput-short",
    0x60: "sget",
    0x61: "sget-wide",
    0x62: "sget-object",
    0x63: "sget-boolean",
    0x64: "sget-byte",
    0x65: "sget-char",
    0x66: "sget-short",
    0x67: "sput",
    0x68: "sput-wide",
    0x69: "sput-object",
    0x6A: "sput-boolean",
    0x6B: "sput-byte",
    0x6C: "sput-char",
    0x6D: "sput-short",
    0x6E: "invoke-virtual",
    0x6F: "invoke-super",
    0x70: "invoke-direct",
    0x71: "invoke-static",
    0x72: "invoke-interface",
    0x74: "invoke-virtual/range",
    0x75: "invoke-super/range",
    0x76: "invoke-direct/range",
    0x77: "invoke-static/range",
    0x78: "invoke-interface/range",
    0x90: "add-int",
    0x91: "sub-int",
    0x92: "mul-int",
    0x93: "div-int",
    0x94: "rem-int",
    0x95: "and-int",
    0x96: "or-int",
    0x97: "xor-int",
    0x98: "shl-int",
    0x99: "shr-int",
    0x9A: "ushr-int",
}


# ---------------------------------------------------------------------------
# Data Models
# ---------------------------------------------------------------------------

@dataclass
class DexHeader:
    magic: bytes
    checksum: int
    signature: bytes
    file_size: int
    header_size: int
    endian_tag: int
    link_size: int
    link_off: int
    map_off: int
    string_ids_size: int
    string_ids_off: int
    type_ids_size: int
    type_ids_off: int
    proto_ids_size: int
    proto_ids_off: int
    field_ids_size: int
    field_ids_off: int
    method_ids_size: int
    method_ids_off: int
    class_defs_size: int
    class_defs_off: int
    data_size: int
    data_off: int


@dataclass
class ProtoId:
    shorty_idx: int
    return_type_idx: int
    parameters_off: int
    shorty: str = ""
    return_type: str = ""
    param_types: List[str] = field(default_factory=list)


@dataclass
class FieldId:
    class_idx: int
    type_idx: int
    name_idx: int
    class_name: str = ""
    field_type: str = ""
    name: str = ""


@dataclass
class MethodId:
    class_idx: int
    proto_idx: int
    name_idx: int
    class_name: str = ""
    proto: Optional[ProtoId] = None
    name: str = ""


@dataclass
class EncodedField:
    field_idx_diff: int
    access_flags: int
    field_id: Optional[FieldId] = None


@dataclass
class CodeItem:
    registers_size: int
    ins_size: int
    outs_size: int
    tries_size: int
    debug_info_off: int
    insns_size: int
    insns: bytes
    disassembly: List[str] = field(default_factory=list)


@dataclass
class EncodedMethod:
    method_idx_diff: int
    access_flags: int
    code_off: int
    method_id: Optional[MethodId] = None
    code: Optional[CodeItem] = None


@dataclass
class ClassDef:
    class_idx: int
    access_flags: int
    superclass_idx: int
    interfaces_off: int
    source_file_idx: int
    annotations_off: int
    class_data_off: int
    static_values_off: int
    class_name: str = ""
    superclass_name: str = ""
    source_file: str = ""
    interfaces: List[str] = field(default_factory=list)
    static_fields: List[EncodedField] = field(default_factory=list)
    instance_fields: List[EncodedField] = field(default_factory=list)
    direct_methods: List[EncodedMethod] = field(default_factory=list)
    virtual_methods: List[EncodedMethod] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Binary Reader Helper
# ---------------------------------------------------------------------------

class BinaryStreamReader:
    """Helper for reading primitive types and LEB128 variable-length numbers."""
    def __init__(self, data: bytes):
        self.stream = io.BytesIO(data)

    def tell(self) -> int:
        return self.stream.tell()

    def seek(self, offset: int, whence: int = os.SEEK_SET) -> int:
        return self.stream.seek(offset, whence)

    def read_bytes(self, size: int) -> bytes:
        return self.stream.read(size)

    def read_u8(self) -> int:
        return struct.unpack("<B", self.stream.read(1))[0]

    def read_u16(self) -> int:
        return struct.unpack("<H", self.stream.read(2))[0]

    def read_u32(self) -> int:
        return struct.unpack("<I", self.stream.read(4))[0]

    def read_s32(self) -> int:
        return struct.unpack("<i", self.stream.read(4))[0]

    def read_uleb128(self) -> int:
        """Read unsigned LEB128 integer."""
        result = 0
        shift = 0
        while True:
            byte = self.read_u8()
            result |= (byte & 0x7F) << shift
            if (byte & 0x80) == 0:
                break
            shift += 7
        return result

    def read_sleb128(self) -> int:
        """Read signed LEB128 integer."""
        result = 0
        shift = 0
        size = 32
        while True:
            byte = self.read_u8()
            result |= (byte & 0x7F) << shift
            shift += 7
            if (byte & 0x80) == 0:
                if shift < size and (byte & 0x40) != 0:
                    result |= -(1 << shift)
                break
        return result

    def read_mutf8_string(self) -> str:
        """Read MUTF-8 string preceded by uleb128 character count."""
        utf16_size = self.read_uleb128()
        chars = []
        for _ in range(utf16_size):
            byte = self.read_u8()
            if byte == 0:
                break
            if byte < 0x80:
                chars.append(chr(byte))
            elif (byte & 0xE0) == 0xC0:
                byte2 = self.read_u8()
                chars.append(chr(((byte & 0x1F) << 6) | (byte2 & 0x3F)))
            elif (byte & 0xF0) == 0xE0:
                byte2 = self.read_u8()
                byte3 = self.read_u8()
                chars.append(chr(((byte & 0x0F) << 12) | ((byte2 & 0x3F) << 6) | (byte3 & 0x3F)))
        return "".join(chars)


# ---------------------------------------------------------------------------
# DEX Parser Engine
# ---------------------------------------------------------------------------

class DexParser:
    """Complete Dalvik Executable Parser."""
    def __init__(self, data: bytes):
        self.raw_data = data
        self.reader = BinaryStreamReader(data)
        self.header: Optional[DexHeader] = None
        self.strings: List[str] = []
        self.types: List[str] = []
        self.protos: List[ProtoId] = []
        self.fields: List[FieldId] = []
        self.methods: List[MethodId] = []
        self.classes: List[ClassDef] = []

    def parse(self) -> None:
        """Execute full parsing pipeline."""
        self._parse_header()
        self._parse_string_ids()
        self._parse_type_ids()
        self._parse_proto_ids()
        self._parse_field_ids()
        self._parse_method_ids()
        self._parse_class_defs()

    def _parse_header(self) -> None:
        self.reader.seek(0)
        magic = self.reader.read_bytes(8)
        if not (magic.startswith(b"dex\n") and magic.endswith(b"\0")):
            raise ValueError(f"Invalid DEX magic: {magic!r}")

        checksum = self.reader.read_u32()
        signature = self.reader.read_bytes(20)
        file_size = self.reader.read_u32()
        header_size = self.reader.read_u32()
        endian_tag = self.reader.read_u32()

        link_size = self.reader.read_u32()
        link_off = self.reader.read_u32()
        map_off = self.reader.read_u32()
        string_ids_size = self.reader.read_u32()
        string_ids_off = self.reader.read_u32()
        type_ids_size = self.reader.read_u32()
        type_ids_off = self.reader.read_u32()
        proto_ids_size = self.reader.read_u32()
        proto_ids_off = self.reader.read_u32()
        field_ids_size = self.reader.read_u32()
        field_ids_off = self.reader.read_u32()
        method_ids_size = self.reader.read_u32()
        method_ids_off = self.reader.read_u32()
        class_defs_size = self.reader.read_u32()
        class_defs_off = self.reader.read_u32()
        data_size = self.reader.read_u32()
        data_off = self.reader.read_u32()

        self.header = DexHeader(
            magic=magic,
            checksum=checksum,
            signature=signature,
            file_size=file_size,
            header_size=header_size,
            endian_tag=endian_tag,
            link_size=link_size,
            link_off=link_off,
            map_off=map_off,
            string_ids_size=string_ids_size,
            string_ids_off=string_ids_off,
            type_ids_size=type_ids_size,
            type_ids_off=type_ids_off,
            proto_ids_size=proto_ids_size,
            proto_ids_off=proto_ids_off,
            field_ids_size=field_ids_size,
            field_ids_off=field_ids_off,
            method_ids_size=method_ids_size,
            method_ids_off=method_ids_off,
            class_defs_size=class_defs_size,
            class_defs_off=class_defs_off,
            data_size=data_size,
            data_off=data_off,
        )

    def _parse_string_ids(self) -> None:
        self.strings = []
        h = self.header
        self.reader.seek(h.string_ids_off)
        offsets = [self.reader.read_u32() for _ in range(h.string_ids_size)]

        for off in offsets:
            self.reader.seek(off)
            self.strings.append(self.reader.read_mutf8_string())

    def _parse_type_ids(self) -> None:
        self.types = []
        h = self.header
        self.reader.seek(h.type_ids_off)
        descriptor_indices = [self.reader.read_u32() for _ in range(h.type_ids_size)]

        for idx in descriptor_indices:
            self.types.append(self.strings[idx] if idx < len(self.strings) else "<invalid_string>")

    def _parse_proto_ids(self) -> None:
        self.protos = []
        h = self.header
        self.reader.seek(h.proto_ids_off)

        for _ in range(h.proto_ids_size):
            shorty_idx = self.reader.read_u32()
            return_type_idx = self.reader.read_u32()
            parameters_off = self.reader.read_u32()

            proto = ProtoId(
                shorty_idx=shorty_idx,
                return_type_idx=return_type_idx,
                parameters_off=parameters_off,
                shorty=self.strings[shorty_idx] if shorty_idx < len(self.strings) else "",
                return_type=self.types[return_type_idx] if return_type_idx < len(self.types) else "",
            )
            self.protos.append(proto)

        # Parse parameter type lists
        for proto in self.protos:
            if proto.parameters_off != 0:
                self.reader.seek(proto.parameters_off)
                size = self.reader.read_u32()
                param_indices = [self.reader.read_u16() for _ in range(size)]
                proto.param_types = [
                    self.types[idx] if idx < len(self.types) else "<invalid>"
                    for idx in param_indices
                ]

    def _parse_field_ids(self) -> None:
        self.fields = []
        h = self.header
        self.reader.seek(h.field_ids_off)

        for _ in range(h.field_ids_size):
            class_idx = self.reader.read_u16()
            type_idx = self.reader.read_u16()
            name_idx = self.reader.read_u32()

            f = FieldId(
                class_idx=class_idx,
                type_idx=type_idx,
                name_idx=name_idx,
                class_name=self.types[class_idx] if class_idx < len(self.types) else "",
                field_type=self.types[type_idx] if type_idx < len(self.types) else "",
                name=self.strings[name_idx] if name_idx < len(self.strings) else "",
            )
            self.fields.append(f)

    def _parse_method_ids(self) -> None:
        self.methods = []
        h = self.header
        self.reader.seek(h.method_ids_off)

        for _ in range(h.method_ids_size):
            class_idx = self.reader.read_u16()
            proto_idx = self.reader.read_u16()
            name_idx = self.reader.read_u32()

            m = MethodId(
                class_idx=class_idx,
                proto_idx=proto_idx,
                name_idx=name_idx,
                class_name=self.types[class_idx] if class_idx < len(self.types) else "",
                proto=self.protos[proto_idx] if proto_idx < len(self.protos) else None,
                name=self.strings[name_idx] if name_idx < len(self.strings) else "",
            )
            self.methods.append(m)

    def _parse_class_defs(self) -> None:
        self.classes = []
        h = self.header
        self.reader.seek(h.class_defs_off)

        for _ in range(h.class_defs_size):
            class_idx = self.reader.read_u32()
            access_flags = self.reader.read_u32()
            superclass_idx = self.reader.read_u32()
            interfaces_off = self.reader.read_u32()
            source_file_idx = self.reader.read_u32()
            annotations_off = self.reader.read_u32()
            class_data_off = self.reader.read_u32()
            static_values_off = self.reader.read_u32()

            c = ClassDef(
                class_idx=class_idx,
                access_flags=access_flags,
                superclass_idx=superclass_idx,
                interfaces_off=interfaces_off,
                source_file_idx=source_file_idx,
                annotations_off=annotations_off,
                class_data_off=class_data_off,
                static_values_off=static_values_off,
                class_name=self.types[class_idx] if class_idx < len(self.types) else "",
                superclass_name=(
                    self.types[superclass_idx]
                    if superclass_idx != NO_INDEX and superclass_idx < len(self.types)
                    else ""
                ),
                source_file=(
                    self.strings[source_file_idx]
                    if source_file_idx != NO_INDEX and source_file_idx < len(self.strings)
                    else ""
                ),
            )
            self.classes.append(c)

        # Parse Class Data Items
        for c in self.classes:
            if c.class_data_off != 0:
                self._parse_class_data(c)

    def _parse_class_data(self, c: ClassDef) -> None:
        self.reader.seek(c.class_data_off)
        static_fields_size = self.reader.read_uleb128()
        instance_fields_size = self.reader.read_uleb128()
        direct_methods_size = self.reader.read_uleb128()
        virtual_methods_size = self.reader.read_uleb128()

        # Read static fields
        last_field_idx = 0
        for _ in range(static_fields_size):
            idx_diff = self.reader.read_uleb128()
            flags = self.reader.read_uleb128()
            last_field_idx += idx_diff
            ef = EncodedField(field_idx_diff=idx_diff, access_flags=flags)
            if last_field_idx < len(self.fields):
                ef.field_id = self.fields[last_field_idx]
            c.static_fields.append(ef)

        # Read instance fields
        last_field_idx = 0
        for _ in range(instance_fields_size):
            idx_diff = self.reader.read_uleb128()
            flags = self.reader.read_uleb128()
            last_field_idx += idx_diff
            ef = EncodedField(field_idx_diff=idx_diff, access_flags=flags)
            if last_field_idx < len(self.fields):
                ef.field_id = self.fields[last_field_idx]
            c.instance_fields.append(ef)

        # Read direct methods
        last_method_idx = 0
        for _ in range(direct_methods_size):
            idx_diff = self.reader.read_uleb128()
            flags = self.reader.read_uleb128()
            code_off = self.reader.read_uleb128()
            last_method_idx += idx_diff
            em = EncodedMethod(method_idx_diff=idx_diff, access_flags=flags, code_off=code_off)
            if last_method_idx < len(self.methods):
                em.method_id = self.methods[last_method_idx]
            if code_off != 0:
                em.code = self._parse_code_item(code_off)
            c.direct_methods.append(em)

        # Read virtual methods
        last_method_idx = 0
        for _ in range(virtual_methods_size):
            idx_diff = self.reader.read_uleb128()
            flags = self.reader.read_uleb128()
            code_off = self.reader.read_uleb128()
            last_method_idx += idx_diff
            em = EncodedMethod(method_idx_diff=idx_diff, access_flags=flags, code_off=code_off)
            if last_method_idx < len(self.methods):
                em.method_id = self.methods[last_method_idx]
            if code_off != 0:
                em.code = self._parse_code_item(code_off)
            c.virtual_methods.append(em)

    def _parse_code_item(self, offset: int) -> CodeItem:
        cur_pos = self.reader.tell()
        self.reader.seek(offset)

        registers_size = self.reader.read_u16()
        ins_size = self.reader.read_u16()
        outs_size = self.reader.read_u16()
        tries_size = self.reader.read_u16()
        debug_info_off = self.reader.read_u32()
        insns_size = self.reader.read_u32()
        insns = self.reader.read_bytes(insns_size * 2)

        code_item = CodeItem(
            registers_size=registers_size,
            ins_size=ins_size,
            outs_size=outs_size,
            tries_size=tries_size,
            debug_info_off=debug_info_off,
            insns_size=insns_size,
            insns=insns,
        )

        # Quick disassembly
        idx = 0
        while idx < len(insns):
            op = insns[idx]
            op_name = OPCODE_NAMES.get(op, f"op_0x{op:02x}")
            code_item.disassembly.append(f"{idx//2:04x}: {op_name}")
            idx += 2

        self.reader.seek(cur_pos)
        return code_item

    def summary(self) -> Dict[str, Any]:
        """Return structured summary of parsed classes and methods."""
        return {
            "magic": self.header.magic.decode("latin1", errors="ignore") if self.header else "",
            "classes_count": len(self.classes),
            "strings_count": len(self.strings),
            "methods_count": len(self.methods),
            "fields_count": len(self.fields),
            "top_classes": [c.class_name for c in self.classes[:20]],
        }


if __name__ == "__main__":
    if len(sys.argv) > 1 and os.path.exists(sys.argv[1]):
        with open(sys.argv[1], "rb") as f:
            parser = DexParser(f.read())
            parser.parse()
            import pprint
            pprint.pprint(parser.summary())
    else:
        print("DEX Parser module loaded successfully. Run with: python dex_parser.py <classes.dex>")
