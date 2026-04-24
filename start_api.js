/**
 * Starts the FastAPI backend using python -m uvicorn.
 * Cross-platform: works on Windows, Mac, and Linux.
 * Checks .venv first, then falls back to system Python.
 */
const { spawn, spawnSync } = require("child_process");
const path = require("path");
const fs = require("fs");

const ROOT = __dirname;
const isWin = process.platform === "win32";

function findPython() {
  // 1. Project virtual environment
  const venvPython = isWin
    ? path.join(ROOT, ".venv", "Scripts", "python.exe")
    : path.join(ROOT, ".venv", "bin", "python");
  if (fs.existsSync(venvPython)) return venvPython;

  // 2. python3 / python on PATH
  for (const cmd of ["python3", "python"]) {
    try {
      const r = spawnSync(cmd, ["--version"], { timeout: 3000, encoding: "utf8" });
      if (r.status === 0) return cmd;
    } catch (_) {}
  }

  return null;
}

const python = findPython();
if (!python) {
  console.error("[API] ERROR: Python not found. Install it from https://www.python.org/downloads/");
  console.error("[API]        Then run: pip install -r requirements.txt");
  process.exit(1);
}

console.log(`[API] Starting FastAPI with: ${python}`);

const proc = spawn(
  python,
  ["-m", "uvicorn", "apps.api.main:app", "--reload", "--host", "127.0.0.1", "--port", "8000"],
  { cwd: ROOT, stdio: "inherit", shell: false }
);

proc.on("error", (err) => {
  console.error("[API] Failed to start:", err.message);
  if (err.code === "ENOENT") {
    console.error("[API] Make sure uvicorn is installed: pip install -r requirements.txt");
  }
  process.exit(1);
});

proc.on("exit", (code) => process.exit(code ?? 0));

process.on("SIGTERM", () => proc.kill("SIGTERM"));
process.on("SIGINT",  () => proc.kill("SIGINT"));
