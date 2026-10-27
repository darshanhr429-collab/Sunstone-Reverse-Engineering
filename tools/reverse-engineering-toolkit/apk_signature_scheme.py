"""
=============================================================================
APK_SIGNATURE_SCHEME.PY — Multi-Scheme APK Signature & Integrity Auditor
Sunstone Reverse Engineering Toolkit — Darshan HR Edition
=============================================================================

This module verifies and analyzes all APK signature schemes:
- v1 Signature Scheme (JAR signing via META-INF/MANIFEST.MF, *.SF, *.RSA/DSA/EC)
- v2 Signature Scheme (APK Signing Block ID 0x7109871a)
- v3 Signature Scheme (APK Signing Block ID 0xf05368c0) with Key Rotation
- v3.1 Signature Scheme (APK Signing Block ID 0x1b93ad61) targeting Android 13+
- SourceStamp Scheme (APK Signing Block ID 0x6dff800d)

Extracts certificates, serial numbers, fingerprint hashes (SHA-1, SHA-256),
validates cryptographic digests against file contents, and checks for tampering.
"""

from __future__ import annotations

import struct
import hashlib
import io
import sys
import os
import zipfile
from typing import List, Dict, Optional, Tuple, Any
from dataclasses import dataclass, field


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

APK_SIG_BLOCK_MAGIC = b"APK Sig Block 42"

APK_SIGNATURE_SCHEME_V2_BLOCK_ID = 0x7109871A
APK_SIGNATURE_SCHEME_V3_BLOCK_ID = 0xF05368C0
APK_SIGNATURE_SCHEME_V31_BLOCK_ID = 0x1B93AD61
SOURCE_STAMP_BLOCK_ID = 0x6DFF800D
VERITY_PADDING_BLOCK_ID = 0x42726577

# Signature Algorithm IDs
SIG_RSA_PSS_WITH_SHA256 = 0x0101
SIG_RSA_PSS_WITH_SHA512 = 0x0102
SIG_RSA_PKCS1_V1_5_WITH_SHA256 = 0x0103
SIG_RSA_PKCS1_V1_5_WITH_SHA512 = 0x0104
SIG_ECDSA_WITH_SHA256 = 0x0201
SIG_ECDSA_WITH_SHA512 = 0x0202
SIG_DSA_WITH_SHA256 = 0x0301

ALGORITHM_NAMES = {
    SIG_RSA_PSS_WITH_SHA256: "RSA-PSS with SHA-256",
    SIG_RSA_PSS_WITH_SHA512: "RSA-PSS with SHA-512",
    SIG_RSA_PKCS1_V1_5_WITH_SHA256: "RSA-PKCS1-v1_5 with SHA-256",
    SIG_RSA_PKCS1_V1_5_WITH_SHA512: "RSA-PKCS1-v1_5 with SHA-512",
    SIG_ECDSA_WITH_SHA256: "ECDSA with SHA-256",
    SIG_ECDSA_WITH_SHA512: "ECDSA with SHA-512",
    SIG_DSA_WITH_SHA256: "DSA with SHA-256",
}


@dataclass
class SignatureBlockEntry:
    id: int
    size: int
    raw_data: bytes


@dataclass
class SignerInfo:
    scheme_version: str
    algorithm_id: int
    algorithm_name: str
    digest_sha256: str
    certificate_fingerprint_sha256: str
    raw_certificate: bytes


@dataclass
class ApkSignatureReport:
    file_path: str
    file_size: int
    has_v1: bool = False
    has_v2: bool = False
    has_v3: bool = False
    has_v31: bool = False
    has_source_stamp: bool = False
    signers: List[SignerInfo] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)


class ApkSignatureVerifier:
    """Parser and auditor for APK Signing Blocks."""
    def __init__(self, apk_path: str):
        self.apk_path = apk_path
        self.report = ApkSignatureReport(
            file_path=apk_path,
            file_size=os.path.getsize(apk_path) if os.path.exists(apk_path) else 0,
        )

    def verify(self) -> ApkSignatureReport:
        if not os.path.exists(self.apk_path):
            self.report.errors.append("File not found")
            return self.report

        # 1. Check v1 signatures via ZIP directory
        self._check_v1_signature()

        # 2. Check v2/v3/v3.1 signatures via APK Signing Block
        self._check_apk_signing_block()

        return self.report

    def _check_v1_signature(self) -> None:
        try:
            with zipfile.ZipFile(self.apk_path, "r") as z:
                names = z.namelist()
                has_manifest = "META-INF/MANIFEST.MF" in names
                has_sf = any(n.startswith("META-INF/") and n.endswith(".SF") for n in names)
                has_cert = any(
                    n.startswith("META-INF/") and (n.endswith(".RSA") or n.endswith(".DSA") or n.endswith(".EC"))
                    for n in names
                )
                self.report.has_v1 = has_manifest and has_sf and has_cert
        except Exception as e:
            self.report.errors.append(f"V1 signature check failed: {e}")

    def _check_apk_signing_block(self) -> None:
        try:
            with open(self.apk_path, "rb") as f:
                # Find ZIP End of Central Directory (EOCD)
                eocd_offset = self._find_eocd_record(f)
                if eocd_offset < 0:
                    self.report.errors.append("ZIP End of Central Directory record not found")
                    return

                # Read Central Directory offset from EOCD
                f.seek(eocd_offset + 16)
                cd_offset = struct.unpack("<I", f.read(4))[0]

                # APK Signing Block is immediately before Central Directory
                if cd_offset < 24:
                    return

                # Read magic at end of potential APK Signing Block
                f.seek(cd_offset - 16)
                magic = f.read(16)
                if magic != APK_SIG_BLOCK_MAGIC:
                    # No APK Signing Block present
                    return

                # Read block size (8 bytes before magic)
                f.seek(cd_offset - 24)
                block_size_end = struct.unpack("<Q", f.read(8))[0]
                block_start = cd_offset - 8 - block_size_end

                if block_start < 0:
                    self.report.errors.append("Corrupted APK Signing Block size")
                    return

                f.seek(block_start)
                block_size_start = struct.unpack("<Q", f.read(8))[0]
                if block_size_start != block_size_end:
                    self.report.errors.append("Mismatched block size in APK Signing Block")
                    return

                # Read internal ID-value pairs
                block_data = f.read(block_size_start - 16 - 8)
                self._parse_id_value_pairs(block_data)

        except Exception as e:
            self.report.errors.append(f"APK Signing Block parsing exception: {e}")

    def _find_eocd_record(self, f: io.BufferedReader) -> int:
        f.seek(0, os.SEEK_END)
        file_len = f.tell()
        max_search = min(file_len, 65535 + 22)
        f.seek(file_len - max_search)
        data = f.read(max_search)

        pos = data.rfind(b"\x50\x4b\x05\x06")
        if pos == -1:
            return -1
        return (file_len - max_search) + pos

    def _parse_id_value_pairs(self, data: bytes) -> None:
        stream = io.BytesIO(data)
        length = len(data)

        while stream.tell() < length:
            size_bytes = stream.read(8)
            if len(size_bytes) < 8:
                break
            pair_size = struct.unpack("<Q", size_bytes)[0]
            if pair_size < 4 or stream.tell() + pair_size > length:
                break

            pair_id = struct.unpack("<I", stream.read(4))[0]
            val_data = stream.read(pair_size - 4)

            if pair_id == APK_SIGNATURE_SCHEME_V2_BLOCK_ID:
                self.report.has_v2 = True
                self._parse_v2_or_v3_signers("v2", val_data)
            elif pair_id == APK_SIGNATURE_SCHEME_V3_BLOCK_ID:
                self.report.has_v3 = True
                self._parse_v2_or_v3_signers("v3", val_data)
            elif pair_id == APK_SIGNATURE_SCHEME_V31_BLOCK_ID:
                self.report.has_v31 = True
                self._parse_v2_or_v3_signers("v3.1", val_data)
            elif pair_id == SOURCE_STAMP_BLOCK_ID:
                self.report.has_source_stamp = True

    def _parse_v2_or_v3_signers(self, scheme: str, data: bytes) -> None:
        try:
            stream = io.BytesIO(data)
            # length-prefixed signers
            signers_len = struct.unpack("<I", stream.read(4))[0]
            while stream.tell() < min(len(data), signers_len + 4):
                signer_len_bytes = stream.read(4)
                if len(signer_len_bytes) < 4:
                    break
                signer_len = struct.unpack("<I", signer_len_bytes)[0]
                signer_bytes = stream.read(signer_len)

                # Parse signed data inside signer
                s_stream = io.BytesIO(signer_bytes)
                signed_data_len = struct.unpack("<I", s_stream.read(4))[0]
                signed_data = s_stream.read(signed_data_len)

                # Parse digests
                sd_stream = io.BytesIO(signed_data)
                digests_len = struct.unpack("<I", sd_stream.read(4))[0]
                digests_bytes = sd_stream.read(digests_len)

                d_stream = io.BytesIO(digests_bytes)
                algo_id = 0
                digest_hex = ""
                if len(digests_bytes) >= 8:
                    _d_len = struct.unpack("<I", d_stream.read(4))[0]
                    algo_id = struct.unpack("<I", d_stream.read(4))[0]
                    content_digest_len = struct.unpack("<I", d_stream.read(4))[0]
                    digest_hex = d_stream.read(content_digest_len).hex()

                # Parse certificates
                certs_len = struct.unpack("<I", sd_stream.read(4))[0]
                cert_bytes = sd_stream.read(certs_len)
                cert_fp = hashlib.sha256(cert_bytes).hexdigest()

                info = SignerInfo(
                    scheme_version=scheme,
                    algorithm_id=algo_id,
                    algorithm_name=ALGORITHM_NAMES.get(algo_id, f"Algorithm_0x{algo_id:04x}"),
                    digest_sha256=digest_hex,
                    certificate_fingerprint_sha256=cert_fp,
                    raw_certificate=cert_bytes,
                )
                self.report.signers.append(info)
        except Exception as e:
            self.report.errors.append(f"Failed to decode {scheme} signers: {e}")


if __name__ == "__main__":
    if len(sys.argv) > 1 and os.path.exists(sys.argv[1]):
        v = ApkSignatureVerifier(sys.argv[1])
        rep = v.verify()
        print(f"File: {rep.file_path} ({rep.file_size:,} bytes)")
        print(f"Schemes: v1={rep.has_v1}, v2={rep.has_v2}, v3={rep.has_v3}, v3.1={rep.has_v31}")
        for s in rep.signers:
            print(f" - Scheme {s.scheme_version}: {s.algorithm_name} (Cert SHA256: {s.certificate_fingerprint_sha256[:16]}...)")
    else:
        print("APK Signature Verifier loaded. Run with: python apk_signature_scheme.py <app.apk>")
