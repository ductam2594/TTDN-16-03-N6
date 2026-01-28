#!/bin/bash
# Script tự động cài đặt module payment
# Chạy trong WSL: bash RUN_THIS.sh

set -e  # Dừng nếu có lỗi

echo "=========================================="
echo "Đang cài đặt module payment..."
echo "=========================================="

# Đảm bảo đang ở đúng thư mục
cd /home/duy/odoo-fitdnu

# Kiểm tra file config
if [ ! -f "odoo.conf" ]; then
    echo "❌ Không tìm thấy file odoo.conf"
    exit 1
fi

# Database name (có thể thay đổi nếu cần)
DB_NAME="odoo_fitdnu"

echo "Database: $DB_NAME"
echo ""

# Kiểm tra xem có virtual environment không
if [ -d "venv" ]; then
    echo "📦 Kích hoạt virtual environment..."
    source venv/bin/activate
fi

# Chạy lệnh cài đặt payment
echo "🔄 Đang cài đặt module payment..."
python3 odoo-bin -c odoo.conf -u payment -d "$DB_NAME" --stop-after-init

if [ $? -eq 0 ]; then
    echo ""
    echo "=========================================="
    echo "✅ THÀNH CÔNG! Module payment đã được cài đặt."
    echo "=========================================="
    echo ""
    echo "Bây giờ bạn có thể:"
    echo "1. Khởi động lại Odoo server"
    echo "2. Kiểm tra log để đảm bảo không còn lỗi"
else
    echo ""
    echo "=========================================="
    echo "❌ Có lỗi xảy ra khi cài đặt"
    echo "=========================================="
    echo ""
    echo "💡 Thử các giải pháp:"
    echo "   1. Kiểm tra xem Odoo server đã được dừng chưa"
    echo "   2. Kiểm tra tên database: $DB_NAME"
    echo "   3. Kiểm tra log để xem lỗi chi tiết"
    exit 1
fi

