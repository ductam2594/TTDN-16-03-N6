#!/bin/bash
# Script để chạy Odoo server
# Chạy trong WSL: bash CHAY_ODOO.sh

set -e  # Dừng nếu có lỗi

echo "=========================================="
echo "🚀 Khởi động Odoo Server"
echo "=========================================="

# Đảm bảo đang ở đúng thư mục
cd /home/duy/odoo-fitdnu

# Kiểm tra file config
if [ ! -f "odoo.conf" ]; then
    echo "❌ Không tìm thấy file odoo.conf"
    exit 1
fi

# Kiểm tra file odoo-bin
if [ ! -f "odoo-bin" ]; then
    echo "❌ Không tìm thấy file odoo-bin"
    exit 1
fi

# Kiểm tra xem có virtual environment không
if [ -d "venv" ]; then
    echo "📦 Kích hoạt virtual environment..."
    source venv/bin/activate
else
    echo "⚠️  Không tìm thấy virtual environment, sử dụng Python hệ thống"
fi

# Kiểm tra database connection
echo "🔍 Kiểm tra kết nối database..."
if ! python3 -c "import psycopg2; conn = psycopg2.connect(host='localhost', port=5431, user='odoo', password='odoo', dbname='postgres'); conn.close()" 2>/dev/null; then
    echo "⚠️  Không thể kết nối database. Đảm bảo PostgreSQL đang chạy:"
    echo "   docker-compose up -d"
    echo ""
    echo "Hoặc tiếp tục chạy Odoo (sẽ tạo database mới nếu cần)..."
    read -p "Tiếp tục? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo ""
echo "=========================================="
echo "✅ Bắt đầu chạy Odoo Server"
echo "=========================================="
echo ""
echo "🌐 Truy cập tại: http://localhost:8069"
echo "📝 Database port: 5431"
echo "🔧 Config file: odoo.conf"
echo ""
echo "Nhấn Ctrl+C để dừng server"
echo ""

# Chạy Odoo
python3 odoo-bin -c odoo.conf

