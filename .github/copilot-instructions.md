# TourBillon — Instructions Copilot & Plan de refonte

> Ce fichier sert de **contexte permanent** pour tout développement sur TourBillon.
> Chargez-le systématiquement avant de coder. Il décrit le domaine métier, l'état
> actuel du code et le plan de migration de wxPython vers une architecture web.

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
- Elle marque un nombre de points forfaitaire égal au paramètre **`points_par_manche`**
  (points de victoire d'une manche, p. ex. 12) et compte comme une **partie gagnée**.
- Une même équipe ne doit pas être chapeau deux fois dans la mesure du possible.

### Vocabulaire (le code mélange français et anglais — à uniformiser en anglais)
| Français (legacy)   | Anglais (cible)   | Description                                        |
|---------------------|-------------------|----------------------------------------------------|
| Tournoi             | Tournament        | L'événement complet                                |
| Partie              | Round             | Un tour d'appariements (Swiss round)               |
| Manche              | Match             | Une rencontre entre `teams_by_match` équipes       |
| Équipe              | Team              | Une équipe (1..N joueurs)                           |
| Joueur              | Player            | Un joueur                                          |
| Tirage              | Draw              | L'algorithme d'appariement d'un round              |
| Chapeau             | Bye               | Équipe sans adversaire sur un round (points forfait)|
| Piquet / location   | Location / lane   | Emplacement physique de jeu                        |
| Classement          | Ranking           | Classement des équipes                             |

### États (voir `tourbillon/core/cst.py`)
- **Match** : `M_EN_COURS`, `M_TERMINEE`
- **Team** : `E_INCOMPLETE`, `E_ATTEND_TIRAGE`, `E_EN_COURS`
- **Round** : `P_ATTEND_TIRAGE`, `P_EN_COURS`, `P_COMPLETE`, `P_TERMINEE`
- **Tournament** : `T_INSCRIPTION`, `T_ATTEND_TIRAGE`, `T_PARTIE_EN_COURS`

---

## 2. État actuel du code (legacy)

### Structure `TourBillon/tourbillon/`
- `__main__.py` — point d'entrée ; choisit GUI (wxPython) ou serveur selon options.
- `config.py`, `logger.py` — configuration et logs.
- `core/` — **cœur métier réutilisable** :
  - `tournament.py` — classe `Tournament` (+ `load`/`dump` YAML).
  - `round.py` — classe `Round`.
  - `team.py` — classe `Team`.
  - `player.py` — classe `Player` + `PlayerHistory`.
  - `match.py` — classe `Match`.
  - `cst.py` — constantes d'état.
  - `exception.py` — exceptions métier.
  - `draws/` — algorithmes de tirage (voir §3).
- `gui/` — **interface wxPython (à supprimer)** : `app.py`, `fenetre.py`, `grille.py`,
  `dlg*.py`, `barres.py`, `evenements.py`.
- `server/app.py` — squelette serveur non implémenté (`TourBillonServer`).
- `assets/` — ressources statiques hors code : `banner.txt` (entête ASCII écrite en
  tête des dumps YAML) exposée via `assets.banner()`. L'ancien dossier `images/`,
  spécifique wxPython, a été supprimé.

### Persistance
- Format **YAML** (`.yml` / `.trb`), voir `Sauvegardes Tournois/`.
- Clés YAML en français : `tournoi`, `inscription`, `jokers`, `parties`, `enregistrement`.
- **À conserver** : la rétro-compatibilité de lecture des anciens fichiers est
  obligatoire (données historiques 2005→aujourd'hui).

### Le projet `billon-web/` (prototype existant)
- FastAPI minimal (`main.py`) + pages HTML statiques (`ranking.html`, `round.html`)
  + jQuery. Lit les données via `billon/loader.py`, `rankings.py`, `rounds.py`.
- **Rôle** : c'est une **HMI d'affichage** (dashboard) destinée à montrer les
  résultats de la partie en cours sur **écran géant** (classement, matchs du round).
  Lecture seule, pas de saisie. Sert de **base d'inspiration** pour l'interface
  d'affichage (voir §6), mais sera remplacé/fusionné (abandon de jQuery).

---

## 3. Algorithmes de tirage (`core/draws/`)

Chargement dynamique des modules dans `draws/__init__.py` ; chaque module expose
une classe `ThreadTirage` avec `NOM`, `DESCRIPTION`, `DEFAUT` (config).

Modules présents : `ascending.py`, `level_ag.py`, `level_dt.py`, `random_ag.py`,
plus des `.pyc` legacy (algorithmes génétiques `*_ag`, `*_dt`).

**Correspondance legacy → cible** (repartir de zéro, supprimer le legacy) :
- `level_dt` (`*_dt`) → nouveau tirage **`deterministic`**.
- `level_ag` (`*_ag`) → nouveau tirage **`genetic`**.
- `random_ag` → nouveau tirage **`random`** (sans règles suisses).
- `ascending` et les autres variantes legacy → **supprimés**.
Les anciens modules servent uniquement de **référence** (règles, calculs) ; le code
est réécrit proprement (async, typage primitif, testable), pas migré tel quel.

### Problèmes actuels
- Basés sur `threading.Thread` (`BaseThreadTirage` dans `utils.py`) avec `Event`,
  callbacks et rapports — complexe et difficile à tester.
- Mélange de la logique de calcul et de la mécanique de threads.
- Algorithmes génétiques (`*_ag`) coûteux et peu déterministes.

### Cible
- **Fonctions/coroutines pures** : `async def draw(...) -> list[Match]`.
- Remplacer `threading` par **`asyncio`** (+ `run_in_executor` si CPU-bound, ou
  `anyio.to_thread` pour les gros calculs). Progression via `async` generator /
  callback `async`.
- **Trois types de tirages à refaire** (les autres variantes legacy sont supprimées) :
  1. **Déterministe** (`deterministic`) — applique les règles du système suisse.
     Calcule une **matrice de possibilités** d'appariements (compatibilités entre
     équipes selon victoires, re-rencontres, `max_disparity`) puis en dérive un
     appariement valide. À **optimiser via du calcul matriciel** (p. ex. `numpy`)
     pour accélérer le calcul sur beaucoup d'équipes. Algorithme **par défaut**
     (déterministe et reproductible).
  2. **Génétique** (`genetic`) — applique aussi les règles du système suisse.
     Recherche heuristique (population/mutation/sélection) pour les cas où l'espace
     de solutions est trop grand ; CPU-bound → isoler via un executor. Rendre le
     résultat **reproductible** en tests (seed fixée).
  3. **Aléatoire** (`random`) — **n'applique pas** les règles du système suisse.
     Appariement purement aléatoire (utile pour tests, démo, ou premier round sans
     historique). Seed configurable pour la reproductibilité.
- Respecter la contrainte **`max_disparity`** (§1) — paramètre **de tirage** fourni
  via `config`, pas un paramètre global : n'apparier que des équipes dont l'écart de
  victoires est `<= max_disparity`. Si aucun appariement valide n'existe, lever une
  exception métier (voir `core/exception.py`) invitant l'opérateur à augmenter le
  paramètre — ne pas produire un tirage invalide. (Ne s'applique pas au tirage
  `random`, qui ignore les règles suisses.)
- API cible d'un tirage (typage primitif uniquement, pas d'import `typing`) :
  ```python
  async def generate_draw(
      teams_by_match: int,
      stats: dict,
      bye_teams: list = (),
      config: dict | None = None,
      on_progress=None,  # optional async callback: async (percent: float, message: str)
  ) -> list:            # list of matches, each a tuple of team numbers
      ...
  ```

---

## 4. Objectifs de la refonte

1. **Supprimer wxPython** et tout le dossier `gui/`.
2. **Interface 100 % web** : backend API + frontend web moderne.
3. **Simplifier les tirages** : logique pure, `asyncio` au lieu de `threading`.
4. **Conserver le cœur métier** `core/` (Tournament/Round/Team/Player/Match) en le
   nettoyant progressivement (nommage anglais, typage, tests).
5. **Garder la compatibilité YAML** en lecture (fichiers historiques).
6. **Refondre la configuration** (`config.py`) : purger les paramètres liés à
   wxPython, réorganiser autour des nouveaux besoins (API, UI web, tirages).

### Non-objectifs (pour l'instant)
- Réécriture complète du modèle de données (migration progressive préférée).
- Changement de format de persistance (YAML conservé, DB optionnelle plus tard).

---

## 5. Architecture cible

```
tourbillon/
  core/                 # Domaine métier (conservé, nettoyé, typé, testé)
    tournament.py, round.py, team.py, player.py, match.py, cst.py, exception.py
    draws/              # Tirages : fonctions async pures + registre
  api/                  # NOUVEAU : backend FastAPI
    app.py              # création de l'app + montage des routers
    routers/            # tournaments, rounds, teams, draws, rankings
    schemas.py          # modèles Pydantic (DTO)
    services.py         # orchestration métier ↔ persistance
    state.py            # état applicatif (tournoi courant, verrous asyncio)
  web/                  # NOUVEAU : frontend (3 interfaces, voir §6)
    admin/              # Inscription des équipes + gestion des résultats
    display/            # Affichage écran géant de la partie en cours (lecture seule)
    history/            # Statistiques par joueur d'année en année (tous les fichiers)
  __main__.py           # point d'entrée : lance uvicorn (plus de wxPython)
```

- **Backend** : FastAPI + Uvicorn, endpoints REST + **WebSocket/SSE** pour la
  progression des tirages et le rafraîchissement temps réel des scores.
- **Persistance** : services au-dessus de `core.tournament.load/dump` (YAML).
- **Concurrence** : `asyncio`, un verrou par tournoi pour les écritures.

### Rework de la configuration (`config.py`)

La config actuelle (`TypedConfigParser`, format `.ini`, clés en français) est
fortement couplée à wxPython et mélange des préoccupations très différentes. Elle
doit être refondue :

- **À supprimer** (spécifique wxPython / affichage legacy) : section `INTERFACE`
  (`GEOMETRIE`, `MAXIMISER`, `PLEIN_ECRAN`, `IMAGE`…) et toute la section `AFFICHAGE`
  (polices au format wx `"12;70;90;..."`, couleurs RGBA, `GRILLE_*`, `MESSAGE_*`).
- **À conserver / migrer** (métier, réutilisable) : section `TOURNOI`
  (`JOUEURS_PAR_EQUIPE`, `POINTS_PAR_MANCHE`, `EQUIPES_PAR_MANCHE`,
  `CLASSEMENT_*`, `ALGORITHME_DEFAUT`…) et les sections de **tirages** (une par
  algorithme, alimentées par `draws.TIRAGES[...].DEFAUT`).
- **Cible** :
  - Séparer clairement **3 domaines** de configuration :
    1. **Serveur / API** (hôte, port, chemin des sauvegardes, auto-save…).
    2. **Métier / tournoi** (valeurs par défaut d'un nouveau tournoi + tirages).
    3. **UI web** : préférences côté client (thème, langue, options d'affichage
       écran géant), gérées par le frontend et **non** dans `config.py` Python.
  - Remplacer le `.ini` par un format simple et typé côté backend (au choix :
    YAML/TOML chargé en `dict`, ou modèles Pydantic `Settings`).
  - Clés et valeurs en **anglais**, **typage primitif uniquement** (§9).
  - Exposer les valeurs par défaut du tournoi et les options de tirage via l'API
    (`GET /api/draws`, config d'un nouveau tournoi) pour que l'UI web les consomme.

---

## 6. Frontend web

- **Stack imposée** : **Vue 3** + Vite. UI moderne et responsive. Éviter jQuery
  (le prototype `billon-web` est legacy).
- **Trois interfaces distinctes** :

  ### 6.1 Interface d'administration (`web/admin/`)
  Poste opérateur — inscription et gestion. Écrans :
  1. **Inscription** des équipes / joueurs.
  2. **Lancement d'un tirage** (choix algorithme + options, barre de progression).
  3. **Round courant** : matchs par emplacement, **saisie des scores**.
  4. **Classement** (consultation), filtrable par round.
  5. **Historique** / export (impression, PDF).

  ### 6.2 Interface d'affichage écran géant (`web/display/`)
  HMI **lecture seule** (inspirée de `billon-web/`), plein écran, grande
  typographie, pensée pour être projetée dans la salle. Écrans :
  1. **Inscription** des équipes / joueurs (uniquement pendant la phase d'inscription).
  2. **Classement en temps réel** de la partie en cours.
  3. **Matchs du round courant** par emplacement (qui joue où).
  - Rafraîchissement automatique via WebSocket/SSE, aucune interaction requise.

  ### 6.3 Interface d'historique (`web/history/`)
  HMI **lecture seule** de consultation transverse — **statistiques par joueur
  d'année en année**. Charge **tous les fichiers de sauvegarde** présents dans le
  dossier des sauvegardes (`Sauvegardes Tournois/*.yml` / `*.trb`), les agrège et
  affiche l'évolution des performances par personne au fil des éditions. Écrans :
  1. **Fiche joueur** : participations, classements, victoires, points par année.
  2. **Palmarès / comparatifs** : évolution multi-années, records, tendances.
  - S'appuie sur des endpoints d'agrégation (voir §7) ; la lecture doit rester
    rétro-compatible avec les anciens fichiers YAML (§2).

- Communication : REST pour CRUD, WebSocket/SSE pour temps réel.
- Servir le(s) build(s) statique(s) via FastAPI (`StaticFiles`) en production.

---

## 7. API REST (esquisse)

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
| WS      | `/ws/draw`                    | Progression du tirage en cours      |
| GET     | `/api/history/tournaments`    | Liste des sauvegardes (toutes années)|
| GET     | `/api/history/players`        | Stats agrégées par joueur (multi-années)|
| GET     | `/api/history/players/{name}` | Fiche joueur : détail année par année|

---

## 8. Plan de migration (par étapes)

1. **Étape 0 — Cadre** : ce fichier + mise à jour `pyproject.toml`
   (retirer le groupe `gui`/`wxPython`, ajouter `fastapi`, `uvicorn`, `websockets`).
2. **Étape 1 — Nettoyer le cœur** : typage, tests `pytest` sur
   `core/` (tournament, round, team, player, match). Supprimer les `.pyc` legacy.
3. **Étape 2 — Tirages async** : refondre `draws/` en fonctions/coroutines pures,
   implémenter les 3 tirages (`deterministic`, `genetic`, `random`), retirer
   `BaseThreadTirage` et les variantes legacy, couvrir de tests.
4. **Étape 3 — Backend API** : créer `tourbillon/api/` (FastAPI) avec services de
   persistance YAML et endpoints REST + WebSocket de progression. Inclut le
   **rework de `config.py`** (voir §5) : purge wxPython, découpage serveur/métier,
   format typé, exposition via l'API.
5. **Étape 4 — Frontend** : SPA (Vue/Vite) consommant l'API ; écrans inscription,
   tirage, round, classement.
6. **Étape 5 — Suppression wxPython** : supprimer `gui/`, adapter `__main__.py`
   pour lancer uvicorn, mettre à jour la doc (`README.rst`).
7. **Étape 6 — Packaging** : build frontend servi par FastAPI, scripts poetry,
   éventuel binaire (pyinstaller) mono-fichier lançant le serveur + navigateur.

---

## 9. Conventions de développement

- **Gestion des dépendances & venv** : **Poetry** exclusivement (`pyproject.toml`,
  `poetry.lock`). Ne pas utiliser pip/venv/pipenv/conda directement.
- **Python 3.10+**, avec annotations de type dans le nouveau code, mais **typage
  simple uniquement** : n'utiliser que les **primitives Python** (`int`, `str`,
  `float`, `bool`, `list`, `dict`, `tuple`, `set`, `None`). **Pas de types
  complexes** ni d'`import` depuis `typing` (pas de `Optional`, `Union`, `Callable`,
  `Awaitable`, `TypeVar`, `Generic`, etc.). Utiliser la syntaxe native
  (`list`, `dict`, `str | None`) plutôt que des génériques importés.
- **Langue : anglais obligatoire pour TOUT** — noms (variables, fonctions, classes,
  modules), commentaires, docstrings, messages de log/exception, et documentation
  technique (README, docstrings, commentaires de code). Migrer le legacy français
  au fil de l'eau. (Ce fichier d'instructions peut rester en français.)
- **Tests** : `pytest` (dossier `tests/`). Toute nouvelle logique métier ou de
  tirage doit être testée. Les tirages doivent être **déterministes et testables**.
- **Async** : privilégier `asyncio` ; isoler le CPU-bound via un executor.
- **Ne jamais casser** la lecture des anciens fichiers YAML (`Sauvegardes Tournois/`).
- Garder `core/` **indépendant** de l'API et du framework web (pas d'import FastAPI
  dans `core/`).
- **Exceptions** : importer directement les exceptions métier depuis
  `core/exception.py` là où on en a besoin (p. ex. `from ...core.exception import
  DrawError`). Ne pas créer de module d'indirection/ré-export dans l'API. Les
  sous-classes suffisent : attraper `DrawError` couvre `DrawImpossibleError` et
  `DrawStopError`.
- Commits/PR ciblés par étape du plan ci-dessus.

---

## 10. Références rapides

- Fichiers de sauvegarde d'exemple : `../Sauvegardes Tournois/*.yml` / `*.trb`.
- Prototype web existant : `../billon-web/` (FastAPI + jQuery — pour l'affichage sur écran gean de l'inscription ou de la partie en cours).
- Algorithmes de référence (legacy, à réécrire) : `tourbillon/core/draws/level_dt.py`
  (→ `deterministic`), `level_ag.py` (→ `genetic`), `random_ag.py` (→ `random`).
