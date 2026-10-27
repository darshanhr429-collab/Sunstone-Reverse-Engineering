"""
=============================================================================
MOBILE_THREAT_INTELLIGENCE.PY — MITRE ATT&CK for Mobile Threat Evaluator
Sunstone Reverse Engineering Toolkit — Darshan HR Edition
=============================================================================

Evaluates reverse-engineered mobile artifacts against MITRE ATT&CK for Mobile:
- T1406: Obfuscated Files or Information (custom Base64, encrypted DEX)
- T1407: Download New Code at Runtime (DexClassLoader from remote URL)
- T1418: Software Discovery (scanning installed packages for banking apps)
- T1426: System Information Discovery (IMEI, IMSI, MAC address harvesting)
- T1437: Application Layer Protocol (C2 telemetry over HTTP/WebSocket)
- T1516: Input Capture via Accessibility Services
"""

from __future__ import annotations

from typing import Dict, List, Optional, NamedTuple
from dataclasses import dataclass, field


class ThreatPattern(NamedTuple):
    technique_id: str
    tactic: str
    name: str
    description: str
    severity: str
    weight: int


MOBILE_ATTACK_PATTERNS: Dict[str, ThreatPattern] = {
    "T1406": ThreatPattern(
        "T1406", "Defense Evasion", "Obfuscated Files or Information",
        "Application uses encrypted strings, hidden ELF symbols, or packed DEX payloads.",
        "Medium", 15
    ),
    "T1407": ThreatPattern(
        "T1407", "Defense Evasion", "Download New Code at Runtime",
        "Application uses DexClassLoader or System.load to execute unverified remote code.",
        "Critical", 40
    ),
    "T1418": ThreatPattern(
        "T1418", "Discovery", "Software Discovery",
        "Application queries PackageManager.getInstalledPackages to profile user device.",
        "Medium", 10
    ),
    "T1426": ThreatPattern(
        "T1426", "Discovery", "System Information Discovery",
        "Application queries hardware identifiers (IMEI, MAC, serial numbers) for fingerprinting.",
        "High", 25
    ),
    "T1437": ThreatPattern(
        "T1437", "Command and Control", "Application Layer Protocol",
        "Application communicates with external C2 or telemetry servers over HTTP/HTTPS/WebSocket.",
        "Medium", 15
    ),
    "T1516": ThreatPattern(
        "T1516", "Collection", "Input Capture via Accessibility Services",
        "Application requests AccessibilityService to capture screen text and keystrokes.",
        "Critical", 50
    ),
}


@dataclass
class ThreatEvaluationResult:
    threat_score: int
    risk_tier: str  # "Low" | "Medium" | "High" | "Critical"
    detected_techniques: List[ThreatPattern] = field(default_factory=list)


class MobileThreatEvaluator:
    """Computes MITRE ATT&CK risk scores for mobile applications."""

    def evaluate_detections(self, detected_ids: List[str]) -> ThreatEvaluationResult:
        patterns: List[ThreatPattern] = []
        score = 0

        for tid in detected_ids:
            if tid in MOBILE_ATTACK_PATTERNS:
                p = MOBILE_ATTACK_PATTERNS[tid]
                patterns.append(p)
                score += p.weight

        if score >= 60:
            tier = "Critical"
        elif score >= 35:
            tier = "High"
        elif score >= 15:
            tier = "Medium"
        else:
            tier = "Low"

        return ThreatEvaluationResult(threat_score=score, risk_tier=tier, detected_techniques=patterns)


if __name__ == "__main__":
    evaluator = MobileThreatEvaluator()
    res = evaluator.evaluate_detections(["T1406", "T1426", "T1437"])
    print(f"Threat Evaluation: Risk Tier = {res.risk_tier} (Score: {res.threat_score}/100)")
    for t in res.detected_techniques:
        print(f" - [{t.technique_id}] {t.name} ({t.tactic})")
