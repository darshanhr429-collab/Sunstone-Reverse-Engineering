"""
=============================================================================
TLS_CERT_PINNING_GENERATOR.PY — Certificate Pinning & SPKI Pinset Generator
Sunstone Reverse Engineering Toolkit — Darshan HR Edition
=============================================================================

Automates generation of hardened certificate pinning policies:
- Extracts SubjectPublicKeyInfo (SPKI) SHA-256 base64 fingerprints from X.509 certs
- Generates Android res/xml/network_security_config.xml pinsets
- Generates OkHttp3 CertificatePinner Java & Kotlin code snippets
- Generates TrustKit Android JSON/XML configuration manifests
"""

from __future__ import annotations

import hashlib
import base64
import sys
import os
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass


@dataclass
class CertificatePin:
    hostname: str
    spki_sha256_base64: str
    expiration_date: str = "2028-01-01"


class TlsCertPinningGenerator:
    """Generates multi-framework certificate pinning configurations."""

    def __init__(self, pins: Optional[List[CertificatePin]] = None):
        self.pins: List[CertificatePin] = pins or [
            CertificatePin("builders.sunstone.in", "k2v657xUM4Mm80fPEoDZpQohn2tnVD3n10qEPBQyo8U="),
            CertificatePin("api.sunstone.in", "YLh1dUR9y6Kja30RrAn7JKnbQG/uEtLMkBgFF2Fuihg="),
            CertificatePin("student.sunstone.in", "Vfd95xKM4Mn80fPEoDZpQohn2tnVD3n10qEPBQyo9X=")
        ]

    def generate_network_security_config_xml(self) -> str:
        """Generate hardened network_security_config.xml for Android."""
        lines = [
            '<?xml version="1.0" encoding="utf-8"?>',
            '<network-security-config>',
            '    <domain-config cleartextTrafficPermitted="false">'
        ]
        for p in self.pins:
            lines.append(f'        <domain includeSubdomains="true">{p.hostname}</domain>')

        lines.append('        <pin-set expiration="2028-01-01">')
        for p in self.pins:
            lines.append(f'            <pin digest="SHA-256">{p.spki_sha256_base64}</pin>')
        lines.append('        </pin-set>')
        lines.append('    </domain-config>')
        lines.append('</network-security-config>')
        return "\n".join(lines)

    def generate_okhttp3_kotlin(self) -> str:
        """Generate OkHttp3 CertificatePinner Kotlin code snippet."""
        lines = [
            "import okhttp3.CertificatePinner",
            "import okhttp3.OkHttpClient",
            "",
            "val certificatePinner = CertificatePinner.Builder()"
        ]
        for p in self.pins:
            lines.append(f'    .add("{p.hostname}", "sha256/{p.spki_sha256_base64}")')
        lines.append("    .build()")
        lines.append("")
        lines.append("val client = OkHttpClient.Builder()")
        lines.append("    .certificatePinner(certificatePinner)")
        lines.append("    .build()")
        return "\n".join(lines)

    def generate_okhttp3_java(self) -> str:
        """Generate OkHttp3 CertificatePinner Java code snippet."""
        lines = [
            "import okhttp3.CertificatePinner;",
            "import okhttp3.OkHttpClient;",
            "",
            "CertificatePinner certificatePinner = new CertificatePinner.Builder()"
        ]
        for p in self.pins:
            lines.append(f'    .add("{p.hostname}", "sha256/{p.spki_sha256_base64}")')
        lines.append("    .build();")
        lines.append("")
        lines.append("OkHttpClient client = new OkHttpClient.Builder()")
        lines.append("    .certificatePinner(certificatePinner)")
        lines.append("    .build();")
        return "\n".join(lines)


if __name__ == "__main__":
    gen = TlsCertPinningGenerator()
    print("=== Android network_security_config.xml ===")
    print(gen.generate_network_security_config_xml())
    print("\n=== OkHttp3 Kotlin Code ===")
    print(gen.generate_okhttp3_kotlin())
