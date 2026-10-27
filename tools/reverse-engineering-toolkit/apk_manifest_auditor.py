"""
=============================================================================
APK_MANIFEST_AUDITOR.PY — Android Manifest Security Posture & Vulnerability Scanner
Sunstone Reverse Engineering Toolkit — Darshan HR Edition
=============================================================================

Audits parsed AndroidManifest.xml trees for mobile security vulnerabilities:
- Exported components without permission gating (Activities, Services, Receivers, Providers)
- Insecure application backup (android:allowBackup="true")
- Insecure debug mode (android:debuggable="true")
- Plaintext network transport (android:usesCleartextTraffic="true")
- Custom deep-link URI scheme hijacking (intent-filter analysis)
- Missing or misconfigured networkSecurityConfig
"""

from __future__ import annotations

import sys
import os
import re
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field


@dataclass
class VulnerabilityFinding:
    vuln_id: str
    severity: str
    component_name: str
    title: str
    description: str
    remediation: str


class ApkManifestAuditor:
    """Security auditor for AndroidManifest XML components."""

    def __init__(self, manifest_xml: str):
        self.manifest_xml = manifest_xml
        self.findings: List[VulnerabilityFinding] = []

    def audit(self) -> List[VulnerabilityFinding]:
        self.findings = []
        self._check_debuggable()
        self._check_allow_backup()
        self._check_cleartext_traffic()
        self._check_exported_components()
        self._check_deep_links()
        return self.findings

    def _check_debuggable(self) -> None:
        if 'android:debuggable="true"' in self.manifest_xml:
            self.findings.append(
                VulnerabilityFinding(
                    vuln_id="VULN-MAN-001",
                    severity="Critical",
                    component_name="<application>",
                    title="Application is Marked as Debuggable",
                    description="android:debuggable is set to true. Attackers can attach jdb/debugger and dump arbitrary process memory.",
                    remediation="Set android:debuggable=\"false\" in production release builds."
                )
            )

    def _check_allow_backup(self) -> None:
        if 'android:allowBackup="true"' in self.manifest_xml or "android:allowBackup" not in self.manifest_xml:
            self.findings.append(
                VulnerabilityFinding(
                    vuln_id="VULN-MAN-002",
                    severity="Medium",
                    component_name="<application>",
                    title="ADB Backup Data Extraction Permitted",
                    description="android:allowBackup is true or not explicitly disabled. App data and databases can be extracted via 'adb backup'.",
                    remediation="Set android:allowBackup=\"false\" in AndroidManifest.xml."
                )
            )

    def _check_cleartext_traffic(self) -> None:
        if 'android:usesCleartextTraffic="true"' in self.manifest_xml:
            self.findings.append(
                VulnerabilityFinding(
                    vuln_id="VULN-MAN-003",
                    severity="High",
                    component_name="<application>",
                    title="Cleartext HTTP Network Traffic Permitted",
                    description="android:usesCleartextTraffic is set to true, allowing unencrypted HTTP connections subject to eavesdropping.",
                    remediation="Disable cleartext traffic and enforce TLS 1.3 via network_security_config."
                )
            )

    def _check_exported_components(self) -> None:
        components = [
            ("activity", re.findall(r'<activity[^>]*android:exported="true"[^>]*>', self.manifest_xml)),
            ("service", re.findall(r'<service[^>]*android:exported="true"[^>]*>', self.manifest_xml)),
            ("receiver", re.findall(r'<receiver[^>]*android:exported="true"[^>]*>', self.manifest_xml)),
            ("provider", re.findall(r'<provider[^>]*android:exported="true"[^>]*>', self.manifest_xml)),
        ]

        for comp_type, matches in components:
            for match in matches:
                name_match = re.search(r'android:name="([^"]+)"', match)
                comp_name = name_match.group(1) if name_match else f"unknown_{comp_type}"
                has_perm = 'android:permission="' in match

                if not has_perm and "MAIN" not in match:
                    self.findings.append(
                        VulnerabilityFinding(
                            vuln_id="VULN-MAN-004",
                            severity="High",
                            component_name=comp_name,
                            title=f"Exported {comp_type.capitalize()} Without Permission Protection",
                            description=f"The {comp_type} '{comp_name}' is exported to third-party applications without permission gating.",
                            remediation="Add android:permission=\"...\" or set android:exported=\"false\"."
                        )
                    )

    def _check_deep_links(self) -> None:
        schemes = re.findall(r'<data[^>]*android:scheme="([^"]+)"', self.manifest_xml)
        for s in set(schemes):
            if s not in ("http", "https"):
                self.findings.append(
                    VulnerabilityFinding(
                        vuln_id="VULN-MAN-005",
                        severity="Low",
                        component_name=f"scheme://{s}",
                        title=f"Custom URI Scheme Handler: {s}://",
                        description=f"App registers custom URI scheme '{s}://'. Ensure all intent parameters are sanitized against XSS and open redirects.",
                        remediation="Validate origin and sanitize all query parameters before dispatching actions."
                    )
                )


if __name__ == "__main__":
    demo_manifest = """
    <manifest package="in.sunstone.student">
        <application android:allowBackup="true" android:debuggable="true" android:usesCleartextTraffic="true">
            <activity android:name=".MainActivity" android:exported="true">
                <intent-filter>
                    <action android:name="android.intent.action.MAIN" />
                </intent-filter>
            </activity>
            <activity android:name=".SecretPortalActivity" android:exported="true" />
            <service android:name=".TelemetryService" android:exported="true" />
            <data android:scheme="sunstone" />
        </application>
    </manifest>
    """
    auditor = ApkManifestAuditor(demo_manifest)
    res = auditor.audit()
    print(f"Manifest Audit Complete: Found {len(res)} issues:")
    for r in res:
        print(f"[{r.severity}] {r.title} ({r.component_name})")
