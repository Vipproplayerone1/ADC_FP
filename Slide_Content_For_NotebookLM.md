# Trợ Lý Học Tập Cá Nhân Hóa — Nội dung tạo slide

> File hướng dẫn cho NotebookLM (hoặc AI tạo slide bất kỳ).
> **Quy tắc bắt buộc:** Mỗi dấu `---` là một slide mới. Toàn bộ chữ trong mỗi mục `## Slide` phải xuất hiện trên slide tương ứng — KHÔNG để bất kỳ thông tin nào trong phần ghi chú diễn giả hoặc bị ẩn. Giữ nguyên thứ tự, tiêu đề, gạch đầu dòng, và bảng. Không tự sáng tạo thêm nội dung.

---

## Slide 1 — Trang bìa

**TRỢ LÝ HỌC TẬP CÁ NHÂN HÓA**

Hệ thống hỗ trợ học tập dựa trên RAG (Truy xuất tăng cường sinh ngữ)

Đồ án Cuối kỳ ADC — Đề tài 3

Công nghệ sử dụng: FastAPI · Streamlit · ChromaDB · Llama 3.1 8B (Ollama)

---

## Slide 2 — Vấn đề thực tế

**Vấn đề sinh viên đang gặp**

- Có hàng chục slide bài giảng, chương sách, ghi chú — nhưng không có thời gian đọc lại tất cả.
- Tìm kiếm từ khóa (Ctrl+F) chỉ tìm đúng chữ, không hiểu khái niệm.
- ChatGPT trả lời được, nhưng không biết tài liệu cụ thể của môn học — dễ bịa thông tin sai.
- Không có công cụ tự tạo câu hỏi ôn tập từ chính tài liệu của mình.

**Hệ quả:** Ôn tập kém hiệu quả, không tự kiểm tra được kiến thức, mất niềm tin vào AI khi học.

---

## Slide 3 — Giải pháp

**Trợ Lý Học Tập Cá Nhân Hóa**

Một hệ thống RAG (Truy xuất tăng cường sinh ngữ) cho phép sinh viên:

1. Tải lên tài liệu PDF của mình (slide, sách, ghi chú).
2. Hỏi đáp dựa trên đúng nội dung tài liệu đó.
3. Tóm tắt nhanh theo chủ đề.
4. Tự sinh câu hỏi trắc nghiệm để luyện tập.

**Cam kết:** Mọi câu trả lời đều có trích nguồn (tên file + số trang). Không bịa thông tin, không "ảo giác" dữ liệu.

---

## Slide 4 — Ba chức năng chính

**1. Hỏi đáp (Question Answering)**
- Hỏi tự nhiên, nhận câu trả lời kèm trích nguồn (tên file, số trang).
- Từ chối trả lời nếu không có thông tin trong tài liệu.

**2. Tóm tắt (Summarization)**
- Tóm tắt theo chủ đề hoặc chương.
- Súc tích, có cấu trúc, kèm trích nguồn.

**3. Sinh câu hỏi trắc nghiệm (MCQ Generation)**
- Tự sinh câu hỏi trắc nghiệm 4 đáp án A–D.
- Có đáp án đúng + giải thích + trích nguồn.

---

## Slide 5 — Hệ thống làm việc với mọi tài liệu

**Tính tổng quát**

- Không cố định cho một môn học hay file cụ thể nào.
- Hoạt động với mọi PDF: Học máy, Sinh học, Lịch sử, Toán học, Kinh doanh…
- Mỗi sinh viên có thư viện tài liệu riêng.

**Ví dụ ứng dụng:**

- Sinh viên Công nghệ Thông tin: ôn tập slide bài giảng về thuật toán.
- Sinh viên Y khoa: tra cứu sách giáo trình giải phẫu.
- Sinh viên Luật: hỏi đáp văn bản pháp luật.
- Người tự học: tóm tắt sách phi hư cấu.

---

## Slide 6 — Kiến trúc tổng thể

**Sơ đồ luồng dữ liệu**

```
[Sinh viên] → [Giao diện Streamlit] → [Máy chủ FastAPI]
                                         │
              ┌──────────────────────────┼──────────────────────────┐
              ▼                          ▼                          ▼
       Đường ống Nạp dữ liệu    Đường ống Truy xuất        Dịch vụ Mô hình
       (Phân tích → Chia đoạn   (Mã hóa câu hỏi →           Ngôn ngữ Lớn
        → Mã hóa → Lưu trữ)      Tìm Top-K)                 (Llama 3.1 8B
              │                          │                  qua Ollama)
              │                          │                          │
              └──────► [Cơ sở dữ liệu Vector ChromaDB] ◄────────────┘
```

**Nguyên tắc thiết kế:**
- Các dịch vụ thuần (không phụ thuộc FastAPI), Tuyến đường mỏng, Lược đồ Pydantic.
- Các câu lệnh nhắc (prompt) tách riêng ra file mẫu `.txt`.
- Cấu hình tập trung trong `app/config.py`.

---

## Slide 7 — Đường ống Nạp dữ liệu (xử lý tài liệu)

**Khi sinh viên tải lên PDF**

1. **Phân tích PDF** — PyMuPDF đọc từng trang, trích xuất văn bản.
2. **Chia đoạn văn bản** — RecursiveCharacterTextSplitter chia thành đoạn 800 ký tự, chồng lấp 150 ký tự.
3. **Mã hóa vector** — sentence-transformers/all-MiniLM-L6-v2 chuyển mỗi đoạn thành vector.
4. **Lưu trữ** — Lưu vào ChromaDB kèm metadata bắt buộc:
   - `file_name` (tên file)
   - `page_number` (số trang)
   - `chunk_id` (mã định danh đoạn)

**Tại sao metadata quan trọng:** Đây là cơ sở để hệ thống trích nguồn đúng file + đúng trang ở mọi câu trả lời.

---

## Slide 8 — Đường ống RAG (trả lời câu hỏi)

**Quy trình 6 bước**

1. Nhận câu hỏi từ sinh viên.
2. Mã hóa câu hỏi bằng **cùng mô hình** đã dùng khi lưu trữ (MiniLM-L6-v2).
3. Tìm 5 đoạn gần nhất trong ChromaDB (độ tương đồng cosin).
4. Ghép các đoạn thành ngữ cảnh, đưa vào mẫu câu lệnh nhắc.
5. Gửi câu lệnh nhắc cho Llama 3.1 8B qua Ollama.
6. Trả về câu trả lời + danh sách nguồn (tên file + số trang).

**Cơ chế chống "ảo giác" thông tin:**
- Mẫu câu lệnh nhắc ép mô hình CHỈ dùng ngữ cảnh đã truy xuất.
- Nếu ngữ cảnh không liên quan → mô hình phải từ chối:
  *"Tôi không tìm thấy đủ thông tin trong các tài liệu đã tải lên."*

---

## Slide 9 — Công nghệ sử dụng

| Tầng | Công nghệ | Lý do chọn |
|---|---|---|
| Máy chủ API | FastAPI | Tự sinh Swagger, Lược đồ Pydantic, bất đồng bộ |
| Giao diện | Streamlit | Xây dựng UI nhanh, Python thuần |
| Cơ sở dữ liệu vector | ChromaDB | Nhẹ, lưu file, không cần máy chủ riêng |
| Mô hình mã hóa | sentence-transformers/all-MiniLM-L6-v2 | Nhẹ, nhanh, đủ tốt cho RAG |
| Mô hình ngôn ngữ lớn | Llama 3.1 8B | Chạy trên máy, miễn phí, bảo mật riêng tư |
| Môi trường chạy LLM | Ollama | Quản lý mô hình ngôn ngữ trên máy đơn giản |
| Bộ phân tích PDF | PyMuPDF | Đọc văn bản + metadata trang chính xác |
| Kiểm thử | pytest | 22 bài kiểm thử đơn vị bao phủ toàn bộ dịch vụ |

**Toàn bộ hệ thống chạy trên máy — không cần khóa API trả phí, không gửi dữ liệu sinh viên ra ngoài.**

---

## Slide 10 — Cấu trúc dự án

```
ADC FP/
├── app/
│   ├── api/                    # Bộ điều khiển tuyến đường
│   ├── services/               # Logic nghiệp vụ thuần
│   │   ├── pdf_loader.py
│   │   ├── text_chunker.py
│   │   ├── embedding_service.py
│   │   ├── vector_store.py
│   │   ├── retrieval_service.py
│   │   ├── llm_service.py
│   │   └── rag_service.py
│   ├── prompts/                # Mẫu câu lệnh nhắc (.txt)
│   ├── schemas.py              # Mô hình Pydantic
│   ├── config.py               # Cấu hình tập trung
│   └── main.py                 # Điểm vào ứng dụng FastAPI
├── frontend/streamlit_app.py
├── scripts/                    # Cài đặt, nạp dữ liệu, đánh giá
├── tests/                      # 22 bài kiểm thử đơn vị
├── data/                       # PDF + bộ dữ liệu đánh giá
├── vector_db/chroma/           # Lưu trữ ChromaDB
└── docs/                       # README, báo cáo đánh giá
```

---

## Slide 11 — Demo: Tải lên tài liệu

**Bước 1: Sinh viên tải PDF qua Streamlit**

- Kéo thả file PDF vào vùng tải lên.
- Máy chủ tự động: phân tích → chia đoạn → mã hóa vector → lưu trữ.
- Hiển thị thông báo thành công kèm số đoạn văn bản đã tạo.

**Điểm cuối API:** `POST /upload`

**Đầu ra mong đợi:**
```json
{
  "file_name": "Bai_Giang_03_Toi_Uu_Hoa.pdf",
  "num_chunks": 47,
  "status": "indexed"
}
```

---

## Slide 12 — Demo: Hỏi đáp có trích nguồn

**Câu hỏi:** *"Hạ gradient là gì?"*

**Câu trả lời mẫu:**

> Hạ gradient là một thuật toán tối ưu hóa được sử dụng để giảm thiểu hàm mất mát bằng cách liên tục cập nhật các tham số mô hình theo hướng ngược với gradient.
>
> **Nguồn:**
> - Bai_Giang_03_Toi_Uu_Hoa.pdf, trang 12
> - Bai_Giang_03_Toi_Uu_Hoa.pdf, trang 14

**Điểm nhấn:** Sinh viên có thể mở đúng trang đó trong PDF gốc để đọc thêm. Đây không phải bịa thông tin — đây là câu trả lời có cơ sở.

---

## Slide 13 — Demo: Chống "Ảo giác" thông tin

**Câu hỏi ngoài phạm vi:** *"Thủ đô của Pháp là gì?"*

**Câu trả lời hệ thống:**

> *"Tôi không tìm thấy đủ thông tin trong các tài liệu đã tải lên."*

**Tại sao quan trọng:**

- Một hệ thống RAG yếu sẽ trả lời "Paris" từ kiến thức nền của mô hình — đó là rò rỉ kiến thức ngoài tài liệu.
- Hệ thống của chúng tôi TỪ CHỐI thay vì bịa thông tin.
- Sinh viên có thể tin tưởng: nếu hệ thống trả lời, câu trả lời chắc chắn có trong tài liệu của họ.

**Đây là điểm khác biệt cốt lõi so với ChatGPT thông thường.**

---

## Slide 14 — Demo: Tóm tắt

**Yêu cầu:** *"Tóm tắt phần đánh giá mô hình"*

**Đầu ra mẫu:**

> Đánh giá mô hình đo lường mức độ mô hình đã huấn luyện tổng quát hóa trên dữ liệu chưa từng thấy. Các chỉ số phổ biến bao gồm độ chính xác, độ chính xác dương, độ thu hồi, F1-score và ROC-AUC cho bài toán phân loại, MSE/RMSE cho bài toán hồi quy. Kiểm định chéo giảm phương sai của ước lượng bằng cách chia dữ liệu thành nhiều phần huấn luyện/kiểm thử.
>
> **Nguồn:** Bai_Giang_05_Danh_Gia.pdf (các trang 3, 7, 11)

**Đặc điểm:**
- Tóm tắt chỉ từ tài liệu sinh viên đã tải lên.
- Có cấu trúc, súc tích, kèm trích nguồn.
- Điểm cuối API: `POST /summary`

---

## Slide 15 — Demo: Sinh câu hỏi trắc nghiệm (Điểm nhấn của Đề tài 3)

**Yêu cầu:** *"Sinh 3 câu hỏi trắc nghiệm độ khó trung bình về hồi quy logistic"*

**Mẫu một câu hỏi trắc nghiệm:**

> **Câu 1:** Hồi quy logistic chủ yếu được sử dụng cho loại bài toán nào?
>
> A. Hồi quy tuyến tính trên đầu ra liên tục
> B. Phân loại nhị phân với đầu ra xác suất
> C. Phân cụm dữ liệu chưa gán nhãn
> D. Giảm chiều dữ liệu
>
> **Đáp án đúng:** B
>
> **Giải thích:** Hồi quy logistic áp dụng hàm sigmoid lên tổ hợp tuyến tính của các đặc trưng, tạo ra xác suất trong khoảng [0, 1] phù hợp cho phân loại nhị phân.
>
> **Nguồn:** Bai_Giang_04_Phan_Loai.pdf, trang 8

**Mỗi câu hỏi trắc nghiệm đều có đủ 4 yếu tố — đáp án đúng, giải thích, trích nguồn — đúng yêu cầu rubric của Đề tài 3.**

---

## Slide 16 — Các điểm cuối API

| Phương thức | Điểm cuối | Chức năng |
|---|---|---|
| POST | `/upload` | Tải lên + lưu trữ PDF |
| POST | `/chat` | Hỏi đáp có trích nguồn |
| POST | `/summary` | Tóm tắt theo chủ đề |
| POST | `/mcq` | Sinh câu hỏi trắc nghiệm |
| GET | `/health` | Kiểm tra tình trạng |
| GET | `/docs` | Giao diện Swagger tự sinh |

**Toàn bộ yêu cầu/phản hồi đều được kiểm định bằng lược đồ Pydantic. Không có dữ liệu thô đi qua biên giới API.**

---

## Slide 17 — Kết quả đánh giá (Truy xuất)

**Đo trên `retrieval_eval_set.csv` — mỗi truy vấn có đáp án chuẩn (file, trang)**

| Chỉ số | Giá trị |
|---|---|
| Số lượng truy vấn | 5 |
| Top-K | 5 |
| Độ chính xác @K | 0.2000 |
| Độ thu hồi @K | 1.0000 |
| MRR (Trung bình nghịch đảo thứ hạng) | 1.0000 |
| Tỷ lệ trúng @3 | 1.0000 |
| Tỷ lệ trúng @K | 1.0000 |
| Độ trễ truy xuất trung bình | 0.78 giây |

**Nhận xét:** Truy xuất đạt 100% tỷ lệ trúng @3 và MRR = 1.0 — hệ thống luôn lấy được đúng đoạn chứa câu trả lời trong top-3.

---

## Slide 18 — Kết quả đánh giá (Hỏi đáp và Tóm tắt)

**Hỏi đáp trên bộ dữ liệu đánh giá**

| Chỉ số | Giá trị |
|---|---|
| Độ chính xác Hỏi đáp | 1.0000 |
| ROUGE-L | 0.3736 |
| BLEU | 0.1382 |
| Tỷ lệ có cơ sở | 1.0000 |
| Độ trễ tổng trung bình | 16.31 giây |

**Tóm tắt**

| Chỉ số | Giá trị |
|---|---|
| ROUGE-1 | 0.2565 |
| ROUGE-2 | 0.1251 |
| ROUGE-L | 0.1950 |
| Tỷ lệ có cơ sở | 1.0000 |
| Độ trễ trung bình | 63.43 giây |

**Tỷ lệ có cơ sở = 1.0 ở cả Hỏi đáp và Tóm tắt — 100% câu trả lời đều có trích nguồn hợp lệ.**

---

## Slide 19 — Kết quả đánh giá (Câu hỏi trắc nghiệm)

**Câu hỏi trắc nghiệm trên bộ dữ liệu đánh giá**

| Chỉ số | Giá trị |
|---|---|
| Số lượng yêu cầu | 2 |
| Số câu hỏi sinh ra | 3 |
| Mức độ liên quan | 0.9167 |
| Đáp án khác biệt | 1.0000 |
| Độ dài giải thích (trung bình số từ) | 27.00 |
| Định dạng đúng | 1.0000 |
| Độ trễ trung bình | 112.57 giây |

**Định dạng đúng = 1.0 nghĩa là 100% đầu ra JSON đúng lược đồ yêu cầu (4 lựa chọn A-D + đáp án đúng + giải thích + nguồn).**

---

## Slide 20 — Tổng kết Rubric Đề tài 3

| Yêu cầu Đề tài 3 | Trạng thái |
|---|---|
| Hoạt động với mọi bộ PDF tải lên | ✅ |
| Đầu vào PDF + truy vấn ngôn ngữ tự nhiên | ✅ |
| Đường ống nạp tài liệu (phân tích, chia đoạn, mã hóa, lưu trữ) | ✅ |
| Truy xuất RAG đưa vào mô hình ngôn ngữ Transformer | ✅ |
| Hỏi đáp có trích nguồn | ✅ |
| Tự sinh câu hỏi trắc nghiệm có đáp án + giải thích | ✅ |
| Máy chủ FastAPI + Giao diện Streamlit | ✅ |
| Các chỉ số đánh giá (P@K, R@K, MRR, ROUGE, BLEU, rubric trắc nghiệm, độ trễ) | ✅ |

**Đáp ứng đủ 8/8 yêu cầu rubric.**

---

## Slide 21 — Kiểm thử & Chất lượng mã nguồn

**Bao phủ kiểm thử**

- 22 bài kiểm thử đơn vị
- Bao phủ tất cả các mô-đun dịch vụ: `pdf_loader`, `text_chunker`, `embedding_service`, `vector_store`, `retrieval_service`, `llm_service`, `rag_service`
- Chạy bằng lệnh: `.venv\Scripts\pytest.exe -q`
- Kết quả: **22 bài đều đạt**

**Nguyên tắc phong cách mã nguồn**

- Chú thích kiểu dữ liệu trên mọi hàm công khai.
- Không cố định môn học hay tên file.
- Cùng một mô hình mã hóa cho cả nạp dữ liệu và truy vấn.
- Metadata bắt buộc trên mọi đoạn văn bản: `file_name`, `page_number`, `chunk_id`.
- Không đẩy lên Git các file `.env`, `vector_db/`, `data/raw/`.

---

## Slide 22 — Giới hạn hiện tại

**Giới hạn**

- Chỉ hỗ trợ PDF (chưa hỗ trợ DOCX, PPTX, HTML).
- Llama 3.1 8B có độ trễ cao trên CPU (~16 giây/Hỏi đáp, ~110 giây/Trắc nghiệm).
- Chia đoạn dựa trên số ký tự, chưa chia theo ngữ nghĩa.
- Chưa có đa người dùng, mỗi phiên bản chỉ dành cho 1 sinh viên.
- Chưa hỗ trợ tiếng Việt tối ưu (mô hình đa ngôn ngữ nhưng chưa tinh chỉnh).

**Đây là dự án học thuật, không phải sản phẩm vận hành thực tế.**

---

## Slide 23 — Hướng phát triển

**Cải tiến trong tương lai**

1. **Đa định dạng:** Hỗ trợ DOCX, PPTX, EPUB, markdown.
2. **Chia đoạn theo ngữ nghĩa:** Chia đoạn theo ý nghĩa thay vì số ký tự.
3. **Tìm kiếm lai:** Kết hợp tìm vector + BM25.
4. **Đa người dùng:** Xác thực + không gian riêng cho mỗi người dùng.
5. **Ứng dụng di động:** Chuyển thành ứng dụng React Native hoặc Flutter.
6. **Tiếng Việt:** Tinh chỉnh mô hình mã hóa và LLM cho tiếng Việt.
7. **Ôn tập ngắt quãng:** Kết hợp câu hỏi trắc nghiệm với thuật toán SRS (như Anki).
8. **Xếp hạng lại:** Thêm bộ xếp hạng lại để tăng độ chính xác.

---

## Slide 24 — Cách chạy dự án

**Yêu cầu hệ thống:** Windows 11 · Python 3.12+ · Ollama

**5 bước cài đặt:**

```powershell
# 1. Cài đặt môi trường
.\scripts\setup.ps1

# 2. Tải mô hình ngôn ngữ (~4.7GB, lần đầu)
ollama pull llama3.1:8b

# 3. Sinh PDF mẫu + nạp vào hệ thống
.venv\Scripts\python.exe scripts\generate_demo_pdfs.py
.venv\Scripts\python.exe scripts\ingest_documents.py

# 4. Khởi động máy chủ
.venv\Scripts\uvicorn.exe app.main:app --reload

# 5. Khởi động giao diện (cửa sổ dòng lệnh khác)
.venv\Scripts\streamlit.exe run frontend\streamlit_app.py
```

**Truy cập:**
- Giao diện: http://localhost:8501
- Tài liệu API: http://127.0.0.1:8000/docs

---

## Slide 25 — Kết luận

**Trợ Lý Học Tập Cá Nhân Hóa**

- Một hệ thống RAG hỗ trợ học tập **đầy đủ, đáp ứng 8/8 yêu cầu của Đề tài 3**.
- Hoạt động với **mọi tài liệu PDF**, không cố định môn học.
- Mọi câu trả lời đều **có trích nguồn** (tên file + số trang).
- **Chống "ảo giác" thông tin** bằng mẫu câu lệnh nhắc ép từ chối khi ngữ cảnh không đủ.
- **Chạy hoàn toàn trên máy** — bảo mật riêng tư, miễn phí, không phụ thuộc API trả phí.
- **22 bài kiểm thử đơn vị + báo cáo đánh giá** chứng minh chất lượng định lượng.

**Đây là công cụ học tập thực sự có thể sử dụng được, không phải bản trình diễn cho có.**

---

## Slide 26 — Lời cảm ơn

**Cảm ơn thầy/cô và các bạn đã lắng nghe**

Em xin sẵn sàng nhận câu hỏi.

**Liên hệ dự án:**

- Kho mã nguồn: github.com/Vipproplayerone1/ADC_FP
- Thư điện tử: phong.bui@parcelperform.com

---

# Hướng dẫn cho NotebookLM

**Khi nhập file này vào NotebookLM:**

1. Chọn "Generate Studio output" → "Slides" hoặc tương tự.
2. Trong câu lệnh nhắc thêm: *"Mỗi dấu `---` là một slide. Đặt TẤT CẢ nội dung văn bản trong section đó lên slide — KHÔNG để bất kỳ thông tin nào trong phần ghi chú diễn giả. Giữ nguyên gạch đầu dòng, bảng, khối mã nguồn và thứ tự."*
3. Chọn phong cách tối giản/chuyên nghiệp (tránh mẫu quá rườm rà che mất văn bản).
4. Sau khi sinh ra, xem lại từng slide để chắc chắn không bị cắt ngắn nội dung — nếu slide nào quá dài, tự tách thành 2 slide nhưng giữ đủ thông tin gốc.

**Tổng số slide dự kiến:** 26 slide.
