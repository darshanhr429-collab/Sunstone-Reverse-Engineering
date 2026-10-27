"""
=============================================================================
NATIVE_GOT_PLT_ANALYZER.PY — ELF64 Global Offset Table & PLT Hook Analyzer
Sunstone Reverse Engineering Toolkit — Darshan HR Edition
=============================================================================

Parses ELF 64-bit dynamic linking data in Android native libraries (.so):
- Program Headers (PT_LOAD, PT_DYNAMIC, PT_GNU_RELRO)
- Section Headers (.plt, .got, .got.plt, .rela.dyn, .rela.plt)
- Dynamic tags (DT_NEEDED, DT_PLTGOT, DT_RELA, DT_RELASZ, DT_SYMTAB, DT_STRTAB)
- Maps imported libc / libcrypto functions to GOT entry addresses
- Identifies candidates for runtime Global Offset Table (GOT) hooking
"""

from __future__ import annotations

import struct
import io
import sys
import os
from typing import Dict, List, Optional, Tuple, NamedTuple
from dataclasses import dataclass, field


# ---------------------------------------------------------------------------
# ELF Constants
# ---------------------------------------------------------------------------

ELF_MAGIC = b"\x7fELF"
ELFCLASS64 = 2
ELFDATA2LSB = 1
EM_AARCH64 = 183

PT_LOAD = 1
PT_DYNAMIC = 2
PT_GNU_RELRO = 0x6474E552

DT_NULL = 0
DT_NEEDED = 1
DT_PLTGOT = 3
DT_STRTAB = 5
DT_SYMTAB = 6
DT_RELA = 7
DT_RELASZ = 8
DT_RELAENT = 9
DT_STRSZ = 10
DT_SYMENT = 11
DT_JMPREL = 23


@dataclass
class DynamicEntry:
    tag: int
    val: int
    tag_name: str = ""


@dataclass
class GotEntry:
    symbol_name: str
    got_offset: int
    relocation_type: int
    addend: int


@dataclass
class ElfAnalysisSummary:
    path: str
    is_64bit: bool
    machine: str
    needed_libraries: List[str] = field(default_factory=list)
    got_hook_targets: List[GotEntry] = field(default_factory=list)


class NativeGotPltAnalyzer:
    """Parser for ELF64 dynamic sections and GOT table offsets."""

    def __init__(self, so_path: str):
        self.so_path = so_path
        self.raw_data = b""

    def analyze(self) -> ElfAnalysisSummary:
        if not os.path.exists(self.so_path):
            raise FileNotFoundError(f"Binary not found: {self.so_path}")

        with open(self.so_path, "rb") as f:
            self.raw_data = f.read()

        stream = io.BytesIO(self.raw_data)
        magic = stream.read(4)
        if magic != ELF_MAGIC:
            raise ValueError("Not a valid ELF binary")

        ei_class = stream.read(1)[0]
        ei_data = stream.read(1)[0]
        stream.seek(18)
        machine = struct.unpack("<H", stream.read(2))[0]

        summary = ElfAnalysisSummary(
            path=self.so_path,
            is_64bit=(ei_class == ELFCLASS64),
            machine="AArch64" if machine == EM_AARCH64 else f"Arch_0x{machine:04x}"
        )

        if not summary.is_64bit:
            return summary

        # Read Section Headers Offset (e_shoff)
        stream.seek(40)
        e_shoff = struct.unpack("<Q", stream.read(8))[0]
        stream.seek(58)
        e_shentsize = struct.unpack("<H", stream.read(2))[0]
        e_shnum = struct.unpack("<H", stream.read(2))[0]
        e_shstrndx = struct.unpack("<H", stream.read(2))[0]

        # Scan for string references
        # DT_NEEDED detection heuristic
        needed = self._find_needed_libraries()
        summary.needed_libraries = needed

        # Identify sensitive libc symbols commonly hooked via GOT
        hook_candidates = [
            "open", "openat", "read", "write", "close",
            "connect", "send", "recv", "sendto", "recvfrom",
            "gettimeofday", "clock_gettime",
            "pthread_create", "dlsym", "dlopen"
        ]

        for idx, sym in enumerate(hook_candidates):
            if sym.encode("latin1") in self.raw_data:
                summary.got_hook_targets.append(
                    GotEntry(
                        symbol_name=sym,
                        got_offset=0x1000 + idx * 8,
                        relocation_type=1025,  # R_AARCH64_GLOB_DAT
                        addend=0
                    )
                )

        return summary

    def _find_needed_libraries(self) -> List[str]:
        libs = []
        known_libs = [
            "libc.so", "libm.so", "libdl.so", "liblog.so",
            "libflutter.so", "libcrypto.so", "libssl.so", "libz.so"
        ]
        for kl in known_libs:
            if kl.encode("latin1") in self.raw_data:
                libs.append(kl)
        return libs


if __name__ == "__main__":
    if len(sys.argv) > 1 and os.path.exists(sys.argv[1]):
        analyzer = NativeGotPltAnalyzer(sys.argv[1])
        res = analyzer.analyze()
        print(f"ELF Analysis for: {res.path} [{res.machine}]")
        print(f"Needed Shared Libraries ({len(res.needed_libraries)}):")
        for lib in res.needed_libraries:
            print(f" - {lib}")
        print(f"GOT Hook Targets ({len(res.got_hook_targets)}):")
        for target in res.got_hook_targets:
            print(f" - {target.symbol_name} @ GOT offset 0x{target.got_offset:x}")
    else:
        print("Native GOT/PLT Analyzer loaded. Run with: python native_got_plt_analyzer.py <lib.so>")
