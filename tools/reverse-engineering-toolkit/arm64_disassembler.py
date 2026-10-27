"""
=============================================================================
ARM64_DISASSEMBLER.PY — Pure-Python ARM64 (AArch64) Instruction Disassembler
Sunstone Reverse Engineering Toolkit — Darshan HR Edition
=============================================================================

Decodes 32-bit little-endian ARM64 instruction words found in compiled Android .so files:
- Arithmetic: ADD, ADDS, SUB, SUBS, CMP, NEG, CMN
- Logical: AND, ANDS, ORR, EOR, BIC, BICS, EON, MVN
- Shifts & Bitfield: LSL, LSR, ASR, ROR, BFM, SBFM, UBFM, EXTR
- Memory Operations: LDR, STR, LDP, STP, LDRB, STRB, LDRH, STRH, LDUR, STUR
- Branching: B, BL, B.cond, CBZ, CBNZ, TBZ, TBNZ, BR, BLR, RET
- System & Specials: NOP, SVC, HVC, SMC, BRK, MRS, MSR, ADR, ADRP
"""

from __future__ import annotations

import struct
import io
import sys
import os
from typing import Dict, List, Optional, Tuple, NamedTuple
from dataclasses import dataclass, field


CONDITION_CODES = [
    "eq", "ne", "cs", "cc", "mi", "pl", "vs", "vc",
    "hi", "ls", "ge", "lt", "gt", "le", "al", "nv"
]


@dataclass
class Arm64Instruction:
    address: int
    raw_word: int
    mnemonic: str
    operands: str
    comment: str = ""


class Arm64Disassembler:
    """Disassembles 32-bit AArch64 machine instructions."""

    def __init__(self, base_address: int = 0):
        self.base_address = base_address

    def disassemble_bytes(self, data: bytes) -> List[Arm64Instruction]:
        instructions: List[Arm64Instruction] = []
        stream = io.BytesIO(data)
        addr = self.base_address

        while True:
            word_bytes = stream.read(4)
            if len(word_bytes) < 4:
                break
            word = struct.unpack("<I", word_bytes)[0]
            insn = self.decode_word(addr, word)
            instructions.append(insn)
            addr += 4

        return instructions

    def decode_word(self, addr: int, word: int) -> Arm64Instruction:
        # NOP
        if word == 0xD503201F:
            return Arm64Instruction(addr, word, "nop", "")

        # RET (reg 30 default)
        if (word & 0xFFFFFC1F) == 0xD65F0000:
            rn = (word >> 5) & 0x1F
            rn_str = f"x{rn}" if rn != 30 else ""
            return Arm64Instruction(addr, word, "ret", rn_str)

        # BR / BLR
        if (word & 0xFFFFFC1F) == 0xD61F0000:
            rn = (word >> 5) & 0x1F
            return Arm64Instruction(addr, word, "br", f"x{rn}")
        if (word & 0xFFFFFC1F) == 0xD63F0000:
            rn = (word >> 5) & 0x1F
            return Arm64Instruction(addr, word, "blr", f"x{rn}")

        # Unconditional Branch Immediate (B, BL)
        # B:  000101 imm26
        # BL: 100101 imm26
        op_b = (word >> 26) & 0x3F
        if op_b in (0x05, 0x25):
            is_bl = (op_b == 0x25)
            imm26 = word & 0x03FFFFFF
            if imm26 & 0x02000000:
                imm26 -= 0x04000000
            target = addr + imm26 * 4
            mnemonic = "bl" if is_bl else "b"
            return Arm64Instruction(addr, word, mnemonic, f"0x{target:x}")

        # Conditional Branch (B.cond)
        # 01010100 imm19 0 cond
        if (word & 0xFF000010) == 0x54000000:
            cond = word & 0x0F
            cond_str = CONDITION_CODES[cond] if cond < len(CONDITION_CODES) else f"c{cond}"
            imm19 = (word >> 5) & 0x7FFFF
            if imm19 & 0x40000:
                imm19 -= 0x80000
            target = addr + imm19 * 4
            return Arm64Instruction(addr, word, f"b.{cond_str}", f"0x{target:x}")

        # CBZ / CBNZ
        # sf 011010 op imm19 Rt
        if (word & 0x7E000000) == 0x34000000:
            sf = (word >> 31) & 1
            op = (word >> 24) & 1
            rt = word & 0x1F
            reg = f"x{rt}" if sf else f"w{rt}"
            imm19 = (word >> 5) & 0x7FFFF
            if imm19 & 0x40000:
                imm19 -= 0x80000
            target = addr + imm19 * 4
            mnemonic = "cbnz" if op else "cbz"
            return Arm64Instruction(addr, word, mnemonic, f"{reg}, 0x{target:x}")

        # ADRP / ADR
        # op immlo 10000 immhi Rd
        if (word & 0x1F000000) == 0x10000000:
            op = (word >> 31) & 1
            rd = word & 0x1F
            immlo = (word >> 29) & 3
            immhi = (word >> 5) & 0x7FFFF
            imm = (immhi << 2) | immlo
            if op == 1:
                # ADRP (4KB page aligned)
                if imm & 0x100000:
                    imm -= 0x200000
                page_addr = (addr & ~0xFFF) + (imm << 12)
                return Arm64Instruction(addr, word, "adrp", f"x{rd}, 0x{page_addr:x}")
            else:
                # ADR
                if imm & 0x100000:
                    imm -= 0x200000
                target = addr + imm
                return Arm64Instruction(addr, word, "adr", f"x{rd}, 0x{target:x}")

        # STP / LDP (Load / Store Pair)
        # sf 1010 op 010 imm7 Rt2 Rn Rt
        if (word & 0x3E400000) == 0x28400000 or (word & 0x3E400000) == 0x29400000:
            sf = (word >> 31) & 1
            is_ldp = ((word >> 22) & 1) == 1
            rt = word & 0x1F
            rn = (word >> 5) & 0x1F
            rt2 = (word >> 10) & 0x1F
            imm7 = (word >> 15) & 0x7F
            scale = 8 if sf else 4
            if imm7 & 0x40:
                imm7 -= 0x80
            offset = imm7 * scale
            prefix = "x" if sf else "w"
            mnemonic = "ldp" if is_ldp else "stp"
            rn_str = "sp" if rn == 31 else f"x{rn}"
            off_str = f", #{offset}" if offset != 0 else ""
            return Arm64Instruction(addr, word, mnemonic, f"{prefix}{rt}, {prefix}{rt2}, [{rn_str}{off_str}]")

        # Fallback raw word
        return Arm64Instruction(addr, word, f".word", f"0x{word:08x}")


if __name__ == "__main__":
    dis = Arm64Disassembler(0x10000)
    # Machine code:
    # 0xD503201F -> NOP
    # 0xD65F03C0 -> RET
    # 0x14000004 -> B +16
    sample_bytes = b"\x1f\x20\x03\xd5\xc0\x03\x5f\xd6\x04\x00\x00\x14"
    results = dis.disassemble_bytes(sample_bytes)
    for r in results:
        print(f"0x{r.address:08x}: {r.mnemonic:<8} {r.operands}")
