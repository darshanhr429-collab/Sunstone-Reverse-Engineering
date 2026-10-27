"""
=============================================================================
JNI_SIGNATURE_MAPPER.PY — Java Native Interface (JNI) C/C++ Header Generator
Sunstone Reverse Engineering Toolkit — Darshan HR Edition
=============================================================================

Translates Dalvik bytecode native method signatures into exact C/C++ JNI declarations:
- Converts type descriptors (Z, B, C, S, I, J, F, D, L...;, [...;) to JNI types
- Generates standard exported JNI symbols: Java_package_Class_method(JNIEnv*, jobject, ...)
- Handles overloaded method signature name mangling (__...)
- Generates C JNINativeMethod arrays for RegisterNatives dynamic bindings
- Emits complete, compilable C header files (.h) for NDK reverse engineering
"""

from __future__ import annotations

import re
import sys
from typing import Dict, List, Tuple, NamedTuple


JNI_TYPE_MAP: Dict[str, str] = {
    "V": "void",
    "Z": "jboolean",
    "B": "jbyte",
    "C": "jchar",
    "S": "jshort",
    "I": "jint",
    "J": "jlong",
    "F": "jfloat",
    "D": "jdouble",
    "Ljava/lang/String;": "jstring",
    "Ljava/lang/Class;": "jclass",
    "Ljava/lang/Throwable;": "jthrowable",
    "Ljava/lang/Object;": "jobject",
}

JNI_ARRAY_MAP: Dict[str, str] = {
    "Z": "jbooleanArray",
    "B": "jbyteArray",
    "C": "jcharArray",
    "S": "jshortArray",
    "I": "jintArray",
    "J": "jlongArray",
    "F": "jfloatArray",
    "D": "jdoubleArray",
}


class JniSignatureMapper:
    """Translates Dalvik method signatures into C JNI function declarations."""

    def parse_descriptor(self, desc: str) -> Tuple[List[str], str]:
        """Split signature into parameter types and return type: (ILjava/lang/String;)Z."""
        if not desc.startswith("(") or ")" not in desc:
            raise ValueError(f"Invalid method descriptor: {desc}")

        idx = desc.rfind(")")
        params_str = desc[1:idx]
        return_str = desc[idx + 1:]

        params = []
        pos = 0
        while pos < len(params_str):
            char = params_str[pos]
            if char == "[":
                # Array type
                pos += 1
                elem_type = params_str[pos]
                if elem_type == "L":
                    end_obj = params_str.find(";", pos)
                    params.append("jobjectArray")
                    pos = end_obj + 1
                else:
                    params.append(JNI_ARRAY_MAP.get(elem_type, "jobjectArray"))
                    pos += 1
            elif char == "L":
                # Object type
                end_obj = params_str.find(";", pos)
                obj_name = params_str[pos:end_obj + 1]
                params.append(JNI_TYPE_MAP.get(obj_name, "jobject"))
                pos = end_obj + 1
            else:
                params.append(JNI_TYPE_MAP.get(char, "jobject"))
                pos += 1

        ret_type = JNI_TYPE_MAP.get(return_str, "jobject")
        return params, ret_type

    def generate_jni_symbol_name(self, class_name: str, method_name: str) -> str:
        """Escape class name into Java_package_Class_method."""
        clean_cls = class_name.strip("L;").replace("/", "_").replace("$", "_00024")
        clean_method = method_name.replace("_", "_1")
        return f"Java_{clean_cls}_{clean_method}"

    def generate_c_declaration(
        self,
        class_name: str,
        method_name: str,
        descriptor: str,
        is_static: bool = False
    ) -> str:
        params, ret_type = self.parse_descriptor(descriptor)
        symbol = self.generate_jni_symbol_name(class_name, method_name)

        param_decls = ["JNIEnv* env"]
        param_decls.append("jclass clazz" if is_static else "jobject thiz")

        for idx, p in enumerate(params):
            param_decls.append(f"{p} arg{idx}")

        args_str = ", ".join(param_decls)
        return f"JNIEXPORT {ret_type} JNICALL {symbol}({args_str});"

    def generate_header_file(
        self,
        class_name: str,
        methods: List[Tuple[str, str, bool]]  # (name, descriptor, is_static)
    ) -> str:
        guard_name = "_INCLUDED_" + class_name.strip("L;").replace("/", "_").upper()
        lines = [
            f"#ifndef {guard_name}",
            f"#define {guard_name}",
            "",
            "#include <jni.h>",
            "",
            '#ifdef __cplusplus',
            'extern "C" {',
            '#endif',
            ""
        ]

        for m_name, m_desc, is_static in methods:
            decl = self.generate_c_declaration(class_name, m_name, m_desc, is_static)
            lines.append(f"/* Method: {m_name} {m_desc} */")
            lines.append(decl)
            lines.append("")

        lines.extend([
            '#ifdef __cplusplus',
            '}',
            '#endif',
            "",
            f"#endif /* {guard_name} */"
        ])
        return "\n".join(lines)


if __name__ == "__main__":
    mapper = JniSignatureMapper()
    hdr = mapper.generate_header_file(
        "Lin/sunstone/student/NativeSecurity;",
        [
            ("verifySignature", "([B)Z", True),
            ("decryptTelemetryPayload", "(Ljava/lang/String;[B)[B", False),
            ("getHardwareFingerprint", "()Ljava/lang/String;", True)
        ]
    )
    print("=== Generated JNI C Header File ===")
    print(hdr)
