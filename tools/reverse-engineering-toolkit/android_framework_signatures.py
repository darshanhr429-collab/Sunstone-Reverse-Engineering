"""
=============================================================================
ANDROID_FRAMEWORK_SIGNATURES.PY — Android SDK 34 API Signatures Database
Sunstone Reverse Engineering Toolkit — Darshan HR Edition
=============================================================================

Comprehensive database of Android framework API signatures, dangerous permissions,
implicit intents, and privacy-sensitive system services for static analysis:
- Android Dangerous & Signature Permissions (Android 14 / API 34)
- Sensitive Telemetry & Identifier APIs (getDeviceId, getImei, getMacAddress, getSubscriberId)
- Insecure Android Components & IPC interfaces (PendingIntent, ContentProvider, BroadcastReceiver)
- Location, Camera, Microphone, and Biometric API call references
"""

from __future__ import annotations

from typing import Dict, List, Set, NamedTuple


class PermissionInfo(NamedTuple):
    name: str
    protection_level: str
    description: str


ANDROID_PERMISSIONS: Dict[str, PermissionInfo] = {
    "android.permission.INTERNET": PermissionInfo("INTERNET", "normal", "Allows applications to open network sockets."),
    "android.permission.ACCESS_NETWORK_STATE": PermissionInfo("ACCESS_NETWORK_STATE", "normal", "Allows applications to access information about networks."),
    "android.permission.ACCESS_WIFI_STATE": PermissionInfo("ACCESS_WIFI_STATE", "normal", "Allows applications to access information about Wi-Fi networks."),
    "android.permission.READ_PHONE_STATE": PermissionInfo("READ_PHONE_STATE", "dangerous", "Allows read only access to phone state, including phone number and cellular network."),
    "android.permission.READ_PHONE_NUMBERS": PermissionInfo("READ_PHONE_NUMBERS", "dangerous", "Allows read access to device's phone numbers."),
    "android.permission.ACCESS_FINE_LOCATION": PermissionInfo("ACCESS_FINE_LOCATION", "dangerous", "Allows an app to access precise location (GPS)."),
    "android.permission.ACCESS_COARSE_LOCATION": PermissionInfo("ACCESS_COARSE_LOCATION", "dangerous", "Allows an app to access approximate location (Cell-ID/WiFi)."),
    "android.permission.ACCESS_BACKGROUND_LOCATION": PermissionInfo("ACCESS_BACKGROUND_LOCATION", "dangerous", "Allows an app to access location in the background."),
    "android.permission.CAMERA": PermissionInfo("CAMERA", "dangerous", "Required to be able to access the camera device."),
    "android.permission.RECORD_AUDIO": PermissionInfo("RECORD_AUDIO", "dangerous", "Allows an application to record audio."),
    "android.permission.READ_EXTERNAL_STORAGE": PermissionInfo("READ_EXTERNAL_STORAGE", "dangerous", "Allows an application to read from external storage."),
    "android.permission.WRITE_EXTERNAL_STORAGE": PermissionInfo("WRITE_EXTERNAL_STORAGE", "dangerous", "Allows an application to write to external storage."),
    "android.permission.READ_MEDIA_IMAGES": PermissionInfo("READ_MEDIA_IMAGES", "dangerous", "Allows an application to read image files from external storage."),
    "android.permission.READ_MEDIA_VIDEO": PermissionInfo("READ_MEDIA_VIDEO", "dangerous", "Allows an application to read video files from external storage."),
    "android.permission.READ_MEDIA_AUDIO": PermissionInfo("READ_MEDIA_AUDIO", "dangerous", "Allows an application to read audio files from external storage."),
    "android.permission.POST_NOTIFICATIONS": PermissionInfo("POST_NOTIFICATIONS", "dangerous", "Allows an application to post notifications."),
    "android.permission.USE_BIOMETRIC": PermissionInfo("USE_BIOMETRIC", "normal", "Allows an application to use biometric hardware."),
    "android.permission.BLUETOOTH_CONNECT": PermissionInfo("BLUETOOTH_CONNECT", "dangerous", "Required to connect to paired Bluetooth devices."),
    "android.permission.BLUETOOTH_SCAN": PermissionInfo("BLUETOOTH_SCAN", "dangerous", "Required to be able to discover and pair nearby Bluetooth devices."),
    "android.permission.SYSTEM_ALERT_WINDOW": PermissionInfo("SYSTEM_ALERT_WINDOW", "signature|appop", "Allows an app to create windows shown on top of all other apps."),
    "android.permission.REQUEST_INSTALL_PACKAGES": PermissionInfo("REQUEST_INSTALL_PACKAGES", "signature|appop", "Allows an application to request installing packages."),
}


SENSITIVE_API_SIGNATURES: Dict[str, str] = {
    # Telephony & Device Identifiers
    "Landroid/telephony/TelephonyManager;->getDeviceId()Ljava/lang/String;": "IMEI / Device ID retrieval (Deprecated/Privileged)",
    "Landroid/telephony/TelephonyManager;->getImei()Ljava/lang/String;": "Hardware IMEI retrieval",
    "Landroid/telephony/TelephonyManager;->getMeid()Ljava/lang/String;": "Hardware MEID retrieval",
    "Landroid/telephony/TelephonyManager;->getSubscriberId()Ljava/lang/String;": "IMSI Subscriber ID retrieval",
    "Landroid/telephony/TelephonyManager;->getSimSerialNumber()Ljava/lang/String;": "SIM ICCID Serial Number retrieval",
    "Landroid/telephony/TelephonyManager;->getLine1Number()Ljava/lang/String;": "User Phone Number retrieval",
    "Landroid/net/wifi/WifiInfo;->getMacAddress()Ljava/lang/String;": "Hardware MAC Address retrieval",
    "Landroid/provider/Settings$Secure;->getString(Landroid/content/ContentResolver;Ljava/lang/String;)Ljava/lang/String;": "Android ID / System Setting retrieval",

    # Location Services
    "Landroid/location/LocationManager;->getLastKnownLocation(Ljava/lang/String;)Landroid/location/Location;": "GPS / Network Last Known Location",
    "Landroid/location/LocationManager;->requestLocationUpdates(Ljava/lang/String;JFLandroid/location/LocationListener;)V": "Continuous Location Tracking",
    "Lcom/google/android/gms/location/FusedLocationProviderClient;->getLastLocation()Lcom/google/android/gms/tasks/Task;": "Google Play Services Fused Location",

    # Cryptography
    "Ljavax/crypto/Cipher;->getInstance(Ljava/lang/String;)Ljavax/crypto/Cipher;": "Cipher transformation instantiation",
    "Ljavax/crypto/Cipher;->init(ILjava/security/Key;)V": "Symmetric/Asymmetric key initialization",
    "Ljava/security/MessageDigest;->getInstance(Ljava/lang/String;)Ljava/security/MessageDigest;": "Cryptographic hash digest instantiation",
    "Ljavax/crypto/KeyGenerator;->getInstance(Ljava/lang/String;)Ljavax/crypto/KeyGenerator;": "Cryptographic key generator instantiation",

    # Dynamic Code Loading & Reflection
    "Ldalvik/system/DexClassLoader;-><init>(Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/ClassLoader;)V": "Dynamic DEX code loading from file",
    "Ldalvik/system/PathClassLoader;-><init>(Ljava/lang/String;Ljava/lang/ClassLoader;)V": "Dynamic path class loading",
    "Ljava/lang/Class;->forName(Ljava/lang/String;)Ljava/lang/Class;": "Dynamic reflection class resolution",
    "Ljava/lang/reflect/Method;->invoke(Ljava/lang/Object;[Ljava/lang/Object;)Ljava/lang/Object;": "Reflective method execution",

    # Native JNI Bridge
    "Ljava/lang/System;->loadLibrary(Ljava/lang/String;)V": "Native shared object (.so) loading",
    "Ljava/lang/System;->load(Ljava/lang/String;)V": "Absolute path native shared library loading",

    # Command Execution
    "Ljava/lang/Runtime;->exec(Ljava/lang/String;)Ljava/lang/Process;": "Native shell command execution",
    "Ljava/lang/ProcessBuilder;->start()Ljava/lang/Process;": "ProcessBuilder command execution",
}


COMMON_INTENT_ACTIONS: Set[str] = {
    "android.intent.action.MAIN",
    "android.intent.action.VIEW",
    "android.intent.action.SEND",
    "android.intent.action.BOOT_COMPLETED",
    "android.intent.action.USER_PRESENT",
    "android.intent.action.SCREEN_ON",
    "android.intent.action.SCREEN_OFF",
    "android.net.conn.CONNECTIVITY_CHANGE",
    "android.intent.action.BATTERY_LOW",
    "android.intent.action.PACKAGE_ADDED",
    "android.intent.action.PACKAGE_REMOVED",
}


def lookup_api_signature(signature: str) -> Optional[str]:
    """Check if method signature matches known sensitive framework API."""
    return SENSITIVE_API_SIGNATURES.get(signature)


if __name__ == "__main__":
    print(f"Android Dangerous Permissions Indexed: {len(ANDROID_PERMISSIONS)}")
    print(f"Sensitive Android API Signatures Indexed: {len(SENSITIVE_API_SIGNATURES)}")
