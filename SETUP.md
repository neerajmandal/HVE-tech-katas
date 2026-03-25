# Setup

The workshop will take about 3 hours to complete. Before starting, please ensure you are able to clone the repo and setup the Django application.

## 1. Install Prerequisites

- [Python](https://www.python.org/downloads/) 3.11 or later
- [uv](https://docs.astral.sh/uv/getting-started/installation/)
- [node.js](https://nodejs.org/en) v20 or later (LTS recommended)

Quick installation:

- MacOS:

  ```sh
  brew install python node uv
  ```

- Windows:

  ```pwsh
  winget install -e astral-sh.uv OpenJS.NodeJS.LTS Git.Git GitHub.CLI
  ```

  > [!WARNING]
  > While this command runs in PowerShell, the next commands should run in `bash`, such as git bash.

> [!TIP]
> You may need to restart your terminal or even computer in order to make the new software available.

## 2. Clone the repo and set up

```bash
git clone https://github.com/neerajmandal/HVE-tech-katas.git
cd HVE-tech-katas
npm run setup
```

> [!WARNING]
> If you already had NodeJS installed, please verify it is >= 20.
>
> If you already tried to run setup with an older version of node and ran into an error, clear your workspace:
>
> 1. Update your NodeJS installation (see above)
> 2. Delete `node_modules`
> 3. Re-run `npm run setup`

## 3. Configure VS Code

1. Open the repository folder in VS Code and when prompted, install suggested extensions.
2. Opening the repo will prompt to open in a devcontainer, which we recommend you **dismiss** it.

   The dev container is provided as a fallback for those who have issues with the local environment setup, but dev container setups lack some MCP functionality.
3. Sign-in to GitHub Copilot if you have not already

## 4. Verify it runs

- Start the server by either:
  - In the terminal, run `npm run dev`
  - In VS Code, `Ctrl+Shift+P` → Run Task → **Django: Run Server**
- Open <http://localhost:8000> and log in with `patient1` / `password123`
- You should see the patient portal dashboard!
