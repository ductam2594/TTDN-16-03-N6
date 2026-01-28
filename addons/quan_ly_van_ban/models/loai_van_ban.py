# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import date
from odoo.exceptions import ValidationError

class LoaiVanBan(models.Model):
    _name = 'loai_van_ban'
    _description = 'Bảng chứa thông tin loại văn bản'
    _rec_name = 'ten_loai_van_ban'
    _order = 'ma_loai_van_ban'

    ma_loai_van_ban = fields.Char(
        "Mã loại văn bản", 
        required=True,
        copy=False,
        help="Mã định danh duy nhất cho loại văn bản"
    )
    ten_loai_van_ban = fields.Char(
        "Tên loại văn bản", 
        required=True,
        help="Tên đầy đủ của loại văn bản (ví dụ: Công văn, Quyết định, Thông báo...)"
    )
    mo_ta = fields.Text(
        "Mô tả",
        help="Mô tả chi tiết về loại văn bản này"
    )
    active = fields.Boolean(
        "Kích hoạt",
        default=True,
        help="Nếu bỏ chọn, loại văn bản này sẽ bị ẩn nhưng không bị xóa"
    )
    
    # Thống kê
    van_ban_den_count = fields.Integer(
        "Số văn bản đến",
        compute="_compute_van_ban_count",
        store=False
    )
    van_ban_di_count = fields.Integer(
        "Số văn bản đi",
        compute="_compute_van_ban_count",
        store=False
    )
    
    @api.depends('ma_loai_van_ban')
    def _compute_van_ban_count(self):
        """Tính số lượng văn bản của loại này"""
        for record in self:
            record.van_ban_den_count = self.env['van_ban_den'].search_count([
                ('loai_van_ban_id', '=', record.id)
            ])
            record.van_ban_di_count = self.env['van_ban_di'].search_count([
                ('loai_van_ban_id', '=', record.id)
            ])
    
    @api.constrains('ma_loai_van_ban')
    def _check_ma_loai_van_ban_unique(self):
        """Kiểm tra mã loại văn bản không trùng"""
        for record in self:
            if record.ma_loai_van_ban:
                existing = self.search([
                    ('ma_loai_van_ban', '=', record.ma_loai_van_ban),
                    ('id', '!=', record.id)
                ])
                if existing:
                    raise ValidationError(f"Mã loại văn bản '{record.ma_loai_van_ban}' đã tồn tại!")
    
    @api.constrains('ma_loai_van_ban', 'ten_loai_van_ban')
    def _check_required_fields(self):
        """Kiểm tra các trường bắt buộc"""
        for record in self:
            if not record.ma_loai_van_ban or not record.ma_loai_van_ban.strip():
                raise ValidationError("Mã loại văn bản không được để trống!")
            if not record.ten_loai_van_ban or not record.ten_loai_van_ban.strip():
                raise ValidationError("Tên loại văn bản không được để trống!")

