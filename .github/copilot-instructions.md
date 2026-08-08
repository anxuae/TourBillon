# TourBillon — Instructions Copilot & documentation technique

> Ce fichier sert de **contexte permanent** pour tout développement sur TourBillon.
> Chargez-le systématiquement avant de coder. Il décrit le domaine métier et
> l'architecture actuelle du projet (backend FastAPI + frontend Vue 3).

---

## 1. Contexte métier : le jeu du Billon

Le **Billon** est un jeu traditionnel du Nord de la France. TourBillon est un
**gestionnaire de tournoi au système suisse (Swiss System)** pour des équipes
d'un ou plusieurs joueur(s).

### Règles du système suisse
- Les équipes sont appariées avec des adversaires de score similaire.
- **Disparité maximale** : chaque tirage expose un paramètre **`max_disparity`**
  (paramètre **de tirage**, propre à l'algorithme — pas un paramètre global du
  tournoi). Il définit l'écart maximum autorisé, en **nombre de parties gagnées**,
  entre deux équipes d'une même manche. L'appariement ne peut associer que des
  équipes dont l'écart de victoires reste `<= max_disparity` (`0` = uniquement des
  équipes à égalité de victoires). Si aucune solution valide n'existe avec cette
  contrainte, le **tirage échoue** en demandant à l'opérateur d'augmenter le
  paramètre.
- Deux équipes ne se rencontrent pas deux fois (dans la mesure du possible).
- Aucune équipe n'est éliminée.
- Le classement se fait **d'abord par nombre de parties gagnées** ; en cas d'ex æquo
  sur les parties gagnées, c'est le **nombre de points** cumulés qui départage.
- Le vainqueur est donc l'équipe ayant le plus de parties gagnées (puis le plus de
  points en cas d'égalité) sur l'ensemble des parties.
- Pour 32 à 64 équipes, on recommande 5 à 6 parties (rounds) par tournoi.

### Le chapeau (bye)
- Lorsqu'un round ne peut pas apparier toutes les équipes (typiquement un **nombre
  impair** d'équipes, ou plus généralement un reliquat non divisible par
  `teams_by_match`), une équipe est mise « au chapeau » : elle ne joue pas ce round.
- L'équipe désignée est choisie **parmi les plus faibles** du classement (celles
  qui n'ont pas encore été chapeau en priorité) et est déclarée **gagnante d'office**.
- Elle marque un nombre de points forfaitaire égal au paramètre **`points_by_match`**
  (points de victoire d'une manche, p. ex. 12) et compte comme une **partie gagnée**.
- Une même équipe ne doit pas être chapeau deux fois dans la mesure du possible.

### Vocabulaire (anglais dans tout le code)
| Concept             | Terme (code)      | Description                                        |
|---------------------|-------------------|----------------------------------------------------|
| Tournoi             | `tournament`      | L'événement complet                                |
| Partie / tour       | `round`           | Un tour d'appariements (Swiss round)               |
| Manche / rencontre  | `match`           | Une rencontre entre `teams_by_match` équipes       |
| Équipe              | `team`            | Une équipe (1..N joueurs)                           |
| Joueur              | `player`          | Un joueur                                          |
| Tirage              | `draw`            | L'algorithme d'appariement d'un round              |
| Chapeau             | `bye`             | Équipe sans adversaire sur un round (points forfait)|
| Piquet / emplacement| `location`        | Emplacement physique de jeu                        |
| Classement          | `ranking` / `rank`| Classement des équipes / rang d'une équipe         |
| Victoire            | `win` / `wins`    | Partie gagnée (terme retenu ; **pas** `victory`)   |
| Score d'une manche  | `score`           | Points marqués sur une manche                      |

> **Joker** : le terme `joker` est conservé (intelligible en anglais). C'est un
> nombre de départage **optionnel** saisi à l'inscription d'une équipe (valeur par
> défaut `0`). L'UI doit permettre de le saisir sans le rendre obligatoire. Il n'est
> utilisé que pour départager le classement.

> **Identifiant d'équipe** : le numéro d'équipe est un **identifiant** (`team.id`,
> pas `number`). Le numéro d'un **round** reste un numéro séquentiel (`round.number`).

> **Uniformisation du vocabulaire** : utiliser **`wins`** (et non `victories`) et
> **`rank`** (et non `place`). Le classement expose `rank` ; une équipe expose `wins`.

### États (voir `tourbillon/core/cst.py`)
Les états ci-dessous sont **calculés à la volée** et **jamais persistés** ; ils portent
donc des **valeurs anglaises stables** exposées **directement** par l'API (pas de table
de traduction dans `services.py`).
- **Match** : `MATCH_IN_PROGRESS='in_progress'`, `MATCH_FINISHED='finished'`
- **Team** : `TEAM_INCOMPLETE='incomplete'`, `TEAM_WAITING_DRAW='awaiting_draw'`,
  `TEAM_IN_PROGRESS='in_progress'`
- **Round** : `ROUND_WAITING_DRAW='awaiting_draw'`, `ROUND_IN_PROGRESS='in_progress'`,
  `ROUND_COMPLETE='complete'`, `ROUND_FINISHED='finished'`
- **Tournament** : `TOURNAMENT_REGISTRATION='registration'`,
  `TOURNAMENT_WAITING_DRAW='awaiting_draw'`,
  `TOURNAMENT_ROUND_IN_PROGRESS='round_in_progress'`
- **Résultat de manche** (valeurs **anglaises en mémoire** : `BYE='bye'`, `WON='won'`,
  `LOST='lost'`, `FORFEIT='forfeit'`). La persistance reste en français legacy
  (`chapeau/gagné/perdu/forfait`) via `Match.load()`/`Match.dump()` — ne pas changer
  les chaînes disque.

---

## 2. Architecture du projet

```
tourbillon/                 # Package Python (backend)
  __main__.py               # Point d'entrée : lance uvicorn (commande `tourbillon`)
  settings.py               # Configuration typée (YAML + env TOURBILLON_*)
  logger.py, singleton.py   # Utilitaires
  assets/                   # Ressources statiques (banner.txt pour l'entête des dumps YAML)
  core/                     # Domaine métier — indépendant de FastAPI
    tournament.py, round.py, team.py, player.py, match.py
    cst.py                  # Constantes d'état et clés de statistiques
    exception.py            # Exceptions métier
    draws/                  # Tirages : coroutines pures + registre
      __init__.py           # Registre (DRAWS, DEFAULT_DRAW, available, generate)
      common.py             # Helpers partagés (stats, disparity, byes…)
      deterministic.py, genetic.py, random.py
  api/                      # Backend FastAPI
    app.py                  # create_app() : monte les routers + StaticFiles
    state.py                # État applicatif (tournoi courant, verrous asyncio)
    schemas.py              # DTO Pydantic (v2)
    services.py             # Orchestration métier ↔ persistance YAML
    history.py              # Agrégation multi-tournois (stats par joueur)
    routers/                # tournament, teams, rounds, draws, rankings, history, ws

tourbillon-ui/              # Frontend SPA Vue 3 + Vite
  src/
    main.js, App.vue
    router/index.js         # Routes /admin, /display, /history
    api/client.js           # Client REST
    stores/tournament.js    # Store Pinia
    views/
      admin/                # Inscription, tirage, round, classement
      display/              # Affichage écran géant (lecture seule)
      history/              # Stats par joueur d'année en année
  dist/                     # Build servi par FastAPI en production

tests/                      # pytest (asyncio_mode=auto)
  conftest.py, data/        # Fixtures + jeux de données
  test_*.py
```

- **Backend** : FastAPI + Uvicorn, endpoints REST + **WebSocket** (`/ws`) pour la
  progression des tirages et le rafraîchissement temps réel.
- **Persistance** : services au-dessus de `core.tournament.load/dump` (YAML).
- **Concurrence** : `asyncio`, verrou par tournoi pour les écritures (voir `state.py`).
- **Frontend** servi en production via `StaticFiles` depuis `tourbillon-ui/dist/`.

### Configuration (`settings.py`)
Une seule classe `Settings` (source unique de vérité) lit/écrit un fichier YAML.
Surcharge possible par variables d'environnement `TOURBILLON_*`. Trois domaines
backend, exposés **en sections** : **`general`** (host, port, `save_dir`, `auto_save`),
**`tournament`** (valeurs par défaut d'un nouveau tournoi + `default_draw`) et
**`draws`** (options effectives par algorithme). Le regroupement des clés en sections
est défini **à un seul endroit** (`SECTIONS` dans `settings.py`) : c'est le format
persisté sur disque **et** le format échangé par l'API (`as_dict()`/`update()` et les
DTO sont **sectionnés**, plus de format plat). En mémoire, l'accès aux scalaires reste
néanmoins direct (`settings.host`, `settings.teams_by_match`…). L'ajout/renommage d'une
section ne se fait donc qu'à cet endroit ; l'API et l'UI (modale) suivent
automatiquement (le front itère sur les sections reçues, sans les redéclarer). Les
préférences UI vivent côté frontend. Les **valeurs par défaut** de chaque tirage
restent définies dans les modules d'algorithme (`DEFAULT`) ; à la construction des
`Settings`, la section `draws` est **initialisée** depuis ces `DEFAULT`, puis
**enrichie** par le fichier de settings au chargement (fusion par algo et par option ;
options inconnues ignorées, manquantes conservées). Le cycle de vie est simple :
**chargement au démarrage, sauvegarde à l'arrêt** (lifespan FastAPI) — tout passe par
le module `settings`, **aucune** mutation/écriture intermédiaire dans les routers ou
services. `GET /api/draws` expose en lecture le `default` (de l'algo) et la `config`
effective (des settings). Le fichier de settings est **indépendant de `save_dir`** :
sans chemin explicite (`-c`), il est lu/écrit dans le **dossier de configuration
standard de la plateforme** (`config_dir()` / `default_settings_path()` — p. ex.
`~/.config/tourbillon/settings.yml` sous Linux, `~/Library/Application Support/
tourbillon/settings.yml` sous macOS, `%APPDATA%\tourbillon\settings.yml` sous Windows),
si bien que changer `save_dir` ne perd jamais les réglages. Le chemin effectivement
chargé est journalisé au démarrage. Pour le rechargement `--reload` d'uvicorn (qui
exige une import string), l'app est reconstruite via la fabrique
`create_app_from_env()`, le chemin de settings étant transmis par la variable
d'environnement `SETTINGS_PATH_ENV` (`TOURBILLON_SETTINGS_PATH`).

---

## 3. Cœur métier (`core/`)

Modèle : `Tournament` contient des `Team` (dict `_teams` indexé par `id`) et des
`Round` (liste `_rounds`). Chaque `Team` porte une liste de résultats (`_results`,
un `Match` par round). Un `Round` calcule ses appariements à partir des résultats
des équipes.

Points clés :
- API **entièrement en anglais** (méthodes, attributs, docstrings, messages).
- `load()`/`dump()` de `tournament.py` **conservent les clés YAML en français**
  (`tournoi`, `inscription`, `jokers`, `parties`, `enregistrement`, `debut`,
  `equipes_par_manche`, `joueurs_par_equipe`, `points_par_manche`) pour la
  **rétro-compatibilité** avec les archives (`../Sauvegardes Tournois/*.yml` / `*.trb`).
- Le dict `Match.data` est **entièrement en anglais** en mémoire (`state`, `start`,
  `end`, `opponents`, `location`, `points`) ; de même les résultats `BYE/WON/LOST/
  FORFEIT` valent `'bye'/'won'/'lost'/'forfeit'`. La **conversion vers le format
  legacy français** (clés `etat`/`debut`/`fin`/`adversaires`/`piquet` et valeurs
  `chapeau`/`gagné`/`perdu`/`forfait`, plus l'ancien `duree`) est **confinée** aux
  méthodes `Match.load()` / `Match.dump()`, appelées uniquement par
  `tournament.load`/`dump`. **Ne jamais casser la lecture des anciens fichiers.**
- `core/` ne doit **jamais** importer FastAPI ni Pydantic (indépendance du framework).
- Motif documenté : `Round` manipule volontairement des membres « protégés » de
  `Team` (`_add_round`, `_modify_round`, `_remove_round`, `_results`). Les
  avertissements de linter « protected member » sur ce point sont attendus.

### Statistiques (clés en mémoire, non persistées — voir `cst.py`)
`STAT_POINTS`, `STAT_WINS`, `STAT_BYES`, `STAT_OPPONENTS`, `STAT_MATCHES`. C'est le format du dict `stats` consommé par les tirages.

---

## 4. Tirages (`core/draws/`)

Chaque tirage est un module exposant `NAME`, `DESCRIPTION`, `DEFAULT` (dict d'options)
et une coroutine :

```python
async def generate_draw(
    teams_by_match: int,
    stats: dict,
    bye_teams: list = (),
    config: dict | None = None,
    on_progress=None,      # callback async optionnel : async (percent: float, message: str)
) -> list:                 # liste de manches, chaque manche = liste triée de numéros d'équipes
    ...
```

Le registre (`draws/__init__.py`) expose `DRAWS`, `DEFAULT_DRAW`, `available()`,
`default_config(name)` et `generate(name, ...)`.

Trois algorithmes :
1. **`deterministic`** (par défaut) — applique les règles suisses. Calcul matriciel
   (`numpy`) d'une matrice de possibilités puis dérivation d'un appariement valide.
   Déterministe et reproductible.
2. **`genetic`** — applique aussi les règles suisses. Recherche heuristique
   (population/mutation/sélection) pour les grands espaces de solutions ; CPU-bound
   → isoler via un executor. Reproductible avec une seed fixée.
3. **`random`** — **n'applique pas** les règles suisses. Appariement aléatoire
   (tests, démo, premier round sans historique). Seed configurable.

Contrainte `max_disparity` (cf. §1) fournie via `config` (sauf `random`). Si aucun
appariement valide n'existe, lever une exception métier de `core/exception.py`
(`DrawImpossibleError`) invitant à augmenter le paramètre.

---

## 5. API REST + WebSocket

| Méthode | Route                         | Description                         |
|---------|-------------------------------|-------------------------------------|
| GET     | `/api/tournament`             | Tournoi courant + statut            |
| POST    | `/api/tournament`             | Créer / charger un tournoi          |
| GET/POST/DELETE | `/api/teams`          | Gérer les équipes                   |
| GET     | `/api/rounds`                 | Liste des rounds                    |
| POST    | `/api/rounds`                 | Créer un round (déclenche un tirage)|
| GET     | `/api/rounds/{n}`             | Détail d'un round + matchs          |
| PUT     | `/api/rounds/{n}/matches/{m}` | Saisir un résultat                  |
| GET     | `/api/rankings?round=n`       | Classement                          |
| GET     | `/api/draws`                  | Algorithmes disponibles + options   |
| GET/PUT | `/api/settings`               | Lire / modifier les settings (modale UI)|
| WS      | `/ws`                         | Progression du tirage / temps réel  |
| GET     | `/api/history/tournaments`    | Liste des sauvegardes (toutes années)|
| GET     | `/api/history/players`        | Stats agrégées par joueur (multi-années)|
| GET     | `/api/history/players/{name}` | Fiche joueur : détail année par année|

Les DTO Pydantic (`schemas.py`) exposent des champs anglais : `TeamDTO` (`number`,
`wins`, `byes`, `points`, `status`, `joker`, `players`), `RankEntryDTO`
(`rank`, `team`, `wins`, `points`), etc. La traduction des états métier français vers
des valeurs d'API stables se fait dans `services.py`.

> **Autocomplétion des joueurs** : il n'existe **pas** de stockage d'historique de
> joueurs côté serveur (l'ancienne classe `PlayerHistory`/fichier `hist_jrs`, vestige
> wxPython, a été **supprimée**). Pour proposer des suggestions de prénom/nom à
> l'inscription, le frontend interroge `GET /api/history/players` : chaque entrée
> agrégée expose `name`, `firstname`, `lastname` (+ stats). C'est la **source unique**
> des joueurs des éditions précédentes.

---

## 6. Frontend web (`tourbillon-ui/`)

SPA **Vue 3 + Vite** (Pinia pour l'état, `api/client.js` pour REST). Trois espaces
servis par le routeur (`/admin`, `/display`, `/history`) :

- **Admin** (`views/admin/`) : inscription des équipes/joueurs, lancement d'un tirage
  (choix algo + options + progression), round courant avec **saisie des scores**,
  classement. L'inscription propose l'**autocomplétion des prénoms/noms** à partir de
  `GET /api/history/players` (joueurs des éditions précédentes). L'**édition des
  settings** (modale `SettingsModal.vue`, via `GET`/`PUT /api/settings`) est réservée
  à cet espace : le bouton d'accès vit dans la sidebar Admin. Les espaces **Display**
  et **History** sont en lecture seule et n'exposent **pas** les settings (aucun
  réglage propre à ces vues pour le moment ; on pourra en exposer plus tard si un
  paramètre purement d'affichage apparaît).
- **Display** (`views/display/`) : HMI **lecture seule** plein écran pour projection
  (inscriptions, classement temps réel, matchs du round par emplacement). Rafraîchi
  via WebSocket.
- **History** (`views/history/`) : consultation transverse **lecture seule** — charge
  toutes les sauvegardes du dossier et affiche les **statistiques par joueur d'année
  en année** (fiche joueur, palmarès, évolution).

REST pour le CRUD, WebSocket pour le temps réel. Éviter jQuery.

---

## 7. Conventions de développement

- **Dépendances & venv** : **Poetry** exclusivement (`pyproject.toml`, `poetry.lock`).
  Ne pas utiliser pip/venv/pipenv/conda directement. Toute dépendance **importée
  directement** dans le code doit être **déclarée explicitement** (p. ex. `pydantic`).
  Réciproquement, **ne déclarer QUE les dépendances importées directement** : ne pas
  lister dans le `pyproject.toml` celles qui ne sont que tirées transitivement
  (p. ex. `httpx` ou `websockets`, fournies via `fastapi.testclient`/`uvicorn[standard]`).
- **Python 3.10+**, annotations de type dans le nouveau code, mais **typage simple
  uniquement** : n'utiliser que les **primitives** (`int`, `str`, `float`, `bool`,
  `list`, `dict`, `tuple`, `set`, `None`). **Pas** d'`import` depuis `typing`. Syntaxe
  native (`list`, `dict`, `str | None`).
- **Langue : anglais obligatoire pour TOUT le code** — noms, commentaires, docstrings,
  messages de log/exception, doc technique. (Ce fichier d'instructions peut rester en
  français.) **Seule exception** : les clés/valeurs YAML persistées (format legacy
  français), produites uniquement au moment de la (dé)sérialisation.
- **Tests** : `pytest` (dossier `tests/`, `asyncio_mode = "auto"`). Toute nouvelle
  logique métier ou de tirage doit être testée ; les tirages doivent être
  **déterministes et testables**.
- **Async** : privilégier `asyncio` ; isoler le CPU-bound via un executor.
- **Ne jamais casser** la lecture des anciens fichiers YAML.
- Garder `core/` **indépendant** de l'API et du framework web.
- **Exceptions** : importer directement depuis `core/exception.py` là où on en a
  besoin (p. ex. `from ...core.exception import DrawError`). Pas de module
  d'indirection/ré-export. Attraper `DrawError` couvre `DrawImpossibleError` et
  `DrawStopError`.

### Exécuter localement
```bash
poetry install                      # backend
cd tourbillon-ui && npm install && npm run build && cd ..   # frontend
poetry run tourbillon               # démarre le serveur (http://localhost:8000)
poetry run pytest                   # suite de tests
```
Interfaces : `/admin`, `/display`, `/history`.

> **Note environnement** : dans certains shells la sortie du terminal peut être
> tronquée/brouillée. En cas de doute sur le résultat d'une commande, rediriger vers
> un fichier du workspace puis le lire.

---

## 8. Références rapides

- Fichiers de sauvegarde d'exemple : `../Sauvegardes Tournois/*.yml` / `*.trb`
  (données historiques 2005→aujourd'hui, à garder lisibles).
- Prototype web historique (obsolète, jQuery) : `../billon-web/` — source d'inspiration
  pour l'affichage écran géant uniquement, **ne pas** en réutiliser le code.
- Entête ASCII des dumps YAML : `tourbillon/assets/banner.txt` via `assets.banner()`.
