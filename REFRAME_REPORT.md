# REFRAME_REPORT — đổi tiêu đề và khung đặt vấn đề (03/11/2026)

**Tiêu đề cũ:** Số lượng ứng viên trước NMS có dự đoán được độ trễ của bộ phát hiện không? Một nghiên cứu đo lường trên lõi CPU được ghim và một nghiên cứu tình huống về tối ưu hóa patch

**Tiêu đề mới:** Tấn công cạn kiệt tài nguyên qua NMS có thực sự làm chậm bộ phát hiện? Một nghiên cứu đo lường trên CPU ghim lõi

Header chạy: "Tấn công cạn kiệt tài nguyên qua NMS". Metadata PDF (`pdftitle`) được đặt ở cả `paper_vi/main_vi.tex` và gói nộp.

Không thêm, sửa hay làm tròn con số nào. Mọi số trong các đoạn mới đều đã có trong bản thảo và khớp nguồn: `check_numbers.py --all` báo **ĐẠT**. Giả thuyết và endpoint đã đăng ký giữ nguyên.

Biên dịch: máy không có TeX nên chỉ kiểm tĩnh được — ngoặc và môi trường cân, không có `\ref` hỏng, không có nhãn trùng, đủ 40 trích dẫn. **Cần biên dịch trên Overleaf để xác nhận.**

## Câu đã sửa (cũ → mới, vị trí)

### 1. Tiêu đề

**Cũ:**

> \title{Số lượng ứng viên trước NMS có dự đoán được độ trễ của bộ phát hiện không? Một nghiên cứu đo lường trên lõi CPU được ghim và một nghiên cứu tình huống về tối ưu hóa patch}

**Mới:**

> \title{Tấn công cạn kiệt tài nguyên qua NMS có thực sự làm chậm bộ phát hiện? Một nghiên cứu đo lường trên CPU ghim lõi}

### 2. Metadata PDF

**Cũ:**

> \usepackage[colorlinks=true,linkcolor=blue,citecolor=blue,urlcolor=blue]{hyperref}

**Mới:**

> \usepackage[colorlinks=true,linkcolor=blue,citecolor=blue,urlcolor=blue]{hyperref}
> \hypersetup{pdftitle={Tấn công cạn kiệt tài nguyên qua NMS có thực sự làm chậm bộ phát hiện? Một nghiên cứu đo lường trên CPU ghim lõi}}

### 3. Tóm tắt

**Cũ:**

> \begin{abstract}
> Các tấn công độ trễ lên bộ phát hiện đối tượng thường cực đại hóa số ứng viên trước bước loại bỏ không cực đại (NMS), giả định nhiều ứng viên thì chậm hơn. Chúng tôi hỏi số ứng viên có dự đoán được độ trễ không, và từ mức nào toàn trình chậm đi. Giao thức ghim một lõi CPU laptop có kiểm chứng dưới tải, đo từng công đoạn, hiệu chuẩn A/A để đọc mọi tỷ số so với hiệu ứng nhỏ nhất phát hiện được, và đăng ký trước endpoint. Thứ nhất, với $10^2$ đến $10^4$ ứng viên tiêm, độ trễ NMS tăng ở mọi cách cài đặt và hình học nhưng mức tăng khác nhau hơn hai bậc độ lớn, và giới hạn top-300 chặn phần lớn. Thứ hai, ngưỡng làm toàn trình chậm đi là khoảng một trăm ứng viên với vòng lặp PyTorch và hàng nghìn với nhân thư viện; một mô hình kiểu Amdahl không tham số khớp dự đoán tốt trên ứng viên tiêm (post hoc) nhưng chỉ đạt quy tắc định trước ở một nửa số ô trên tấn công thật. Thứ ba, biến thể của hai tấn công toàn ảnh tăng số ứng viên hàng trăm lần mà toàn trình chỉ tăng vài phần trăm; một bộ tối ưu patch kiểu di truyền không làm tăng số ứng viên. Kết quả chỉ áp dụng cho suy luận trên một lõi CPU, nơi lan truyền thuận chiếm phần lớn thời gian.

**Mới:**

> Các tấn công cạn kiệt tài nguyên nhắm vào bộ phát hiện đối tượng tăng số ứng viên trước bước loại bỏ không cực đại (NMS), với giả định rằng số ứng viên $\Ntau$ cao thì bộ phát hiện chậm đi. Chúng tôi kiểm tra trực tiếp giả định này bằng một giao thức ghim một lõi CPU có kiểm chứng dưới tải, đo từng công đoạn, hiệu chuẩn A/A để đọc mọi tỷ số so với hiệu ứng nhỏ nhất phát hiện được, và đăng ký trước endpoint. Thứ nhất, trong đối chứng dương tiêm $10^2$ đến $10^4$ ứng viên, độ trễ NMS tăng ở mọi cách cài đặt và hình học, nhưng mức tăng khác nhau hơn hai bậc độ lớn và giới hạn top-300 chặn phần lớn. Thứ hai, ngưỡng làm toàn trình chậm đi là khoảng một trăm ứng viên với vòng lặp PyTorch và hàng nghìn với nhân thư viện; biến thể thích nghi theo hai tấn công toàn ảnh vượt ngưỡng này nhưng chỉ làm toàn trình tăng vài phần trăm, còn Sponge Patch, một miếng dán hộp xám tối ưu bằng thuật toán di truyền, không làm tăng $\Ntau$. Thứ ba, $\Ntau$ là một đại lượng thay thế yếu cho độ trễ: dự đoán thời gian NMS chỉ từ $\Ntau$ sai tới vài lần tùy cách cài đặt, và một mô hình ngân sách kiểu Amdahl chỉ đạt quy tắc định trước ở một nửa số ô trên tấn công thật. Kết quả chỉ áp dụng cho YOLOv8n và YOLOv5s suy luận trên một lõi CPU ghim, nơi lan truyền thuận chiếm phần lớn thời gian.

### 4. Từ khóa

**Cũ:**

> \noindent\textbf{Từ khóa:} phát hiện đối tượng; loại bỏ không cực đại (NMS); đo độ trễ; patch đối kháng; tối ưu hộp xám; thuật toán di truyền; tính sẵn sàng

**Mới:**

> \noindent\textbf{Từ khóa:} tấn công cạn kiệt tài nguyên; tấn công độ trễ; loại bỏ không cực đại (NMS); đo độ trễ; miếng dán đối kháng; tính sẵn sàng

### 5. Giới thiệu: ba đoạn động cơ + câu hỏi chính

**Cũ:**

> \section{Giới thiệu}
> Các bộ phát hiện đối tượng dùng NMS tiêu tốn một phần thời gian của mỗi khung hình vào việc loại bỏ các hộp ứng viên chồng lấn nhau. Vì chi phí của NMS tham lam phụ thuộc vào số ứng viên vượt ngưỡng điểm, một hướng nghiên cứu chế tác đầu vào sao cho số này tăng lên để làm chậm quá trình phát hiện \cite{phantom2023,overload2024}, mở rộng ý tưởng tấn công năng lượng--độ trễ trên mạng nơ-ron \cite{shumailov2021sponge}. Trong các công trình này, số ứng viên $\Ntau$ vừa là đại lượng được cực đại hóa vừa là lời giải thích cho mức chậm quan sát được. Vai trò thứ hai là một khẳng định thực nghiệm: chi phí NMS còn phụ thuộc vào cách cài đặt và vào cách các hộp chồng lấn, và NMS chỉ là một công đoạn của pipeline. EVADE đã cho thấy các tấn công độ trễ NMS thường không đạt mức như công bố khi chuyển sang cấu hình triển khai \cite{evade2025}. Bài này không đánh giá lại các tấn công; nó kiểm tra trực tiếp đại lượng mà chúng tối ưu và xây một mô hình định lượng cho biết khi nào $\Ntau$ chuyển thành độ trễ toàn trình.
> 
> Chúng tôi đặt bốn câu hỏi.

**Mới:**

> \section{Giới thiệu}
> Tấn công cạn kiệt tài nguyên, còn gọi là tấn công độ trễ hay tấn công năng lượng--độ trễ, nhắm vào tính sẵn sàng thay vì tính đúng đắn: đầu vào được chế tác để kéo dài thời gian xử lý mà không cần làm sai nhãn \cite{shumailov2021sponge,nicgslowdown2022}. Với một hệ thống tri giác thời gian thực, mỗi khung hình xử lý chậm là một thời hạn có thể bị lỡ. Ở các bộ phát hiện đối tượng một giai đoạn kiểu YOLO, bề mặt tấn công tự nhiên là bước loại bỏ không cực đại (NMS): chi phí của NMS tham lam tăng theo số hộp ứng viên vượt ngưỡng điểm, và số hộp đó phụ thuộc vào nội dung ảnh.
> 
> Các tấn công đã công bố, như Phantom Sponges, Overload và SlowTrack, chế tác đầu vào để cực đại hóa số ứng viên trước NMS, $\Ntau$, với giả định rằng $\Ntau$ cao thì bộ phát hiện chậm đi \cite{phantom2023,overload2024,slowtrack2024}. Trong các công trình này, $\Ntau$ vừa là đại lượng được tối ưu vừa là lời giải thích cho mức chậm quan sát được. Nhưng chi phí NMS còn phụ thuộc vào cách cài đặt, vào cách các hộp chồng lấn và vào giới hạn top-$k$, và NMS chỉ là một công đoạn của pipeline. EVADE cho thấy các tấn công độ trễ NMS hiện có không tạo ra mức tăng như đã công bố khi chuyển sang cấu hình triển khai \cite{evade2025}. Theo hiểu biết của chúng tôi, chưa có nghiên cứu nào kiểm tra trực tiếp giả định ``$\Ntau$ cao thì chậm'' bằng một đối chứng dương, trong đó $\Ntau$ được biết trước, cùng một sàn nhiễu đo được.
> 
> Nhóm bắt đầu bằng việc xây Sponge Patch: một miếng dán cục bộ, hộp xám, chỉ đọc điểm tin cậy trước NMS, được tối ưu bằng thuật toán di truyền để tăng $\Ntau$. Khi đo dưới một giao thức có ghim lõi và sàn nhiễu, patch không làm tăng $\Ntau$ trên YOLOv8n, nên trên cấu hình này nó không làm cạn kiệt tài nguyên qua NMS (\todo{chờ số Việc 1: tác động toàn trình của patch}). Vì vậy bài chuyển trọng tâm sang giả định mà cả dòng tấn công dựa vào: kiểm tra giả định đó, tìm điều kiện để nó đúng, rồi đánh giá Sponge Patch và biến thể thích nghi theo hai tấn công toàn ảnh trên cùng giao thức.
> 
> Câu hỏi chính của bài là: tấn công cạn kiệt tài nguyên nhắm vào NMS có làm chậm bộ phát hiện không, và trong điều kiện nào? Cụ thể, số ứng viên trước NMS, đại lượng mà các tấn công này tối ưu, có dự đoán được độ trễ không, và từ mức nào thì tăng $\Ntau$ mới làm toàn trình chậm đi? Chúng tôi tách câu hỏi này thành bốn câu hỏi con.

### 6. Đóng góp

**Cũ:**

> \paragraph{Đóng góp.}
> (i) Một giao thức đo độ trễ pipeline có ghim lõi được kiểm chứng dưới tải, đo từng công đoạn, hiệu chuẩn A/A và đăng ký trước các endpoint. (ii) Một đối chứng dương tiêm ứng viên tổng hợp vào chính pipeline, lập bản đồ độ trễ NMS theo $\Ntau$, cách cài đặt, hình học và giới hạn top-$k$, và đo ngưỡng $N^{*}$ ở mức toàn trình. (iii) Một mô hình kiểu Amdahl không tham số khớp, $R \approx 1 + \Delta t_{\mathrm{NMS}}/t_{\mathrm{total}}$, trong đó $\Delta t_{\mathrm{NMS}}$ phụ thuộc $\Ntau$, cách cài đặt và hình học; mô hình được đối chiếu post hoc trên phép tiêm toàn pipeline và kiểm tiến cứu trên các tấn công thật, kèm phân tích chỗ mô hình hụt. (iv) Các phép đo dưới giao thức này trên biến thể thích nghi của hai tấn công toàn ảnh đã công bố và trên một bộ tối ưu patch, cho thấy mức tăng toàn trình thực tế trên CPU nhỏ hơn nhiều so với mức tăng của $\Ntau$.

**Mới:**

> \paragraph{Đóng góp.}
> (i) Một giao thức đo cho tấn công cạn kiệt tài nguyên qua NMS, gồm ghim lõi được kiểm chứng dưới tải, đo từng công đoạn, hiệu chuẩn A/A với MDE và đăng ký trước endpoint. (ii) Một đối chứng dương tiêm ứng viên tổng hợp vào chính pipeline, lập bản đồ độ trễ NMS và độ trễ toàn trình theo $\Ntau$, cách cài đặt, hình học và giới hạn top-$k$. (iii) Một mô hình ngân sách kiểu Amdahl, $R \approx 1 + \Delta t_{\mathrm{NMS}}/t_{\mathrm{total}}$, cho biết khi nào việc tăng $\Ntau$ có thể nhìn thấy ở mức toàn trình. (iv) Một đánh giá Sponge Patch và biến thể thích nghi theo hai tấn công toàn ảnh trên cùng giao thức.

### 7. Bảng định vị (tab:related), dòng của bài này

**Cũ:**

> \textbf{Sponge Patch (bài này)} & Cục bộ; hộp xám (phản hồi điểm tin cậy trước NMS, không gradient) & Quan hệ giữa $\Ntau$ và độ trễ, hiệu chuẩn bằng đối chứng dương và sàn nhiễu A/A &

**Mới:**

> \textbf{Sponge Patch (bài này)} & Cục bộ; hộp xám (phản hồi điểm tin cậy trước NMS, không gradient) & Giả định $\Ntau \to$ độ trễ của tấn công cạn kiệt tài nguyên qua NMS; đối chứng dương, sàn nhiễu A/A &

### 8. Mục 2.1, câu định vị Sponge Patch

**Cũ:**

> Sponge Patch nằm ở giao của hai dòng và chọn một điểm quyền truy cập khác (Bảng~\ref{tab:related}): một miếng dán cục bộ, không cần gradient, chỉ dùng phản hồi điểm tin cậy trước NMS làm tín hiệu tối ưu, với mục tiêu khảo sát, chưa khẳng định, khả năng gây tải NMS.

**Mới:**

> Sponge Patch nằm ở giao của hai dòng và chọn một điểm quyền truy cập khác (Bảng~\ref{tab:related}): một miếng dán cục bộ, không cần gradient, chỉ dùng phản hồi điểm tin cậy trước NMS làm tín hiệu tối ưu. Trong bài này, khả năng gây tải NMS của nó là đối tượng được kiểm tra, cùng với giả định mà cả hai dòng tấn công cạn kiệt tài nguyên dựa vào.

### 9. Thảo luận, "Quan hệ với các khẳng định trong tài liệu"

**Cũ:**

> Chúng tôi không đưa ra khẳng định nào về các bộ phát hiện hay thiết bị khác, và không kiểm tra các tấn công do các công trình được trích dẫn đề xuất.

**Mới:**

> Chúng tôi không đưa ra khẳng định nào về các bộ phát hiện hay thiết bị khác, và không tái lập các thí nghiệm gốc của các công trình được trích dẫn; chúng tôi chỉ đo biến thể thích nghi theo hai tấn công toàn ảnh trên cấu hình của mình.

### 10. Thảo luận: đoạn mới "Khi nào … có thể hiệu quả"

**Cũ:**

> \subsection{Hướng dẫn cho đánh giá và phòng thủ}

**Mới:**

> \subsection{Khi nào tấn công cạn kiệt tài nguyên qua NMS có thể hiệu quả}
> Mô hình ngân sách kiểu Amdahl cho biết điều kiện cần: một tấn công chỉ làm toàn trình chậm đi phát hiện được khi nó thêm vào công đoạn NMS ít nhất $\mathrm{MDE}\times t_{\mathrm{total}}$, tức khi NMS chiếm một tỷ phần đủ lớn của thời gian xử lý sau khi bị tấn công. Trên cấu hình của bài, lan truyền thuận trên một lõi CPU chiếm phần lớn thời gian, nên ngay cả khi công đoạn NMS tăng hơn một bậc độ lớn, nó vẫn chỉ là một phần nhỏ của toàn trình. Từ biểu thức đó, chúng tôi nêu ba cấu hình mà tấn công cạn kiệt tài nguyên qua NMS có thể hiệu quả: lan truyền thuận được tăng tốc (GPU, bộ tăng tốc thần kinh) trong khi NMS vẫn chạy tuần tự, làm mẫu số nhỏ đi; NMS cài đặt bằng vòng lặp, nơi mỗi hộp được giữ lại tốn một vòng; và pipeline không có giới hạn top-$k$ trước NMS. Đối chứng dương của bài có đúng tổ hợp thứ hai và thứ ba (vòng lặp PyTorch thuần, không giới hạn), và ở đó toàn trình chậm đi phát hiện được từ khoảng một trăm ứng viên. Hai cấu hình còn lại, nhất là bộ tăng tốc, là giả thuyết cho nghiên cứu sau, không phải kết quả của bài này.
> 
> \subsection{Hướng dẫn cho đánh giá và phòng thủ}

### 11. Kết luận: mở đầu bằng câu trả lời có điều kiện

**Cũ:**

> \section{Kết luận và hướng phát triển}
> \label{sec:conclusion}
> Chúng tôi đã kiểm tra liệu số ứng viên trước NMS có dự đoán được độ trễ của bộ phát hiện không. Số ứng viên có ảnh hưởng đến thời gian NMS, nhưng mức ảnh hưởng phụ thuộc cách cài đặt và hình học tới hơn hai bậc độ lớn, và giới hạn top-$k$ chặn phần lớn. Ở mức toàn trình, một mô hình kiểu Amdahl không tham số khớp dự đoán tỷ số với sai số khoảng 1\% trên ứng viên tổng hợp (post hoc), và cho biết cần bao nhiêu ứng viên để thấy toàn trình chậm đi. Trên biến thể thích nghi của hai tấn công toàn ảnh đẩy $\Ntau$ lên 340 đến 389 lần, toàn trình chỉ tăng 2,9 đến 3,4\% với YOLOv5s trên một lõi CPU; mô hình đạt quy tắc định trước ở một nửa số ô và hụt vì đường cong tổng hợp đánh giá quá cao chi phí NMS của ứng viên thật và vì các công đoạn khác cũng tăng theo $\Ntau$. Một bộ tối ưu patch kiểu thuật toán di truyền không làm tăng $\Ntau$ và không vượt tìm kiếm ngẫu nhiên.

**Mới:**

> \section{Kết luận và hướng phát triển}
> \label{sec:conclusion}
> Câu trả lời cho câu hỏi ở tiêu đề phụ thuộc vào cấu hình. Trên một lõi CPU ghim, với các nhân NMS thư viện, biến thể thích nghi theo Overload và theo Phantom Sponges (YOLOv5s, 640 px) đẩy $\Ntau$ lên 340 đến 389 lần nhưng chỉ làm toàn trình tăng 2,9 đến 3,4\%: mức tăng vượt sàn nhiễu trong phiên với \texttt{nms} của torchvision và chưa vượt với hai nhân còn lại. Trên YOLOv8n, Sponge Patch không làm tăng $\Ntau$, nên nó không làm cạn kiệt tài nguyên qua NMS (\todo{chờ số Việc 1: tác động toàn trình của patch}). Lý do là lan truyền thuận chiếm phần lớn thời gian: sau khi bị tấn công, NMS vẫn chỉ chiếm 1,4 đến 2,3\% toàn trình. Ngược lại, khi NMS là một vòng lặp không có giới hạn top-$k$, chỉ cần khoảng một trăm ứng viên tiêm vào đã làm toàn trình chậm đi phát hiện được.
> 
> Về giả định của dòng tấn công này: số ứng viên có ảnh hưởng đến thời gian NMS, nhưng mức ảnh hưởng phụ thuộc cách cài đặt và hình học tới hơn hai bậc độ lớn, và giới hạn top-$k$ chặn phần lớn. Ở mức toàn trình, một mô hình kiểu Amdahl không tham số khớp dự đoán tỷ số với sai số khoảng 1\% trên ứng viên tổng hợp (post hoc) và cho biết cần bao nhiêu ứng viên để thấy toàn trình chậm đi; trên các biến thể tấn công toàn ảnh, mô hình đạt quy tắc định trước ở một nửa số ô và hụt vì đường cong tổng hợp đánh giá quá cao chi phí NMS của ứng viên thật và vì các công đoạn khác cũng tăng theo $\Ntau$. Bộ tối ưu của Sponge Patch không vượt tìm kiếm ngẫu nhiên.

### 12. Tóm tắt (cắt cho đủ 250 từ, sau lượt trên)

**Cũ:**

> … bằng một giao thức ghim một lõi CPU có kiểm chứng dưới tải, đo từng công đoạn, hiệu chuẩn A/A để đọc mọi tỷ số so với hiệu ứng nhỏ nhất phát hiện được, và đăng ký trước endpoint.

**Mới:**

> … bằng một giao thức ghim một lõi CPU có kiểm chứng dưới tải, đo từng công đoạn và hiệu chuẩn A/A để đọc mọi tỷ số so với sàn nhiễu.

### 13. Gói nộp: build_submission.py (header chạy, metadata PDF)

**Cũ:**

> \shorttitle{Số ứng viên trước NMS và độ trễ}

**Mới:**

> \hypersetup{pdftitle={<tiêu đề mới>}} và \shorttitle{Tấn công cạn kiệt tài nguyên qua NMS}

### 14. supplement_vi.tex, README_BUILD.md (gói v4), README_ZENODO.md, REPORT_Q3.md, CLAUDE.md (dòng tiêu đề)

**Cũ:**

> tên bài cũ

**Mới:**

> tên bài mới

## Rà khung cũ trong toàn bài
- Đã tìm các cụm "chúng tôi đề xuất tấn công", "DoS", "làm cạn kiệt tài nguyên máy chủ biên", "edge server", "hiệu quả tấn công cao" trong `main_vi.tex` và `supplement_vi.tex`: **không còn câu nào**.
- Còn và giữ nguyên:
  - Cụm "từ chối dịch vụ" ở phần Tính hợp lệ bên ngoài: đó là câu phủ nhận ("không khẳng định một tấn công từ chối dịch vụ…").
  - Cụm "thiết bị biên" ở phần Công trình liên quan và bảng định vị: dùng để mô tả bối cảnh của Overload.
  - Cụm "nghiên cứu tình huống" ở Phương pháp và Thảo luận: chỉ bộ tối ưu GA của Sponge Patch, vẫn khớp khung mới.
- Câu "Bài này không đánh giá lại các tấn công" ở Giới thiệu cũ đã bị bỏ, vì khung mới có đánh giá biến thể thích nghi. Câu "không kiểm tra các tấn công do các công trình được trích dẫn đề xuất" ở Thảo luận đã sửa (mục 9 ở trên).

## \todo còn lại
- Mới thêm: hai chỗ `\todo{chờ số Việc 1: tác động toàn trình của patch}`, một ở Giới thiệu (đoạn 3) và một ở Kết luận (đoạn 1).
- Từ trước, vẫn còn: các chỗ chờ số đo lại patch (E11) ở bảng patch, bảng ngưỡng, bảng cài đặt, Hình 6, mục "Ngưỡng tính bằng mili giây", mục "Patch thật" và hai đoạn Thảo luận; cùng tác giả liên hệ, ORCID, CRediT, DOI Zenodo.

## Chỗ chưa chắc khung mới khớp số liệu (cần quyết)
1. **Câu mẫu cho Kết luận không khớp dữ liệu.** Câu mẫu viết "không làm toàn trình chậm vượt sàn nhiễu đáng kể". Nhưng với `nms` của torchvision, cả hai biến thể tấn công toàn ảnh **có vượt** sàn nhiễu trong phiên: tỷ số 1,034 và 1,032, cận dưới KTC 1,022 và 1,021, so với MDE 1,98%. Bảng 6 ghi "có". Kết luận vì vậy được viết đúng số liệu: tăng 2,9–3,4%, vượt sàn nhiễu ở torchvision `nms`, chưa vượt ở hai nhân còn lại. Nếu muốn dùng chữ "không đáng kể" thì cần một ngưỡng ý nghĩa thực tiễn định trước; hiện chưa có ngưỡng nào như vậy.
2. **Bộ phát hiện.** Các biến thể tấn công toàn ảnh chạy trên **YOLOv5s** (mô hình mà nhiễu loạn được tối ưu), không phải YOLOv8n. Vì vậy Kết luận và tóm tắt ghi điều kiện theo từng mô hình, không viết "trên YOLOv8n" cho mọi kết luận.
3. **Câu "patch không làm cạn kiệt tài nguyên trên cấu hình này" (Giới thiệu đoạn 3, Kết luận).** Câu này dựa trên kết quả GA không làm tăng $N_\tau$. Kết quả đó không bị lỗi chèn patch ảnh hưởng, vì $N_\tau$ được đếm tất định trước khi bấm giờ. Tác động lên thời gian toàn trình thì còn chờ E11. Nếu E11 cho thấy một patch GA vượt MDE trong phiên, câu này phải sửa.
4. **Khẳng định khoảng trống** ("chưa có nghiên cứu nào kiểm tra trực tiếp giả định … bằng đối chứng dương và sàn nhiễu") đã kèm "theo hiểu biết của chúng tôi". EVADE là công trình gần nhất; phản biện có thể hỏi điểm khác. Bảng định vị đã nêu điểm khác: EVADE đánh giá các tấn công, bài này kiểm tra đại lượng được tối ưu.
5. **Không thấy kết luận nào mâu thuẫn trực tiếp với tiêu đề.** Tiêu đề là một câu hỏi, và bài trả lời có điều kiện. Đối chứng dương cho thấy tấn công qua NMS *có thể* làm chậm (vòng lặp NMS không có top-k, từ khoảng 100 ứng viên). Các biến thể thật trên cấu hình thư viện chỉ làm tăng vài phần trăm. Hai ý này khớp với khung mới.
6. Bản tiếng Anh `paper_en/main.tex` chưa đổi theo khung mới (theo yêu cầu không dịch). `CLAUDE.md` đã cập nhật dòng tiêu đề.
