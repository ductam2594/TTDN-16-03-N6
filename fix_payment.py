#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script tự động cài đặt module payment để sửa lỗi "Missing model payment.acquirer"
Chạy từ thư mục gốc: python3 fix_payment.py
"""

import subprocess
import sys
import os

def main():
    # Đường dẫn và tham số
    script_dir = os.path.dirname(os.path.abspath(__file__))
    odoo_bin = os.path.join(script_dir, 'odoo-bin')
    config_file = os.path.join(script_dir, 'odoo.conf')
    db_name = 'odoo_fitdnu'  # Có thể thay đổi nếu cần
    
    print("=" * 60)
    print("Đang cài đặt module payment để sửa lỗi...")
    print("=" * 60)
    print(f"Database: {db_name}")
    print(f"Config: {config_file}")
    print()
    
    # Kiểm tra file tồn tại
    if not os.path.exists(odoo_bin):
        print(f"❌ Không tìm thấy file: {odoo_bin}")
        sys.exit(1)
    
    if not os.path.exists(config_file):
        print(f"❌ Không tìm thấy file: {config_file}")
        sys.exit(1)
    
    # Chạy lệnh cài đặt payment
    cmd = [
        'python3',
        odoo_bin,
        '-c', config_file,
        '-u', 'payment',
        '-d', db_name,
        '--stop-after-init'
    ]
    
    print(f"Chạy lệnh: {' '.join(cmd)}")
    print()
    
    try:
        result = subprocess.run(cmd, cwd=script_dir, check=True, 
                                capture_output=False, text=True)
        print()
        print("=" * 60)
        print("✅ Hoàn thành! Module payment đã được cài đặt.")
        print("=" * 60)
        return 0
    except subprocess.CalledProcessError as e:
        print()
        print("=" * 60)
        print(f"❌ Có lỗi xảy ra (exit code: {e.returncode})")
        print("=" * 60)
        print("\n💡 Thử các giải pháp sau:")
        print("   1. Kiểm tra xem virtual environment đã được kích hoạt chưa")
        print("   2. Kiểm tra xem Odoo server đã được dừng chưa")
        print("   3. Kiểm tra tên database có đúng không")
        print(f"   4. Chạy thủ công: python3 {odoo_bin} -c {config_file} -u payment -d {db_name} --stop-after-init")
        return 1
    except FileNotFoundError:
        print()
        print("=" * 60)
        print("❌ Không tìm thấy python3")
        print("=" * 60)
        print("\n💡 Đảm bảo Python 3 đã được cài đặt và có trong PATH")
        return 1

if __name__ == '__main__':
    sys.exit(main())

