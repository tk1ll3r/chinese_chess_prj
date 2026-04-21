# Tuan 1 - Kien truc tong quat va pham vi DSA

## Project Assumptions

- Thoi gian thuc hien: 4 tuan.
- Hinh thuc thuc hien: ca nhan.
- Ngon ngu chon cho ban scaffold hien tai: Python.
- Muc tieu uu tien: engine dung, AI muc co ban, UI don gian.
- Week 1 chi lam cac phan nen tang; chua tuyen bo da hoan tat engine day du.

## Minimal Playable Version

Phien ban choi duoc toi thieu cua do an can co:

- ban co 10x9 va setup dung
- sinh duoc nuoc di hop le cho cac quan
- luan phien luot choi
- phat hien thang thua co ban
- co it nhat 1 muc AI chay duoc bang Minimax + Alpha-Beta
- giao dien don gian de nguoi dung danh voi AI

## Milestones

### Week 1 - Study and Foundation

- tom tat luat co tuong
- phan tich repo tham khao
- chot kien truc
- xac dinh DSA trong tam
- tao scaffold ban dau

### Week 2 - Rules Engine

- sinh nuoc di cho tung loai quan
- kiem tra nuoc hop le
- xu ly chieu tuong, doi mat tuong
- viet test cho cac tinh huong mini

### Week 3 - AI and Play Loop

- ham danh gia ban co
- Minimax
- Alpha-Beta pruning
- giao dien/CLI cho phep choi co ban

### Week 4 - Integration and Report

- sua loi
- test lai cac truong hop chinh
- hoan thien bao cao
- chuan bi demo

## Must-Have vs Nice-to-Have

### Must-Have

- state model ro rang
- make/undo dung
- move generation hop le
- AI co the tim nuoc di
- bo test co ban cho engine
- phan bao cao DSA ro rang

### Nice-to-Have

- danh gia vi tri chi tiet hon
- move ordering
- giao dien `pygame`
- undo/redo tren giao dien
- ghi log nuoc di dep hon

## Testing Plan

- test setup ban dau:
  - so quan
  - vi tri 2 tuong
  - ben di truoc
- test state transition:
  - `make_move`
  - `undo_move`
  - round-trip khong lam hong board
- test rules theo vi tri nho:
  - ma bi can chan
  - tinh qua song
  - phao an qua man
  - doi mat tuong
- test AI:
  - tra ve nuoc hop le
  - khong tu dua minh vao trang thai sai

## DSA Report Scope

### Main DSA Contributions

- mo hinh ban co 10x9
- cau truc du lieu luu trang thai tran dau
- sinh va loc nuoc di hop le
- make/undo cho cay tro choi
- tim kiem Minimax va Alpha-Beta
- ham danh gia heuristic

### Data Structures

| Cau truc | Vi tri trong project | Vai tro |
| --- | --- | --- |
| Ma tran 10x9 | `chinese_chess_ai/engine/state.py` | Luu trang thai ban co |
| Enum + dataclass | `chinese_chess_ai/engine/types.py` | Bieu dien ben choi va loai quan |
| Stack lich su nuoc di | `move_history` trong `GameState` | Phuc vu undo va AI search |
| Cau hinh AI | `chinese_chess_ai/ai/search.py` | Gom tham so cho tim kiem |

### Algorithms

| Thuat toan / ky thuat | Trang thai hien tai | Ghi chu |
| --- | --- | --- |
| Sinh nuoc di theo tung quan | chua hoan tat | de lam week 2 |
| Legal move validation | chua hoan tat | de lam week 2 |
| Make/undo state transition | da co ban | da code trong week 1 |
| Material evaluation | da co ban | baseline cho week 1 |
| Minimax | chua hoan tat | de lam week 3 |
| Alpha-Beta pruning | chua hoan tat | de lam week 3 |

### DSA Area Tracking

| DSA area | Concept name | Where it appears in the project | Original or reference-inspired | Final report note |
| --- | --- | --- | --- | --- |
| Board representation | 10x9 matrix + `Piece` dataclass | `chinese_chess_ai/engine/state.py`, `types.py` | original implementation | Su dung ma tran 10x9 de truy cap theo toa do va de sinh nuoc di |
| Move generation | Piece-specific generators | `chinese_chess_ai/engine/rules.py` | own implementation target | Se tach ham cho tung quan de de debug va test |
| Legal move validation | Pseudo-legal then filter | `chinese_chess_ai/engine/rules.py` | reference-inspired idea, own implementation | Cach lam tham khao tu repo, nhung tu viet lai bo loc nuoc hop le |
| Game tree search | State tree exploration | `chinese_chess_ai/ai/search.py` | reference-inspired idea | Bai toan AI duyet cay trang thai tu `GameState` |
| Minimax | Depth-limited search | `chinese_chess_ai/ai/search.py` | own implementation target | Se mo ta Minimax de chon nuoc co loi nhat |
| Alpha-beta pruning | Branch pruning | `chinese_chess_ai/ai/search.py` | own implementation target | Se giai thich cat tia de giam thoi gian tim kiem |
| Evaluation function | Material heuristic | `chinese_chess_ai/ai/evaluate.py` | original implementation | Week 1 moi tao baseline bang diem gia tri quan |
| Game state transitions | Apply and undo move | `chinese_chess_ai/engine/state.py` | original implementation | Nen tang cho test va search |
| Debugging logic | Focused unit tests | `tests/test_state.py` | original implementation | Dung test vi tri mini thay vi debug tren van co lon |
| Complexity discussion | `O(b^d)` and transition cost | bao cao va `search.py` | reference-inspired framing | Giai thich muc sinh vien, khong dua ra con so qua chi tiet |

## Risks and De-Scoping Plan

- Rui ro lon nhat la luat co tuong co nhieu rang buoc dac thu.
- Neu UI cham, co the demo bang CLI truoc, UI de sau.
- Neu heuristic vi tri qua ton thoi gian, se giu muc material-first.
- Neu repetition rule qua phuc tap, co the de o muc ghi nhan gioi han cua phien ban.

## Kien truc module da chot

```text
chinese_chess_ai/
├── engine/
│   ├── types.py
│   ├── constants.py
│   ├── moves.py
│   ├── state.py
│   └── rules.py
└── ai/
    ├── evaluate.py
    └── search.py
```

- `engine/` la phan DSA cot loi.
- `ai/` la phan DSA nang hon, se duoc bo sung sau khi engine on dinh.
- `docs/week1/` luu toan bo dau ra va co so viet bao cao tien do.
