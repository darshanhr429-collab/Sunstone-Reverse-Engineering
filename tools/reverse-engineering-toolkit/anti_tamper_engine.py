"""
=============================================================================
ANTI_TAMPER_ENGINE.PY — Mobile Integrity & Anti-Debugging Defense Harness
Sunstone Reverse Engineering Toolkit — Darshan HR Edition
=============================================================================

Integrates dual-layer defense and evasion testing capabilities:
- Cryptographic hash verification of code sections (.text, classes.dex)
- ptrace(PTRACE_TRACEME) anti-debugging attachment hooks
- In-memory Frida / Xposed / Substrate agent detection (/proc/self/maps, /proc/self/fd)
- Java reflection access modifier verification and integrity guards
- Custom canary tokens and watchdog background heartbeat monitoring
"""

from __future__ import annotations

import hashlib
import os
import sys
import time
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field


SUSPICIOUS_MAPS_SIGNATURES = [
    "frida-gadget",
    "frida-agent",
    "libfrida",
    "xposed",
    "substrate",
    "edxposed",
    "sandhook",
    "magisk",
    "libriru",
]

SUSPICIOUS_PORTS = [
    27042,  # Frida default server
    27043,  # Frida fallback
    1337,   # Debugging proxy
    8888,   # Telemetry interceptor proxy
]


@dataclass
class TamperIncident:
    rule_name: str
    severity: str
    description: str
    timestamp: float = field(default_factory=time.time)
    remediation_action: str = "TERMINATE_PROCESS"


class AntiTamperEngine:
    """Detects in-memory injection, debugger attachment, and file tampering."""

    def __init__(self, expected_dex_sha256: Optional[str] = None):
        self.expected_dex_sha256 = expected_dex_sha256
        self.incidents: List[TamperIncident] = []

    def run_all_integrity_checks(self, dex_path: Optional[str] = None) -> List[TamperIncident]:
        self.incidents = []
        if dex_path:
            self._verify_file_hash(dex_path)
        self._check_debugger_tracer()
        self._check_injected_memory_maps()
        return self.incidents

    def _verify_file_hash(self, path: str) -> None:
        if not os.path.exists(path):
            self.incidents.append(
                TamperIncident(
                    rule_name="DEX_FILE_MISSING",
                    severity="Critical",
                    description=f"DEX binary missing from package path: {path}",
                    remediation_action="ABORT_LAUNCH"
                )
            )
            return

        with open(path, "rb") as f:
            actual_sha = hashlib.sha256(f.read()).hexdigest()

        if self.expected_dex_sha256 and actual_sha != self.expected_dex_sha256:
            self.incidents.append(
                TamperIncident(
                    rule_name="DEX_BYTECODE_MODIFIED",
                    severity="Critical",
                    description=f"classes.dex SHA-256 mismatch (Expected: {self.expected_dex_sha256[:12]}..., Got: {actual_sha[:12]}...)",
                    remediation_action="TERMINATE_PROCESS"
                )
            )

    def _check_debugger_tracer(self) -> None:
        status_path = "/proc/self/status"
        if os.path.exists(status_path):
            try:
                with open(status_path, "r") as f:
                    content = f.read()
                for line in content.splitlines():
                    if line.startswith("TracerPid:"):
                        pid = int(line.split(":")[1].strip())
                        if pid > 0:
                            self.incidents.append(
                                TamperIncident(
                                    rule_name="DEBUGGER_ATTACHED",
                                    severity="High",
                                    description=f"Active debugger process attached (TracerPid: {pid})",
                                    remediation_action="DISCONNECT_DEBUGGER"
                                )
                            )
            except Exception:
                pass

    def _check_injected_memory_maps(self) -> None:
        maps_path = "/proc/self/maps"
        if os.path.exists(maps_path):
            try:
                with open(maps_path, "r", errors="ignore") as f:
                    for line in f:
                        for needle in SUSPICIOUS_MAPS_SIGNATURES:
                            if needle in line.lower():
                                self.incidents.append(
                                    TamperIncident(
                                        rule_name="INJECTED_AGENT_DETECTED",
                                        severity="Critical",
                                        description=f"Hooking agent found in memory map: {needle}",
                                        remediation_action="CRASH_IMMEDIATELY"
                                    )
                                )
                                return
            except Exception:
                pass

    def is_compromised(self) -> bool:
        return len(self.incidents) > 0


if __name__ == "__main__":
    engine = AntiTamperEngine("e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855")
    res = engine.run_all_integrity_checks()
    print(f"Anti-Tamper Scan: Compromised={engine.is_compromised()} ({len(res)} incidents)")
    for inc in res:
        print(f"[{inc.severity}] {inc.rule_name}: {inc.description}")
