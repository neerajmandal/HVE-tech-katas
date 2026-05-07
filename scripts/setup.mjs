#!/usr/bin/env node

import { execSync } from "node:child_process";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const WORKSPACE_ROOT = path.resolve(__dirname, "..");
const DATA_DIR = path.join(WORKSPACE_ROOT, "data");
const ZIP_PATH = path.join(DATA_DIR, "10-patients.zip");
const DATASET_URL =
  "https://github.com/smart-on-fhir/sample-bulk-fhir-datasets/archive/refs/heads/10-patients.zip";

const VENV_DIR = path.join(WORKSPACE_ROOT, ".venv");
const IS_WINDOWS = process.platform === "win32";
const VENV_PYTHON = IS_WINDOWS
  ? path.join(VENV_DIR, "Scripts", "python.exe")
  : path.join(VENV_DIR, "bin", "python");

// Ensure all operations run from the workspace root
process.chdir(WORKSPACE_ROOT);

function quote(value) {
  return `"${value}"`;
}

function pickSystemPython() {
  const candidates = IS_WINDOWS ? ["py -3", "python", "python3"] : ["python3", "python"];
  for (const candidate of candidates) {
    try {
      execSync(`${candidate} --version`, { stdio: "ignore", shell: true });
      return candidate;
    } catch {
      // try next
    }
  }
  throw new Error(
    "Unable to find a Python 3 interpreter on PATH. Install Python 3.11+ and try again.",
  );
}

function printStage(message) {
  console.log(`\n\n*** ${message}`);
}

function printStep(message) {
  console.log(`- ${message}`);
}

function run(command) {
  execSync(command, {
    cwd: WORKSPACE_ROOT,
    stdio: "inherit",
    shell: true,
  });
}

async function downloadDatasetArchive() {
  if (fs.existsSync(ZIP_PATH)) {
    return;
  }

  printStep("Downloading 10-patients dataset archive...");
  const response = await fetch(DATASET_URL);
  if (!response.ok) {
    throw new Error(
      `Failed to download sample dataset: ${response.status} ${response.statusText}`,
    );
  }

  const arrayBuffer = await response.arrayBuffer();
  fs.writeFileSync(ZIP_PATH, Buffer.from(arrayBuffer));
}

function extractDatasetArchive() {
  if (process.platform === "win32") {
    const powershellCommand = [
      "powershell",
      "-NoProfile",
      "-ExecutionPolicy",
      "Bypass",
      "-Command",
      `Expand-Archive -Path '${ZIP_PATH}' -DestinationPath '${DATA_DIR}' -Force`,
    ].join(" ");
    run(powershellCommand);
    return;
  }

  run(`unzip -d \"${DATA_DIR}\" -o \"${ZIP_PATH}\"`);
}

async function main() {
  printStage("Extracting sample data archive...");
  fs.mkdirSync(DATA_DIR, { recursive: true });
  await downloadDatasetArchive();
  extractDatasetArchive();

  printStage("Setting up Python environment...");
  if (fs.existsSync(VENV_PYTHON)) {
    // Existing venvs created without pip (e.g. by uv) need to be recreated.
    try {
      execSync(`${quote(VENV_PYTHON)} -m pip --version`, { stdio: "ignore", shell: true });
      printStep("Virtual environment already exists, reusing it.");
    } catch {
      printStep("Existing virtual environment is missing pip; recreating it...");
      fs.rmSync(VENV_DIR, { recursive: true, force: true });
    }
  }
  if (!fs.existsSync(VENV_PYTHON)) {
    const systemPython = pickSystemPython();
    printStep(`Creating virtual environment at ${VENV_DIR}...`);
    run(`${systemPython} -m venv ${quote(VENV_DIR)}`);
  }

  printStep("Upgrading pip...");
  run(`${quote(VENV_PYTHON)} -m pip install --upgrade pip`);

  printStep("Installing Python dependencies...");
  run(`${quote(VENV_PYTHON)} -m pip install -r requirements-dev.txt`);

  printStage("Setting up Node environment...");
  run("npm install");

  printStage("Setting up Django...");
  printStep("Compiling Tailwind CSS...");
  run(
    "npx @tailwindcss/cli -i static/input.css -o static/output.css --config tailwind.config.js",
  );

  printStep("Collecting static files...");
  run(`${quote(VENV_PYTHON)} manage.py collectstatic --noinput`);

  printStep("Running database migrations...");
  run(`${quote(VENV_PYTHON)} manage.py migrate`);

  printStep("Populating sample data...");
  run(`${quote(VENV_PYTHON)} manage.py seed_dummy_data`);

  printStage("Setup complete!");
  const activateHint = IS_WINDOWS
    ? "  .venv\\Scripts\\activate           (cmd / PowerShell)\n  source .venv/Scripts/activate    (Git Bash)"
    : "  source .venv/bin/activate";
  console.log(`Activate the virtual environment with:\n${activateHint}`);
}

main().catch((error) => {
  console.error("\n*** ERROR: setup failed");
  console.error(String(error));
  process.exit(1);
});
