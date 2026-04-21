# Tuan 1 - Nhat ky thuc hien

Tai lieu nay ghi lai dung nhung gi da lam trong tuan 1, theo tung buoc.

## Buoc 1 - Tim hieu va tom tat luat co tuong

- Da lam gi:
  - tong hop lai cac luat can thiet de xay dung engine cho do an
  - xac dinh cac rang buoc dac thu anh huong truc tiep den code, nhu doi mat tuong, ma bi can chan, tinh khong qua song, va phao can man hinh khi an
- Dau ra tao duoc:
  - `docs/week1/01_rules_summary.md`
- Phan nao lien quan den DSA:
  - xac dinh cau truc du lieu 10x9
  - xac dinh bo sinh nuoc di theo tung quan
  - xac dinh nhu cau legal filtering sau khi sinh nuoc di gia
- Phan loai tham khao / tu lam / nhan manh DSA:
  - tham khao: luat choi chuan cua co tuong
  - tu lam: cach quy doi luat sang yeu cau module
  - can nhan manh: board representation, move generation, legal validation

## Buoc 2 - Doc va phan tich repo tham khao

- Da lam gi:
  - doc skill `repo-reader`
  - doc tai lieu noi bo `dylannni-reference-analysis.md`
  - doi chieu them mot repo cong khai ve Chinese Chess
  - tach ro y tuong co the hoc hoi va phan khong duoc sao chep
- Dau ra tao duoc:
  - `docs/week1/02_reference_repo_analysis.md`
- Phan nao lien quan den DSA:
  - board state
  - move generation
  - make/undo
  - evaluation
  - minimax va alpha-beta
- Phan loai tham khao / tu lam / nhan manh DSA:
  - y tuong tham khao:
    - tach engine, AI, UI
    - dung state object
    - co make/undo cho AI
  - se tu lam lai:
    - model du lieu
    - code engine
    - heuristic
    - test
  - can nhan manh:
    - phan DSA nam o engine va search, khong nam o viec doc repo

## Buoc 3 - Xac dinh kien truc tong quat cua project

- Da lam gi:
  - doc skill planner noi bo cho project Chinese Chess
  - chot huong rules-first
  - tach project thanh 2 cum chinh: `engine/` va `ai/`
  - xac dinh milestone 4 tuan de week 1 khong lam qua tam
- Dau ra tao duoc:
  - `docs/week1/03_architecture_and_dsa.md`
- Phan nao lien quan den DSA:
  - phan tach state, transitions, rules, search, evaluation
  - testing plan cho engine
- Phan loai tham khao / tu lam / nhan manh DSA:
  - y tuong tham khao:
    - tach engine va AI
    - uu tien dung engine truoc UI
  - se tu lam lai:
    - ten module
    - data model
    - test strategy
  - can nhan manh:
    - state transition, move legality, search complexity

## Buoc 4 - Xac dinh cac phan DSA chinh cua do an

- Da lam gi:
  - doc skill `dsa-explainer`
  - lap bang theo 10 nhom DSA can co trong bao cao
  - gan tung nhom vao module cu the trong project scaffold
- Dau ra tao duoc:
  - bang `DSA Area Tracking` trong `docs/week1/03_architecture_and_dsa.md`
- Phan nao lien quan den DSA:
  - toan bo buoc nay la phan DSA trong tam
- Phan loai tham khao / tu lam / nhan manh DSA:
  - y tuong tham khao:
    - dung 10 nhom DSA de trinh bay
  - se tu lam lai:
    - noi dung tung module va cach giai thich cho do an cua minh
  - can nhan manh:
    - board representation
    - make/undo
    - move generation
    - legal validation
    - minimax
    - alpha-beta
    - evaluation

## Buoc 5 - Tao khung project ban dau va module nen tang

- Da lam gi:
  - doc skill `board-game-ai-builder`
  - tao folder `chinese_chess_project/`
  - tao cac module:
    - `chinese_chess_ai/engine/types.py`
    - `chinese_chess_ai/engine/constants.py`
    - `chinese_chess_ai/engine/moves.py`
    - `chinese_chess_ai/engine/state.py`
    - `chinese_chess_ai/engine/rules.py`
    - `chinese_chess_ai/ai/evaluate.py`
    - `chinese_chess_ai/ai/search.py`
  - tao `main.py`, `README.md`, `requirements.txt`, `.gitignore`
  - tao `tests/test_state.py`
  - hien thuc duoc:
    - piece model bang enum + dataclass
    - setup ban dau cua van co
    - `GameState.initial()`
    - `build_move`
    - `make_move`
    - `undo_move`
    - render ASCII
    - material evaluation baseline
  - chua hien thuc:
    - full move generation
    - legal move filtering
    - minimax
    - alpha-beta
- Dau ra tao duoc:
  - ma nguon trong `chinese_chess_project/`
  - test tu dong co ban trong `tests/test_state.py`
- Phan nao lien quan den DSA:
  - state model
  - stack lich su nuoc di
  - board traversal
  - state transition
  - heuristic co ban
- Phan loai tham khao / tu lam / nhan manh DSA:
  - y tuong tham khao:
    - co make/undo de phuc vu search
    - tach rules va search
  - se tu lam lai:
    - tat ca code da tao trong folder moi
  - can nhan manh:
    - `GameState`
    - `move_history`
    - `material_score`
    - test round-trip make/undo

## Buoc 6 - Ghi lai ket qua va lap bao cao tien do

- Da lam gi:
  - tong hop lai cac dau ra da tao
  - viet ban tom tat tuan 1
  - viet bao cao tien do tuan 1 dua tren dung nhung muc da thuc hien
- Dau ra tao duoc:
  - `docs/week1/week1_summary.md`
  - `docs/week1/week1_progress_report.md`
- Phan nao lien quan den DSA:
  - lam ro phan nao la DSA cot loi, phan nao chi la scaffold
- Phan loai tham khao / tu lam / nhan manh DSA:
  - tham khao:
    - khung noi dung tu skill `dsa-explainer`
  - tu lam:
    - noi dung bao cao dua tren code va tai lieu vua tao
  - can nhan manh:
    - bao cao khong nhan nham UI la phan DSA chinh
