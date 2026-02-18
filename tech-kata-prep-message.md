# Tech Kata Prep: Stingray Health Portal – Secure Patient Messaging

Hi team! We have a 2.5-hour tech kata coming up where we'll build a secure messaging feature into a Django patient portal using GitHub Copilot. To hit the ground running, please complete the following **before** the session:

## 1. Install prerequisites

- **Python 3.11+** — [python.org](https://www.python.org/downloads/)
- **uv** (Python package manager) — [install guide](https://docs.astral.sh/uv/getting-started/installation/)
- **Node.js** — [download](https://nodejs.org/en/download)
- **WSL** (Windows only) — `wsl --install`

Quick install (Windows):

```pwsh
winget install -e --id astral-sh.uv OpenJS.NodeJS
```

Quick install (Mac):

```bash
brew install node uv
```

## 2. Clone the repo and set up

```bash
git clone <repo-url>
cd HVE-tech-katas
bash ./scripts/setup.sh
```

## 3. Verify it runs

- Start the server: `Ctrl+Shift+P` → Run Task → **Django: Run Server**
- Open <http://localhost:8000> and log in with `patient1` / `password123`
- You should see the patient portal dashboard

## 4. Have VS Code ready with GitHub Copilot enabled

If you run into setup issues, ping in the thread so we can troubleshoot before the session — we don't want to spend kata time on installs!
