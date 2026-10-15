import http from "node:http";
import fs from "node:fs";
import path from "node:path";
import { exec } from "node:child_process";

const PORT = 3000;
const DIR = path.resolve(process.cwd(), "darshan-hub-portal");

const MIME_TYPES = {
  ".html": "text/html",
  ".css": "text/css",
  ".js": "application/javascript",
  ".json": "application/json",
  ".png": "image/png",
  ".jpg": "image/jpeg",
  ".apk": "application/vnd.android.package-archive",
  ".svg": "image/svg+xml",
};

const server = http.createServer((req, res) => {
  let reqPath = decodeURI(req.url.split("?")[0]);
  if (reqPath === "/") reqPath = "/index.html";

  let filePath = path.join(DIR, reqPath);
  if (!fs.existsSync(filePath)) {
    const rootPath = path.join(process.cwd(), reqPath);
    if (fs.existsSync(rootPath)) {
      filePath = rootPath;
    } else {
      res.writeHead(404, { "Content-Type": "text/plain" });
      return res.end("404 Not Found");
    }
  }

  const ext = path.extname(filePath).toLowerCase();
  const contentType = MIME_TYPES[ext] || "application/octet-stream";

  const stat = fs.statSync(filePath);
  res.writeHead(200, {
    "Content-Type": contentType,
    "Content-Length": stat.size,
    "Access-Control-Allow-Origin": "*",
  });

  fs.createReadStream(filePath).pipe(res);
});

server.listen(PORT, () => {
  const url = `http://localhost:${PORT}`;
  console.log(`\n🚀 Sunstone Portal is running at: ${url}`);
  console.log(`📁 Serving from: ${DIR}`);
  console.log(
    `📱 APK downloads available: Sunstone-Darshan-God.apk, sunstone.apk\n`,
  );

  const startCmd =
    process.platform === "win32"
      ? `start ${url}`
      : process.platform === "darwin"
        ? `open ${url}`
        : `xdg-open ${url}`;
  exec(startCmd);
});
