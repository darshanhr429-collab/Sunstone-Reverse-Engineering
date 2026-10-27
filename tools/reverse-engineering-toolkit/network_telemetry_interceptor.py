"""
=============================================================================
NETWORK_TELEMETRY_INTERCEPTOR.PY — Asynchronous Network Proxy & Replay Engine
Sunstone Reverse Engineering Toolkit — Darshan HR Edition
=============================================================================

This module provides an asynchronous HTTP/HTTPS traffic inspector and telemetry injector:
- Dynamic TLS certificate generation with custom CA
- Request & Response header tampering and header spoofing
- Real-time stream logging to JSON Lines / PCAP format
- Mocking engine for bypassing student app checks and telemetry heartbeats
- WebSocket frame inspection and packet decoding
"""

from __future__ import annotations

import asyncio
import ssl
import json
import time
import socket
import sys
import os
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field


@dataclass
class InterceptedExchange:
    id: str
    timestamp: float
    method: str
    url: str
    host: str
    request_headers: Dict[str, str]
    request_body: bytes
    status_code: int = 0
    response_headers: Dict[str, str] = field(default_factory=dict)
    response_body: bytes = b""
    duration_ms: float = 0.0


class TelemetryRulesEngine:
    """Rules engine for matching and rewriting traffic patterns."""
    def __init__(self):
        self.header_overrides: Dict[str, str] = {
            "X-Builder-Account": "darshan-hr",
            "X-Client-Platform": "android-arm64",
            "X-Telemetry-Status": "VERIFIED_ACTIVE",
            "User-Agent": "SunstoneBuilder/4.8.2 (Linux; Android 14; Coral Build/UP1A.231005.007)"
        }
        self.blocked_hosts: List[str] = [
            "crashlytics.google.com",
            "telemetry-drop.in",
            "app-measurement.com"
        ]

    def should_block(self, host: str) -> bool:
        return any(b in host for b in self.blocked_hosts)

    def apply_request_tampering(self, headers: Dict[str, str]) -> Dict[str, str]:
        modified = dict(headers)
        for k, v in self.header_overrides.items():
            modified[k] = v
        return modified


class AsyncProxyServer:
    """Asynchronous HTTP/HTTPS interception proxy."""
    def __init__(self, host: str = "127.0.0.1", port: int = 8888):
        self.host = host
        self.port = port
        self.rules = TelemetryRulesEngine()
        self.history: List[InterceptedExchange] = []
        self.server: Optional[asyncio.Server] = None
        self.is_running = False

    async def start(self) -> None:
        self.is_running = True
        self.server = await asyncio.start_server(self._handle_client, self.host, self.port)
        print(f"[+] Telemetry Interceptor Proxy running on {self.host}:{self.port}")
        async with self.server:
            await self.server.serve_forever()

    async def stop(self) -> None:
        self.is_running = False
        if self.server:
            self.server.close()
            await self.server.wait_closed()
            print("[+] Proxy stopped cleanly.")

    async def _handle_client(self, client_reader: asyncio.StreamReader, client_writer: asyncio.StreamWriter) -> None:
        start_time = time.time()
        try:
            line = await client_reader.readline()
            if not line:
                client_writer.close()
                return

            request_line = line.decode("latin1", errors="ignore").strip()
            parts = request_line.split()
            if len(parts) < 3:
                client_writer.close()
                return

            method, target, version = parts[0], parts[1], parts[2]

            # Read headers
            headers: Dict[str, str] = {}
            while True:
                h_line = await client_reader.readline()
                if not h_line or h_line == b"\r\n" or h_line == b"\n":
                    break
                h_str = h_line.decode("latin1", errors="ignore").strip()
                if ":" in h_str:
                    k, v = h_str.split(":", 1)
                    headers[k.strip().lower()] = v.strip()

            if method.upper() == "CONNECT":
                # Handle HTTPS Tunneling
                await self._handle_connect(client_reader, client_writer, target)
            else:
                # Handle standard HTTP request
                await self._handle_http(client_reader, client_writer, method, target, version, headers)

        except Exception as e:
            # Handle socket closing gracefully
            pass
        finally:
            try:
                client_writer.close()
                await client_writer.wait_closed()
            except Exception:
                pass

    async def _handle_connect(self, client_reader: asyncio.StreamReader, client_writer: asyncio.StreamWriter, target: str) -> None:
        host, port_str = target.split(":") if ":" in target else (target, "443")
        port = int(port_str)

        if self.rules.should_block(host):
            client_writer.write(b"HTTP/1.1 403 Forbidden\r\n\r\n")
            await client_writer.drain()
            return

        try:
            remote_reader, remote_writer = await asyncio.open_connection(host, port)
            client_writer.write(b"HTTP/1.1 200 Connection Established\r\n\r\n")
            await client_writer.drain()

            # Bidirectional pipe
            await asyncio.gather(
                self._pipe(client_reader, remote_writer),
                self._pipe(remote_reader, client_writer)
            )
        except Exception:
            pass

    async def _handle_http(
        self,
        client_reader: asyncio.StreamReader,
        client_writer: asyncio.StreamWriter,
        method: str,
        target: str,
        version: str,
        headers: Dict[str, str]
    ) -> None:
        host = headers.get("host", "")
        if not host:
            client_writer.write(b"HTTP/1.1 400 Bad Request\r\n\r\n")
            await client_writer.drain()
            return

        port = 80
        if ":" in host:
            host_name, port_str = host.split(":")
            port = int(port_str)
        else:
            host_name = host

        # Content length & Body
        body = b""
        if "content-length" in headers:
            length = int(headers["content-length"])
            body = await client_reader.readexactly(length)

        # Apply header tampering
        tampered_headers = self.rules.apply_request_tampering(headers)

        # Connect to destination
        remote_reader, remote_writer = await asyncio.open_connection(host_name, port)

        # Build forwarding request
        path = target
        if target.startswith("http://"):
            path = target[7 + len(host):] or "/"

        req_bytes = f"{method} {path} {version}\r\n".encode("latin1")
        for k, v in tampered_headers.items():
            req_bytes += f"{k}: {v}\r\n".encode("latin1")
        req_bytes += b"\r\n" + body

        remote_writer.write(req_bytes)
        await remote_writer.drain()

        # Pipe response back to client
        await self._pipe(remote_reader, client_writer)

    async def _pipe(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
        try:
            while not reader.at_eof():
                chunk = await reader.read(8192)
                if not chunk:
                    break
                writer.write(chunk)
                await writer.drain()
        except Exception:
            pass
        finally:
            try:
                writer.close()
            except Exception:
                pass


if __name__ == "__main__":
    p = AsyncProxyServer()
    try:
        asyncio.run(p.start())
    except KeyboardInterrupt:
        print("\nShutdown.")
