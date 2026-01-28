# 🚀 Hướng Dẫn Chạy Odoo

## Bước 1: Kiểm tra Database

Đảm bảo PostgreSQL đang chạy:

```bash
cd /home/duy/odoo-fitdnu
docker-compose up -d
```

Kiểm tra database đã chạy:
```bash
docker ps | grep postgres
```

---

## Bước 2: Cập nhật Module (Sau khi sửa code)

Sau khi sửa code module `quan_ly_van_ban`, cần cập nhật:

### Cách 1: Dùng script tự động
```bash
bash CAP_NHAT_MODULE.sh
```

### Cách 2: Chạy lệnh trực tiếp
```bash
cd /home/duy/odoo-fitdnu

# Kích hoạt virtual environment (nếu có)
source venv/bin/activate

# Cập nhật module
python3 odoo-bin -c odoo.conf -u quan_ly_van_ban -d odoo_fitdnu --stop-after-init
```

**Lưu ý:** Thay `odoo_fitdnu` bằng tên database của bạn nếu khác.

---

## Bước 3: Chạy Odoo Server

### Cách 1: Dùng script tự động
```bash
bash CHAY_ODOO.sh
```

### Cách 2: Chạy lệnh trực tiếp
```bash
cd /home/duy/odoo-fitdnu

# Kích hoạt virtual environment (nếu có)
source venv/bin/activate

# Chạy Odoo
python3 odoo-bin -c odoo.conf
```

---

## Truy cập Odoo

Sau khi server khởi động, truy cập:
- **URL:** http://localhost:8069
- **Database:** Tên database của bạn (ví dụ: `odoo_fitdnu`)
- **Username:** admin (hoặc user bạn đã tạo)
- **Password:** Mật khẩu bạn đã đặt

---

## Các Lệnh Hữu Ích

### Dừng Odoo Server
Nhấn `Ctrl+C` trong terminal đang chạy Odoo

### Xem log
Log sẽ hiển thị trực tiếp trong terminal. Nếu muốn lưu log:
```bash
python3 odoo-bin -c odoo.conf --logfile=odoo.log
```

### Cập nhật nhiều module cùng lúc
```bash
python3 odoo-bin -c odoo.conf -u module1,module2,module3 -d database_name --stop-after-init
```

### Chạy với chế độ developer
```bash
python3 odoo-bin -c odoo.conf --dev=all
```

### Tạo database mới
Truy cập http://localhost:8069 và chọn "Create Database"

---

## Xử Lý Lỗi

### Lỗi: "Could not connect to database"
- Kiểm tra PostgreSQL đang chạy: `docker ps`
- Kiểm tra port trong `odoo.conf` (mặc định: 5431)
- Kiểm tra username/password trong `odoo.conf`

### Lỗi: "Module not found"
- Kiểm tra `addons_path` trong `odoo.conf`
- Đảm bảo module có trong thư mục `addons/`
- Kiểm tra `__manifest__.py` có đúng format

### Lỗi: "Permission denied"
- Kiểm tra quyền truy cập file: `chmod +x odoo-bin`
- Kiểm tra quyền thư mục: `chmod -R 755 addons/`

### Lỗi: "Python module not found"
- Kích hoạt virtual environment: `source venv/bin/activate`
- Cài đặt dependencies: `pip install -r requirements.txt`

---

## Cấu Hình Database

Nếu cần thay đổi thông tin database, sửa file `odoo.conf`:

```ini
db_host = localhost
db_port = 5431
db_user = odoo
db_password = odoo
```

---

## Tips

1. **Luôn dừng server trước khi cập nhật module**
2. **Backup database trước khi cập nhật module quan trọng**
3. **Sử dụng `--stop-after-init` khi cập nhật để tự động dừng sau khi xong**
4. **Kiểm tra log để debug lỗi**

---

## Liên Kết Nhanh

- **Chạy Odoo:** `bash CHAY_ODOO.sh`
- **Cập nhật module:** `bash CAP_NHAT_MODULE.sh`
- **Xem log:** Xem trong terminal hoặc file log

