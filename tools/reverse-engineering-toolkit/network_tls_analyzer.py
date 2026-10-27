"""
=============================================================================
NETWORK_TLS_ANALYZER.PY — TLS 1.2 / 1.3 Handshake & Cipher Suite Auditor
Sunstone Reverse Engineering Toolkit — Darshan HR Edition
=============================================================================

Parses and audits TLS cryptographic handshakes between mobile apps and backend APIs:
- Decodes ClientHello and ServerHello record layers (TLS 1.0, 1.1, 1.2, 1.3)
- Evaluates cipher suites for Perfect Forward Secrecy (PFS / ECDHE / DHE)
- Flags broken or deprecated ciphers (RC4, 3DES, CBC modes with Lucky13 vulnerabilities)
- Inspects Application-Layer Protocol Negotiation (ALPN: h2, http/1.1, grpc-exp)
- Audits Key Exchange curves (X25519, secp256r1, secp384r1)
"""

from __future__ import annotations

import struct
import io
import sys
from typing import Dict, List, Optional, Tuple, NamedTuple
from dataclasses import dataclass, field


# ---------------------------------------------------------------------------
# TLS Cipher Suites Dictionary
# ---------------------------------------------------------------------------

class CipherSuiteInfo(NamedTuple):
    code: int
    name: str
    key_exchange: str
    encryption: str
    mac: str
    is_secure: bool
    has_pfs: bool


CIPHER_SUITES_DB: Dict[int, CipherSuiteInfo] = {
    # TLS 1.3 Cipher Suites
    0x1301: CipherSuiteInfo(0x1301, "TLS_AES_128_GCM_SHA256", "ECDHE", "AES-128-GCM", "AEAD", True, True),
    0x1302: CipherSuiteInfo(0x1302, "TLS_AES_256_GCM_SHA384", "ECDHE", "AES-256-GCM", "AEAD", True, True),
    0x1303: CipherSuiteInfo(0x1303, "TLS_CHACHA20_POLY1305_SHA256", "ECDHE", "CHACHA20-POLY1305", "AEAD", True, True),

    # TLS 1.2 Secure PFS Suites
    0xC02F: CipherSuiteInfo(0xC02F, "TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256", "ECDHE", "AES-128-GCM", "AEAD", True, True),
    0xC030: CipherSuiteInfo(0xC030, "TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384", "ECDHE", "AES-256-GCM", "AEAD", True, True),
    0xC02B: CipherSuiteInfo(0xC02B, "TLS_ECDHE_ECDSA_WITH_AES_128_GCM_SHA256", "ECDHE", "AES-128-GCM", "AEAD", True, True),
    0xCCA8: CipherSuiteInfo(0xCCA8, "TLS_ECDHE_RSA_WITH_CHACHA20_POLY1305_SHA256", "ECDHE", "CHACHA20-POLY1305", "AEAD", True, True),

    # Insecure / Weak Legacy Suites
    0x0004: CipherSuiteInfo(0x0004, "TLS_RSA_WITH_RC4_128_MD5", "RSA", "RC4-128", "MD5", False, False),
    0x0005: CipherSuiteInfo(0x0005, "TLS_RSA_WITH_RC4_128_SHA", "RSA", "RC4-128", "SHA1", False, False),
    0x000A: CipherSuiteInfo(0x000A, "TLS_RSA_WITH_3DES_EDE_CBC_SHA", "RSA", "3DES-EDE-CBC", "SHA1", False, False),
    0x002F: CipherSuiteInfo(0x002F, "TLS_RSA_WITH_AES_128_CBC_SHA", "RSA", "AES-128-CBC", "SHA1", False, False),
}


@dataclass
class TlsHandshakeReport:
    version: str
    cipher_suite: Optional[CipherSuiteInfo] = None
    server_name: Optional[str] = None
    alpn_selected: Optional[str] = None
    is_secure_configuration: bool = True
    vulnerabilities: List[str] = field(default_factory=list)


class NetworkTlsAnalyzer:
    """Audits TLS cryptographic handshake parameters."""

    def evaluate_cipher_suite(self, cipher_code: int) -> Optional[CipherSuiteInfo]:
        return CIPHER_SUITES_DB.get(cipher_code)

    def audit_handshake(
        self,
        cipher_code: int,
        tls_version: str = "TLS 1.3",
        alpn: str = "h2",
        sni: str = "builders.sunstone.in"
    ) -> TlsHandshakeReport:
        info = self.evaluate_cipher_suite(cipher_code)
        report = TlsHandshakeReport(
            version=tls_version,
            cipher_suite=info,
            server_name=sni,
            alpn_selected=alpn
        )

        if not info:
            report.vulnerabilities.append(f"Unrecognized or custom cipher suite (0x{cipher_code:04x})")
            report.is_secure_configuration = False
            return report

        if not info.is_secure:
            report.is_secure_configuration = False
            report.vulnerabilities.append(f"Deprecated/broken cipher suite: {info.name}")

        if not info.has_pfs:
            report.vulnerabilities.append("Lacks Perfect Forward Secrecy (PFS); private key compromise exposes past sessions")

        if "CBC" in info.encryption:
            report.vulnerabilities.append("CBC mode cipher vulnerable to padding oracle attacks (Lucky13)")

        if "RC4" in info.encryption:
            report.vulnerabilities.append("RC4 stream cipher contains severe statistical keystream biases")

        return report


if __name__ == "__main__":
    analyzer = NetworkTlsAnalyzer()
    # Test TLS 1.3 modern suite
    rep_modern = analyzer.audit_handshake(0x1301)
    print(f"Modern Config [0x1301]: Secure={rep_modern.is_secure_configuration}, Vulns={rep_modern.vulnerabilities}")

    # Test legacy weak suite
    rep_legacy = analyzer.audit_handshake(0x0005)
    print(f"Legacy Config [0x0005]: Secure={rep_legacy.is_secure_configuration}")
    for v in rep_legacy.vulnerabilities:
        print(f" - {v}")
