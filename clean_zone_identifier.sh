#!/bin/bash
# Script để xóa các file Zone.Identifier (Windows Alternate Data Stream)
# Chạy trong WSL: bash clean_zone_identifier.sh

echo "=========================================="
echo "Đang xóa các file Zone.Identifier..."
echo "=========================================="

# Đếm số file trước khi xóa
COUNT=$(find addons -name "*Zone.Identifier*" 2>/dev/null | wc -l)
echo "Tìm thấy $COUNT file Zone.Identifier"

if [ $COUNT -eq 0 ]; then
    echo "✅ Không có file Zone.Identifier nào cần xóa"
    exit 0
fi

# Xóa các file Zone.Identifier
find addons -name "*Zone.Identifier*" -type f -delete 2>/dev/null

# Đếm lại sau khi xóa
REMAINING=$(find addons -name "*Zone.Identifier*" 2>/dev/null | wc -l)

if [ $REMAINING -eq 0 ]; then
    echo "✅ Đã xóa thành công tất cả file Zone.Identifier"
else
    echo "⚠️  Còn lại $REMAINING file Zone.Identifier (có thể là thư mục)"
fi

echo "=========================================="

