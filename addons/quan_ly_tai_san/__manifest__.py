# -*- coding: utf-8 -*-
{
    'name': "Quản lý Tài sản & Khấu hao",
    'summary': """
        Module quản lý tài sản với tính năng tự động tính khấu hao hàng tháng
        và ghi nhận vào sổ cái kế toán. Tích hợp với module Quản lý Nhân sự.
    """,
    'description': """
        Module Quản lý Tài sản & Khấu hao
        ==================================
        
        Tính năng chính:
        - Quản lý danh mục tài sản (máy tính, bàn ghế, thiết bị văn phòng...)
        - Phân loại tài sản theo loại và phòng ban
        - Tự động tính khấu hao hàng tháng theo phương pháp đường thẳng
        - Ghi nhận khấu hao vào sổ cái kế toán tự động
        - Gán tài sản cho nhân viên sử dụng
        - Theo dõi lịch sử khấu hao và giá trị còn lại
        - Báo cáo tài sản và khấu hao
        
        Tích hợp:
        - Module Quản lý Nhân sự (nhan_su): Gán tài sản cho nhân viên
        - Module Kế toán (account): Tạo journal entries cho khấu hao
    """,
    'author': "FIT-DNU",
    'website': "https://github.com/FIT-DNU",
    'category': 'Accounting/Finance',
    'version': '15.0.1.0.0',
    'depends': ['base', 'account', 'nhan_su'],
    'external_dependencies': {
        'python': ['google-generativeai'],
    },
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'data/depreciation_data.xml',
        'views/tai_san.xml',
        'views/loai_tai_san.xml',
        'views/khau_hao.xml',
        'views/phieu_kiem_ke.xml',
        'views/bao_tri_sua_chua.xml',
        'views/thanh_ly_tai_san.xml',
        'views/tinh_khau_hao_wizard.xml',
        'views/nhan_vien_extend.xml',
        'views/ai_views.xml',
        'views/tai_san_image.xml',
        'views/menu.xml',
    ],
    # View fix cho module payment - chỉ load nếu module payment được cài đặt
    # Nếu không có module payment, có thể bỏ qua file này
    # 'views/payment_fix.xml',  # Uncomment nếu cần fix lỗi payment_acquirer_id
    'demo': [
        'demo/demo.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}

