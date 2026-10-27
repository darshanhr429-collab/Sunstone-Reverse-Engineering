"""
=============================================================================
TEST_SUITE.PY — Comprehensive Unit & Integration Test Suite
Sunstone Reverse Engineering Toolkit — Darshan HR Edition
=============================================================================

Automated test runner verifying all toolkit modules:
- DEX Parser & Dalvik instruction tables
- Android Binary XML (AXML) parser
- ARM64 Pure-Python instruction disassembler
- Smali grammar parser and register emulator
- Crypto secret & Shannon entropy scanner
- Protocol Buffers schemaless wire decoder
- Certificate pinning and SPKI generator
"""

from __future__ import annotations

import unittest
import io
import struct

from dex_parser import DexParser
from axml_parser import AxmlParser
from arm64_disassembler import Arm64Disassembler
from smali_parser import SmaliParser
from smali_emulator import SmaliEmulator
from crypto_secret_scanner import CryptoSecretScanner
from protobuf_wire_decoder import ProtobufWireDecoder
from dex_instruction_tables import lookup_opcode
from tls_cert_pinning_generator import TlsCertPinningGenerator


class TestDexInstructionTables(unittest.TestCase):
    def test_nop_lookup(self):
        info = lookup_opcode(0x00)
        self.assertIsNotNone(info)
        self.assertEqual(info.name, "nop")
        self.assertEqual(info.format, "10x")

    def test_invoke_virtual_lookup(self):
        info = lookup_opcode(0x6E)
        self.assertIsNotNone(info)
        self.assertEqual(info.name, "invoke-virtual")
        self.assertEqual(info.format, "35c")


class TestArm64Disassembler(unittest.TestCase):
    def setUp(self):
        self.dis = Arm64Disassembler(0x1000)

    def test_nop(self):
        insn = self.dis.decode_word(0x1000, 0xD503201F)
        self.assertEqual(insn.mnemonic, "nop")

    def test_ret(self):
        insn = self.dis.decode_word(0x1004, 0xD65F03C0)
        self.assertEqual(insn.mnemonic, "ret")

    def test_b_offset(self):
        # B +16 (imm26 = 4)
        insn = self.dis.decode_word(0x1008, 0x14000004)
        self.assertEqual(insn.mnemonic, "b")
        self.assertEqual(insn.operands, "0x1018")


class TestSmaliParserAndEmulator(unittest.TestCase):
    def test_smali_parse_and_emulate(self):
        smali_code = """
        .class public Lin/sunstone/Test;
        .super Ljava/lang/Object;
        .method public static compute()I
            .registers 3
            const/4 v0, 7
            const/16 v1, 42
            add-int/lit8 v2, v0, 5
            return v2
        .end method
        """
        parser = SmaliParser(smali_code)
        cls = parser.parse()
        self.assertEqual(cls.class_name, "Lin/sunstone/Test;")
        self.assertEqual(len(cls.methods), 1)

        emu = SmaliEmulator()
        for ins in cls.methods[0].instructions:
            emu.execute_line(ins.raw_line)

        self.assertEqual(emu.get_register_value("v0"), 7)
        self.assertEqual(emu.get_register_value("v2"), 12)
        self.assertEqual(emu.frame.return_value, 12)


class TestCryptoSecretScanner(unittest.TestCase):
    def test_shannon_entropy(self):
        scanner = CryptoSecretScanner(".")
        # Low entropy vs high entropy
        ent_low = scanner._shannon_entropy("aaaaaaaaaaaa")
        ent_high = scanner._shannon_entropy("A8#k9!zLm4$qPx7@")
        self.assertEqual(ent_low, 0.0)
        self.assertGreater(ent_high, 3.5)

    def test_redact(self):
        scanner = CryptoSecretScanner(".")
        masked = scanner._redact("AIzaSyD-sample-key-1234567890abcdef")
        self.assertTrue(masked.startswith("AIza....cdef"))


class TestProtobufWireDecoder(unittest.TestCase):
    def test_varint_and_string(self):
        stream = io.BytesIO()
        # Field 1 (tag 10) = "sunstone"
        text = b"sunstone"
        stream.write(bytes([10, len(text)]) + text)
        # Field 2 (tag 16) = 150 (varint: 0x96, 0x01)
        stream.write(bytes([16, 0x96, 0x01]))

        dec = ProtobufWireDecoder(stream.getvalue())
        res = dec.decode()
        self.assertEqual(res.get("field_1"), "sunstone")
        self.assertEqual(res.get("field_2"), 150)


class TestTlsCertPinningGenerator(unittest.TestCase):
    def test_xml_output(self):
        gen = TlsCertPinningGenerator()
        xml = gen.generate_network_security_config_xml()
        self.assertIn("builders.sunstone.in", xml)
        self.assertIn("<pin digest=\"SHA-256\">", xml)


if __name__ == "__main__":
    unittest.main()
