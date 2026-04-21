# Tuan 1 - Phan tich repo tham khao

Reference repo duoc doc va doi chieu:

- Mot repo cong khai ve Chinese Chess duoc viet bang Python
- Tai lieu phan tich noi bo dung de tach ranh gioi tham khao va phan tu trien khai

## Reference Snapshot

- Ten repo: public Chinese Chess Python reference repo
- Ngon ngu: Python
- Thu vien giao dien: `pygame`
- Tep chinh quan trong:
  - `CchessEngine.py`
  - `CchessAI.py`
  - `CchessMain.py`
  - `requirements.txt`
- Dac diem chung:
  - repo nho, tap trung vao demo game choi duoc
  - engine, AI va UI da tach thanh 3 tep chinh, nhung van con kha don khoi

## Architecture

- Modules and responsibilities:
  - `CchessEngine.py`: luu trang thai ban co, sinh nuoc di, kiem tra chieu, doi tuong nuoc di
  - `CchessAI.py`: danh gia ban co va tim nuoc di bang Minimax/Alpha-Beta
  - `CchessMain.py`: game loop, xu ly input, ve giao dien, chon do kho
- Board representation:
  - ban co 10x9 dang danh sach 2 chieu
  - moi o luu ma chuoi ngan cho mau quan va loai quan
- Move generation flow:
  - sinh nuoc di theo tung loai quan
  - loc lai cac nuoc khong hop le
- State transition and undo flow:
  - co `makeMove`
  - co `undoMove`
  - cache vi tri tuong de kiem tra nhanh hon
- AI/search/evaluation flow:
  - dung heuristic material + bang gia tri vi tri
  - dung tim kiem de sau theo do kho

## Reference-Inspired Ideas

- Tach `engine`, `ai`, `ui` thanh cac module rieng.
- Dung mot doi tuong trang thai ban co de luu:
  - ban co
  - ben den luot
  - vi tri 2 tuong
  - lich su nuoc di
- Ho tro `make_move` va `undo_move` som de ve sau co the tai su dung cho tim kiem.
- Sinh nuoc di gia truoc, sau do loc nuoc hop le.
- Dieu chinh do kho AI bang do sau tim kiem.

## Do Not Copy Directly

- Khong sao chep logic sinh nuoc di theo tung quan.
- Khong sao chep nguyen ten tep, ten ham, ten lop.
- Khong sao chep bang diem vi tri va cac hang so heuristic.
- Khong sao chep giao dien, hinh anh va cau chuc README.
- Khong sao chep nguyen kieu to chuc 3 tep lon neu co the tach module sach hon.

## DSA Extraction

| DSA area | Where it appears in the reference repo | Huong su dung cho do an moi | Cach dua vao bao cao cuoi ky |
| --- | --- | --- | --- |
| Board representation | `CchessEngine.py` luu ban co 10x9 | reference-inspired idea | Nhan manh viec tu xay dung mo hinh ban co 10x9 phu hop luat co tuong |
| Move generation | `CchessEngine.py` co ham sinh nuoc theo tung quan | own implementation target | Bao cao ve cach tach bo sinh nuoc theo tung loai quan |
| Legal move validation | `CchessEngine.py` loc nuoc khong hop le, xu ly doi mat tuong | own implementation target | Giai thich bo loc nuoc hop le sau khi sinh nuoc di gia |
| Game tree search | `CchessAI.py` duyet cay trang thai | reference-inspired idea | Trinh bay bai toan cay tro choi va cac trang thai ke tiep |
| Minimax | `CchessAI.py` | reference-inspired idea | Neu ro se tu viet lai Minimax dua tren state transition cua project |
| Alpha-beta pruning | `CchessAI.py` | reference-inspired idea | Nhan manh cat tia de giam so nut duyet trong thuc nghiem |
| Evaluation function | `CchessAI.py` dung gia tri quan co + vi tri | own implementation target | Bao cao cach chon heuristic don gian, phu hop muc tieu sinh vien |
| Game state transitions | `makeMove`, `undoMove` trong `CchessEngine.py` | own implementation target | Nhan manh make/undo la tang nen cho AI va kiem thu |
| Debugging logic | repo chua co test ro rang | own implementation target | Bao cao cach tu them test vi tri mini va test round-trip make/undo |
| Complexity discussion | de sau tim kiem va so nuoc di anh huong toc do | reference-inspired idea | Giai thich muc sinh vien theo `O(b^d)` va vai tro cat tia |

## Quality Notes

- Repo tham khao chua co test tu dong, day la diem can tranh lap lai.
- `requirements.txt` co ca module thu vien chuan, khong nen hoc theo nguyen xi.
- UI va engine van con gan nhau hon muc can thiet.
- Cach loc nuoc hop le duoc nhan xet la dung duoc cho demo, nhung co the cham neu lap lai qua nhieu.
- Co dau hieu mot so kiem tra nuoc di viet theo cach mong manh, vi vay khong nen sao chep dong ma lenh.

## Ket luan cho pham vi tu lam

- Se tham khao y tuong tach module, state object, make/undo, va huong AI search.
- Se tu viet lai:
  - mo hinh quan co
  - setup ban dau
  - sinh nuoc di
  - bo loc nuoc hop le
  - heuristic
  - test
- Phan DSA can nhan manh trong bao cao la engine, state transition, move generation, legal filtering, va AI search; giao dien chi la phan ho tro.
