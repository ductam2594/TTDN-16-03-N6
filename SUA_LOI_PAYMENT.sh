#!/bin/bash
# Script để sửa lỗi Missing model payment.acquirer
# Chạy trong WSL: bash SUA_LOI_PAYMENT.sh

set -e  # Dừng nếu có lỗi

echo "=========================================="
echo "🔧 Sửa lỗi Missing model payment.acquirer"
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

# Kiểm tra xem module payment có tồn tại không
if [ ! -d "addons/payment" ]; then
    echo "⚠️  Module payment không có trong thư mục addons/"
    echo "   Module payment là module chuẩn của Odoo, nên có sẵn."
    echo "   Nếu không có, có thể bỏ qua lỗi này (không ảnh hưởng chức năng chính)."
    echo ""
    read -p "Bạn có muốn tiếp tục cài đặt không? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Cài đặt module payment
echo "🔄 Đang cài đặt module payment..."
python3 odoo-bin -c odoo.conf -u payment -d "$DB_NAME" --stop-after-init

if [ $? -eq 0 ]; then
    echo ""
    echo "=========================================="
    echo "✅ THÀNH CÔNG! Module payment đã được cài đặt."
    echo "=========================================="
    echo ""
    echo "Lỗi 'Missing model payment.acquirer' sẽ không còn xuất hiện."
    echo ""
    echo "Bây giờ bạn có thể:"
    echo "1. Chạy Odoo server: python3 odoo-bin -c odoo.conf"
    echo "2. Lỗi sẽ không còn xuất hiện trong log"
else
    echo ""
    echo "=========================================="
    echo "❌ Có lỗi xảy ra khi cài đặt"
    echo "=========================================="
    echo ""
    echo "💡 Nếu lỗi này không ảnh hưởng đến chức năng chính,"
    echo "   bạn có thể bỏ qua. Lỗi chỉ là warning về missing model."
    exit 1
fi

