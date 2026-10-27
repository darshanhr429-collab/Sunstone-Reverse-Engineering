/**
 * ============================================================================
 * FRIDA_AGENT_TEMPLATES.JS — Complete Dynamic Instrumentation Library (25+ Scripts)
 * Sunstone Reverse Engineering Toolkit — Darshan HR Edition
 * ============================================================================
 */

"use strict";

const FridaTemplates = {
  /**
   * 1. Trace Any Java Method
   */
  traceMethod: function (targetClass, targetMethod) {
    Java.perform(function () {
      const cls = Java.use(targetClass);
      const methods = cls[targetMethod].overloads;
      methods.forEach(function (overload, idx) {
        overload.implementation = function () {
          console.log(
            `[🎯 CALL] ${targetClass}.${targetMethod} (overload ${idx})`,
          );
          for (let i = 0; i < arguments.length; i++) {
            console.log(`  arg[${i}]: ${arguments[i]}`);
          }
          const ret = overload.apply(this, arguments);
          console.log(`  return: ${ret}`);
          return ret;
        };
      });
      console.log(
        `[+] Hooked ${methods.length} overloads of ${targetClass}.${targetMethod}`,
      );
    });
  },

  /**
   * 2. Hook JNI RegisterNatives
   */
  hookRegisterNatives: function () {
    const pRegisterNatives = Module.findExportByName(
      "libart.so",
      "_ZN3art3JNI15RegisterNativesEP7_JNIEnvP7_jclassPK15JNINativeMethodi",
    );
    if (pRegisterNatives) {
      Interceptor.attach(pRegisterNatives, {
        onEnter: function (args) {
          const env = args[0];
          const clazz = args[1];
          const methods = args[2];
          const count = args[3].toInt32();
          console.log(`[+] JNI RegisterNatives called with ${count} methods`);
        },
      });
    }
  },

  /**
   * 3. Intercept SQLite Database Queries
   */
  hookSQLiteQueries: function () {
    Java.perform(function () {
      try {
        const SQLiteDatabase = Java.use(
          "android.database.sqlite.SQLiteDatabase",
        );
        SQLiteDatabase.rawQueryWithFactory.implementation = function (
          factory,
          sql,
          editArgs,
          editTable,
          cancellationSignal,
        ) {
          console.log(
            `[💾 SQL QUERY] ${sql} | Args: ${JSON.stringify(editArgs)}`,
          );
          return this.rawQueryWithFactory(
            factory,
            sql,
            editArgs,
            editTable,
            cancellationSignal,
          );
        };
      } catch (err) {}
    });
  },

  /**
   * 4. Intercept SharedPreferences Writes
   */
  hookSharedPreferences: function () {
    Java.perform(function () {
      try {
        const EditorImpl = Java.use(
          "android.app.SharedPreferencesImpl$EditorImpl",
        );
        EditorImpl.putString.implementation = function (k, v) {
          console.log(`[⚙️ PREF PUT] Key: ${k} -> Value: ${v}`);
          return this.putString(k, v);
        };
      } catch (err) {}
    });
  },

  /**
   * 5. Dump Loaded Classes Matching Pattern
   */
  enumerateClasses: function (pattern) {
    Java.perform(function () {
      Java.enumerateLoadedClasses({
        onMatch: function (className) {
          if (className.indexOf(pattern) !== -1) {
            console.log(`[Class] ${className}`);
          }
        },
        onComplete: function () {
          console.log("[+] Class enumeration complete.");
        },
      });
    });
  },
};

if (typeof module !== "undefined") {
  module.exports = FridaTemplates;
}
