# Bao cao tien do tuan 1

## 1. Muc tieu tuan 1

- Tim hieu luat co tuong va chuyen hoa thanh yeu cau ky thuat.
- Doc repo tham khao de rut ra y tuong va gioi han tham khao an toan.
- Xac dinh kien truc tong quat va cac phan DSA trong tam cua do an.
- Tao khung project ban dau cho game co tuong co AI.

## 2. Cac cong viec da thuc hien

- Tom tat cac luat co tuong can thiet cho engine.
- Phan tich mot repo tham khao cong khai ve Chinese Chess.
- Xac dinh cach tach project thanh `engine/` va `ai/`.
- Lap bang cac nhom DSA can theo doi trong bao cao.
- Tao project `chinese_chess_project/` va cac module nen tang.
- Viet test co ban cho setup ban dau va state transition.

## 3. Ket qua dat duoc

- Co tai lieu tong hop luat o `docs/week1/01_rules_summary.md`.
- Co tai lieu phan tich repo tham khao o `docs/week1/02_reference_repo_analysis.md`.
- Co tai lieu kien truc va pham vi DSA o `docs/week1/03_architecture_and_dsa.md`.
- Da tao duoc scaffold ma nguon gom:
  - `chinese_chess_ai/engine/types.py`
  - `chinese_chess_ai/engine/constants.py`
  - `chinese_chess_ai/engine/moves.py`
  - `chinese_chess_ai/engine/state.py`
  - `chinese_chess_ai/engine/rules.py`
  - `chinese_chess_ai/ai/evaluate.py`
  - `chinese_chess_ai/ai/search.py`
- Da hien thuc duoc:
  - ban co 10x9
  - setup vi tri ban dau
  - luu ben den luot
  - luu lich su nuoc di
  - `make_move` va `undo_move`
  - ham danh gia material co ban
- Da co bo test don gian trong `tests/test_state.py`.

## 4. Cac phan DSA da xac dinh

- Board representation bang ma tran 10x9.
- Data model cho quan co bang enum va dataclass.
- Game state transition voi `make_move` va `undo_move`.
- Move history dong vai tro stack de phuc vu quay lui.
- Move generation va legal move validation la phan DSA se lam tiep.
- Heuristic evaluation, Minimax, Alpha-Beta la phan AI/DSA cot loi cua cac tuan sau.
- Complexity se bao cao o muc sinh vien theo mo hinh `O(b^d)` cho tim kiem.

## 5. Kho khan / van de ton dong

- Luat co tuong co nhieu rang buoc dac thu, dac biet la phao, ma bi chan, tinh, va doi mat tuong.
- Chua hien thuc sinh nuoc di day du nen AI chua the chay.
- Chua co UI; hien tai moi dung scaffold va test nen tang.

## 6. Ke hoach tuan 2

- Hien thuc bo sinh nuoc di cho tung loai quan.
- Bo sung legal move filtering.
- Them test cho cac tinh huong luat dac biet.
- Neu engine on dinh, bat dau noi vao khung AI da tao san.
