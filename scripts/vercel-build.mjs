import { cpSync, mkdirSync, existsSync } from "node:fs";
import { resolve } from "node:path";

const rootDir = process.cwd();
const portalDir = resolve(rootDir, "darshan-hub-portal");
const distDir = resolve(rootDir, "dist");

console.log("[vercel-build] Preparing Sunstone portal distribution...");
mkdirSync(distDir, { recursive: true });
cpSync(portalDir, distDir, { recursive: true });

// Ensure APKs exist in both dist/ and darshan-hub-portal/
const apkFiles = ["Sunstone-Darshan-God.apk", "sunstone.apk"];
for (const apk of apkFiles) {
  const rootApk = resolve(rootDir, apk);
  const portalApk = resolve(portalDir, apk);
  const distApk = resolve(distDir, apk);

  if (existsSync(rootApk)) {
    if (!existsSync(portalApk)) cpSync(rootApk, portalApk);
    cpSync(rootApk, distApk);
  } else if (existsSync(portalApk)) {
    cpSync(portalApk, distApk);
  }
}

console.log(
  "[vercel-build] Sunstone portal successfully staged to dist/ and darshan-hub-portal/",
);
