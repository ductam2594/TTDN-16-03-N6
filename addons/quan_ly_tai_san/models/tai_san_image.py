# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError

class TaiSanImage(models.Model):
    _name = 'tai_san.image'
    _description = 'Ảnh Tài sản'
    _order = 'sequence, id desc'

    tai_san_id = fields.Many2one(
        'tai_san',
        string="Tài sản",
        required=True,
        ondelete='cascade'
    )
    name = fields.Char(
        string="Tên ảnh",
        help="Tên mô tả cho ảnh"
    )
    loai_anh = fields.Selection([
        ('anh_san_pham', 'Ảnh sản phẩm')
    ], string="Loại ảnh", required=True, default='anh_san_pham', readonly=True)
    
    image = fields.Binary(
        string="Ảnh",
        required=True,
        help="Upload ảnh tại đây"
    )
    image_filename = fields.Char(
        string="Tên file",
        help="Tên file ảnh"
    )
    sequence = fields.Integer(
        string="Thứ tự",
        default=10,
        help="Thứ tự hiển thị ảnh"
    )
    ngay_upload = fields.Datetime(
        string="Ngày upload",
        default=fields.Datetime.now,
        readonly=True
    )
    nguoi_upload_id = fields.Many2one(
        'res.users',
        string="Người upload",
        default=lambda self: self.env.user,
        readonly=True
    )
    
    
    @api.constrains('image')
    def _check_image_size(self):
        """Kiểm tra kích thước ảnh (tùy chọn)"""
        for record in self:
            if record.image:
                # Có thể thêm validation kích thước file nếu cần
                # Ví dụ: giới hạn 10MB
                pass

