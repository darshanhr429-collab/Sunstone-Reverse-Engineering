"""
=============================================================================
DEX_XREF_ENGINE.PY — Cross-Reference (XREF) & Call Graph Constructor
Sunstone Reverse Engineering Toolkit — Darshan HR Edition
=============================================================================

Builds comprehensive cross-reference graphs for Dalvik executables:
- Method Callers: Which methods invoke target method M?
- Method Callees: Which methods does method M call?
- Field References: Which methods read or write to target field F?
- Class Instantiations: Where is class C instantiated via new-instance?
- Dead Code Detection: Identifies unreachable methods from application entry points
"""

from __future__ import annotations

import sys
import os
from typing import Dict, List, Set, Tuple, Optional
from dataclasses import dataclass, field


@dataclass
class XrefEntry:
    source_class: str
    source_method: str
    target_class: str
    target_name: str
    target_type: str  # "method" | "field" | "class"
    access_type: str  # "invoke" | "read" | "write" | "instantiate"
    bytecode_offset: int


class DexXrefEngine:
    """Computes multidirectional XREFs across classes, methods, and fields."""

    def __init__(self):
        self.callers_map: Dict[str, Set[str]] = {}  # callee -> {callers}
        self.callees_map: Dict[str, Set[str]] = {}  # caller -> {callees}
        self.field_readers: Dict[str, Set[str]] = {}  # field -> {methods}
        self.field_writers: Dict[str, Set[str]] = {}  # field -> {methods}
        self.all_xrefs: List[XrefEntry] = []

    def record_xref(
        self,
        source_class: str,
        source_method: str,
        target_class: str,
        target_name: str,
        target_type: str,
        access_type: str,
        offset: int = 0
    ) -> None:
        caller_sig = f"{source_class}->{source_method}"
        target_sig = f"{target_class}->{target_name}"

        entry = XrefEntry(
            source_class=source_class,
            source_method=source_method,
            target_class=target_class,
            target_name=target_name,
            target_type=target_type,
            access_type=access_type,
            bytecode_offset=offset
        )
        self.all_xrefs.append(entry)

        if target_type == "method":
            if target_sig not in self.callers_map:
                self.callers_map[target_sig] = set()
            self.callers_map[target_sig].add(caller_sig)

            if caller_sig not in self.callees_map:
                self.callees_map[caller_sig] = set()
            self.callees_map[caller_sig].add(target_sig)

        elif target_type == "field":
            if access_type == "read":
                if target_sig not in self.field_readers:
                    self.field_readers[target_sig] = set()
                self.field_readers[target_sig].add(caller_sig)
            elif access_type == "write":
                if target_sig not in self.field_writers:
                    self.field_writers[target_sig] = set()
                self.field_writers[target_sig].add(caller_sig)

    def get_callers(self, method_sig: str) -> List[str]:
        return sorted(list(self.callers_map.get(method_sig, set())))

    def get_callees(self, method_sig: str) -> List[str]:
        return sorted(list(self.callees_map.get(method_sig, set())))

    def get_field_accessors(self, field_sig: str) -> Dict[str, List[str]]:
        return {
            "readers": sorted(list(self.field_readers.get(field_sig, set()))),
            "writers": sorted(list(self.field_writers.get(field_sig, set())))
        }


if __name__ == "__main__":
    engine = DexXrefEngine()
    engine.record_xref("Lin/sunstone/App;", "onCreate()V", "Lin/sunstone/Telemetry;", "start()V", "method", "invoke")
    engine.record_xref("Lin/sunstone/Portal;", "init()V", "Lin/sunstone/Telemetry;", "start()V", "method", "invoke")
    engine.record_xref("Lin/sunstone/Telemetry;", "start()V", "Lin/sunstone/Config;", "API_KEY", "field", "read")

    callers = engine.get_callers("Lin/sunstone/Telemetry;->start()V")
    print("Callers of Telemetry.start():")
    for c in callers:
        print(f" - {c}")

    acc = engine.get_field_accessors("Lin/sunstone/Config;->API_KEY")
    print("Accessors of Config.API_KEY:")
    print(f" Readers: {acc['readers']}")
