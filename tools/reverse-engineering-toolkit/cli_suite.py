"""
=============================================================================
CLI_SUITE.PY — Unified CLI Runner for Sunstone Reverse Engineering Suite
Sunstone Reverse Engineering Toolkit — Darshan HR Edition
=============================================================================

Command-line orchestrator providing one-command analysis:
$ python cli_suite.py apk analyze <app.apk>
$ python cli_suite.py apk patch <app.apk> --out <patched.apk>
$ python cli_suite.py native decompile <lib.so>
$ python cli_suite.py proxy start --port 8888
$ python cli_suite.py ranks sync --board github
"""

from __future__ import annotations

import argparse
import sys
import os
import asyncio
from typing import List

from dex_parser import DexParser
from axml_parser import AxmlParser
from apk_signature_scheme import ApkSignatureVerifier
from ghidra_headless_analyzer import GhidraHeadlessBridge
from apk_rebuilder import ApkRebuilder
from sunstone_api_client import SunstoneApiClient


def cmd_apk_analyze(args):
    print(f"\n[+] Analyzing APK: {args.path}")
    if not os.path.exists(args.path):
        print(f"[-] Error: File not found: {args.path}")
        return 1

    # 1. Signature check
    sig_verifier = ApkSignatureVerifier(args.path)
    report = sig_verifier.verify()
    print(f"[*] Size: {report.file_size:,} bytes")
    print(f"[*] Signatures: v1={report.has_v1}, v2={report.has_v2}, v3={report.has_v3}, v3.1={report.has_v31}")
    for s in report.signers:
        print(f"    - {s.scheme_version}: {s.algorithm_name} (Cert: {s.certificate_fingerprint_sha256[:16]}...)")

    print("[+] APK analysis complete.")
    return 0


def cmd_apk_patch(args):
    print(f"\n[+] Patching APK: {args.path} -> {args.out}")
    rebuilder = ApkRebuilder(args.path, args.out)
    rebuilder.run_patch_pipeline()
    return 0


def cmd_native_decompile(args):
    print(f"\n[+] Decompiling Native Library: {args.path}")
    bridge = GhidraHeadlessBridge()
    res = bridge.analyze_library(args.path)
    print(f"[*] Architecture: {res.architecture}")
    print(f"[*] JNI Exports: {len(res.jni_methods)}")
    for j in res.jni_methods:
        print(f"    - {j.name} -> {j.demangled}")
    print(f"[*] Crypto Signatures: {res.crypto_references}")
    return 0


def cmd_ranks_sync(args):
    async def run():
        async with SunstoneApiClient() as client:
            board = await client.get_github_leaderboard()
            print("\n=== Sunstone Builders GitHub Leaderboard ===")
            for b in board:
                prefix = "👑" if b.rank == 1 else f"#{b.rank}"
                print(f"{prefix} {b.name:<18} ({b.campus:<5}) — {b.lines_added:>7,} lines of code")
    asyncio.run(run())
    return 0


def main():
    parser = argparse.ArgumentParser(
        prog="sunstone-re",
        description="Sunstone Reverse Engineering Toolkit — Darshan HR Edition"
    )
    subparsers = parser.add_subparsers(dest="command", help="Sub-commands")

    # apk analyze
    apk_p = subparsers.add_parser("apk", help="APK Operations")
    apk_subs = apk_p.add_subparsers(dest="action")

    p_analyze = apk_subs.add_parser("analyze", help="Analyze APK structure, manifest, and signatures")
    p_analyze.add_argument("path", help="Path to .apk file")

    p_patch = apk_subs.add_parser("patch", help="Patch APK with network-security-config and debuggable")
    p_patch.add_argument("path", help="Input APK file")
    p_patch.add_argument("--out", default="Sunstone-Patched.apk", help="Output APK file")

    # native decompile
    nat_p = subparsers.add_parser("native", help="Native Library Operations")
    nat_subs = nat_p.add_subparsers(dest="action")
    p_decomp = nat_subs.add_parser("decompile", help="Inspect and decompile .so libraries")
    p_decomp.add_argument("path", help="Path to .so file")

    # ranks sync
    rank_p = subparsers.add_parser("ranks", help="Leaderboard Operations")
    rank_subs = rank_p.add_subparsers(dest="action")
    p_rank_sync = rank_subs.add_parser("sync", help="Sync latest GitHub LoC ranks")
    p_rank_sync.add_argument("--board", default="github", choices=["github", "leetcode"])

    args = parser.parse_args()
    if args.command == "apk":
        if args.action == "analyze":
            return cmd_apk_analyze(args)
        elif args.action == "patch":
            return cmd_apk_patch(args)
    elif args.command == "native":
        if args.action == "decompile":
            return cmd_native_decompile(args)
    elif args.command == "ranks":
        if args.action == "sync":
            return cmd_ranks_sync(args)

    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
