# Setup

The workshop will take about 3 hours to complete. Before starting, please ensure you are able to clone the repo and setup the Django application.

## 1. Install Prerequisites

- [Python](https://www.python.org/downloads/) 3.11 or later (includes `pip` and the built-in `venv` module)
- [node.js](https://nodejs.org/en) v20 or later (LTS recommended)

Quick installation:

- MacOS:

  ```sh
  brew install python node
  ```

- Windows:

  ```pwsh
  winget install -e Python.Python.3.11 OpenJS.NodeJS.LTS Git.Git GitHub.CLI
  ```

  > [!TIP]
  > You may need to restart your terminal in order to make the new software available.

## 2. Clone the repo and set up

```bash
git clone https://github.com/neerajmandal/HVE-tech-katas.git
cd HVE-tech-katas
npm run setup
```

The `npm run setup` step will:

1. Download the sample FHIR dataset.
2. Create a Python virtual environment in `.venv/`.
3. Install Python dependencies from `requirements-dev.txt`.
4. Install Node dependencies and compile Tailwind CSS.
5. Run database migrations and seed dummy patient data.

> [!WARNING]
> If you already had NodeJS installed, please verify it is >= 20.
>
> If you already tried to run setup with an older version of node and ran into an error, clear your workspace:
>
> 1. Update your NodeJS installation (see above)
> 2. Delete `node_modules`
> 3. Re-run `npm run setup`

## 3. Activate the virtual environment

Before running any Python / Django commands directly, activate the local virtual environment:

- macOS / Linux / WSL:

  ```bash
  source .venv/bin/activate
  ```

- Windows (PowerShell):

  ```pwsh
  .venv\Scripts\Activate.ps1
  ```

- Windows (Git Bash):

  ```bash
  source .venv/Scripts/activate
  ```

You should see `(.venv)` appear in your shell prompt. The `npm run dev` and `npm run migrate` scripts also expect the virtual environment to be active.

## 4. Configure VS Code

1. Open the repository folder in VS Code and when prompted, install suggested extensions.
2. Opening the repo will prompt to open in a devcontainer, which we recommend you **dismiss** it.

   The dev container is provided as a fallback for those who have issues with the local environment setup, but dev container setups lack some MCP functionality.
3. Sign-in to GitHub Copilot if you have not already.
4. When VS Code asks for a Python interpreter, pick the one inside `.venv/`.

## 5. Verify it runs

- Start the server by either:
  - In the terminal (with `.venv` activated), run `npm run dev`
  - In VS Code, `Ctrl+Shift+P` → Run Task → **Django: Run Server**
- Open <http://localhost:8000> and log in with `patient1` / `password123`
- You should see the patient portal dashboard!
