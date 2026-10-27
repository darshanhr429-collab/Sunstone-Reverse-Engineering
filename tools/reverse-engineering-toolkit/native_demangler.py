"""
=============================================================================
NATIVE_DEMANGLER.PY — Pure-Python Itanium C++ ABI Symbol Demangler
Sunstone Reverse Engineering Toolkit — Darshan HR Edition
=============================================================================

Demangles native symbol names found in Android ARM64 .so files without external tools:
- Itanium C++ ABI standard prefixes (_Z...)
- Nested namespaces and class structures (_ZN...E)
- Standard substitution compression (St, Sa, Ss, Sb, Si)
- Basic and pointer parameter types (int, float, void, const, pointers, references)
- Special member functions (constructors C1/C2, destructors D1/D2, operators)
"""

from __future__ import annotations

import re
import sys
from typing import Dict, List, Optional, Tuple


STANDARD_SUBSTITUTIONS: Dict[str, str] = {
    "St": "std",
    "Sa": "std::allocator",
    "Sb": "std::basic_string",
    "Ss": "std::string",
    "Si": "std::istream",
    "So": "std::ostream",
    "Sd": "std::iostream",
}

BUILTIN_TYPES: Dict[str, str] = {
    "v": "void",
    "w": "wchar_t",
    "b": "bool",
    "c": "char",
    "a": "signed char",
    "h": "unsigned char",
    "s": "short",
    "t": "unsigned short",
    "i": "int",
    "j": "unsigned int",
    "l": "long",
    "m": "unsigned long",
    "x": "long long",
    "y": "unsigned long long",
    "f": "float",
    "d": "double",
    "e": "long double",
}

OPERATORS: Dict[str, str] = {
    "nw": "operator new",
    "na": "operator new[]",
    "dl": "operator delete",
    "da": "operator delete[]",
    "ps": "operator+",
    "ng": "operator-",
    "ad": "operator&",
    "de": "operator*",
    "co": "operator~",
    "pl": "operator+",
    "mi": "operator-",
    "ml": "operator*",
    "dv": "operator/",
    "rm": "operator%",
    "an": "operator&",
    "or": "operator|",
    "eo": "operator^",
    "aS": "operator=",
    "eq": "operator==",
    "ne": "operator!=",
    "lt": "operator<",
    "gt": "operator>",
    "le": "operator<=",
    "ge": "operator>=",
    "cl": "operator()",
    "ix": "operator[]",
}


class NativeDemangler:
    """Pure-Python Itanium ABI symbol demangler."""

    def demangle(self, mangled: str) -> str:
        if not mangled.startswith("_Z"):
            return mangled

        # Strip _Z
        s = mangled[2:]

        # Nested name: N...E
        if s.startswith("N"):
            return self._demangle_nested(s)

        # Simple function
        name, rest = self._consume_name(s)
        if name and rest:
            params = self._demangle_params(rest)
            return f"{name}({params})"

        return mangled

    def _demangle_nested(self, s: str) -> str:
        # Strip leading N and trailing E
        inner = s[1:]
        if "E" in inner:
            idx = inner.rfind("E")
            path_part = inner[:idx]
            rest = inner[idx + 1:]
        else:
            path_part = inner
            rest = ""

        tokens = []
        pos = 0
        while pos < len(path_part):
            # Check for standard substitutions
            if path_part[pos:pos+2] in STANDARD_SUBSTITUTIONS:
                tokens.append(STANDARD_SUBSTITUTIONS[path_part[pos:pos+2]])
                pos += 2
                continue

            # Check for constructor / destructor
            if path_part[pos:pos+2] in ("C1", "C2"):
                prev = tokens[-1] if tokens else "Class"
                tokens.append(prev)  # Constructor name matches class
                pos += 2
                continue
            if path_part[pos:pos+2] in ("D1", "D2"):
                prev = tokens[-1] if tokens else "Class"
                tokens.append(f"~{prev}")  # Destructor
                pos += 2
                continue

            # Length-prefixed identifier
            m = re.match(r"^(\d+)", path_part[pos:])
            if m:
                length = int(m.group(1))
                pos += len(m.group(1))
                name = path_part[pos:pos + length]
                tokens.append(name)
                pos += length
            else:
                break

        full_name = "::".join(tokens)
        if rest:
            params = self._demangle_params(rest)
            return f"{full_name}({params})"
        return full_name

    def _consume_name(self, s: str) -> Tuple[str, str]:
        m = re.match(r"^(\d+)", s)
        if m:
            length = int(m.group(1))
            start = len(m.group(1))
            name = s[start : start + length]
            return name, s[start + length :]
        return "", s

    def _demangle_params(self, s: str) -> str:
        params = []
        pos = 0
        while pos < len(s):
            char = s[pos]
            is_const = False
            is_ptr = False

            if char == "K":
                is_const = True
                pos += 1
                if pos >= len(s):
                    break
                char = s[pos]

            if char == "P":
                is_ptr = True
                pos += 1
                if pos >= len(s):
                    break
                char = s[pos]

            if char in BUILTIN_TYPES:
                t = BUILTIN_TYPES[char]
                if is_const:
                    t = f"const {t}"
                if is_ptr:
                    t = f"{t}*"
                params.append(t)
                pos += 1
            else:
                # Named type
                m = re.match(r"^(\d+)", s[pos:])
                if m:
                    length = int(m.group(1))
                    pos += len(m.group(1))
                    name = s[pos:pos+length]
                    if is_ptr:
                        name += "*"
                    params.append(name)
                    pos += length
                else:
                    pos += 1

        return ", ".join(params) if params else "void"


if __name__ == "__main__":
    d = NativeDemangler()
    tests = [
        "_ZN8sunstone8telemetry11EventClientC1Ei",
        "_ZN8sunstone8telemetry11EventClient13dispatchFrameEPKci",
        "_Z7computePKc",
        "_ZN3std6vectorIiSaIiEED1Ev"
    ]
    for t in tests:
        print(f"{t}\n -> {d.demangle(t)}\n")
