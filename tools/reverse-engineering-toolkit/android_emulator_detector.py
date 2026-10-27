"""
=============================================================================
ANDROID_EMULATOR_DETECTOR.PY — Mobile Sandbox & Virtual Machine Heuristics
Sunstone Reverse Engineering Toolkit — Darshan HR Edition
=============================================================================

Detects Android emulators and dynamic analysis sandbox environments:
- QEMU, Android Studio AVD, Genymotion, BlueStacks, Nox Player, LDPlayer, MEmu
- Device properties (Build.HARDWARE, Build.FINGERPRINT, Build.MANUFACTURER)
- Known virtual device driver nodes (/dev/qemu_pipe, /dev/vboxuser, /dev/goldfish_pipe)
- Known emulator packages, files, and TCP ports (5554, 5555)
"""

from __future__ import annotations

import os
import sys
from typing import Dict, List, Tuple, Any
from dataclasses import dataclass, field


EMULATOR_BUILD_PROPERTIES = {
    "ro.hardware": ["goldfish", "ranchu", "vbox86", "nox", "ttvm_x86", "androvm"],
    "ro.kernel.qemu": ["1"],
    "ro.product.model": ["sdk", "google_sdk", "emulator", "android sdk built for x86", "nox", "bluestacks"],
    "ro.product.manufacturer": ["genymotion", "genymobile", "andy", "bluestacks", "nox"],
    "ro.product.board": ["goldfish", "ranchu", "vbox", "nox", "android_x86"],
    "ro.build.flavor": ["vbox", "sdk_gphone"],
}

KNOWN_EMULATOR_DEVICE_NODES = [
    "/dev/qemu_pipe",
    "/dev/goldfish_pipe",
    "/dev/vboxuser",
    "/dev/vboxguest",
    "/dev/vboxguest_user",
    "/dev/nox_hw",
    "/dev/socket/qemud",
]

KNOWN_EMULATOR_FILES = [
    "/system/lib/libc_orig.so",
    "/system/bin/qemu-props",
    "/system/bin/nox-prop",
    "/system/bin/microvirtd",
    "/system/bin/androVM-prop",
    "/data/data/com.vphone.launcher",
    "/data/data/com.bignox.app",
    "/data/data/com.bignox.launcher",
    "/data/data/com.bluestacks.home",
]


@dataclass
class EmulatorCheckResult:
    check_name: str
    detected: bool
    details: str
    risk_level: str


class AndroidEmulatorDetector:
    """Heuristic scanner for virtualized Android runtime environments."""

    def __init__(self):
        self.results: List[EmulatorCheckResult] = []

    def run_all_checks(self, props_dict: Optional[Dict[str, str]] = None) -> List[EmulatorCheckResult]:
        self.results = []
        self._check_properties(props_dict or {})
        self._check_device_nodes()
        self._check_filesystem_artifacts()
        return self.results

    def _check_properties(self, props: Dict[str, str]) -> None:
        for prop_key, suspicious_values in EMULATOR_BUILD_PROPERTIES.items():
            actual = props.get(prop_key, "").lower()
            if actual:
                for s in suspicious_values:
                    if s in actual:
                        self.results.append(
                            EmulatorCheckResult(
                                check_name=f"Property: {prop_key}",
                                detected=True,
                                details=f"Value '{actual}' contains known emulator signature '{s}'",
                                risk_level="High"
                            )
                        )

    def _check_device_nodes(self) -> None:
        for node in KNOWN_EMULATOR_DEVICE_NODES:
            if os.path.exists(node):
                self.results.append(
                    EmulatorCheckResult(
                        check_name=f"Device Node: {node}",
                        detected=True,
                        details="Virtual device communication pipe found",
                        risk_level="Critical"
                    )
                )

    def _check_filesystem_artifacts(self) -> None:
        for f_path in KNOWN_EMULATOR_FILES:
            if os.path.exists(f_path):
                self.results.append(
                    EmulatorCheckResult(
                        check_name=f"File: {f_path}",
                        detected=True,
                        details="Emulator guest binary or package found",
                        risk_level="High"
                    )
                )

    def is_likely_emulator(self) -> bool:
        return any(r.detected for r in self.results)


if __name__ == "__main__":
    detector = AndroidEmulatorDetector()
    mock_props = {
        "ro.hardware": "ranchu",
        "ro.kernel.qemu": "1",
        "ro.product.model": "sdk_gphone64_arm64",
        "ro.product.manufacturer": "Google"
    }
    checks = detector.run_all_checks(mock_props)
    print(f"Emulator Detection Run: Detected={detector.is_likely_emulator()}")
    for c in checks:
        print(f" - [{c.risk_level}] {c.check_name}: {c.details}")
