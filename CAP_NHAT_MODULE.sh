#!/bin/bash
# Script để cập nhật module quan_ly_van_ban sau khi sửa
# Chạy trong WSL: bash CAP_NHAT_MODULE.sh

set -e  # Dừng nếu có lỗi

echo "=========================================="
echo "🔄 Cập nhật Module quan_ly_van_ban"
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

# Cập nhật module quan_ly_van_ban
echo "🔄 Đang cập nhật module quan_ly_van_ban..."
python3 odoo-bin -c odoo.conf -u quan_ly_van_ban -d "$DB_NAME" --stop-after-init

if [ $? -eq 0 ]; then
    echo ""
    echo "=========================================="
    echo "✅ THÀNH CÔNG! Module đã được cập nhật."
    echo "=========================================="
    echo ""
    echo "Bây giờ bạn có thể:"
    echo "1. Chạy Odoo server: bash CHAY_ODOO.sh"
    echo "2. Hoặc chạy: python3 odoo-bin -c odoo.conf"
else
    echo ""
    echo "=========================================="
    echo "❌ Có lỗi xảy ra khi cập nhật"
    echo "=========================================="
    echo ""
    echo "💡 Thử các giải pháp:"
    echo "   1. Kiểm tra xem Odoo server đã được dừng chưa"
    echo "   2. Kiểm tra tên database: $DB_NAME"
    echo "   3. Kiểm tra log để xem lỗi chi tiết"
    exit 1
fi

