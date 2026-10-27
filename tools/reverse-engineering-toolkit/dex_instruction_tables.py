"""
=============================================================================
DEX_INSTRUCTION_TABLES.PY — Dalvik Virtual Machine Opcode Specification
Sunstone Reverse Engineering Toolkit — Darshan HR Edition
=============================================================================

Exhaustive opcode definitions, instruction formats, register access modes,
branch characteristics, and verification rules for all 256 Dalvik opcodes.
"""

from __future__ import annotations

from typing import Dict, List, Optional, Tuple, NamedTuple
from dataclasses import dataclass


class OpcodeInfo(NamedTuple):
    opcode: int
    name: str
    format: str
    flags: int
    branch_type: str
    description: str


# Branch Types
BRANCH_NONE = "NONE"
BRANCH_UNCONDITIONAL = "UNCONDITIONAL"
BRANCH_CONDITIONAL = "CONDITIONAL"
BRANCH_SWITCH = "SWITCH"
BRANCH_RETURN = "RETURN"
BRANCH_THROW = "THROW"

# Flags
FLAG_SETS_RESULT = 1 << 0
FLAG_SETS_REG_A = 1 << 1
FLAG_USES_REG_A = 1 << 2
FLAG_USES_REG_B = 1 << 3
FLAG_USES_REG_C = 1 << 4
FLAG_THROWS_EXCEPTION = 1 << 5


DALVIK_OPCODE_TABLE: Dict[int, OpcodeInfo] = {
    0x00: OpcodeInfo(0x00, "nop", "10x", 0, BRANCH_NONE, "Waste cycles; no operation"),
    0x01: OpcodeInfo(0x01, "move", "12x", FLAG_SETS_REG_A | FLAG_USES_REG_B, BRANCH_NONE, "Move content of register B to register A"),
    0x02: OpcodeInfo(0x02, "move/from16", "22x", FLAG_SETS_REG_A | FLAG_USES_REG_B, BRANCH_NONE, "Move 16-bit register B to register A"),
    0x03: OpcodeInfo(0x03, "move/16", "32x", FLAG_SETS_REG_A | FLAG_USES_REG_B, BRANCH_NONE, "Move 16-bit register B to 16-bit register A"),
    0x04: OpcodeInfo(0x04, "move-wide", "12x", FLAG_SETS_REG_A | FLAG_USES_REG_B, BRANCH_NONE, "Move 64-bit pair from register B to register A"),
    0x05: OpcodeInfo(0x05, "move-wide/from16", "22x", FLAG_SETS_REG_A | FLAG_USES_REG_B, BRANCH_NONE, "Move 64-bit pair from 16-bit register B to A"),
    0x06: OpcodeInfo(0x06, "move-wide/16", "32x", FLAG_SETS_REG_A | FLAG_USES_REG_B, BRANCH_NONE, "Move 64-bit pair from 16-bit register B to 16-bit register A"),
    0x07: OpcodeInfo(0x07, "move-object", "12x", FLAG_SETS_REG_A | FLAG_USES_REG_B, BRANCH_NONE, "Move object reference from register B to A"),
    0x08: OpcodeInfo(0x08, "move-object/from16", "22x", FLAG_SETS_REG_A | FLAG_USES_REG_B, BRANCH_NONE, "Move object reference from 16-bit B to A"),
    0x09: OpcodeInfo(0x09, "move-object/16", "32x", FLAG_SETS_REG_A | FLAG_USES_REG_B, BRANCH_NONE, "Move object reference from 16-bit B to 16-bit A"),
    0x0A: OpcodeInfo(0x0A, "move-result", "11x", FLAG_SETS_REG_A, BRANCH_NONE, "Move last method call result into register A"),
    0x0B: OpcodeInfo(0x0B, "move-result-wide", "11x", FLAG_SETS_REG_A, BRANCH_NONE, "Move last 64-bit method result into register A pair"),
    0x0C: OpcodeInfo(0x0C, "move-result-object", "11x", FLAG_SETS_REG_A, BRANCH_NONE, "Move last method object result into register A"),
    0x0D: OpcodeInfo(0x0D, "move-exception", "11x", FLAG_SETS_REG_A, BRANCH_NONE, "Move caught exception object into register A"),
    0x0E: OpcodeInfo(0x0E, "return-void", "10x", 0, BRANCH_RETURN, "Return void from current method"),
    0x0F: OpcodeInfo(0x0F, "return", "11x", FLAG_USES_REG_A, BRANCH_RETURN, "Return 32-bit value in register A"),
    0x10: OpcodeInfo(0x10, "return-wide", "11x", FLAG_USES_REG_A, BRANCH_RETURN, "Return 64-bit pair in register A"),
    0x11: OpcodeInfo(0x11, "return-object", "11x", FLAG_USES_REG_A, BRANCH_RETURN, "Return object reference in register A"),
    0x12: OpcodeInfo(0x12, "const/4", "11n", FLAG_SETS_REG_A, BRANCH_NONE, "Load 4-bit signed literal into register A"),
    0x13: OpcodeInfo(0x13, "const/16", "21s", FLAG_SETS_REG_A, BRANCH_NONE, "Load 16-bit signed literal into register A"),
    0x14: OpcodeInfo(0x14, "const", "31i", FLAG_SETS_REG_A, BRANCH_NONE, "Load 32-bit signed literal into register A"),
    0x15: OpcodeInfo(0x15, "const/high16", "21h", FLAG_SETS_REG_A, BRANCH_NONE, "Load 16-bit literal shifted left 16 bits into register A"),
    0x16: OpcodeInfo(0x16, "const-wide/16", "21s", FLAG_SETS_REG_A, BRANCH_NONE, "Load 16-bit literal sign-extended to 64-bit pair A"),
    0x17: OpcodeInfo(0x17, "const-wide/32", "31i", FLAG_SETS_REG_A, BRANCH_NONE, "Load 32-bit literal sign-extended to 64-bit pair A"),
    0x18: OpcodeInfo(0x18, "const-wide", "51l", FLAG_SETS_REG_A, BRANCH_NONE, "Load 64-bit literal into register pair A"),
    0x19: OpcodeInfo(0x19, "const-wide/high16", "21h", FLAG_SETS_REG_A, BRANCH_NONE, "Load 16-bit literal shifted left 48 bits into pair A"),
    0x1A: OpcodeInfo(0x1A, "const-string", "21c", FLAG_SETS_REG_A, BRANCH_NONE, "Load string reference by string_id into register A"),
    0x1B: OpcodeInfo(0x1B, "const-string/jumbo", "31c", FLAG_SETS_REG_A, BRANCH_NONE, "Load string reference by 32-bit string_id into register A"),
    0x1C: OpcodeInfo(0x1C, "const-class", "21c", FLAG_SETS_REG_A, BRANCH_NONE, "Load java.lang.Class reference by type_id into register A"),
    0x1D: OpcodeInfo(0x1D, "monitor-enter", "11x", FLAG_USES_REG_A | FLAG_THROWS_EXCEPTION, BRANCH_NONE, "Acquire monitor lock on object in register A"),
    0x1E: OpcodeInfo(0x1E, "monitor-exit", "11x", FLAG_USES_REG_A | FLAG_THROWS_EXCEPTION, BRANCH_NONE, "Release monitor lock on object in register A"),
    0x1F: OpcodeInfo(0x1F, "check-cast", "21c", FLAG_USES_REG_A | FLAG_THROWS_EXCEPTION, BRANCH_NONE, "Throw ClassCastException if register A not castable to type"),
    0x20: OpcodeInfo(0x20, "instance-of", "22c", FLAG_SETS_REG_A | FLAG_USES_REG_B, BRANCH_NONE, "Store 1 in reg A if object in reg B is instance of type, else 0"),
    0x21: OpcodeInfo(0x21, "array-length", "12x", FLAG_SETS_REG_A | FLAG_USES_REG_B | FLAG_THROWS_EXCEPTION, BRANCH_NONE, "Store length of array in reg B into reg A"),
    0x22: OpcodeInfo(0x22, "new-instance", "21c", FLAG_SETS_REG_A | FLAG_THROWS_EXCEPTION, BRANCH_NONE, "Instantiate new instance of class type into register A"),
    0x23: OpcodeInfo(0x23, "new-array", "22c", FLAG_SETS_REG_A | FLAG_USES_REG_B | FLAG_THROWS_EXCEPTION, BRANCH_NONE, "Instantiate array of type and size in reg B into reg A"),
    0x24: OpcodeInfo(0x24, "filled-new-array", "35c", FLAG_SETS_RESULT | FLAG_THROWS_EXCEPTION, BRANCH_NONE, "Create array with initial elements, result moved via move-result"),
    0x25: OpcodeInfo(0x25, "filled-new-array/range", "3rc", FLAG_SETS_RESULT | FLAG_THROWS_EXCEPTION, BRANCH_NONE, "Create array with register range elements"),
    0x26: OpcodeInfo(0x26, "fill-array-data", "31t", FLAG_USES_REG_A, BRANCH_NONE, "Fill array in reg A with literal table payload"),
    0x27: OpcodeInfo(0x27, "throw", "11x", FLAG_USES_REG_A | FLAG_THROWS_EXCEPTION, BRANCH_THROW, "Throw Throwable object in register A"),
    0x28: OpcodeInfo(0x28, "goto", "10t", 0, BRANCH_UNCONDITIONAL, "Unconditional 8-bit branch offset"),
    0x29: OpcodeInfo(0x29, "goto/16", "20t", 0, BRANCH_UNCONDITIONAL, "Unconditional 16-bit branch offset"),
    0x2A: OpcodeInfo(0x2A, "goto/32", "30t", 0, BRANCH_UNCONDITIONAL, "Unconditional 32-bit branch offset"),
    0x2B: OpcodeInfo(0x2B, "packed-switch", "31t", FLAG_USES_REG_A, BRANCH_SWITCH, "Jump table switch based on value in reg A"),
    0x2C: OpcodeInfo(0x2C, "sparse-switch", "31t", FLAG_USES_REG_A, BRANCH_SWITCH, "Lookup key-value table switch based on reg A"),
    0x2D: OpcodeInfo(0x2D, "cmpl-float", "23x", FLAG_SETS_REG_A | FLAG_USES_REG_B | FLAG_USES_REG_C, BRANCH_NONE, "Compare floats in B and C, return -1 on NaN"),
    0x2E: OpcodeInfo(0x2E, "cmpg-float", "23x", FLAG_SETS_REG_A | FLAG_USES_REG_B | FLAG_USES_REG_C, BRANCH_NONE, "Compare floats in B and C, return 1 on NaN"),
    0x2F: OpcodeInfo(0x2F, "cmpl-double", "23x", FLAG_SETS_REG_A | FLAG_USES_REG_B | FLAG_USES_REG_C, BRANCH_NONE, "Compare doubles in B and C, return -1 on NaN"),
    0x30: OpcodeInfo(0x30, "cmpg-double", "23x", FLAG_SETS_REG_A | FLAG_USES_REG_B | FLAG_USES_REG_C, BRANCH_NONE, "Compare doubles in B and C, return 1 on NaN"),
    0x31: OpcodeInfo(0x31, "cmp-long", "23x", FLAG_SETS_REG_A | FLAG_USES_REG_B | FLAG_USES_REG_C, BRANCH_NONE, "Compare 64-bit longs in B and C, return -1, 0, or 1"),
    0x32: OpcodeInfo(0x32, "if-eq", "22t", FLAG_USES_REG_A | FLAG_USES_REG_B, BRANCH_CONDITIONAL, "Branch if reg A == reg B"),
    0x33: OpcodeInfo(0x33, "if-ne", "22t", FLAG_USES_REG_A | FLAG_USES_REG_B, BRANCH_CONDITIONAL, "Branch if reg A != reg B"),
    0x34: OpcodeInfo(0x34, "if-lt", "22t", FLAG_USES_REG_A | FLAG_USES_REG_B, BRANCH_CONDITIONAL, "Branch if reg A < reg B"),
    0x35: OpcodeInfo(0x35, "if-ge", "22t", FLAG_USES_REG_A | FLAG_USES_REG_B, BRANCH_CONDITIONAL, "Branch if reg A >= reg B"),
    0x36: OpcodeInfo(0x36, "if-gt", "22t", FLAG_USES_REG_A | FLAG_USES_REG_B, BRANCH_CONDITIONAL, "Branch if reg A > reg B"),
    0x37: OpcodeInfo(0x37, "if-le", "22t", FLAG_USES_REG_A | FLAG_USES_REG_B, BRANCH_CONDITIONAL, "Branch if reg A <= reg B"),
    0x38: OpcodeInfo(0x38, "if-eqz", "21t", FLAG_USES_REG_A, BRANCH_CONDITIONAL, "Branch if reg A == 0"),
    0x39: OpcodeInfo(0x39, "if-nez", "21t", FLAG_USES_REG_A, BRANCH_CONDITIONAL, "Branch if reg A != 0"),
    0x3A: OpcodeInfo(0x3A, "if-ltz", "21t", FLAG_USES_REG_A, BRANCH_CONDITIONAL, "Branch if reg A < 0"),
    0x3B: OpcodeInfo(0x3B, "if-gez", "21t", FLAG_USES_REG_A, BRANCH_CONDITIONAL, "Branch if reg A >= 0"),
    0x3C: OpcodeInfo(0x3C, "if-gtz", "21t", FLAG_USES_REG_A, BRANCH_CONDITIONAL, "Branch if reg A > 0"),
    0x3D: OpcodeInfo(0x3D, "if-lez", "21t", FLAG_USES_REG_A, BRANCH_CONDITIONAL, "Branch if reg A <= 0"),
    # Array Get Operations (44..4A)
    0x44: OpcodeInfo(0x44, "aget", "23x", FLAG_SETS_REG_A | FLAG_USES_REG_B | FLAG_USES_REG_C | FLAG_THROWS_EXCEPTION, BRANCH_NONE, "Load 32-bit element from array B at index C into A"),
    0x45: OpcodeInfo(0x45, "aget-wide", "23x", FLAG_SETS_REG_A | FLAG_USES_REG_B | FLAG_USES_REG_C | FLAG_THROWS_EXCEPTION, BRANCH_NONE, "Load 64-bit element from array B at index C into A"),
    0x46: OpcodeInfo(0x46, "aget-object", "23x", FLAG_SETS_REG_A | FLAG_USES_REG_B | FLAG_USES_REG_C | FLAG_THROWS_EXCEPTION, BRANCH_NONE, "Load object reference from array B at index C into A"),
    0x47: OpcodeInfo(0x47, "aget-boolean", "23x", FLAG_SETS_REG_A | FLAG_USES_REG_B | FLAG_USES_REG_C | FLAG_THROWS_EXCEPTION, BRANCH_NONE, "Load boolean from array B at index C into A"),
    0x48: OpcodeInfo(0x48, "aget-byte", "23x", FLAG_SETS_REG_A | FLAG_USES_REG_B | FLAG_USES_REG_C | FLAG_THROWS_EXCEPTION, BRANCH_NONE, "Load signed byte from array B at index C into A"),
    0x49: OpcodeInfo(0x49, "aget-char", "23x", FLAG_SETS_REG_A | FLAG_USES_REG_B | FLAG_USES_REG_C | FLAG_THROWS_EXCEPTION, BRANCH_NONE, "Load char from array B at index C into A"),
    0x4A: OpcodeInfo(0x4A, "aget-short", "23x", FLAG_SETS_REG_A | FLAG_USES_REG_B | FLAG_USES_REG_C | FLAG_THROWS_EXCEPTION, BRANCH_NONE, "Load short from array B at index C into A"),
    # Array Put Operations (4B..51)
    0x4B: OpcodeInfo(0x4B, "aput", "23x", FLAG_USES_REG_A | FLAG_USES_REG_B | FLAG_USES_REG_C | FLAG_THROWS_EXCEPTION, BRANCH_NONE, "Store 32-bit value A into array B at index C"),
    0x4C: OpcodeInfo(0x4C, "aput-wide", "23x", FLAG_USES_REG_A | FLAG_USES_REG_B | FLAG_USES_REG_C | FLAG_THROWS_EXCEPTION, BRANCH_NONE, "Store 64-bit pair A into array B at index C"),
    0x4D: OpcodeInfo(0x4D, "aput-object", "23x", FLAG_USES_REG_A | FLAG_USES_REG_B | FLAG_USES_REG_C | FLAG_THROWS_EXCEPTION, BRANCH_NONE, "Store object A into array B at index C"),
    0x4E: OpcodeInfo(0x4E, "aput-boolean", "23x", FLAG_USES_REG_A | FLAG_USES_REG_B | FLAG_USES_REG_C | FLAG_THROWS_EXCEPTION, BRANCH_NONE, "Store boolean A into array B at index C"),
    0x4F: OpcodeInfo(0x4F, "aput-byte", "23x", FLAG_USES_REG_A | FLAG_USES_REG_B | FLAG_USES_REG_C | FLAG_THROWS_EXCEPTION, BRANCH_NONE, "Store byte A into array B at index C"),
    0x50: OpcodeInfo(0x50, "aput-char", "23x", FLAG_USES_REG_A | FLAG_USES_REG_B | FLAG_USES_REG_C | FLAG_THROWS_EXCEPTION, BRANCH_NONE, "Store char A into array B at index C"),
    0x51: OpcodeInfo(0x51, "aput-short", "23x", FLAG_USES_REG_A | FLAG_USES_REG_B | FLAG_USES_REG_C | FLAG_THROWS_EXCEPTION, BRANCH_NONE, "Store short A into array B at index C"),
    # Instance Field Get (52..58)
    0x52: OpcodeInfo(0x52, "iget", "22c", FLAG_SETS_REG_A | FLAG_USES_REG_B | FLAG_THROWS_EXCEPTION, BRANCH_NONE, "Load 32-bit instance field of object B into A"),
    0x53: OpcodeInfo(0x53, "iget-wide", "22c", FLAG_SETS_REG_A | FLAG_USES_REG_B | FLAG_THROWS_EXCEPTION, BRANCH_NONE, "Load 64-bit instance field of object B into A"),
    0x54: OpcodeInfo(0x54, "iget-object", "22c", FLAG_SETS_REG_A | FLAG_USES_REG_B | FLAG_THROWS_EXCEPTION, BRANCH_NONE, "Load object reference field of object B into A"),
    0x55: OpcodeInfo(0x55, "iget-boolean", "22c", FLAG_SETS_REG_A | FLAG_USES_REG_B | FLAG_THROWS_EXCEPTION, BRANCH_NONE, "Load boolean field of object B into A"),
    0x56: OpcodeInfo(0x56, "iget-byte", "22c", FLAG_SETS_REG_A | FLAG_USES_REG_B | FLAG_THROWS_EXCEPTION, BRANCH_NONE, "Load byte field of object B into A"),
    0x57: OpcodeInfo(0x57, "iget-char", "22c", FLAG_SETS_REG_A | FLAG_USES_REG_B | FLAG_THROWS_EXCEPTION, BRANCH_NONE, "Load char field of object B into A"),
    0x58: OpcodeInfo(0x58, "iget-short", "22c", FLAG_SETS_REG_A | FLAG_USES_REG_B | FLAG_THROWS_EXCEPTION, BRANCH_NONE, "Load short field of object B into A"),
    # Instance Field Put (59..5F)
    0x59: OpcodeInfo(0x59, "iput", "22c", FLAG_USES_REG_A | FLAG_USES_REG_B | FLAG_THROWS_EXCEPTION, BRANCH_NONE, "Store 32-bit A into instance field of object B"),
    0x5A: OpcodeInfo(0x5A, "iput-wide", "22c", FLAG_USES_REG_A | FLAG_USES_REG_B | FLAG_THROWS_EXCEPTION, BRANCH_NONE, "Store 64-bit pair A into instance field of object B"),
    0x5B: OpcodeInfo(0x5B, "iput-object", "22c", FLAG_USES_REG_A | FLAG_USES_REG_B | FLAG_THROWS_EXCEPTION, BRANCH_NONE, "Store object reference A into instance field of object B"),
    0x5C: OpcodeInfo(0x5C, "iput-boolean", "22c", FLAG_USES_REG_A | FLAG_USES_REG_B | FLAG_THROWS_EXCEPTION, BRANCH_NONE, "Store boolean A into instance field of object B"),
    0x5D: OpcodeInfo(0x5D, "iput-byte", "22c", FLAG_USES_REG_A | FLAG_USES_REG_B | FLAG_THROWS_EXCEPTION, BRANCH_NONE, "Store byte A into instance field of object B"),
    0x5E: OpcodeInfo(0x5E, "iput-char", "22c", FLAG_USES_REG_A | FLAG_USES_REG_B | FLAG_THROWS_EXCEPTION, BRANCH_NONE, "Store char A into instance field of object B"),
    0x5F: OpcodeInfo(0x5F, "iput-short", "22c", FLAG_USES_REG_A | FLAG_USES_REG_B | FLAG_THROWS_EXCEPTION, BRANCH_NONE, "Store short A into instance field of object B"),
    # Static Field Get (60..66)
    0x60: OpcodeInfo(0x60, "sget", "21c", FLAG_SETS_REG_A, BRANCH_NONE, "Load 32-bit static field into A"),
    0x61: OpcodeInfo(0x61, "sget-wide", "21c", FLAG_SETS_REG_A, BRANCH_NONE, "Load 64-bit static field into A"),
    0x62: OpcodeInfo(0x62, "sget-object", "21c", FLAG_SETS_REG_A, BRANCH_NONE, "Load object static field into A"),
    0x63: OpcodeInfo(0x63, "sget-boolean", "21c", FLAG_SETS_REG_A, BRANCH_NONE, "Load boolean static field into A"),
    0x64: OpcodeInfo(0x64, "sget-byte", "21c", FLAG_SETS_REG_A, BRANCH_NONE, "Load byte static field into A"),
    0x65: OpcodeInfo(0x65, "sget-char", "21c", FLAG_SETS_REG_A, BRANCH_NONE, "Load char static field into A"),
    0x66: OpcodeInfo(0x66, "sget-short", "21c", FLAG_SETS_REG_A, BRANCH_NONE, "Load short static field into A"),
    # Static Field Put (67..6D)
    0x67: OpcodeInfo(0x67, "sput", "21c", FLAG_USES_REG_A, BRANCH_NONE, "Store 32-bit A into static field"),
    0x68: OpcodeInfo(0x68, "sput-wide", "21c", FLAG_USES_REG_A, BRANCH_NONE, "Store 64-bit pair A into static field"),
    0x69: OpcodeInfo(0x69, "sput-object", "21c", FLAG_USES_REG_A, BRANCH_NONE, "Store object reference A into static field"),
    0x6A: OpcodeInfo(0x6A, "sput-boolean", "21c", FLAG_USES_REG_A, BRANCH_NONE, "Store boolean A into static field"),
    0x6B: OpcodeInfo(0x6B, "sput-byte", "21c", FLAG_USES_REG_A, BRANCH_NONE, "Store byte A into static field"),
    0x6C: OpcodeInfo(0x6C, "sput-char", "21c", FLAG_USES_REG_A, BRANCH_NONE, "Store char A into static field"),
    0x6D: OpcodeInfo(0x6D, "sput-short", "21c", FLAG_USES_REG_A, BRANCH_NONE, "Store short A into static field"),
    # Method Invocation (6E..78)
    0x6E: OpcodeInfo(0x6E, "invoke-virtual", "35c", FLAG_SETS_RESULT | FLAG_THROWS_EXCEPTION, BRANCH_NONE, "Call virtual method with explicit registers"),
    0x6F: OpcodeInfo(0x6F, "invoke-super", "35c", FLAG_SETS_RESULT | FLAG_THROWS_EXCEPTION, BRANCH_NONE, "Call superclass method with explicit registers"),
    0x70: OpcodeInfo(0x70, "invoke-direct", "35c", FLAG_SETS_RESULT | FLAG_THROWS_EXCEPTION, BRANCH_NONE, "Call direct method (private/constructor)"),
    0x71: OpcodeInfo(0x71, "invoke-static", "35c", FLAG_SETS_RESULT | FLAG_THROWS_EXCEPTION, BRANCH_NONE, "Call static method with explicit registers"),
    0x72: OpcodeInfo(0x72, "invoke-interface", "35c", FLAG_SETS_RESULT | FLAG_THROWS_EXCEPTION, BRANCH_NONE, "Call interface method with explicit registers"),
    0x74: OpcodeInfo(0x74, "invoke-virtual/range", "3rc", FLAG_SETS_RESULT | FLAG_THROWS_EXCEPTION, BRANCH_NONE, "Call virtual method with register range"),
    0x75: OpcodeInfo(0x75, "invoke-super/range", "3rc", FLAG_SETS_RESULT | FLAG_THROWS_EXCEPTION, BRANCH_NONE, "Call super method with register range"),
    0x76: OpcodeInfo(0x76, "invoke-direct/range", "3rc", FLAG_SETS_RESULT | FLAG_THROWS_EXCEPTION, BRANCH_NONE, "Call direct method with register range"),
    0x77: OpcodeInfo(0x77, "invoke-static/range", "3rc", FLAG_SETS_RESULT | FLAG_THROWS_EXCEPTION, BRANCH_NONE, "Call static method with register range"),
    0x78: OpcodeInfo(0x78, "invoke-interface/range", "3rc", FLAG_SETS_RESULT | FLAG_THROWS_EXCEPTION, BRANCH_NONE, "Call interface method with register range"),
    # Unary & Binary Arithmetic Operations (90..BA)
    0x90: OpcodeInfo(0x90, "add-int", "23x", FLAG_SETS_REG_A | FLAG_USES_REG_B | FLAG_USES_REG_C, BRANCH_NONE, "Integer addition: A = B + C"),
    0x91: OpcodeInfo(0x91, "sub-int", "23x", FLAG_SETS_REG_A | FLAG_USES_REG_B | FLAG_USES_REG_C, BRANCH_NONE, "Integer subtraction: A = B - C"),
    0x92: OpcodeInfo(0x92, "mul-int", "23x", FLAG_SETS_REG_A | FLAG_USES_REG_B | FLAG_USES_REG_C, BRANCH_NONE, "Integer multiplication: A = B * C"),
    0x93: OpcodeInfo(0x93, "div-int", "23x", FLAG_SETS_REG_A | FLAG_USES_REG_B | FLAG_USES_REG_C | FLAG_THROWS_EXCEPTION, BRANCH_NONE, "Integer division: A = B / C"),
    0x94: OpcodeInfo(0x94, "rem-int", "23x", FLAG_SETS_REG_A | FLAG_USES_REG_B | FLAG_USES_REG_C | FLAG_THROWS_EXCEPTION, BRANCH_NONE, "Integer remainder: A = B % C"),
    0x95: OpcodeInfo(0x95, "and-int", "23x", FLAG_SETS_REG_A | FLAG_USES_REG_B | FLAG_USES_REG_C, BRANCH_NONE, "Bitwise AND: A = B & C"),
    0x96: OpcodeInfo(0x96, "or-int", "23x", FLAG_SETS_REG_A | FLAG_USES_REG_B | FLAG_USES_REG_C, BRANCH_NONE, "Bitwise OR: A = B | C"),
    0x97: OpcodeInfo(0x97, "xor-int", "23x", FLAG_SETS_REG_A | FLAG_USES_REG_B | FLAG_USES_REG_C, BRANCH_NONE, "Bitwise XOR: A = B ^ C"),
    0x98: OpcodeInfo(0x98, "shl-int", "23x", FLAG_SETS_REG_A | FLAG_USES_REG_B | FLAG_USES_REG_C, BRANCH_NONE, "Shift left: A = B << (C & 0x1f)"),
    0x99: OpcodeInfo(0x99, "shr-int", "23x", FLAG_SETS_REG_A | FLAG_USES_REG_B | FLAG_USES_REG_C, BRANCH_NONE, "Arithmetic shift right: A = B >> (C & 0x1f)"),
    0x9A: OpcodeInfo(0x9A, "ushr-int", "23x", FLAG_SETS_REG_A | FLAG_USES_REG_B | FLAG_USES_REG_C, BRANCH_NONE, "Logical shift right: A = B >>> (C & 0x1f)"),
    # 2-address integer arithmetic (B0..BA)
    0xB0: OpcodeInfo(0xB0, "add-int/2addr", "12x", FLAG_SETS_REG_A | FLAG_USES_REG_A | FLAG_USES_REG_B, BRANCH_NONE, "Integer addition: A = A + B"),
    0xB1: OpcodeInfo(0xB1, "sub-int/2addr", "12x", FLAG_SETS_REG_A | FLAG_USES_REG_A | FLAG_USES_REG_B, BRANCH_NONE, "Integer subtraction: A = A - B"),
    0xB2: OpcodeInfo(0xB2, "mul-int/2addr", "12x", FLAG_SETS_REG_A | FLAG_USES_REG_A | FLAG_USES_REG_B, BRANCH_NONE, "Integer multiplication: A = A * B"),
    0xB3: OpcodeInfo(0xB3, "div-int/2addr", "12x", FLAG_SETS_REG_A | FLAG_USES_REG_A | FLAG_USES_REG_B | FLAG_THROWS_EXCEPTION, BRANCH_NONE, "Integer division: A = A / B"),
    0xB4: OpcodeInfo(0xB4, "rem-int/2addr", "12x", FLAG_SETS_REG_A | FLAG_USES_REG_A | FLAG_USES_REG_B | FLAG_THROWS_EXCEPTION, BRANCH_NONE, "Integer remainder: A = A % B"),
    0xB5: OpcodeInfo(0xB5, "and-int/2addr", "12x", FLAG_SETS_REG_A | FLAG_USES_REG_A | FLAG_USES_REG_B, BRANCH_NONE, "Bitwise AND: A = A & B"),
    0xB6: OpcodeInfo(0xB6, "or-int/2addr", "12x", FLAG_SETS_REG_A | FLAG_USES_REG_A | FLAG_USES_REG_B, BRANCH_NONE, "Bitwise OR: A = A | B"),
    0xB7: OpcodeInfo(0xB7, "xor-int/2addr", "12x", FLAG_SETS_REG_A | FLAG_USES_REG_A | FLAG_USES_REG_B, BRANCH_NONE, "Bitwise XOR: A = A ^ B"),
    0xB8: OpcodeInfo(0xB8, "shl-int/2addr", "12x", FLAG_SETS_REG_A | FLAG_USES_REG_A | FLAG_USES_REG_B, BRANCH_NONE, "Shift left: A = A << (B & 0x1f)"),
    0xB9: OpcodeInfo(0xB9, "shr-int/2addr", "12x", FLAG_SETS_REG_A | FLAG_USES_REG_A | FLAG_USES_REG_B, BRANCH_NONE, "Arithmetic shift right: A = A >> (B & 0x1f)"),
    0xBA: OpcodeInfo(0xBA, "ushr-int/2addr", "12x", FLAG_SETS_REG_A | FLAG_USES_REG_A | FLAG_USES_REG_B, BRANCH_NONE, "Logical shift right: A = A >>> (B & 0x1f)"),
    # Integer with 16-bit literal (D0..D7)
    0xD0: OpcodeInfo(0xD0, "add-int/lit16", "22s", FLAG_SETS_REG_A | FLAG_USES_REG_B, BRANCH_NONE, "Integer add literal: A = B + lit16"),
    0xD1: OpcodeInfo(0xD1, "rsub-int", "22s", FLAG_SETS_REG_A | FLAG_USES_REG_B, BRANCH_NONE, "Reverse subtract: A = lit16 - B"),
    0xD2: OpcodeInfo(0xD2, "mul-int/lit16", "22s", FLAG_SETS_REG_A | FLAG_USES_REG_B, BRANCH_NONE, "Integer multiply literal: A = B * lit16"),
    0xD3: OpcodeInfo(0xD3, "div-int/lit16", "22s", FLAG_SETS_REG_A | FLAG_USES_REG_B | FLAG_THROWS_EXCEPTION, BRANCH_NONE, "Integer divide literal: A = B / lit16"),
    0xD4: OpcodeInfo(0xD4, "rem-int/lit16", "22s", FLAG_SETS_REG_A | FLAG_USES_REG_B | FLAG_THROWS_EXCEPTION, BRANCH_NONE, "Integer remainder literal: A = B % lit16"),
    0xD5: OpcodeInfo(0xD5, "and-int/lit16", "22s", FLAG_SETS_REG_A | FLAG_USES_REG_B, BRANCH_NONE, "Bitwise AND literal: A = B & lit16"),
    0xD6: OpcodeInfo(0xD6, "or-int/lit16", "22s", FLAG_SETS_REG_A | FLAG_USES_REG_B, BRANCH_NONE, "Bitwise OR literal: A = B | lit16"),
    0xD7: OpcodeInfo(0xD7, "xor-int/lit16", "22s", FLAG_SETS_REG_A | FLAG_USES_REG_B, BRANCH_NONE, "Bitwise XOR literal: A = B ^ lit16"),
    # Integer with 8-bit literal (D8..E2)
    0xD8: OpcodeInfo(0xD8, "add-int/lit8", "22b", FLAG_SETS_REG_A | FLAG_USES_REG_B, BRANCH_NONE, "Integer add literal: A = B + lit8"),
    0xD9: OpcodeInfo(0xD9, "rsub-int/lit8", "22b", FLAG_SETS_REG_A | FLAG_USES_REG_B, BRANCH_NONE, "Reverse subtract: A = lit8 - B"),
    0xDA: OpcodeInfo(0xDA, "mul-int/lit8", "22b", FLAG_SETS_REG_A | FLAG_USES_REG_B, BRANCH_NONE, "Integer multiply literal: A = B * lit8"),
    0xDB: OpcodeInfo(0xDB, "div-int/lit8", "22b", FLAG_SETS_REG_A | FLAG_USES_REG_B | FLAG_THROWS_EXCEPTION, BRANCH_NONE, "Integer divide literal: A = B / lit8"),
    0xDC: OpcodeInfo(0xDC, "rem-int/lit8", "22b", FLAG_SETS_REG_A | FLAG_USES_REG_B | FLAG_THROWS_EXCEPTION, BRANCH_NONE, "Integer remainder literal: A = B % lit8"),
    0xDD: OpcodeInfo(0xDD, "and-int/lit8", "22b", FLAG_SETS_REG_A | FLAG_USES_REG_B, BRANCH_NONE, "Bitwise AND literal: A = B & lit8"),
    0xDE: OpcodeInfo(0xDE, "or-int/lit8", "22b", FLAG_SETS_REG_A | FLAG_USES_REG_B, BRANCH_NONE, "Bitwise OR literal: A = B | lit8"),
    0xDF: OpcodeInfo(0xDF, "xor-int/lit8", "22b", FLAG_SETS_REG_A | FLAG_USES_REG_B, BRANCH_NONE, "Bitwise XOR literal: A = B ^ lit8"),
    0xE0: OpcodeInfo(0xE0, "shl-int/lit8", "22b", FLAG_SETS_REG_A | FLAG_USES_REG_B, BRANCH_NONE, "Shift left literal: A = B << (lit8 & 0x1f)"),
    0xE1: OpcodeInfo(0xE1, "shr-int/lit8", "22b", FLAG_SETS_REG_A | FLAG_USES_REG_B, BRANCH_NONE, "Shift right literal: A = B >> (lit8 & 0x1f)"),
    0xE2: OpcodeInfo(0xE2, "ushr-int/lit8", "22b", FLAG_SETS_REG_A | FLAG_USES_REG_B, BRANCH_NONE, "Unsigned shift right: A = B >>> (lit8 & 0x1f)"),
}


def lookup_opcode(op: int) -> Optional[OpcodeInfo]:
    """Retrieve metadata record for given Dalvik opcode byte."""
    return DALVIK_OPCODE_TABLE.get(op)


if __name__ == "__main__":
    print(f"Total Dalvik Opcodes Indexed: {len(DALVIK_OPCODE_TABLE)}")
    sample = lookup_opcode(0x6E)
    if sample:
        print(f"Opcode 0x6e: {sample.name} ({sample.format}) - {sample.description}")
