# Chinese Chess Project

Week 1 scaffold for a Data Structures and Algorithms course project about building a Chinese Chess game with AI.

## Week 1 scope completed

- summarized the core Chinese Chess rules
- analyzed a public Python Chinese Chess reference repository
- defined the project architecture and DSA scope
- created the initial Python project scaffold
- implemented the first engine foundation:
  - board representation
  - piece data model
  - initial state setup
  - move history
  - `make_move` and `undo_move`
  - baseline material evaluation
- added basic unit tests for the week 1 foundation

## What is intentionally not done yet

- full move generation for all pieces
- legal move filtering and check detection
- minimax
- alpha-beta pruning
- playable UI

These items are left for the next weeks so the report stays aligned with the real implementation status.

## Project structure

```text
chinese_chess_project/
├── tests/
├── chinese_chess_ai/
│   ├── ai/
│   └── engine/
├── main.py
└── requirements.txt
```

## Run

```bash
python3 main.py
python3 -m unittest discover -s tests
```

## Reference boundary

- Reference-inspired ideas:
  - split engine, AI, and UI
  - use a dedicated game state object
  - support apply/undo for future search
  - use search plus heuristic evaluation for the AI
- Own implementation in this folder:
  - module structure
  - board data model using enums and dataclasses
  - initial state setup
  - state transition code
  - test layout
  - report wording
