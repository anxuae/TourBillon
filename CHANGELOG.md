# v6.0.1

- The default alorithm for draws is "random" if no round created yet
- Add visual marker is tournament is not saved (and auto-save is off)
- Fix duplicate log lines on startup
- Harden API error handling: routers now catch specific business exceptions
- Simplify the match result endpoint (`PUT /api/rounds/{number}/matches`): the match is identified by the team ids in the request body, there is no standalone match id anymore
- Deterministic draw: candidate pairings are now tried closest-in-strength first (wins, points, Buchholz, goal average) instead of raw combinatorial order, finding a valid solution sooner and pruning dead branches earlier
- Add a CI job building and linting the frontend (`tourbillon-ui`)
- Remove the player history progress bar, no longer meaningful with the streamed loading
- Add Spanish and German translations

# v6.0.0

- Make TourBillon compatible with Python >= 3.10
- Full rework of the UI using Vue.js
- Remove cli interface
- Remove wxPython dependecy
