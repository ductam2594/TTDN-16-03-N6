<h2 align="center">
    <a href="https://dainam.edu.vn/vi/khoa-cong-nghe-thong-tin">
    🎓 Faculty of Information Technology (DaiNam University)
    </a>
</h2>
<h2 align="center">
    PLATFORM ERP
</h2>
<div align="center">
    <p align="center">
        <img src="docs/logo/aiotlab_logo.png" alt="AIoTLab Logo" width="170"/>
        <img src="docs/logo/fitdnu_logo.png" alt="AIoTLab Logo" width="180"/>
        <img src="docs/logo/dnu_logo.png" alt="DaiNam University Logo" width="200"/>
    </p>

[![AIoTLab](https://img.shields.io/badge/AIoTLab-green?style=for-the-badge)](https://www.facebook.com/DNUAIoTLab)
[![Faculty of Information Technology](https://img.shields.io/badge/Faculty%20of%20Information%20Technology-blue?style=for-the-badge)](https://dainam.edu.vn/vi/khoa-cong-nghe-thong-tin)
[![DaiNam University](https://img.shields.io/badge/DaiNam%20University-orange?style=for-the-badge)](https://dainam.edu.vn)

</div>

## 📖 1. Giới thiệu

### 1.1. Về đề tài

**Platform ERP** là một hệ thống quản lý doanh nghiệp được phát triển dựa trên nền tảng mã nguồn mở **Odoo 15.0**, được áp dụng vào học phần **Thực tập doanh nghiệp** tại Khoa Công nghệ Thông tin - Đại học Đại Nam.

#### Mục tiêu:
- Xây dựng một hệ thống ERP hoàn chỉnh để quản lý các hoạt động của doanh nghiệp
- Tích hợp các module quản lý: Nhân sự, Tài sản, Văn bản, Kế toán
- Ứng dụng công nghệ AI (Google Gemini) để hỗ trợ phân tích và tư vấn thông minh
- Tạo môi trường thực hành cho sinh viên trong việc phát triển phần mềm doanh nghiệp

### 1.2. Các chức năng chính

#### 📦 Module Quản lý Tài sản & Khấu hao
- **Quản lý Loại Tài sản**: Phân loại tài sản, cấu hình thời gian khấu hao, tài khoản kế toán
- **Quản lý Tài sản**: Quản lý thông tin chi tiết tài sản, gán cho nhân viên, theo dõi trạng thái
- **Tính Khấu hao Tự động**: Tính khấu hao theo phương pháp đường thẳng, tự động tạo bút toán kế toán
- **Kiểm kê Tài sản**: Tạo phiếu kiểm kê, so sánh trạng thái thực tế với hệ thống
- **Bảo trì & Sửa chữa**: Quản lý lịch sử bảo trì, sửa chữa, bảo dưỡng tài sản
- **Thanh lý Tài sản**: Quản lý quy trình thanh lý, tính lãi/lỗ, tự động tạo bút toán
- **Trợ lý ảo AI**: Tích hợp Google Gemini AI để:
  - Dự báo bảo trì tài sản
  - Tư vấn thanh lý tài sản
  - Trả lời câu hỏi về tài sản, khấu hao, bảo trì

#### 👥 Module Quản lý Nhân sự
- Quản lý thông tin nhân viên, phòng ban, chức vụ
- Chấm công, quản lý lương
- Lịch sử công tác, chứng chỉ
- Tích hợp với module Tài sản để theo dõi tài sản được gán cho nhân viên

#### 📄 Module Quản lý Văn bản
- Quản lý văn bản đến, văn bản đi
- Workflow xử lý văn bản
- Phân loại và tìm kiếm văn bản

#### 💰 Tích hợp Kế toán
- Tự động tạo bút toán kế toán cho khấu hao
- Ghi nhận chi phí bảo trì/sửa chữa
- Xử lý bút toán thanh lý tài sản
- Liên kết với module Kế toán của Odoo

## 💻 2. Ngôn ngữ lập trình và công nghệ sử dụng

### 2.1. Ngôn ngữ lập trình
- **Python 3.10**: Ngôn ngữ chính để phát triển các module
- **XML**: Định nghĩa views, menus, security rules
- **JavaScript**: Xử lý tương tác trên giao diện (nếu có)

### 2.2. Framework và thư viện
- **Odoo 15.0**: Framework ERP mã nguồn mở
- **PostgreSQL**: Hệ quản trị cơ sở dữ liệu
- **Google Generative AI (Gemini)**: API AI để phân tích và tư vấn
- **Python Libraries**:
  - `odoo`: Core framework
  - `google-generativeai`: Tích hợp Google Gemini AI
  - `psycopg2`: Kết nối PostgreSQL
  - `dateutil`: Xử lý ngày tháng

### 2.3. Công cụ và môi trường
- **Docker**: Chạy PostgreSQL database
- **Virtual Environment (venv)**: Quản lý môi trường Python
- **Git**: Quản lý phiên bản mã nguồn
- **WSL (Windows Subsystem for Linux)**: Môi trường phát triển trên Windows

## 🔄 3. Cập nhật gần đây

### 3.1. Cải thiện Module Quản lý Tài sản

#### ✅ Sửa lỗi hiển thị định dạng số tiền
- **Vấn đề:** Các trường giá trị tiền hiển thị với ",00" (ví dụ: `30.000.000,00`)
- **Giải pháp:** Đã đổi `digits` từ `(16, 2)` sang `(16, 0)` cho tất cả các trường giá trị tiền trong module:
  - `tai_san.py`: `gia_tri_nguyen_gia`, `gia_tri_khau_hao_thang`, `tong_khau_hao`, `gia_tri_con_lai`
  - `khau_hao.py`: `so_tien_khau_hao`, `gia_tri_con_lai`
  - `thanh_ly_tai_san.py`: `gia_tri_con_lai`, `gia_tri_thanh_ly`, `lai_lo`
  - `bao_tri_sua_chua.py`: `chi_phi`
  - `nhan_vien_extend.py`: `tong_gia_tri_tai_san`
- **Kết quả:** Giá trị tiền hiển thị không có phần thập phân (ví dụ: `30.000.000`)

#### ✅ Sửa lỗi AI không hiển thị dữ liệu
- **Vấn đề:** Khi nhấn nút "Dự báo bảo trì" hoặc "Tư vấn thanh lý", chỉ hiển thị thông báo thành công nhưng không có dữ liệu trong các trường tương ứng
- **Giải pháp:** 
  - Sửa hàm `action_predict_maintenance()` và `action_analyze_liquidation()` trong `tai_san.py`
  - Thay đổi return từ `display_notification` sang `ir.actions.act_window` để reload form sau khi ghi dữ liệu
- **Kết quả:** Form tự động reload và hiển thị đầy đủ dữ liệu AI sau khi xử lý

#### ✅ Cải thiện AI Chatbot - Trả lời chính xác về khấu hao
- **Vấn đề:** AI trả lời sai về tình trạng khấu hao (nói "chưa khấu hao" khi đã có khấu hao)
- **Giải pháp:**
  - Format số liệu với 2 chữ số thập phân (`:,.2f`) trong `_get_database_summary()` để không bị làm tròn sai
  - Thêm "Giá trị nguyên giá" vào thông tin chi tiết từng tài sản
  - Cải thiện prompt với hướng dẫn rõ ràng về cách xử lý câu hỏi khấu hao
  - Thêm yêu cầu bắt buộc: Nếu "Tổng khấu hao" > 0 thì PHẢI nói rõ là đã khấu hao
- **Kết quả:** AI trả lời chính xác về tình trạng khấu hao dựa trên dữ liệu thực tế

#### ✅ Cải thiện AI Chatbot - Trả lời về bảo trì/sửa chữa
- **Vấn đề:** Khi hỏi "PC có sửa chữa gì không", AI trả lời không rõ ràng, không liệt kê chi tiết
- **Giải pháp:**
  - Thêm lịch sử bảo trì/sửa chữa vào phần chi tiết từng tài sản trong `_get_database_summary()`
  - Hiển thị đầy đủ: số lần, loại (Bảo trì/Sửa chữa/Bảo dưỡng/Bảo hành), ngày, chi phí, mô tả
  - Cải thiện prompt với hướng dẫn cụ thể về cách trả lời câu hỏi bảo trì/sửa chữa
  - Thêm ví dụ minh họa cách trả lời
- **Kết quả:** AI trả lời chi tiết và rõ ràng về lịch sử bảo trì/sửa chữa của từng tài sản

#### ✅ Cải thiện AI Tư vấn Thanh lý
- **Vấn đề:** AI tư vấn thanh lý vẫn nói "chưa khấu hao" khi tài sản đã có khấu hao
- **Giải pháp:**
  - Format số liệu với 2 chữ số thập phân trong prompt (`:,.2f`)
  - Thêm yêu cầu bắt buộc trong prompt: Nếu giá trị đã khấu hao > 0 thì PHẢI khẳng định rõ tài sản đã được khấu hao
  - Cải thiện cách trình bày thông tin trong prompt để AI dễ hiểu hơn
- **Kết quả:** AI tư vấn thanh lý chính xác, không còn nói sai về tình trạng khấu hao

### 3.2. Tóm tắt các file đã chỉnh sửa
- `addons/quan_ly_tai_san/models/tai_san.py` - Sửa format số tiền, sửa hàm AI, cải thiện prompt
- `addons/quan_ly_tai_san/models/khau_hao.py` - Sửa format số tiền
- `addons/quan_ly_tai_san/models/thanh_ly_tai_san.py` - Sửa format số tiền
- `addons/quan_ly_tai_san/models/bao_tri_sua_chua.py` - Sửa format số tiền
- `addons/quan_ly_tai_san/models/nhan_vien_extend.py` - Sửa format số tiền
- `addons/quan_ly_tai_san/wizard/ai_chatbot.py` - Cải thiện database summary, format số liệu, cải thiện prompt 


## 🚀 4. Các project đã thực hiện dựa trên Platform

Một số project sinh viên đã thực hiện:
- #### [Khoá 15](./docs/projects/K15/README.md)
- #### [Khoá 16]() (Coming soon)

## ⚙️ 5. Cài đặt

### 5.1. Cài đặt công cụ, môi trường và các thư viện cần thiết

#### 5.1.1. Clone project.
```
git clone https://gitlab.com/anhlta/odoo-fitdnu.git
cd odoo-fitdnu
```
#### 5.1.2. Cài đặt các thư viện cần thiết
Người sử dụng thực thi các lệnh sau đề cài đặt các thư viện cần thiết

```
sudo apt-get install libxml2-dev libxslt-dev libldap2-dev libsasl2-dev libssl-dev python3.10-distutils python3.10-dev build-essential libssl-dev libffi-dev zlib1g-dev python3.10-venv libpq-dev
```
#### 5.1.3. Khởi tạo môi trường ảo.
- Khởi tạo môi trường ảo
```
python3.10 -m venv ./venv
```
- Thay đổi trình thông dịch sang môi trường ảo
```
source venv/bin/activate
```
- Chạy requirements.txt để cài đặt tiếp các thư viện được yêu cầu
```
pip3 install -r requirements.txt
```
### 5.2. Setup database

Khởi tạo database trên docker bằng việc thực thi file dockercompose.yml.
```
sudo docker-compose up -d
```
### 5.3. Setup tham số chạy cho hệ thống
Tạo tệp **odoo.conf** có nội dung như sau:
```
[options]
addons_path = addons
db_host = localhost
db_password = odoo
db_user = odoo
db_port = 5431
xmlrpc_port = 8069
```
Có thể kế thừa từ file **odoo.conf.template**
### 5.4. Chạy hệ thống và cài đặt các ứng dụng cần thiết
Lệnh chạy
```
python3 odoo-bin.py -c odoo.conf -u all
```
Người sử dụng truy cập theo đường dẫn _http://localhost:8069/_ để đăng nhập vào hệ thống.

## 📝 5. License

© 2024 AIoTLab, Faculty of Information Technology, DaiNam University. All rights reserved.

---

    
