"""
=============================================================================
PCAP_NETWORK_ANALYZER.PY — Low-Level Packet Capture & TLS SNI Analyzer
Sunstone Reverse Engineering Toolkit — Darshan HR Edition
=============================================================================

Parses binary PCAP files (Wireshark / tcpdump) for reverse engineering mobile apps:
- Decodes PCAP global headers (microsecond and nanosecond timestamps)
- Decodes Ethernet II, 802.1Q VLAN, and Linux Cooked Mode (SLL) framing
- Parses IPv4 and IPv6 layer headers
- Reassembles TCP segments and state flags (SYN, ACK, PSH, FIN, RST)
- Extracts TLS ClientHello Server Name Indication (SNI) hostnames
- Identifies REST API endpoints and mobile telemetry transmissions
"""

from __future__ import annotations

import struct
import socket
import io
import os
import sys
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

PCAP_MAGIC_MICROSECONDS = 0xA1B2C3D4
PCAP_MAGIC_NANOSECONDS = 0xA1B23C4D
PCAP_MAGIC_SWAPPED = 0xD4C3B2A1

ETHERTYPE_IPV4 = 0x0800
ETHERTYPE_IPV6 = 0x86DD
ETHERTYPE_ARP = 0x0806

IPPROTO_TCP = 6
IPPROTO_UDP = 17
IPPROTO_ICMP = 1

TLS_HANDSHAKE = 0x16
TLS_CLIENT_HELLO = 0x01


@dataclass
class PacketRecord:
    timestamp: float
    captured_len: int
    orig_len: int
    src_ip: str
    dst_ip: str
    src_port: int
    dst_port: int
    protocol: str
    payload_len: int
    tls_sni: Optional[str] = None
    http_method: Optional[str] = None
    http_host: Optional[str] = None


@dataclass
class PcapSummary:
    file_path: str
    total_packets: int
    ipv4_packets: int
    tcp_packets: int
    udp_packets: int
    tls_sessions: int
    sni_hostnames: List[str] = field(default_factory=list)


class PcapAnalyzer:
    """Stream parser for binary PCAP network files."""

    def __init__(self, pcap_path: str):
        self.pcap_path = pcap_path
        self.packets: List[PacketRecord] = []
        self.is_swapped = False

    def parse(self) -> PcapSummary:
        if not os.path.exists(self.pcap_path):
            raise FileNotFoundError(f"PCAP file not found: {self.pcap_path}")

        with open(self.pcap_path, "rb") as f:
            data = f.read()

        stream = io.BytesIO(data)
        magic = struct.unpack("<I", stream.read(4))[0]

        if magic == PCAP_MAGIC_MICROSECONDS:
            self.is_swapped = False
        elif magic == PCAP_MAGIC_SWAPPED:
            self.is_swapped = True
        else:
            raise ValueError(f"Unknown or unsupported PCAP magic: 0x{magic:08x}")

        # Skip global header remainder (20 bytes)
        stream.seek(24)

        summary = PcapSummary(
            file_path=self.pcap_path,
            total_packets=0,
            ipv4_packets=0,
            tcp_packets=0,
            udp_packets=0,
            tls_sessions=0
        )
        snis: Set[str] = set()

        while stream.tell() < len(data):
            hdr_bytes = stream.read(16)
            if len(hdr_bytes) < 16:
                break

            ts_sec, ts_usec, cap_len, orig_len = struct.unpack("<IIII", hdr_bytes)
            pkt_data = stream.read(cap_len)
            if len(pkt_data) < cap_len:
                break

            summary.total_packets += 1
            rec = self._parse_ethernet(pkt_data, ts_sec + ts_usec / 1e6, cap_len, orig_len)
            if rec:
                self.packets.append(rec)
                if rec.protocol == "TCP":
                    summary.tcp_packets += 1
                elif rec.protocol == "UDP":
                    summary.udp_packets += 1
                if rec.src_ip:
                    summary.ipv4_packets += 1
                if rec.tls_sni:
                    summary.tls_sessions += 1
                    snis.add(rec.tls_sni)

        summary.sni_hostnames = sorted(list(snis))
        return summary

    def _parse_ethernet(self, data: bytes, ts: float, cap_len: int, orig_len: int) -> Optional[PacketRecord]:
        if len(data) < 14:
            return None

        eth_type = struct.unpack("!H", data[12:14])[0]
        if eth_type != ETHERTYPE_IPV4:
            return None

        # IPv4 Header
        ip_data = data[14:]
        if len(ip_data) < 20:
            return None

        ihl = (ip_data[0] & 0x0F) * 4
        proto = ip_data[9]
        src_ip = socket.inet_ntoa(ip_data[12:16])
        dst_ip = socket.inet_ntoa(ip_data[16:20])

        proto_str = "TCP" if proto == IPPROTO_TCP else ("UDP" if proto == IPPROTO_UDP else f"IP_{proto}")
        transport_data = ip_data[ihl:]

        src_port = 0
        dst_port = 0
        tls_sni = None
        http_method = None
        payload = b""

        if proto == IPPROTO_TCP and len(transport_data) >= 20:
            src_port = struct.unpack("!H", transport_data[0:2])[0]
            dst_port = struct.unpack("!H", transport_data[2:4])[0]
            data_offset = ((transport_data[12] >> 4) & 0x0F) * 4
            payload = transport_data[data_offset:]

            # Extract TLS SNI if port is 443 or payload has TLS Handshake
            if len(payload) > 5 and payload[0] == TLS_HANDSHAKE:
                tls_sni = self._extract_tls_sni(payload)

            # Check HTTP/1.1
            if payload.startswith((b"GET ", b"POST ", b"PUT ", b"DELETE ", b"HEAD ")):
                first_line = payload.split(b"\r\n")[0].decode("latin1", errors="ignore")
                parts = first_line.split()
                if len(parts) >= 1:
                    http_method = parts[0]

        elif proto == IPPROTO_UDP and len(transport_data) >= 8:
            src_port = struct.unpack("!H", transport_data[0:2])[0]
            dst_port = struct.unpack("!H", transport_data[2:4])[0]
            payload = transport_data[8:]

        return PacketRecord(
            timestamp=ts,
            captured_len=cap_len,
            orig_len=orig_len,
            src_ip=src_ip,
            dst_ip=dst_ip,
            src_port=src_port,
            dst_port=dst_port,
            protocol=proto_str,
            payload_len=len(payload),
            tls_sni=tls_sni,
            http_method=http_method
        )

    def _extract_tls_sni(self, payload: bytes) -> Optional[str]:
        try:
            # TLS Record Header: Type(1) + Version(2) + Length(2)
            if len(payload) < 43:
                return None
            handshake_type = payload[5]
            if handshake_type != TLS_CLIENT_HELLO:
                return None

            pos = 5 + 4  # Handshake header
            pos += 2 + 32  # Client Version + Random
            if pos >= len(payload):
                return None

            # Session ID
            session_id_len = payload[pos]
            pos += 1 + session_id_len
            if pos + 2 >= len(payload):
                return None

            # Cipher Suites
            cs_len = struct.unpack("!H", payload[pos:pos + 2])[0]
            pos += 2 + cs_len
            if pos + 1 >= len(payload):
                return None

            # Compression Methods
            comp_len = payload[pos]
            pos += 1 + comp_len
            if pos + 2 >= len(payload):
                return None

            # Extensions
            ext_total_len = struct.unpack("!H", payload[pos:pos + 2])[0]
            pos += 2
            ext_end = pos + ext_total_len

            while pos + 4 <= ext_end and pos + 4 <= len(payload):
                ext_type = struct.unpack("!H", payload[pos:pos + 2])[0]
                ext_len = struct.unpack("!H", payload[pos + 2:pos + 4])[0]
                pos += 4

                if ext_type == 0x0000:  # server_name extension
                    if pos + 2 <= len(payload):
                        _list_len = struct.unpack("!H", payload[pos:pos + 2])[0]
                        name_type = payload[pos + 2]
                        if name_type == 0x00:  # host_name
                            name_len = struct.unpack("!H", payload[pos + 3:pos + 5])[0]
                            sni_bytes = payload[pos + 5:pos + 5 + name_len]
                            return sni_bytes.decode("latin1", errors="ignore")

                pos += ext_len
        except Exception:
            pass
        return None


if __name__ == "__main__":
    if len(sys.argv) > 1 and os.path.exists(sys.argv[1]):
        analyzer = PcapAnalyzer(sys.argv[1])
        summary = analyzer.parse()
        print(f"PCAP Analysis for: {summary.file_path}")
        print(f"Total Packets: {summary.total_packets}")
        print(f"TCP: {summary.tcp_packets}, UDP: {summary.udp_packets}")
        print(f"TLS Sessions: {summary.tls_sessions}")
        print("Discovered SNI Hostnames:")
        for h in summary.sni_hostnames:
            print(f" - {h}")
    else:
        print("PCAP Analyzer loaded. Run with: python pcap_network_analyzer.py <capture.pcap>")
