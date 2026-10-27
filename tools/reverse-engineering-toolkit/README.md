# 🛠️ Sunstone Reverse Engineering & Telemetry Toolkit

**Author & Lead Architect:** [Darshan H R](https://builders.sunstone.in/builders/darshan-hr) (`@darshanhr429-collab`)  
**College Campus:** RITB (B.E. 2025)  
**Repository:** [Sunstone-Reverse-Engineering](https://github.com/darshanhr429-collab/Sunstone-Reverse-Engineering)  
**Portal & Command Center:** [Darshan Hub Portal](https://sunstone-reverse-engineering.vercel.app)

---

## 📖 Overview

The **Sunstone Reverse Engineering Toolkit** is a production-grade, multi-paradigm security analysis, decompilation, and telemetry inspection platform designed specifically for Android mobile applications, Flutter Dart VM runtimes, and distributed AI engineering workloads.

This toolkit provides end-to-end tooling across bytecode decompilation, native binary analysis, cryptographic secret scanning, and automated APK modding.

---

## 📦 Architecture & Module Index

| Module                                                                 | Language   | Category          | Description                                                                                                                             |
| :--------------------------------------------------------------------- | :--------- | :---------------- | :-------------------------------------------------------------------------------------------------------------------------------------- |
| [`dex_parser.py`](dex_parser.py)                                       | Python 3   | Dalvik VM         | Full binary parser for Android DEX files (format versions 035-039). Extracts headers, strings, types, methods, fields, and raw opcodes. |
| [`dalvik_bytecode_analyzer.py`](dalvik_bytecode_analyzer.py)           | Python 3   | Bytecode / CFG    | Disassembles 256 Dalvik opcodes, constructs method BasicBlocks and Control Flow Graphs (CFG), and computes cyclomatic complexity.       |
| [`dex_instruction_tables.py`](dex_instruction_tables.py)               | Python 3   | Spec / Tables     | Exhaustive metadata table for all 256 Dalvik opcodes, formats (10x, 22c, 35c, etc.), and branch behaviors.                              |
| [`axml_parser.py`](axml_parser.py)                                     | Python 3   | Android AXML      | Binary Android XML decoder that converts compiled `AndroidManifest.xml` files back into formatted, indented XML.                        |
| [`apk_signature_scheme.py`](apk_signature_scheme.py)                   | Python 3   | Integrity         | Multi-scheme signature verifier supporting v1 (JAR), v2 (APK Signing Block), v3 (Rotation), and v3.1 schemes.                           |
| [`apk_rebuilder.py`](apk_rebuilder.py)                                 | Python 3   | Modding / Build   | Automated unpacking, `network_security_config` injection, debuggable enabling, and re-signing pipeline.                                 |
| [`frida_hooks.js`](frida_hooks.js)                                     | JavaScript | Dynamic Hooking   | Universal SSL pinning bypass, root/emulator cloaking, crypto key interceptor, and Flutter MethodChannel sniffer.                        |
| [`ghidra_headless_analyzer.py`](ghidra_headless_analyzer.py)           | Python 3   | Native ELF        | Headless Ghidra automation bridge for ARM64 shared objects (`libflutter.so`, `libapp.so`, `libcrypto.so`).                              |
| [`arm64_disassembler.py`](arm64_disassembler.py)                       | Python 3   | Disassembler      | Pure-Python 32-bit AArch64 instruction disassembler supporting arithmetic, memory pairs (LDP/STP), and branches.                        |
| [`native_got_plt_analyzer.py`](native_got_plt_analyzer.py)             | Python 3   | ELF Linking       | Dynamic linking and Global Offset Table (GOT) / Procedure Linkage Table (PLT) analyzer for runtime function hooks.                      |
| [`flutter_aot_engine.py`](flutter_aot_engine.py)                       | Python 3   | Flutter / Dart    | Dart Ahead-of-Time (AOT) snapshot inspector and embedded object pool string/URL extractor.                                              |
| [`flutter_isolate_dumper.py`](flutter_isolate_dumper.py)               | Python 3   | Memory Analysis   | Dart VM isolate heap memory dumper with tagged object pointer resolution.                                                               |
| [`crypto_secret_scanner.py`](crypto_secret_scanner.py)                 | Python 3   | Static Security   | Heuristic scanner for leaked API keys, hardcoded symmetric cipher keys, Shannon entropy analysis, and weak ciphers.                     |
| [`android_framework_signatures.py`](android_framework_signatures.py)   | Python 3   | Signatures        | Database of Android 14 (API 34) dangerous permissions, sensitive identifiers (IMEI, MAC, IMSI), and dangerous APIs.                     |
| [`android_emulator_detector.py`](android_emulator_detector.py)         | Python 3   | Evasion Detection | 20+ checks for QEMU, Genymotion, BlueStacks, Nox, and virtual driver communication pipes.                                               |
| [`pcap_network_analyzer.py`](pcap_network_analyzer.py)                 | Python 3   | Packet Sniffing   | Low-level binary PCAP packet decoder extracting IPv4, TCP, UDP, and TLS ClientHello Server Name Indication (SNI).                       |
| [`network_telemetry_interceptor.py`](network_telemetry_interceptor.py) | Python 3   | Proxy / Tamper    | Asynchronous MITM TLS proxy with dynamic header injection and builder account spoofing.                                                 |
| [`network_traffic_recorder.py`](network_traffic_recorder.py)           | Python 3   | HAR / PCAP        | Raw socket traffic capture recorder and Chrome-compatible HTTP Archive (HAR 1.2) exporter.                                              |
| [`api_endpoint_fuzzer.py`](api_endpoint_fuzzer.py)                     | Python 3   | API Security      | Asynchronous REST and GraphQL security fuzzer with SQLi, IDOR, path traversal, and timing anomaly detection.                            |
| [`api_replay_benchmark.py`](api_replay_benchmark.py)                   | Python 3   | Load Testing      | High-concurrency API performance benchmarking tool computing P50, P90, P95, and P99 latency percentiles.                                |
| [`sunstone_api_client.py`](sunstone_api_client.py)                     | Python 3   | Client SDK        | Asynchronous client for Sunstone Builders API, leaderboard sync, and student profile verification.                                      |
| [`code_metrics_reporter.py`](code_metrics_reporter.py)                 | Python 3   | Analytics         | Physical LOC, SLOC, comment density, and cyclomatic complexity reporter for git repositories.                                           |
| [`cli_suite.py`](cli_suite.py)                                         | Python 3   | Unified CLI       | One-command CLI runner integrating APK inspection, patching, native decompile, and leaderboard syncing.                                 |

---

## 🚀 Quick Start Guide

### 1. Analyze an Android APK

```bash
python tools/reverse-engineering-toolkit/cli_suite.py apk analyze path/to/app.apk
```

### 2. Patch APK with Universal SSL Bypass & Custom Network Security

```bash
python tools/reverse-engineering-toolkit/cli_suite.py apk patch path/to/app.apk --out Sunstone-Patched.apk
```

### 3. Decompile Native Shared Library

```bash
python tools/reverse-engineering-toolkit/cli_suite.py native decompile path/to/libapp.so
```

### 4. Sync Leaderboard & Verify Lines of Code

```bash
python tools/reverse-engineering-toolkit/cli_suite.py ranks sync --board github
```

---

## 🛡️ License

Built with pride by Darshan H R for the Sunstone Builders Community. Licensed under the MIT License.
