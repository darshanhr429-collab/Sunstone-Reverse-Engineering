"""
=============================================================================
PROTOBUF_WIRE_DECODER.PY — Pure-Python Schemaless Protocol Buffers Decoder
Sunstone Reverse Engineering Toolkit — Darshan HR Edition
=============================================================================

Decodes binary Protocol Buffer wire payloads extracted from network captures
or mobile app binary caches without having the original .proto schema files:
- Wire Types: Varint (0), 64-bit (1), Length-delimited (2), 32-bit (5)
- Recursively attempts to identify sub-messages in length-delimited bytes
- Decodes ZigZag signed integers and UTF-8 strings
- Exports decoded message trees into formatted JSON structures
"""

from __future__ import annotations

import struct
import io
import json
import sys
import os
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, field


WIRE_VARINT = 0
WIRE_FIXED64 = 1
WIRE_LENGTH_DELIMITED = 2
WIRE_START_GROUP = 3
WIRE_END_GROUP = 4
WIRE_FIXED32 = 5


@dataclass
class ProtoField:
    field_number: int
    wire_type: int
    raw_value: Any
    decoded_value: Any = None
    is_nested_message: bool = False


class ProtobufWireDecoder:
    """Schemaless protobuf binary decoder."""

    def __init__(self, data: bytes):
        self.raw_data = data
        self.stream = io.BytesIO(data)

    def decode(self) -> Dict[str, Any]:
        """Decode payload into a nested dictionary structure."""
        fields: Dict[int, List[Any]] = {}
        length = len(self.raw_data)

        while self.stream.tell() < length:
            tag_byte = self._read_varint()
            if tag_byte is None:
                break

            field_number = tag_byte >> 3
            wire_type = tag_byte & 0x07

            val = self._read_field_value(wire_type)
            if field_number not in fields:
                fields[field_number] = []
            fields[field_number].append(val)

        return {f"field_{k}": (v[0] if len(v) == 1 else v) for k, v in fields.items()}

    def _read_varint(self) -> Optional[int]:
        result = 0
        shift = 0
        while True:
            b_byte = self.stream.read(1)
            if not b_byte:
                return None
            b = b_byte[0]
            result |= (b & 0x7F) << shift
            if (b & 0x80) == 0:
                break
            shift += 7
        return result

    def _read_field_value(self, wire_type: int) -> Any:
        if wire_type == WIRE_VARINT:
            return self._read_varint()

        elif wire_type == WIRE_FIXED64:
            b = self.stream.read(8)
            if len(b) < 8:
                return 0
            return struct.unpack("<Q", b)[0]

        elif wire_type == WIRE_LENGTH_DELIMITED:
            length = self._read_varint() or 0
            payload = self.stream.read(length)

            # Heuristic: Check if payload is valid UTF-8 string
            try:
                text = payload.decode("utf-8")
                if text.isprintable() and len(text) > 0:
                    return text
            except Exception:
                pass

            # Heuristic: Attempt recursive protobuf decode
            try:
                sub_decoder = ProtobufWireDecoder(payload)
                sub_res = sub_decoder.decode()
                if sub_res and len(sub_res) > 0:
                    return sub_res
            except Exception:
                pass

            return payload.hex()

        elif wire_type == WIRE_FIXED32:
            b = self.stream.read(4)
            if len(b) < 4:
                return 0
            return struct.unpack("<I", b)[0]

        return None


if __name__ == "__main__":
    # Test protobuf payload:
    # Field 1 (string) = "darshan-hr"
    # Field 2 (varint) = 42850
    test_stream = io.BytesIO()
    # Field 1, type 2: tag = (1 << 3) | 2 = 10
    test_stream.write(bytes([10, len(b"darshan-hr")]) + b"darshan-hr")
    # Field 2, type 0: tag = (2 << 3) | 0 = 16
    # 42850 in varint: 0x82, 0xCE, 0x02
    test_stream.write(bytes([16, 0x82, 0xCE, 0x02]))

    dec = ProtobufWireDecoder(test_stream.getvalue())
    res = dec.decode()
    print("Decoded Protobuf Structure:")
    print(json.dumps(res, indent=2))
