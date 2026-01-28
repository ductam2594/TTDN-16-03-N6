# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError

class LoaiTaiSan(models.Model):
    _name = 'loai_tai_san'
    _description = 'Loại Tài sản'
    _rec_name = 'ten_loai'

    ten_loai = fields.Char(string="Tên loại tài sản", required=True)
    ma_loai = fields.Char(string="Mã loại", required=True)
    mo_ta = fields.Text(string="Mô tả")
    thoi_gian_khau_hao = fields.Integer(
        string="Thời gian khấu hao (tháng)",
        required=True,
        default=60,
        help="Thời gian khấu hao tính bằng tháng (ví dụ: 60 tháng = 5 năm)"
    )
    ty_le_khau_hao = fields.Float(
        string="Tỷ lệ khấu hao (%)",
        compute='_compute_ty_le_khau_hao',
        store=True,
        help="Tỷ lệ khấu hao hàng tháng tự động tính từ thời gian khấu hao"
    )
    
    # Company
    company_id = fields.Many2one(
        'res.company',
        string="Công ty",
        default=lambda self: self.env.company,
        required=True
    )
    
    # Tài khoản kế toán
    tai_khoan_tai_san_id = fields.Many2one(
        'account.account',
        string="Tài khoản Tài sản",
        domain="[('deprecated', '=', False), ('user_type_id.type', '=', 'asset')]",
        check_company=True,
        help="Tài khoản để ghi nhận giá trị tài sản"
    )
    tai_khoan_khau_hao_id = fields.Many2one(
        'account.account',
        string="Tài khoản Khấu hao",
        domain="[('deprecated', '=', False), ('user_type_id.type', '=', 'asset')]",
        check_company=True,
        help="Tài khoản để ghi nhận khấu hao tích lũy"
    )
    tai_khoan_chi_phi_id = fields.Many2one(
        'account.account',
        string="Tài khoản Chi phí Khấu hao",
        domain="[('deprecated', '=', False), ('user_type_id.type', 'in', ['expense', 'other'])]",
        check_company=True,
        help="Tài khoản để ghi nhận chi phí khấu hao hàng tháng"
    )
    
    tai_san_ids = fields.One2many('tai_san', 'loai_tai_san_id', string="Danh sách tài sản")
    so_luong_tai_san = fields.Integer(string="Số lượng tài sản", compute='_compute_so_luong_tai_san', store=False)

    @api.depends('thoi_gian_khau_hao')
    def _compute_ty_le_khau_hao(self):
        for record in self:
            if record.thoi_gian_khau_hao > 0:
                record.ty_le_khau_hao = 100.0 / record.thoi_gian_khau_hao
            else:
                record.ty_le_khau_hao = 0.0

    @api.depends('tai_san_ids')
    def _compute_so_luong_tai_san(self):
        for record in self:
            record.so_luong_tai_san = len(record.tai_san_ids)

    @api.constrains('thoi_gian_khau_hao')
    def _check_thoi_gian_khau_hao(self):
        for record in self:
            if record.thoi_gian_khau_hao <= 0:
                raise ValidationError("Thời gian khấu hao phải lớn hơn 0!")
    
    @api.constrains('tai_khoan_tai_san_id', 'tai_khoan_khau_hao_id', 'tai_khoan_chi_phi_id', 'company_id')
    def _check_tai_khoan_company(self):
        """Kiểm tra tài khoản phải cùng company với loại tài sản"""
        for record in self:
            if record.tai_khoan_tai_san_id and record.tai_khoan_tai_san_id.company_id != record.company_id:
                raise ValidationError(f"Tài khoản Tài sản phải thuộc cùng công ty với loại tài sản!")
            if record.tai_khoan_khau_hao_id and record.tai_khoan_khau_hao_id.company_id != record.company_id:
                raise ValidationError(f"Tài khoản Khấu hao phải thuộc cùng công ty với loại tài sản!")
            if record.tai_khoan_chi_phi_id and record.tai_khoan_chi_phi_id.company_id != record.company_id:
                raise ValidationError(f"Tài khoản Chi phí phải thuộc cùng công ty với loại tài sản!")




