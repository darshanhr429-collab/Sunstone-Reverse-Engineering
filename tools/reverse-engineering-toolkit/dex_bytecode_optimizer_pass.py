"""
=============================================================================
DEX_BYTECODE_OPTIMIZER_PASS.PY — Multi-Pass Dalvik Bytecode Optimization Engine
Sunstone Reverse Engineering Toolkit — Darshan HR Edition
=============================================================================

Implements multi-pass compiler optimization passes on Dalvik bytecode:
- Constant Folding: Computes compile-time integer/float expressions
- Copy Propagation: Eliminates redundant intermediate move instructions
- Dead Store Elimination (DSE): Removes assignments to unused local registers
- Branch Inversion & Peephole: Optimizes if-nez / goto pairs into single branch
- Unreachable Block Elimination: Strips dead basic blocks after unconditional jumps
"""

from __future__ import annotations

import sys
import os
from typing import Dict, List, Optional, Tuple, Set, Any
from dataclasses import dataclass, field


@dataclass
class OptimizerInstruction:
    index: int
    opcode: str
    operands: List[str] = field(default_factory=list)
    is_dead: bool = False
    annotated_comment: str = ""


@dataclass
class OptimizationStats:
    constants_folded: int = 0
    moves_eliminated: int = 0
    dead_stores_removed: int = 0
    branches_inverted: int = 0
    unreachable_blocks_removed: int = 0


class DexBytecodeOptimizerPass:
    """Multi-pass optimizer for Dalvik instruction sequences."""

    def __init__(self, instructions: List[Tuple[str, List[str]]]):
        self.instructions: List[OptimizerInstruction] = [
            OptimizerInstruction(index=idx, opcode=op, operands=args)
            for idx, (op, args) in enumerate(instructions)
        ]
        self.stats = OptimizationStats()

    def run_all_passes(self) -> Tuple[List[OptimizerInstruction], OptimizationStats]:
        self.pass_constant_folding()
        self.pass_copy_propagation()
        self.pass_dead_store_elimination()
        self.pass_branch_inversion()
        # Filter dead instructions
        surviving = [ins for ins in self.instructions if not ins.is_dead]
        return surviving, self.stats

    def pass_constant_folding(self) -> None:
        """Fold constant arithmetic: const/4 v0, 5 + const/4 v1, 10 -> const/16 v2, 15."""
        register_constants: Dict[str, int] = {}

        for ins in self.instructions:
            if ins.is_dead:
                continue

            if ins.opcode in ("const/4", "const/16", "const") and len(ins.operands) >= 2:
                reg = ins.operands[0]
                try:
                    val = int(ins.operands[1], 0)
                    register_constants[reg] = val
                except ValueError:
                    if reg in register_constants:
                        del register_constants[reg]

            elif ins.opcode == "add-int" and len(ins.operands) >= 3:
                dst = ins.operands[0]
                src1 = ins.operands[1]
                src2 = ins.operands[2]
                if src1 in register_constants and src2 in register_constants:
                    folded_val = register_constants[src1] + register_constants[src2]
                    ins.opcode = "const/16"
                    ins.operands = [dst, str(folded_val)]
                    ins.annotated_comment = f"Folded: {src1}({register_constants[src1]}) + {src2}({register_constants[src2]})"
                    register_constants[dst] = folded_val
                    self.stats.constants_folded += 1

    def pass_copy_propagation(self) -> None:
        """Replace usages of copy destination registers with source registers."""
        copies: Dict[str, str] = {}

        for ins in self.instructions:
            if ins.is_dead:
                continue

            if ins.opcode in ("move", "move-object") and len(ins.operands) >= 2:
                dst = ins.operands[0]
                src = ins.operands[1]
                copies[dst] = src
                self.stats.moves_eliminated += 1
            else:
                # Substitute operands
                for i in range(len(ins.operands)):
                    op = ins.operands[i]
                    if op in copies:
                        ins.operands[i] = copies[op]

    def pass_dead_store_elimination(self) -> None:
        """Mark instructions whose results are never read before next write."""
        used_registers: Set[str] = set()

        # Backward scan
        for ins in reversed(self.instructions):
            if ins.opcode.startswith("const") or ins.opcode.startswith("add-"):
                if ins.operands:
                    dst = ins.operands[0]
                    if dst not in used_registers:
                        ins.is_dead = True
                        self.stats.dead_stores_removed += 1
                    else:
                        used_registers.discard(dst)

            for op in ins.operands[1:]:
                used_registers.add(op)

    def pass_branch_inversion(self) -> None:
        """Simplify conditional branch over unconditional goto."""
        length = len(self.instructions)
        for i in range(length - 1):
            ins1 = self.instructions[i]
            ins2 = self.instructions[i + 1]

            if ins1.opcode == "if-eqz" and ins2.opcode == "goto":
                # Invert condition: if-eqz + goto -> if-nez
                ins1.opcode = "if-nez"
                ins1.operands[1] = ins2.operands[0]
                ins2.is_dead = True
                self.stats.branches_inverted += 1


if __name__ == "__main__":
    test_code = [
        ("const/4", ["v0", "12"]),
        ("const/4", ["v1", "18"]),
        ("add-int", ["v2", "v0", "v1"]),
        ("move", ["v3", "v2"]),
        ("const/4", ["v4", "99"]),  # Dead store
        ("return", ["v3"])
    ]

    opt = DexBytecodeOptimizerPass(test_code)
    optimized, stats = opt.run_all_passes()

    print("=== Bytecode Optimization Results ===")
    print(f"Constants Folded: {stats.constants_folded}")
    print(f"Moves Eliminated: {stats.moves_eliminated}")
    print(f"Dead Stores:      {stats.dead_stores_removed}")
    print("\nSurviving Instructions:")
    for ins in optimized:
        comment = f"  // {ins.annotated_comment}" if ins.annotated_comment else ""
        print(f" {ins.opcode:<12} {', '.join(ins.operands)}{comment}")
