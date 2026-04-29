# Chinese Chess Project

Week 2 state of a Data Structures and Algorithms course project for building a
Chinese Chess game with AI.

## Scope completed so far

- summarized the core Chinese Chess rules
- defined the project architecture and DSA scope
- implemented the engine foundation:
  - 10x9 board representation
  - piece data model
  - initial state setup
  - move history
  - `make_move` and `undo_move`
- completed the rules engine:
  - pseudo-legal move generation for all piece types
  - legal move filtering
  - check detection
  - flying-general handling
- added the first AI foundation:
  - material evaluation
  - positional bonus for soldiers
  - depth-limited negamax search
  - alpha-beta pruning
- added focused tests for state, rules, and search
- added week 2 report and DSA docstring notes in `docs/week2/`

## Current status

- `main.py` prints a simple engine summary from the initial position
- rules for all main piece types are implemented
- legal move filtering and check detection are available
- the AI search module can choose a move from legal candidates
- automated tests currently cover state, rules, and search behavior

## What is still minimal

- `main.py` is still a lightweight entry point, not a full playable interface
- evaluation is intentionally simple
- no repetition handling
- no advanced move ordering beyond basic heuristics
- no public GUI code is included in the current repo state

## Project structure

```text
chinese_chess_project/
├── docs/week2/
├── tests/
├── chinese_chess_ai/
│   ├── ai/
│   ├── engine/
│   └── gui/
├── main.py
└── requirements.txt
```

## Run

Print the current engine summary:

```bash
python3 main.py
```

Run all automated tests:

```bash
python3 -m unittest discover -s tests
```

Run one test module directly:

```bash
python3 tests/test_state.py
python3 tests/test_rules.py
python3 tests/test_search.py
```

## Implementation boundary

- Reference-inspired ideas:
  - split engine, AI, and UI
  - use a dedicated game state object
  - support apply/undo for search
  - use search plus heuristic evaluation for the AI
- Own implementation in this folder:
  - module structure
  - board data model using enums and dataclasses
  - initial state setup
  - state transition code
  - piece-specific move generation
  - legal-move filtering
  - search implementation
  - test layout
  - report wording
