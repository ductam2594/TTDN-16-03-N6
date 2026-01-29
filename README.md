<h2 align="center">
    <a href="https://dainam.edu.vn/vi/khoa-cong-nghe-thong-tin">
    🎓 Faculty of Information Technology (DaiNam University)
    </a>
</h2>
<h2 align="center">
    QUẢN LÝ TÀI SẢN TÍCH HỢP QUẢN LÝ TÀI CHÍNH - KẾ TOÁN
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

## 🖼️ 3. Hình ảnh giao diện
### 3.1. Giao diện Quản lý Tài sản
<p align="center">
  <img src="docs/logo/tai san.jpg" alt="" width="700"/>
</p>

- **Danh sách tài sản**: Hiển thị danh sách tất cả tài sản với thông tin cơ bản
- **Form chi tiết tài sản**: Quản lý thông tin đầy đủ về tài sản, khấu hao, bảo trì
- **Tab Phân tích AI**: Tích hợp AI để dự báo bảo trì và tư vấn thanh lý

### 3.2. Giao diện Khấu hao
<p align="center">
  <img src="docs/logo/z7474622662167_1783dbc7863f03556c51e63914842b73.jpg" alt="" width="700"/>
</p>

- **Lịch sử khấu hao**: Xem tất cả các bút toán khấu hao đã ghi sổ
- **Wizard tính khấu hao**: Tính khấu hao cho tháng bất kỳ

### 3.3. Giao diện Bảo trì & Sửa chữa
<p align="center">
  <img src="docs/logo/z7474625268914_17149b63910ca1ed59f20d1db936f51c.jpg" alt="" width="700"/>
</p>

- **Danh sách bảo trì**: Quản lý các phiếu bảo trì, sửa chữa
- **Form chi tiết**: Ghi nhận thông tin bảo trì, chi phí, người thực hiện

### 3.4. Giao diện Trợ lý ảo AI
<p align="center">
  <img src="docs/logo/ai.jpg" alt="" width="700"/>
</p>
- **Chatbot AI**: Tương tác với AI để hỏi về tài sản, khấu hao, bảo trì
- **Cấu hình AI**: Cấu hình API Key cho Google Gemini


## ⚙️ 4. Cài đặt

### 4.1. Cài đặt công cụ, môi trường và các thư viện cần thiết

#### 4.1.1. Clone project.
```
git clone https://gitlab.com/anhlta/odoo-fitdnu.git
cd odoo-fitdnu
```
#### 4.1.2. Cài đặt các thư viện cần thiết
Người sử dụng thực thi các lệnh sau đề cài đặt các thư viện cần thiết

```
sudo apt-get install libxml2-dev libxslt-dev libldap2-dev libsasl2-dev libssl-dev python3.10-distutils python3.10-dev build-essential libssl-dev libffi-dev zlib1g-dev python3.10-venv libpq-dev
```
#### 4.1.3. Khởi tạo môi trường ảo.
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
### 4.2. Setup database

Khởi tạo database trên docker bằng việc thực thi file dockercompose.yml.
```
sudo docker-compose up -d
```
### 4.3. Setup tham số chạy cho hệ thống
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
### 4.4. Chạy hệ thống và cài đặt các ứng dụng cần thiết
Lệnh chạy
```
python3 odoo-bin.py -c odoo.conf -u all
```
Người sử dụng truy cập theo đường dẫn _http://localhost:8069/_ để đăng nhập vào hệ thống.

## 📝 5. License

© 2024 AIoTLab, Faculty of Information Technology, DaiNam University. All rights reserved.

---


    
