# Setup — Manufacturing Kata

This is one of two self-contained kata apps in the repository. It runs
independently from this folder (`verticals/manufacturing/`). Before starting,
ensure you can clone the repo and set up the Django application.

> This kata was **generated** from the [healthcare baseline](../healthcare/) by
> the [Industry Adapter](../../industry-adapter/). It is structurally identical
> to healthcare; only the display copy and seed data differ.

## 1. Install Prerequisites

- [Git](https://git-scm.com/downloads)
- [Docker Desktop](https://docs.docker.com/desktop/)
- [Visual Studio Code](https://code.visualstudio.com/)
- [Dev Containers extension](https://code.visualstudio.com/docs/devcontainers/containers)

With the devcontainer installation, the required toolchains are installed automatically in a consistent runtime environment.

Quick installation:

- macOS:

  ```bash
  brew install git docker-desktop visual-studio-code worktrunk
  ```

- Windows:

  ```pwsh
  winget install -e Git.Git Microsoft.VisualStudioCode Docker.DockerDesktop max-sixty.worktrunk
  ```

## 2. Clone the Repo

```bash
git clone https://github.com/neerajmandal/HVE-tech-katas.git
cd HVE-tech-katas/verticals/manufacturing
```

## 3. Open the Dev Container

1. Open the repository in VS Code.
1. Reopen it in the existing devcontainer when prompted.
1. Wait (~2-5 min) for the one-time post-create provisioning to finish.
This installs Python and Node dependencies, seeds the database, and provisions Chromium for Playwright inside the container.

   > The devcontainer provisions the **healthcare** kata by default. To work this
   > kata instead, set `STINGRAY_DEFAULT_KATA=verticals/manufacturing` before the
   > container builds, or just run the commands below from this folder.

1. Start the app in the container:

    ```bash
    npm run dev
    ```

2. Open forwarded port 6080 from VS Code, or browse to <http://localhost:6080> if port forwarding is mapped locally.
3. When the noVNC viewer prompts for a password, enter `vscode`.
4. Launch the in-container browser from a separate terminal in the devcontainer:

    ```bash
    npm run browser:open
    ```

## 4. Verify it runs

- Start the server with `npm run dev` (from `verticals/manufacturing/`).
- Open <http://localhost:8000> and log in with `operator1` / `password123`.
- You should see the Operations Portal dashboard.
- Open port 6080 and confirm the Fluxbox desktop loads.
- Run `npm run browser:open` and confirm Chromium appears in the noVNC session.

## 5. Troubleshooting

- If port 6080 shows a blank page, run `npm run setup`, `npm run dev`, then `npm run browser:open`.
- If Chromium opens and immediately exits, rebuild the devcontainer so the one-time browser dependency provisioning runs again.
- If the desktop is sluggish on macOS or Windows, [increase Docker Desktop CPU and memory allocation](https://docs.docker.com/desktop/settings-and-maintenance/settings/).

### Local Installation

If you hit issues using the dev container, installing the toolchains onto your host machine is available as a fallback.

#### 1. Install dependencies

- [Python](https://www.python.org/downloads/) 3.11 or later
- [uv](https://docs.astral.sh/uv/getting-started/installation/)
- [node.js](https://nodejs.org/en) v20 or later (LTS recommended)
- [GitHub CLI](https://cli.github.com/)

Quick installation:

- macOS:

  ```bash
  brew install git visual-studio-code docker-desktop worktrunk gh node uv
  ```

- Windows:

  ```pwsh
  winget install -e Git.Git Microsoft.VisualStudioCode Docker.DockerDesktop max-sixty.worktrunk GitHub.CLI OpenJS.NodeJS.LTS astral-sh.uv
  ```

#### 2. Clone the repo and set up

```bash
git clone https://github.com/neerajmandal/HVE-tech-katas.git
cd HVE-tech-katas/verticals/manufacturing

npm run setup
```

`npm run setup` runs the `seed_manufacturing` command, which creates demo
operators (`operator1`, `operator2`, …) with password `password123`.

#### 3. Verify it runs

- Start the server with `npm run dev`.
- Open <http://localhost:8000> and log in with `operator1` / `password123`.
- You should see the Operations Portal dashboard!
