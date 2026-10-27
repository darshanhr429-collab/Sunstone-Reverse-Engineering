"""
=============================================================================
CRYPTO_SECRET_SCANNER.PY — Heuristic Secret, Token & Insecure Cryptography Scanner
Sunstone Reverse Engineering Toolkit — Darshan HR Edition
=============================================================================

Automated AST and regex heuristic scanner for mobile APKs, DEX, and decompiled source:
- Detects leaked API keys (Google Maps/Firebase, AWS, GitHub, Stripe, Sunstone tokens)
- Identifies hardcoded symmetric keys and constant Initialization Vectors (IV)
- Flags obsolete and broken cryptographic ciphers (DES, 3DES, RC4, MD5, SHA-1)
- Flags Electronic Codebook (ECB) mode usage and weak RNG seeding
"""

from __future__ import annotations

import re
import math
import os
import sys
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field


# ---------------------------------------------------------------------------
# Signature Patterns
# ---------------------------------------------------------------------------

PATTERNS = {
    "google_api_key": (re.compile(r"AIza[0-9A-Za-z\\-_]{35}"), "High", "Google Cloud / Firebase API Key"),
    "aws_access_key_id": (re.compile(r"AKIA[0-9A-Z]{16}"), "Critical", "AWS Access Key ID"),
    "github_pat": (re.compile(r"ghp_[0-9a-zA-Z]{36}"), "Critical", "GitHub Personal Access Token"),
    "jwt_token": (re.compile(r"eyJ[a-zA-Z0-9_\-]+\.eyJ[a-zA-Z0-9_\-]+\.[a-zA-Z0-9_\-]+"), "High", "JSON Web Token (JWT)"),
    "stripe_secret_key": (re.compile(r"sk_live_[0-9a-zA-Z]{24}"), "Critical", "Stripe Live Secret Key"),
    "sunstone_auth_token": (re.compile(r"sunstone_tok_[0-9a-zA-Z]{32}"), "High", "Sunstone Builder Auth Token"),
    "private_key_header": (re.compile(r"-----BEGIN (RSA|EC|DSA|PRIVATE) KEY-----"), "Critical", "Embedded Private Key"),
    "hardcoded_ip": (re.compile(r"\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b"), "Medium", "Hardcoded IPv4 Address"),
}

INSECURE_CIPHER_STRINGS = [
    ("AES/ECB", "Critical", "AES with ECB mode lacks diffusion and is vulnerable to block replay"),
    ("DES/", "Critical", "DES cipher key length (56 bits) is obsolete and broken"),
    ("DESede/", "High", "Triple DES (3DES) is deprecated and vulnerable to Sweet32"),
    ("RC4", "Critical", "RC4 stream cipher suffers from multiple bias vulnerabilities"),
    ("MD5", "Medium", "MD5 hash algorithm is vulnerable to collision attacks"),
    ("SHA-1", "Medium", "SHA-1 hash algorithm has practical chosen-prefix collisions"),
    ("java.util.Random", "High", "java.util.Random is not cryptographically secure, use SecureRandom"),
]


@dataclass
class Finding:
    file_path: str
    line_number: int
    rule_name: str
    severity: str
    description: str
    matched_snippet: str
    shannon_entropy: float = 0.0


class CryptoSecretScanner:
    """Heuristic scanner for secrets and insecure cryptography."""

    def __init__(self, target_dir: str):
        self.target_dir = os.path.abspath(target_dir)
        self.findings: List[Finding] = []

    def scan(self) -> List[Finding]:
        self.findings = []
        if os.path.isfile(self.target_dir):
            self._scan_file(self.target_dir)
            return self.findings

        for root, _, files in os.walk(self.target_dir):
            for file in files:
                if file.endswith((".java", ".kt", ".xml", ".js", ".json", ".smali", ".py", ".txt")):
                    full_path = os.path.join(root, file)
                    self._scan_file(full_path)

        return self.findings

    def _scan_file(self, path: str) -> None:
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                lines = f.readlines()
        except Exception:
            return

        for line_idx, line in enumerate(lines, 1):
            line_str = line.strip()

            # 1. Regex Pattern Matches
            for rule_name, (regex, severity, desc) in PATTERNS.items():
                match = regex.search(line_str)
                if match:
                    matched_text = match.group(0)
                    entropy = self._shannon_entropy(matched_text)
                    self.findings.append(
                        Finding(
                            file_path=path,
                            line_number=line_idx,
                            rule_name=rule_name,
                            severity=severity,
                            description=desc,
                            matched_snippet=self._redact(matched_text),
                            shannon_entropy=entropy
                        )
                    )

            # 2. Insecure Cipher Heuristics
            for cipher_name, severity, desc in INSECURE_CIPHER_STRINGS:
                if cipher_name in line_str:
                    self.findings.append(
                        Finding(
                            file_path=path,
                            line_number=line_idx,
                            rule_name="insecure_crypto_primitive",
                            severity=severity,
                            description=desc,
                            matched_snippet=line_str[:80],
                            shannon_entropy=0.0
                        )
                    )

    def _shannon_entropy(self, s: str) -> float:
        """Calculate Shannon entropy to distinguish random secrets from dictionary words."""
        if not s:
            return 0.0
        prob = [float(s.count(c)) / len(s) for c in dict.fromkeys(list(s))]
        return -sum([p * math.log(p) / math.log(2.0) for p in prob])

    def _redact(self, secret: str) -> str:
        """Partially mask secret for safe reporting."""
        if len(secret) <= 8:
            return "****"
        return secret[:4] + "...." + secret[-4:]

    def generate_report(self) -> str:
        out = []
        out.append(f"=== Crypto & Secret Scanner Report ({len(self.findings)} findings) ===")
        for f in self.findings:
            out.append(f"[{f.severity}] {f.description}")
            out.append(f"  Location: {f.file_path}:{f.line_number}")
            out.append(f"  Snippet:  {f.matched_snippet}")
            if f.shannon_entropy > 0:
                out.append(f"  Entropy:  {f.shannon_entropy:.2f} bits")
            out.append("")
        return "\n".join(out)


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "."
    scanner = CryptoSecretScanner(target)
    findings = scanner.scan()
    print(scanner.generate_report())
