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
const args = new Set(process.argv.slice(2));

// Ensure all operations run from the workspace root
process.chdir(WORKSPACE_ROOT);

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

function hasCommand(command) {
  try {
    execSync(`command -v ${command}`, {
      cwd: WORKSPACE_ROOT,
      stdio: "ignore",
      shell: true,
    });
    return true;
  } catch {
    return false;
  }
}

function shouldProvisionBrowser() {
  return args.has("--provision-browser");
}

function provisionBrowser() {
  printStage("Provisioning browser prerequisites...");

  if (process.platform === "linux" && hasCommand("sudo")) {
    run("npm run install:browser:container");
    return;
  }

  run("npm run install:browser");
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
  run("uv sync");

  printStage("Setting up Node environment...");
  run("npm install");

  if (shouldProvisionBrowser()) {
    provisionBrowser();
  }

  printStage("Setting up Django...");
  printStep("Compiling Tailwind CSS...");
  run(
    "npx @tailwindcss/cli -i static/input.css -o static/output.css --config tailwind.config.js",
  );

  printStep("Collecting static files...");
  run("uv run python manage.py collectstatic --noinput");

  printStep("Running database migrations...");
  run("uv run python manage.py migrate");

  printStep("Populating sample data...");
  run("uv run python manage.py seed_dummy_data");
}

main().catch((error) => {
  console.error("\n*** ERROR: setup failed");
  console.error(String(error));
  process.exit(1);
});
