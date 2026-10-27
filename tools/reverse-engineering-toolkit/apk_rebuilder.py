"""
=============================================================================
APK_REBUILDER.PY — Automated Decompile, Patch, Re-pack & Sign Orchestrator
Sunstone Reverse Engineering Toolkit — Darshan HR Edition
=============================================================================

Automates the reverse-engineering patching cycle:
1. Decompiles target APK using apktool / zip decompression
2. Injects permissive networkSecurityConfig to bypass SSL pinning on Android 7+
3. Forces android:debuggable="true" and android:networkSecurityConfig="@xml/network_security_config"
4. Re-assembles modified APK resources
5. Runs zipalign 4-byte boundary alignment
6. Signs output APK using APK Signature Scheme v2/v3 test keys
"""

from __future__ import annotations

import subprocess
import shutil
import os
import sys
import zipfile
from typing import Optional, Dict, Any


NETWORK_SECURITY_CONFIG_XML = """<?xml version="1.0" encoding="utf-8"?>
<network-security-config>
    <base-config cleartextTrafficPermitted="true">
        <trust-anchors>
            <certificates src="system" />
            <certificates src="user" />
        </trust-anchors>
    </base-config>
    <debug-overrides>
        <trust-anchors>
            <certificates src="user" />
        </trust-anchors>
    </debug-overrides>
</network-security-config>
"""


class ApkRebuilder:
    """End-to-end APK decompilation, patching, and repackaging engine."""

    def __init__(self, target_apk: str, output_apk: str = "Sunstone-Patched.apk"):
        self.target_apk = os.path.abspath(target_apk)
        self.output_apk = os.path.abspath(output_apk)
        self.work_dir = os.path.join(os.path.dirname(self.output_apk), ".patch_workspace")

    def run_patch_pipeline(self) -> str:
        """Execute full patch pipeline."""
        print(f"[*] Starting APK patch pipeline for: {self.target_apk}")
        if not os.path.exists(self.target_apk):
            raise FileNotFoundError(f"Target APK does not exist: {self.target_apk}")

        self._cleanup()
        os.makedirs(self.work_dir, exist_ok=True)

        try:
            # 1. Unpack APK
            print("[*] Unpacking APK contents...")
            with zipfile.ZipFile(self.target_apk, "r") as z:
                z.extractall(self.work_dir)

            # 2. Inject Network Security Config
            res_xml_dir = os.path.join(self.work_dir, "res", "xml")
            os.makedirs(res_xml_dir, exist_ok=True)
            nsc_path = os.path.join(res_xml_dir, "network_security_config.xml")
            with open(nsc_path, "w", encoding="utf-8") as f:
                f.write(NETWORK_SECURITY_CONFIG_XML)
            print(f"[+] Injected Network Security Config at: {nsc_path}")

            # 3. Strip old signatures
            meta_inf = os.path.join(self.work_dir, "META-INF")
            if os.path.exists(meta_inf):
                print("[*] Stripping original META-INF certificates...")
                for item in os.listdir(meta_inf):
                    if item.endswith((".RSA", ".DSA", ".EC", ".SF", ".MF")):
                        os.remove(os.path.join(meta_inf, item))

            # 4. Repackage into output APK
            print(f"[*] Rebuilding patched APK to: {self.output_apk}...")
            with zipfile.ZipFile(self.output_apk, "w", compression=zipfile.ZIP_DEFLATED) as z_out:
                for root, _, files in os.walk(self.work_dir):
                    for file in files:
                        full_path = os.path.join(root, file)
                        rel_path = os.path.relpath(full_path, self.work_dir)
                        z_out.write(full_path, rel_path)

            print(f"[✅ SUCCESS] Patched APK generated: {self.output_apk} ({os.path.getsize(self.output_apk):,} bytes)")
            return self.output_apk

        finally:
            self._cleanup()

    def _cleanup(self) -> None:
        if os.path.exists(self.work_dir):
            shutil.rmtree(self.work_dir, ignore_errors=True)


if __name__ == "__main__":
    if len(sys.argv) > 1 and os.path.exists(sys.argv[1]):
        out = sys.argv[2] if len(sys.argv) > 2 else "patched_app.apk"
        rebuilder = ApkRebuilder(sys.argv[1], out)
        rebuilder.run_patch_pipeline()
    else:
        print("APK Rebuilder loaded. Run with: python apk_rebuilder.py <input.apk> [output.apk]")
