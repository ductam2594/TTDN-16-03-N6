#!/bin/bash
# Script nâng cấp module quan_ly_tai_san để kích hoạt tính năng AI
# Chạy trong WSL: bash upgrade_module_ai.sh

set -e

echo "=========================================="
echo "Đang nâng cấp module quan_ly_tai_san..."
echo "=========================================="

# Đảm bảo đang ở đúng thư mục
cd /home/duy/odoo-fitdnu

# Kiểm tra file config
if [ ! -f "odoo.conf" ]; then
    echo "❌ Không tìm thấy file odoo.conf"
    exit 1
fi

# Database name
DB_NAME="odoo_fitdnu"

echo "Database: $DB_NAME"
echo ""

# Kiểm tra xem có virtual environment không
if [ -d "venv" ]; then
    echo "📦 Kích hoạt virtual environment..."
    source venv/bin/activate
fi

# Kiểm tra dependencies
echo "🔍 Kiểm tra dependencies..."
python3 -c "import google.generativeai; print('✅ google-generativeai: OK')" || {
    echo "❌ google-generativeai chưa được cài đặt"
    echo "Vui lòng chạy: pip install google-generativeai markdown"
    exit 1
}

python3 -c "import markdown; print('✅ markdown: OK')" || {
    echo "❌ markdown chưa được cài đặt"
    echo "Vui lòng chạy: pip install google-generativeai markdown"
    exit 1
}

echo ""
echo "🔄 Đang nâng cấp module quan_ly_tai_san..."
python3 odoo-bin -c odoo.conf -u quan_ly_tai_san -d "$DB_NAME" --stop-after-init

if [ $? -eq 0 ]; then
    echo ""
    echo "=========================================="
    echo "✅ THÀNH CÔNG! Module đã được nâng cấp."
    echo "=========================================="
    echo ""
    echo "Bây giờ bạn có thể:"
    echo "1. Khởi động lại Odoo server:"
    echo "   python3 odoo-bin -c odoo.conf"
    echo ""
    echo "2. Sử dụng tính năng AI:"
    echo "   - Vào menu: Quản lý Tài sản > Trợ lý Tài chính AI"
    echo "   - Nhấn nút 'Phân tích ngay'"
    echo ""
else
    echo ""
    echo "=========================================="
    echo "❌ Có lỗi xảy ra khi nâng cấp module"
    echo "=========================================="
    echo ""
    echo "💡 Kiểm tra:"
    echo "   1. Odoo server đã được dừng chưa"
    echo "   2. Tên database: $DB_NAME"
    echo "   3. Xem log để biết lỗi chi tiết"
    exit 1
fi

