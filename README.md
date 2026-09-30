[![Python](https://img.shields.io/badge/python-3.10+-red.svg)](https://www.python.org/downloads)
[![PyPi package](https://badge.fury.io/py/tourbillon-app.svg)](https://pypi.org/project/tourbillon-app)
[![Downloads](https://img.shields.io/pypi/dm/tourbillon-app?color=purple)](https://pypi.org/project/tourbillon-app)
[![Tests](https://github.com/anxuae/TourBillon/actions/workflows/tests.yml/badge.svg)](https://github.com/anxuae/TourBillon/actions/workflows/tests.yml)
[![Codecov](https://codecov.io/gh/anxuae/TourBillon/branch/py3/graph/badge.svg)](https://codecov.io/gh/anxuae/TourBillon)

# <img src="https://raw.githubusercontent.com/anxuae/TourBillon/py3/tourbillon-ui/src/assets/icon.png" alt="" width="32" valign="middle"> TourBillon

TourBillon is free software (distributed under the LPG license) that helps you
organize tournaments using the **Swiss system**, for teams of one or more
player(s). It was originally built for the game of
[Billon](https://www.facebook.com/labillonniere), but can be used for any
Swiss-system tournament.

With TourBillon you can:

- register the teams and their players,
- automatically pair teams round after round (draw),
- enter the scores of each match,
- follow the live ranking, including on a big screen in the room,
- browse the history of past editions, player by player.

## 📦 Installation

TourBillon is published on PyPI under the name `tourbillon-app`. If you only
want to run the application, install it with `pip`:

```bash
pip install tourbillon-app
```

Then start the application:

```bash
tourbillon
```

## 🚀 Getting started

Open your web browser. Three interfaces are available:

| Interface   | Address                          | What it is for                                             |
|-------------|----------------------------------|------------------------------------------------------------|
| **Admin**   | <http://localhost:8000/admin>    | Register teams, run the draws, enter scores, view rankings.|
| **Display** | <http://localhost:8000/display>  | Read-only live rankings and current round for the big screen (projector). |
| **History** | <http://localhost:8000/history>  | Player statistics year after year, across every saved tournament. |

## 🏆 A typical tournament

1. Open the **Admin** interface and register every team and its players.
2. Launch the first **draw** to pair the teams for round 1.
3. Play the matches, then **enter each score** in the Admin interface.
4. Launch the next draw, and repeat for every round (usually 5 to 6).
5. Show the **Display** interface on the big screen so everyone can follow the
   live ranking and see who plays where.
6. After the event, use the **History** interface to review player performances
   across the years.

Your tournaments are saved automatically and remain compatible with the files
from previous editions.

## 📊 How the ranking works

Teams are paired with opponents who have a similar score, never play the same
opponent twice, and are never eliminated. Teams are ranked **first by the number
of games won**; in case of a tie, the **total number of points** decides. The
winner is the team with the most games won (then the most points) across all
rounds.

For 32 to 64 teams, it is recommended to play between 5 and 6 rounds.

# 🛠️ Developer mode

Developer mode needs **Python**, **Poetry**, **Node.js**, and **npm**. On macOS,
you can install them step by step as follows.

## 📦 Installation

### 1. Install Python

TourBillon requires **Python 3.10 or higher**. Check whether it is already
installed:

```bash
python3 --version
```

If it is missing or too old, install it with [Homebrew](https://brew.sh):

```bash
brew install python
```

or download it from [python.org](https://www.python.org/downloads/).

### 2. Install Poetry

Poetry is used to install the Python dependencies and run the project from the
source tree:

```bash
pip install poetry
poetry --version
```

### 3. Install Node.js and npm

Node.js (which bundles `npm`) is needed to build the web interface. Check if it
is installed:

```bash
node --version
npm --version
```

If the command is not found, or reports a version below 18, install it using one
of the options below.

**Option A — Homebrew**

```bash
# Install Homebrew if you don't have it yet
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Node.js (includes npm)
brew install node

# Verify the installation
node --version
npm --version
```

**Option B — official installer**

Download the macOS `.pkg` installer from [nodejs.org](https://nodejs.org/)
(choose the **LTS** version) and follow the graphical installer. It installs
both `node` and `npm`.

> After installation, make sure `node --version` reports **18 or higher**.

### 4. Install TourBillon from source

From the TourBillon folder, install the backend dependencies with Poetry:

```bash
poetry install
```

Then build the web interface:

```bash
cd tourbillon-ui
npm install
npm run build
cd ..
```

### 5. Start the application

```bash
poetry run tourbillon
```

## 🏗️ Build the packages

The frontend must be built once beforehand, then bundled into the Python
package via a dedicated script, before running Poetry's build. This keeps
the resulting wheel a portable `py3-none-any` package:

```bash
poetry run python scripts/build-ui.py
poetry build
```

To build the Windows executable locally (on Windows, with the `build`
dependency group installed):

```bash
poetry install --with build
poetry run python scripts/build-ui.py
poetry run pyinstaller scripts/build-exe.spec --noconfirm
```

All packages are generated in the `dist/` folder. To inspect
the build artifacts before publishing, list that directory:

```bash
ls dist/
```

### Publishing a new release

Publishing is automated: pushing a Git tag `X.Y.Z` triggers the
[`publish.yml`](.github/workflows/publish.yml) workflow, which builds the
frontend, builds the package, and uploads it to PyPI using
[Trusted Publishing](https://docs.pypi.org/trusted-publishers/) (OIDC, no
token to manage). In parallel, it also builds a standalone **Windows
executable** with [PyInstaller](https://pyinstaller.org/) (no Python
installation required on the target machine). Both the PyPI artifacts
(sdist + wheel) and the Windows executable are then attached to the matching
GitHub release.

```bash
poetry version <X.Y.Z>
git add pyproject.toml
git commit -m "Bump version to $(poetry version -s)"
git tag "$(poetry version -s)"
git push && git push --tags
```

The workflow refuses to publish if the tag does not match the version in
`pyproject.toml`.
