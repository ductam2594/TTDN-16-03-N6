# Module Quản lý Tài sản & Khấu hao

## Mô tả

Module này cung cấp hệ thống quản lý tài sản với tính năng tự động tính khấu hao hàng tháng và ghi nhận vào sổ cái kế toán. Module được tích hợp với module Quản lý Nhân sự để theo dõi tài sản được gán cho nhân viên.

## Tính năng chính

### 1. Quản lý Loại Tài sản
- Phân loại tài sản theo loại (máy tính, bàn ghế, thiết bị...)
- Cấu hình thời gian khấu hao cho từng loại
- Tự động tính tỷ lệ khấu hao hàng tháng
- Cấu hình tài khoản kế toán cho từng loại tài sản

### 2. Quản lý Tài sản
- Quản lý thông tin chi tiết tài sản (mã, tên, giá trị, ngày mua...)
- Gán tài sản cho nhân viên sử dụng
- Theo dõi trạng thái tài sản (đang sử dụng, bảo trì, thanh lý...)
- Tự động tính giá trị khấu hao hàng tháng
- Theo dõi giá trị còn lại của tài sản

### 3. Tính Khấu hao Tự động
- Tính khấu hao theo phương pháp đường thẳng
- Tự động tạo bút toán kế toán khi ghi sổ khấu hao
- Scheduled action tự động tính khấu hao hàng tháng
- Wizard tính khấu hao thủ công cho tháng bất kỳ

### 4. Kiểm kê Tài sản
- Tạo phiếu kiểm kê tài sản
- So sánh trạng thái thực tế với hệ thống
- Phát hiện sự khác biệt trong kiểm kê

### 5. Tích hợp với Module Nhân sự
- Hiển thị danh sách tài sản đang sử dụng trong form nhân viên
- Thống kê số lượng và tổng giá trị tài sản của nhân viên
- Liên kết tài sản với phòng ban thông qua nhân viên

## Cài đặt

1. Copy module vào thư mục `addons` của Odoo
2. Cập nhật danh sách ứng dụng: `Settings > Apps > Update Apps List`
3. Tìm và cài đặt module "Quản lý Tài sản & Khấu hao"
4. Cấu hình tài khoản kế toán cho các loại tài sản

## Cấu hình

### Cấu hình Tài khoản Kế toán

Trước khi sử dụng tính năng khấu hao, cần cấu hình tài khoản kế toán cho từng loại tài sản:

1. Vào **Quản lý Tài sản > Cấu hình > Loại Tài sản**
2. Chọn loại tài sản cần cấu hình
3. Trong tab "Tài khoản Kế toán", cấu hình:
   - **Tài khoản Tài sản**: Tài khoản để ghi nhận giá trị tài sản
   - **Tài khoản Khấu hao**: Tài khoản để ghi nhận khấu hao tích lũy
   - **Tài khoản Chi phí Khấu hao**: Tài khoản để ghi nhận chi phí khấu hao hàng tháng

### Kích hoạt Scheduled Action

Để tự động tính khấu hao hàng tháng:

1. Vào **Settings > Technical > Automation > Scheduled Actions**
2. Tìm "Tính khấu hao tài sản hàng tháng"
3. Kích hoạt và cấu hình thời gian chạy

## Sử dụng

### Tạo Tài sản mới

1. Vào **Quản lý Tài sản > Tài sản**
2. Click **Create**
3. Điền thông tin:
   - Tên tài sản, Loại tài sản
   - Ngày mua, Ngày đưa vào sử dụng
   - Giá trị nguyên giá
   - Nhân viên sử dụng (nếu có)
4. Lưu

### Tính Khấu hao

#### Tính khấu hao thủ công:
1. Vào **Quản lý Tài sản > Khấu hao > Tính Khấu hao**
2. Chọn tháng khấu hao và sổ nhật ký
3. Chọn "Tự động ghi sổ" nếu muốn tự động tạo bút toán
4. Click **Tính Khấu hao**

#### Tự động tính khấu hao:
- Scheduled action sẽ tự động chạy vào đầu mỗi tháng
- Tự động tạo các bút toán khấu hao và ghi sổ

### Xem Lịch sử Khấu hao

1. Vào **Quản lý Tài sản > Khấu hao > Lịch sử Khấu hao**
2. Hoặc từ form tài sản, click **Xem Khấu hao**

### Kiểm kê Tài sản

1. Vào **Quản lý Tài sản > Kiểm kê**
2. Click **Create**
3. Điền thông tin phiếu kiểm kê
4. Thêm chi tiết các tài sản cần kiểm kê
5. Xác nhận và hoàn thành

## Báo cáo

- **Danh sách Tài sản**: Xem tất cả tài sản với thông tin khấu hao
- **Lịch sử Khấu hao**: Xem chi tiết các bút toán khấu hao đã ghi sổ
- **Tài sản theo Nhân viên**: Xem trong form nhân viên, tab "Tài sản"

## Tích hợp với Module Khác

### Module Kế toán (account)
- Tự động tạo journal entries khi ghi sổ khấu hao
- Liên kết với tài khoản kế toán đã cấu hình

### Module Nhân sự (nhan_su)
- Hiển thị tài sản đang sử dụng trong form nhân viên
- Thống kê tài sản theo phòng ban

## Yêu cầu

- Odoo 15.0
- Module `account` (Kế toán)
- Module `nhan_su` (Quản lý Nhân sự)

## Tác giả

FIT-DNU

## License

LGPL-3






