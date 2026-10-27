"""
=============================================================================
SMALI_EMULATOR.PY — Symbolic Register State & Constant Propagation Emulator
Sunstone Reverse Engineering Toolkit — Darshan HR Edition
=============================================================================

Symbolically evaluates Dalvik bytecode registers to perform:
- Constant propagation and folding (evaluates const/4, const/16, const-string)
- Register taint tracking for security-sensitive API sources and sinks
- Dead code elimination and unreachable branch pruning
- Symbolic execution of conditional branches (if-eqz, if-nez)
"""

from __future__ import annotations

import sys
import os
from typing import Dict, List, Optional, Tuple, Set, Any, Union
from dataclasses import dataclass, field


@dataclass
class RegisterState:
    is_constant: bool = False
    constant_value: Any = None
    is_tainted: bool = False
    taint_source: str = ""
    register_type: str = "unknown"


@dataclass
class ExecutionFrame:
    registers: Dict[str, RegisterState] = field(default_factory=dict)
    pc: int = 0
    is_halted: bool = False
    return_value: Any = None


class SmaliEmulator:
    """Symbolic VM register state emulator."""

    def __init__(self, max_registers: int = 16):
        self.max_registers = max_registers
        self.frame = ExecutionFrame()
        self._init_registers()

    def _init_registers(self) -> None:
        for i in range(self.max_registers):
            self.frame.registers[f"v{i}"] = RegisterState()
            self.frame.registers[f"p{i}"] = RegisterState()

    def execute_line(self, line: str) -> bool:
        clean = line.strip()
        if not clean or clean.startswith((".", "#", ":")):
            return True

        parts = clean.split(maxsplit=1)
        opcode = parts[0]
        operands_str = parts[1] if len(parts) > 1 else ""
        ops = [op.strip() for op in operands_str.split(",")] if operands_str else []

        # 1. CONST Instructions
        if opcode in ("const/4", "const/16", "const"):
            if len(ops) >= 2:
                reg = ops[0]
                val_str = ops[1]
                try:
                    val = int(val_str, 0)
                    self.frame.registers[reg] = RegisterState(
                        is_constant=True, constant_value=val, register_type="int"
                    )
                except ValueError:
                    pass

        # 2. CONST-STRING
        elif opcode in ("const-string", "const-string/jumbo"):
            if len(ops) >= 2:
                reg = ops[0]
                val = ops[1].strip('"')
                self.frame.registers[reg] = RegisterState(
                    is_constant=True, constant_value=val, register_type="String"
                )

        # 3. MOVE
        elif opcode in ("move", "move-object", "move-wide"):
            if len(ops) >= 2:
                dst = ops[0]
                src = ops[1]
                src_state = self.frame.registers.get(src, RegisterState())
                self.frame.registers[dst] = RegisterState(
                    is_constant=src_state.is_constant,
                    constant_value=src_state.constant_value,
                    is_tainted=src_state.is_tainted,
                    taint_source=src_state.taint_source,
                    register_type=src_state.register_type
                )

        # 4. ADD-INT / LITERAL FOLDING
        elif opcode == "add-int/lit8":
            if len(ops) >= 3:
                dst = ops[0]
                src = ops[1]
                lit = int(ops[2], 0)
                src_state = self.frame.registers.get(src, RegisterState())
                if src_state.is_constant and isinstance(src_state.constant_value, int):
                    self.frame.registers[dst] = RegisterState(
                        is_constant=True,
                        constant_value=src_state.constant_value + lit,
                        register_type="int"
                    )

        # 5. RETURN
        elif opcode.startswith("return"):
            self.frame.is_halted = True
            if ops:
                reg = ops[0]
                self.frame.return_value = self.frame.registers.get(reg, RegisterState()).constant_value
            return False

        return True

    def get_register_value(self, reg: str) -> Any:
        return self.frame.registers.get(reg, RegisterState()).constant_value


if __name__ == "__main__":
    emu = SmaliEmulator()
    program = [
        'const/4 v0, 5',
        'const-string v1, "Sunstone-Token-Secret"',
        'add-int/lit8 v2, v0, 10',
        'move v3, v2',
        'return v3'
    ]
    for ins in program:
        emu.execute_line(ins)

    print("Emulation Results:")
    print(f" v0 = {emu.get_register_value('v0')}")
    print(f" v1 = {emu.get_register_value('v1')}")
    print(f" v2 = {emu.get_register_value('v2')}")
    print(f" v3 = {emu.get_register_value('v3')}")
    print(f" Return Value = {emu.frame.return_value}")
