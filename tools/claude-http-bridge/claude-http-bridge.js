const http = require("http");
const { spawn } = require("child_process");
const { URL } = require("url");

const HOST = process.env.CLAUDE_BRIDGE_HOST || "0.0.0.0";
const PORT = Number.parseInt(process.env.CLAUDE_BRIDGE_PORT || "8811", 10);
const TOKEN = process.env.CLAUDE_BRIDGE_TOKEN || "";
const CLAUDE_BIN = process.env.CLAUDE_BIN || "claude";

function sendJson(res, statusCode, body) {
  const payload = JSON.stringify(body);
  res.writeHead(statusCode, {
    "content-type": "application/json; charset=utf-8",
    "content-length": Buffer.byteLength(payload),
  });
  res.end(payload);
}

function readBody(req, limitBytes = 2 * 1024 * 1024) {
  return new Promise((resolve, reject) => {
    let size = 0;
    const chunks = [];
    req.on("data", (chunk) => {
      size += chunk.length;
      if (size > limitBytes) {
        reject(Object.assign(new Error("Request body too large"), { statusCode: 413 }));
        req.destroy();
        return;
      }
      chunks.push(chunk);
    });
    req.on("end", () => resolve(Buffer.concat(chunks).toString("utf8")));
    req.on("error", reject);
  });
}

function requireAuth(req) {
  if (!TOKEN) return true;
  const header = req.headers["x-claude-bridge-token"];
  return typeof header === "string" && header === TOKEN;
}

function runClaude({ prompt, cwd }) {
  return new Promise((resolve) => {
    const args = ["-p", String(prompt)];
    const child = spawn(CLAUDE_BIN, args, {
      cwd: cwd || process.cwd(),
      windowsHide: true,
      shell: false,
      env: process.env,
    });

    let stdout = "";
    let stderr = "";

    child.stdout.setEncoding("utf8");
    child.stderr.setEncoding("utf8");
    child.stdout.on("data", (d) => (stdout += d));
    child.stderr.on("data", (d) => (stderr += d));

    const killTimer = setTimeout(() => {
      try {
        child.kill();
      } catch {}
    }, 15 * 60 * 1000);

    child.on("close", (code, signal) => {
      clearTimeout(killTimer);
      resolve({ code: code ?? null, signal: signal ?? null, stdout, stderr });
    });
  });
}

const server = http.createServer(async (req, res) => {
  try {
    const url = new URL(req.url || "/", `http://${req.headers.host || "localhost"}`);

    if (req.method === "GET" && url.pathname === "/health") {
      sendJson(res, 200, { ok: true, service: "claude-http-bridge" });
      return;
    }

    if (!requireAuth(req)) {
      sendJson(res, 401, { ok: false, error: "Unauthorized" });
      return;
    }

    if (req.method !== "POST" || url.pathname !== "/") {
      sendJson(res, 404, { ok: false, error: "Not Found" });
      return;
    }

    const raw = await readBody(req);
    let data;
    try {
      data = raw ? JSON.parse(raw) : {};
    } catch {
      sendJson(res, 400, { ok: false, error: "Invalid JSON" });
      return;
    }

    const prompt = data.prompt;
    const cwd = data.cwd;

    if (typeof prompt !== "string" || !prompt.trim()) {
      sendJson(res, 400, { ok: false, error: "Missing required field: prompt" });
      return;
    }
    if (cwd != null && typeof cwd !== "string") {
      sendJson(res, 400, { ok: false, error: "Field cwd must be a string" });
      return;
    }

    const result = await runClaude({ prompt, cwd });
    sendJson(res, 200, { ok: result.code === 0, ...result });
  } catch (err) {
    sendJson(res, err?.statusCode || 500, { ok: false, error: String(err?.message || err) });
  }
});

server.listen(PORT, HOST, () => {
  // eslint-disable-next-line no-console
  console.log(`Claude HTTP bridge listening on http://${HOST}:${PORT}`);
});

