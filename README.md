[![Python](https://img.shields.io/badge/python-3.10+-red.svg)](https://www.python.org/downloads)
[![PyPi package](https://badge.fury.io/py/tourbillon.svg)](https://pypi.org/project/tourbillon)
[![Downloads](https://img.shields.io/pypi/dm/tourbillon?color=purple)](https://pypi.org/project/tourbillon)
[![Tests](https://github.com/anxuae/TourBillon/actions/workflows/tests.yml/badge.svg)](https://github.com/anxuae/TourBillon/actions/workflows/tests.yml)
[![Codecov](https://codecov.io/gh/anxuae/TourBillon/branch/master/graph/badge.svg)](https://codecov.io/gh/anxuae/TourBillon)

```text
    oooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo
    o ---------------------------------------------------------------------------- o
    o |                                                                          | o
    o |    oTTTo                                                                 | o
    o    oTTTo                                                                   | o
       oTTTo#&  ////                                                             | o
     oTTTo& #&//////                     BBBBBBB                                 | o
   oTTTo #& //////                       BB     BB       LL  LL                  | o
      #& #&/////                         BB      BB      LL  LL                  | o
      #&/#&//&                           BB      BB      LL  LL                  | o
     /#&/#& #&                           BB     BB   OO  LL  LL                  | o
   ///#& #& #&                           BBBBBBBB        LL  LL                  | o
 ///  #& #& #&   OOOO   UU  UU  RR RRR   BB     BB   II  LL  LL   OOOO   N NNNN  | o
//     #& #& #&  OO  OO  UU  UU  RRR  RR  BB      BB  II  LL  LL  OO  OO  NNN NN | o
       #& #& #&  OO  OO  UU  UU  RR       BB      BB  II  LL  LL  OO  OO  NN  NN | o
       #& #& #&  OO  OO  UU  UU  RR       BB     BB   II  LL  LL  OO  OO  NN  NN | o
       #& #& #&   OOOO    UUUU   RR       BBBBBBB     II  LL  LL   OOOO   NN  NN | o
       #& #&                                                                     | o
       #& #&    ------------------------------------------------------------------ o
       #&     ooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo
       #&                                              Version 6.0.0 © La Billonnière
```

# TourBillon

TourBillon is free software (distributed under the LPG license) that helps you
organize [Billon tournaments](https://www.facebook.com/labillonniere).
It is a **Swiss-system tournament manager** for teams of one or more player(s).

With TourBillon you can:

- register the teams and their players,
- automatically pair teams round after round (draw),
- enter the scores of each match,
- follow the live ranking, including on a big screen in the room,
- browse the history of past editions, player by player.

### How the ranking works

Teams are paired with opponents who have a similar score, never play the same
opponent twice, and are never eliminated. Teams are ranked **first by the number
of games won**; in case of a tie, the **total number of points** decides. The
winner is the team with the most games won (then the most points) across all
rounds.

For 32 to 64 teams, it is recommended to play between 5 and 6 rounds.

## Installation

TourBillon needs two things: **Python** (to run the application) and
**Node.js** (to build the web interface).

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

### 2. Install Node.js and npm (macOS)

Node.js (which bundles `npm`) is needed to build the web interface. Check if it
is installed:

```bash
node --version
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

### 3. Install TourBillon

Install [Poetry](https://python-poetry.org/) (used to install TourBillon), then
install the application and build the web interface:

```bash
# Install Poetry (once)
pip install poetry

# From the TourBillon folder
poetry install

# Build the web interface
cd tourbillon-ui
npm install
npm run build
cd ..
```

## Getting started

Start TourBillon:

```bash
poetry run tourbillon
```

Then open your web browser. Three interfaces are available:

| Interface   | Address                          | What it is for                                             |
|-------------|----------------------------------|------------------------------------------------------------|
| **Admin**   | <http://localhost:8000/admin>    | Register teams, run the draws, enter scores, view rankings.|
| **Display** | <http://localhost:8000/display>  | Read-only live rankings and current round for the big screen (projector). |
| **History** | <http://localhost:8000/history>  | Player statistics year after year, across every saved tournament. |

### A typical tournament

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
