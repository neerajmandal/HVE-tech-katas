# Setup

The workshop will take about 3 hours to complete. Before starting, please ensure you are able to clone the repo and setup the Django application.

## 1. Install Prerequisites

- [Git](https://git-scm.com/downloads)
- [Docker Desktop](https://docs.docker.com/desktop/)
- [Visual Studio Code](https://code.visualstudio.com/)
- [Dev Containers extension](https://code.visualstudio.com/docs/devcontainers/containers)

  > [!TIP]
  > You may need to restart your terminal in order to make the new software available.

## 2. Clone the Repo

```bash
git clone https://github.com/neerajmandal/HVE-tech-katas.git
cd HVE-tech-katas
```

## 3. Open the Devcontainer

1. Open the repository in VS Code.
1. Reopen it in the existing devcontainer when prompted.
1. Wait (~2-5 min️) for the one-time post-create provisioning to finish.
This installs Python and Node dependencies, seeds the database, and provisions Chromium for Playwright inside the container.
1. Start the app in the container:

    ```bash
    npm run dev
    ```

1. Open forwarded port 6080 from VS Code, or browse to <http://localhost:6080> if port forwarding is mapped locally.
1. When the noVNC viewer prompts for a password, enter `vscode`.
1. Launch the in-container browser from a separate terminal in the devcontainer:

    ```bash
    npm run browser:open
    ```

## 3. Verify it runs

- Start the server by either:
  - In the devcontainer terminal, run `npm run dev`
  - In VS Code, `Ctrl+Shift+P` → Run Task → **Django: Run Server**
- Open <http://localhost:8000> and log in with `patient1` / `password123`.
- You should see the patient portal dashboard.
- Open port 6080 and confirm the Fluxbox desktop loads.
- Run `npm run browser:open` and confirm Chromium appears in the noVNC session.

## 4. Troubleshooting

- If port 6080 shows a blank page, run `npm run dev`, then `npm run browser open`.
- If Chromium opens and immediately exits, rebuild the devcontainer so the one-time browser dependency provisioning runs again.
- If the desktop is sluggish on macOS or Windows, [increase Docker Desktop CPU and memory allocation](https://docs.docker.com/desktop/settings-and-maintenance/settings/).

### Local Installation

If you hit issues using the dev container, local installation is available as a fallback.

#### 1. Install dependencies

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

  > [!TIP]
  > You may need to restart your terminal in order to make the new software available.

#### 2. Clone the repo and set up

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

#### 3. Configure VS Code

1. Open the repository folder in VS Code and when prompted, install suggested extensions.
2. Sign-in to GitHub Copilot if you have not already

#### 4. Verify it runs

- Start the server by either:
  - In the terminal, run `npm run dev`
  - In VS Code, `Ctrl+Shift+P` → Run Task → **Django: Run Server**
- Open <http://localhost:8000> and log in with `patient1` / `password123`
- You should see the patient portal dashboard!
