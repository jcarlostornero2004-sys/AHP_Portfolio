/**
 * Starts the FastAPI backend using python -m uvicorn.
 * Cross-platform: works on Windows, Mac, and Linux.
 * Validates that the chosen Python actually has uvicorn before using it.
 */
const { spawn, spawnSync } = require("child_process");
const path = require("path");
const fs = require("fs");
const os = require("os");

const ROOT = __dirname;
const isWin = process.platform === "win32";
const HOME = os.homedir();

function hasUvicorn(pythonCmd) {
  try {
    const r = spawnSync(
      pythonCmd,
      ["-c", "import uvicorn"],
      { timeout: 5000, encoding: "utf8" }
    );
    return r.status === 0;
  } catch (_) {
    return false;
  }
}

function findPython() {
  // Build candidate list — most specific first, PATH last
  const candidates = [];

  // 1. Project venv (only if uvicorn is actually installed there)
  const venvPython = isWin
    ? path.join(ROOT, ".venv", "Scripts", "python.exe")
    : path.join(ROOT, ".venv", "bin", "python");
  if (fs.existsSync(venvPython)) candidates.push(venvPython);

  // 2. Common Windows install locations (pythoncore / AppData)
  if (isWin) {
    const winCandidates = [
      path.join(HOME, "AppData", "Local", "Python", "pythoncore-3.14-64", "python.exe"),
      path.join(HOME, "AppData", "Local", "Python", "pythoncore-3.13-64", "python.exe"),
      path.join(HOME, "AppData", "Local", "Python", "pythoncore-3.12-64", "python.exe"),
      path.join(HOME, "AppData", "Local", "Programs", "Python", "Python314", "python.exe"),
      path.join(HOME, "AppData", "Local", "Programs", "Python", "Python313", "python.exe"),
      path.join(HOME, "AppData", "Local", "Programs", "Python", "Python312", "python.exe"),
      path.join(HOME, "AppData", "Local", "Programs", "Python", "Python311", "python.exe"),
    ];
    for (const c of winCandidates) {
      if (fs.existsSync(c)) candidates.push(c);
    }
  }

  // 3. PATH fallbacks
  candidates.push("python3", "python");

  // Pick first candidate that can actually import uvicorn
  for (const cmd of candidates) {
    if (hasUvicorn(cmd)) {
      return cmd;
    }
  }
  return null;
}

console.log("[API] Locating Python with uvicorn...");
const python = findPython();

if (!python) {
  console.error("[API] ERROR: No Python installation found that has uvicorn.");
  console.error("[API]        Run: pip install -r requirements.txt");
  console.error("[API]        Then retry: npm run dev");
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
