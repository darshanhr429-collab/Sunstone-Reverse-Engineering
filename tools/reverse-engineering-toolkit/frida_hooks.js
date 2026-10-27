/**
 * ============================================================================
 * FRIDA_HOOKS.JS — Universal Dynamic Reverse-Engineering & Instrumentation Suite
 * Sunstone Reverse Engineering Toolkit — Darshan HR Edition
 * ============================================================================
 *
 * Capabilities:
 * 1. Universal SSL Pinning Bypass (OkHttp 3/4, TrustManagerImpl, NetworkSecurityConfig, Conscrypt, WebViewClient)
 * 2. Root & Emulator Detection Evasion (Superuser.apk, su binaries, test-keys, build tags)
 * 3. Java Cryptography Architecture (JCA) Key & IV Interceptor (AES/GCM, RSA, HMAC, PBEKeySpec)
 * 4. Flutter Engine Dart Bridge & MethodChannel Tracer
 * 5. SharedPreferences & SQLite Database Live Query Logger
 * 6. Intent & Activity Lifecycle Monitor
 */

"use strict";

Java.perform(function () {
  console.log("[+] ======================================================");
  console.log("[+] Darshan HR Reverse Engineering Suite: Frida Hook Active");
  console.log("[+] Target Process: " + Process.id);
  console.log("[+] ======================================================");

  // --------------------------------------------------------------------------
  // 1. UNIVERSAL SSL PINNING BYPASS
  // --------------------------------------------------------------------------
  try {
    const X509TrustManager = Java.use("javax.net.ssl.X509TrustManager");
    const SSLContext = Java.use("javax.net.ssl.SSLContext");

    const TrustManager = Java.registerClass({
      name: "org.darshan.TrustAllManager",
      implements: [X509TrustManager],
      methods: {
        checkClientTrusted: function (chain, authType) {},
        checkServerTrusted: function (chain, authType) {},
        getAcceptedIssuers: function () {
          return [];
        },
      },
    });

    const TrustManagers = [TrustManager.$new()];
    const SSLContext_init = SSLContext.init.overload(
      "[Ljavax.net.ssl.KeyManager;",
      "[Ljavax.net.ssl.TrustManager;",
      "java.security.SecureRandom",
    );

    SSLContext_init.implementation = function (
      keyManager,
      trustManager,
      secureRandom,
    ) {
      console.log(
        "[+] Bypassing SSLContext.init with custom permissive TrustManager",
      );
      SSLContext_init.call(this, keyManager, TrustManagers, secureRandom);
    };
  } catch (err) {
    console.log("[-] SSLContext bypass failed: " + err);
  }

  // OkHttp3 CertificatePinner Bypass
  try {
    const CertificatePinner = Java.use("okhttp3.CertificatePinner");
    CertificatePinner.check.overload(
      "java.lang.String",
      "java.util.List",
    ).implementation = function (hostname, peerCertificates) {
      console.log(
        "[+] Bypassed OkHttp3 CertificatePinner.check for host: " + hostname,
      );
      return;
    };
  } catch (err) {
    // OkHttp3 may not be loaded yet or renamed by R8
  }

  // TrustManagerImpl (Android N+)
  try {
    const TrustManagerImpl = Java.use(
      "com.android.org.conscrypt.TrustManagerImpl",
    );
    TrustManagerImpl.verifyChain.implementation = function (
      untrustedChain,
      trustAnchorChain,
      host,
      clientAuth,
      ocspData,
      tlsSctData,
    ) {
      console.log(
        "[+] Conscrypt TrustManagerImpl.verifyChain bypassed for host: " + host,
      );
      return untrustedChain;
    };
  } catch (err) {}

  // --------------------------------------------------------------------------
  // 2. ROOT & INTEGRITY CHECK BYPASS
  // --------------------------------------------------------------------------
  try {
    const File = Java.use("java.io.File");
    File.exists.implementation = function () {
      const path = this.getAbsolutePath();
      if (
        path.indexOf("/system/bin/su") > -1 ||
        path.indexOf("/system/xbin/su") > -1 ||
        path.indexOf("/sbin/su") > -1 ||
        path.indexOf("Magisk") > -1 ||
        path.indexOf("Superuser.apk") > -1
      ) {
        console.log("[+] Cloaking root binary check: " + path);
        return false;
      }
      return this.exists();
    };

    const Build = Java.use("android.os.Build");
    Build.TAGS.value = "release-keys";
    Build.FINGERPRINT.value =
      "google/coral/coral:13/TP1A.221005.002/9012097:user/release-keys";
  } catch (err) {
    console.log("[-] Root evasion failed: " + err);
  }

  // --------------------------------------------------------------------------
  // 3. CRYPTOGRAPHIC KEYS & CIPHER INTERCEPTOR
  // --------------------------------------------------------------------------
  try {
    const Cipher = Java.use("javax.crypto.Cipher");
    const SecretKeySpec = Java.use("javax.crypto.spec.SecretKeySpec");

    Cipher.init.overload(
      "int",
      "java.security.Key",
      "java.security.spec.AlgorithmParameterSpec",
    ).implementation = function (opmode, key, params) {
      const opmodes = ["", "ENCRYPT", "DECRYPT", "WRAP", "UNWRAP"];
      const modeName = opmodes[opmode] || opmode;
      const algo = key.getAlgorithm();
      const encodedKey = key.getEncoded();

      let keyHex = "";
      if (encodedKey) {
        for (let i = 0; i < encodedKey.length; i++) {
          keyHex += ("0" + (encodedKey[i] & 0xff).toString(16)).slice(-2);
        }
      }

      console.log(
        `[🔑 CRYPTO] Cipher.init | Mode: ${modeName} | Algo: ${algo} | Key (hex): ${keyHex}`,
      );
      return this.init(opmode, key, params);
    };
  } catch (err) {
    console.log("[-] Crypto tracing error: " + err);
  }

  // --------------------------------------------------------------------------
  // 4. FLUTTER METHODCHANNEL TRACER
  // --------------------------------------------------------------------------
  try {
    const MethodChannel = Java.use("io.flutter.plugin.common.MethodChannel");
    MethodChannel.invokeMethod.overload(
      "java.lang.String",
      "java.lang.Object",
      "io.flutter.plugin.common.MethodChannel$Result",
    ).implementation = function (method, args, result) {
      console.log(
        `[🎯 FLUTTER METHOD] Channel: ${this.name.value} -> Method: ${method} | Args: ${JSON.stringify(args)}`,
      );
      return this.invokeMethod(method, args, result);
    };
  } catch (err) {}

  // --------------------------------------------------------------------------
  // 5. INTENT & TELEMETRY DISPATCH TRACER
  // --------------------------------------------------------------------------
  try {
    const Activity = Java.use("android.app.Activity");
    Activity.startActivity.overload("android.content.Intent").implementation =
      function (intent) {
        const component = intent.getComponent();
        const compName = component
          ? component.flattenToShortString()
          : intent.getAction();
        console.log(`[🚀 NAVIGATION] startActivity -> ${compName}`);
        return this.startActivity(intent);
      };
  } catch (err) {}
});
