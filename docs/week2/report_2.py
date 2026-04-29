\documentclass[12pt,a4paper]{article}
\usepackage[utf8]{inputenc}
\usepackage[T5]{fontenc}
\usepackage[vietnamese]{babel}
\usepackage{geometry}
\geometry{top=2.5cm, bottom=2.5cm, left=3cm, right=2cm}
\usepackage{enumitem}
\usepackage{titlesec}
\usepackage{parskip}
\usepackage{xcolor}
\usepackage{amssymb}
\usepackage{hyperref}

% Định dạng tiêu đề các phần cho đẹp mắt
\titleformat{\section}{\large\bfseries\color{blue!70!black}}{\thesection.}{0.5em}{}
\titleformat{\subsection}{\normalsize\bfseries\color{black}}{\thesubsection.}{0.5em}{}

\begin{document}

% --- TRANG BÌA ---
\begin{titlepage}
    \centering
    \vspace*{1.5cm}
    {\Large \textbf{BÁO CÁO TIẾN ĐỘ ĐỒ ÁN - TUẦN 2}}\\[0.5cm]
    {\large \textbf{(Đồ án phát triển ứng dụng)}}\\[1cm]
    
    {\large \textbf{Lớp: IT003.Q21.CTTN}}\\[2.5cm]
    
    \begin{flushleft}
        \large
        \textbf{SINH VIÊN THỰC HIỆN}\\
        \vspace{0.3cm}
        \begin{tabular}{@{}ll}
            \textbf{Mã sinh viên:} & 25521829 \\
            \textbf{Họ và tên:} & Nguyễn Văn Thương \\
        \end{tabular}
    \end{flushleft}
    
    \vspace{2cm}
    
    {\Large \textbf{TÊN ĐỀ TÀI: GAME CỜ TƯỚNG \& AI}}\\[0.7cm]
    {\large \textbf{Chủ đề: Hoàn thiện engine nền tảng và chuẩn bị cho AI heuristic search}}\\[2cm]
    
    \vfill
\end{titlepage}

\newpage

\section*{CÁC NỘI DUNG CẦN BÁO CÁO}

\section{Giới thiệu đồ án}
\subsection{Mô tả chung về ứng dụng}
Đồ án hướng tới xây dựng một ứng dụng Cờ Tướng có khả năng quản lý trạng thái ván cờ, kiểm tra luật chơi và tiến tới tích hợp AI để tự động lựa chọn nước đi. Trong tuần 2, trọng tâm công việc không nằm ở giao diện mà tập trung vào phần lõi xử lý trò chơi, bởi đây là phần quyết định độ đúng đắn của toàn bộ hệ thống về sau.

Từ mã nguồn hiện tại của project, phần engine đã được tổ chức thành các module tương đối rõ ràng như \texttt{engine/state.py}, \texttt{engine/rules.py}, \texttt{ai/evaluate.py} và \texttt{ai/search.py}. Điều này cho thấy hướng triển khai của đồ án là tách riêng ba trách nhiệm chính: quản lý trạng thái bàn cờ, xử lý luật và phát triển AI. Trong phạm vi báo cáo tuần 2, phần đã hoàn thiện nổi bật nhất là mô hình hóa bàn cờ 10x9, dữ liệu quân cờ, lịch sử nước đi, cơ chế sinh nước đi hợp lệ và các hàm đánh giá trạng thái làm nền cho giai đoạn AI.

\subsection{Mô tả công việc đã thực hiện}
\begin{itemize}[label=--]
    \item Hoàn thiện cấu trúc cơ bản của dự án, xác định rõ các nhóm module \texttt{engine}, \texttt{ai}, \texttt{gui}, \texttt{tests} và \texttt{docs}.
    \item Hiện thực hóa các thành phần cốt lõi của engine gồm: khởi tạo bàn cờ, biểu diễn quân cờ, lưu trạng thái lượt đi, cập nhật trạng thái sau mỗi nước đi và hoàn tác nước đi.
    \item Xây dựng bộ luật cơ bản cho từng quân cờ của Cờ Tướng: tướng, sĩ, tượng, mã, xe, pháo, tốt.
    \item Hoàn thiện cơ chế lọc nước đi hợp lệ bằng mô phỏng trạng thái sau nước đi và kiểm tra điều kiện chiếu tướng hoặc đối mặt tướng.
    \item Bước đầu xây dựng phần AI theo hướng heuristic search thông qua hàm đánh giá bàn cờ dựa trên giá trị quân và cấu trúc chọn nước đi từ không gian trạng thái.
    \item Dựng khung báo cáo trên Overleaf, chuẩn hóa bố cục trình bày để thuận tiện đồng bộ với mã nguồn và tài liệu minh họa.
    \item Thực hiện quản lý phiên bản bằng Git, cập nhật mã nguồn tuần 2 lên repository để lưu vết tiến độ, phục vụ đối chiếu thay đổi và làm minh chứng quá trình phát triển đồ án.
\end{itemize}

\subsection{Các CTDL và giải thuật đã được sử dụng}
\begin{itemize}[label=--]
    \item \textbf{Ma trận 2 chiều 10x9:} Bàn cờ được biểu diễn bằng một ma trận gồm 10 hàng và 9 cột. Mỗi ô lưu một quân cờ hoặc giá trị rỗng, giúp truy xuất theo tọa độ hàng/cột nhanh và phù hợp với đặc thù luật Cờ Tướng.
    \item \textbf{Kiểu dữ liệu có cấu trúc cho quân cờ và nước đi:} Project sử dụng các kiểu như \texttt{Piece}, \texttt{Move}, \texttt{MoveRecord} để gom nhóm dữ liệu theo đúng ngữ nghĩa miền bài toán. Cách làm này giúp tách rõ thông tin quân cờ, nước đi hiện tại và lịch sử nước đi.
    \item \textbf{Danh sách động (List/Vector):} Được dùng để lưu tập nước đi sinh ra trong mỗi lượt. Đây là lựa chọn phù hợp vì số nước đi thay đổi theo trạng thái bàn cờ và cần duyệt tuần tự để đánh giá.
    \item \textbf{Ngăn xếp lịch sử nước đi (\texttt{move\_history}):} Lưu lại các thao tác đã thực hiện để hỗ trợ \texttt{undo}. Cấu trúc này đặc biệt quan trọng cho quá trình tìm kiếm trạng thái trong AI, vì mỗi nhánh tìm kiếm đều cần thao tác \texttt{make\_move} rồi \texttt{undo\_move}.
    \item \textbf{Thuật toán sinh nước đi theo luật quân cờ:} Mỗi loại quân được cài đặt một hàm sinh nước đi riêng, ví dụ mã kiểm tra cản chân, tượng kiểm tra chặn mắt và không vượt sông, pháo xử lý luật ăn qua màn.
    \item \textbf{Thuật toán lọc nước hợp lệ:} Tập nước đi ban đầu được sinh theo hướng \textit{pseudo-legal}. Sau đó hệ thống mô phỏng từng nước bằng \texttt{make\_move}, kiểm tra trạng thái chiếu tướng và loại bỏ các nước làm vi phạm luật.
    \item \textbf{Thuật toán kiểm tra tấn công ô và chiếu tướng:} Các hàm như \texttt{is\_square\_attacked}, \texttt{is\_in\_check} và \texttt{generals\_face\_each\_other} giúp đảm bảo tính hợp lệ của bàn cờ ở mức chiến thuật.
    \item \textbf{Heuristic evaluation:} Trạng thái bàn cờ được chấm điểm dựa trên \textit{material score} và một phần \textit{positional score} cho quân tốt sau khi qua sông. Đây là nền tảng cần thiết cho các thuật toán tìm kiếm trạng thái.
    \item \textbf{Heuristic search:} Mã nguồn hiện tại đã phát triển theo hướng tìm kiếm không gian trạng thái với \texttt{choose\_move} và cơ chế duyệt cây nước đi. Trong phạm vi tuần 2, phần này được ghi nhận như bước đầu hình thành lõi AI dựa trên đánh giá heuristic và thao tác thử nước đi trên cây trạng thái.
\end{itemize}

\section{Quá trình thực hiện}
\subsection*{Tuần 1}
\begin{itemize}[label=$\ast$]
    \item Tìm hiểu luật Cờ Tướng và xác định phạm vi kỹ thuật của đồ án.
    \item Nghiên cứu cách tổ chức kiến trúc để tách phần engine, AI và giao diện.
    \item Xác định các bài toán DSA cốt lõi cần xử lý trước gồm: biểu diễn bàn cờ, sinh nước đi, kiểm tra tính hợp lệ, lưu lịch sử nước đi và đánh giá trạng thái.
    \item Tạo khung project ban đầu, xây dựng các file nền tảng cho trạng thái và luật chơi.
\end{itemize}

\subsection*{Tuần 2}
\begin{itemize}[label=$\ast$]
    \item \textbf{Hoàn thiện mô hình trạng thái bàn cờ:} Xây dựng lớp \texttt{GameState} để chứa bàn cờ, lượt đi hiện tại, vị trí hai tướng và lịch sử nước đi. Phần này là lõi điều phối của toàn bộ chương trình.
    \item \textbf{Cài đặt thao tác chuyển trạng thái:} Hoàn thiện các hàm \texttt{make\_move} và \texttt{undo\_move} để cập nhật bàn cờ sau khi đi quân và phục hồi lại trạng thái trước đó khi cần quay lui.
    \item \textbf{Xây dựng rules engine cơ bản:} Cài đặt hàm sinh nước đi cho từng loại quân. Các luật đặc thù của Cờ Tướng như mã bị cản chân, tượng bị chặn mắt, pháo ăn qua màn và tướng chỉ đi trong cung đều đã được đưa vào xử lý.
    \item \textbf{Lọc nước đi hợp lệ:} Sau khi sinh nước đi thô, hệ thống dùng cơ chế mô phỏng để loại bỏ các nước khiến bên đi vẫn bị chiếu hoặc tạo trạng thái đối mặt tướng trái luật.
    \item \textbf{Khởi tạo hướng AI heuristic search:} Xây dựng các hàm đánh giá như \texttt{material\_score}, \texttt{positional\_score}, \texttt{evaluate\_position} làm cơ sở định lượng chất lượng trạng thái. Đây là bước tiền đề để nối sang thuật toán tìm kiếm trạng thái.
    \item \textbf{Kiểm thử các tình huống luật quan trọng:} Bổ sung test cho các trường hợp đặc thù như mã bị chặn đường, tượng không qua sông, pháo cần đúng một màn để bắt quân và trạng thái chiếu tướng.
    \item \textbf{Chuẩn hóa tài liệu:} Xây dựng khung báo cáo trên Overleaf, đồng thời chuẩn hóa docstring trong mã nguồn để mô tả chức năng, vai trò, dữ liệu vào/ra và thông tin tác giả.
    \item \textbf{Đồng bộ mã nguồn lên Git:} Thực hiện commit các hạng mục đã hoàn thành trong tuần 2 để bảo toàn lịch sử phát triển, thuận tiện kiểm tra tiến độ và làm căn cứ báo cáo.
\end{itemize}

\section{Kết quả đạt được}
\subsection{Logic bàn cờ và nước đi}
Đến hết tuần 2, phần logic bàn cờ đã hoạt động ổn định ở mức nền tảng. Hệ thống có thể sinh tập nước đi hợp lệ theo trạng thái hiện tại và loại bỏ được các nước đi vi phạm luật. Với các tình huống đặc trưng của Cờ Tướng, project đã thể hiện đúng ràng buộc của từng quân cờ thay vì chỉ xử lý di chuyển theo hình học đơn thuần.

\textbf{Phần cần demo (chụp màn hình):}
\begin{itemize}[label=--]
    \item Chọn một quân cụ thể trong console hoặc giao diện và hiển thị danh sách các vị trí có thể di chuyển.
    \item Minh họa một trường hợp quân mã bị cản chân hoặc pháo chỉ ăn được khi có đúng một quân làm màn.
    \item Có thể sử dụng trạng thái hiển thị từ lệnh chạy chương trình chính hoặc bộ test luật để chụp lại kết quả.
\end{itemize}

\subsection{Hàm đánh giá sơ bộ cho AI}
Hệ thống đã có khả năng chấm điểm trạng thái bàn cờ dựa trên giá trị quân hiện còn trên bàn, đồng thời mở rộng thêm điểm thưởng vị trí cho quân tốt sau khi qua sông. Cách đánh giá này còn đơn giản nhưng phù hợp với giai đoạn đầu vì dễ kiểm chứng, dễ giải thích và đủ để định hướng cho thuật toán chọn nước đi.

\textbf{Phần cần demo (chụp màn hình):}
\begin{itemize}[label=--]
    \item Chụp log hệ thống thể hiện giá trị \texttt{material\_score} hoặc \texttt{evaluate\_position} trước và sau một nước bắt quân.
    \item Chụp tình huống hai nước đi khác nhau dẫn tới hai mức điểm khác nhau để minh họa tác dụng của hàm heuristic.
\end{itemize}

\subsection{Tốc độ xử lý}
Việc tổ chức trạng thái theo hướng \texttt{make\_move}/\texttt{undo\_move} giúp việc duyệt các nhánh nước đi thuận lợi hơn so với cách sao chép toàn bộ bàn cờ cho từng lần thử. Đây là một quyết định DSA quan trọng vì nó giảm chi phí xử lý và chuẩn bị tốt cho giai đoạn mở rộng cây tìm kiếm sâu hơn trong các tuần tiếp theo.

\subsection{Tổng kết kết quả tuần 2}
\begin{itemize}[label=\checkmark]
    \item Đã hoàn thiện bộ khung cốt lõi của project.
    \item Đã biểu diễn được bàn cờ và trạng thái ván cờ bằng cấu trúc dữ liệu phù hợp.
    \item Đã cài đặt các luật di chuyển cơ bản cho từng quân cờ.
    \item Đã kiểm tra được nước đi hợp lệ, chiếu tướng và đối mặt tướng.
    \item Đã xây dựng được hàm đánh giá sơ bộ để phục vụ AI.
    \item Đã chuẩn hóa tài liệu báo cáo và docstring để thuận tiện cho việc bảo trì mã nguồn.
    \item Đã có quy trình lưu vết tiến độ tuần 2 thông qua Git để quản lý phiên bản nguồn.
\end{itemize}

\section{Tài liệu tham khảo}
\begin{enumerate}
    \item Repo tham khảo \texttt{Dylannni/ChineseChess\_XiangQi}.
    \item Các ghi chú phân tích luật Cờ Tướng và thiết kế hệ thống trong quá trình thực hiện đồ án.
    \item Mã nguồn đang phát triển trong project hiện tại, đặc biệt là các module \texttt{engine} và \texttt{ai}.
\end{enumerate}

\section*{Phụ lục}
\subsection*{Phụ lục 1: Gợi ý demo và lệnh chạy}
\begin{itemize}[label=--]
    \item Kiểm tra nhanh trạng thái engine:
    \begin{itemize}[label=*]
        \item \texttt{python3 main.py summary}
    \end{itemize}
    \item Chạy chế độ console để chụp các nước đi hợp lệ:
    \begin{itemize}[label=*]
        \item \texttt{python3 main.py cli}
        \item Dùng lệnh \texttt{moves} để hiển thị toàn bộ nước đi hợp lệ ở lượt hiện tại.
    \end{itemize}
    \item Chạy bộ test phục vụ minh chứng logic:
    \begin{itemize}[label=*]
        \item \texttt{python3 -m unittest tests.test\_rules tests.test\_state tests.test\_search}
    \end{itemize}
\end{itemize}

\subsection*{Phụ lục 2: Chuẩn hóa docstring}
Trong tuần 2, docstring được chuẩn hóa cho các hàm và lớp quan trọng trong các file \texttt{engine/state.py}, \texttt{engine/rules.py}, \texttt{ai/evaluate.py}, \texttt{ai/search.py}. Mẫu docstring thống nhất gồm các trường sau:
\begin{itemize}[label=--]
    \item \textbf{def:} Mô tả ngắn gọn chức năng của hàm hoặc lớp.
    \item \textbf{Role in System:} Giải thích vai trò của thành phần đó trong tổng thể logic trò chơi.
    \item \textbf{Input/Output:} Trình bày dữ liệu vào, dữ liệu ra và ý nghĩa tham số.
    \item \textbf{Author/Date/Ver:} Ghi nhận tác giả, ngày cập nhật và phiên bản tài liệu hóa.
\end{itemize}

Các thành phần được ưu tiên chú thích gồm: \texttt{GameState}, \texttt{make\_move}, \texttt{undo\_move}, \texttt{generate\_pseudo\_legal\_moves}, \texttt{generate\_legal\_moves}, \texttt{is\_in\_check}, \texttt{material\_score}, \texttt{evaluate\_position} và \texttt{choose\_move}.

\end{document}
