# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import date
from odoo.exceptions import ValidationError

class VanBanDen(models.Model):
    _name = 'van_ban_den'
    _description = 'Bảng chứa thông tin văn bản đến'
    _rec_name = 'ten_van_ban'
    _order = 'ngay_nhan desc, so_van_ban_den desc'

    so_van_ban_den = fields.Char("Số văn bản đến", required=True, copy=False)
    ten_van_ban = fields.Char("Tên văn bản", required=True)
    so_hieu_van_ban = fields.Char("Số hiệu văn bản", required=True)
    noi_gui_den = fields.Char("Nơi gửi đến")
    
    # Thông tin ngày tháng
    ngay_nhan = fields.Date("Ngày nhận", required=True, default=fields.Date.today)
    ngay_den_han = fields.Date("Ngày đến hạn xử lý")
    ngay_hoan_thanh = fields.Date("Ngày hoàn thành")
    
    # --- LIÊN KẾT VỚI NHÂN SỰ ---
    nhan_vien_xu_ly_id = fields.Many2one(
        "nhan_vien",
        string="Cán bộ xử lý",
        required=True
    )
    nhan_vien_ky_id = fields.Many2one(
        "nhan_vien",
        string="Người ký"
    )
    nhan_vien_nhan_ids = fields.Many2many(
        "nhan_vien",
        "van_ban_den_nhan_vien_rel",
        "van_ban_den_id",
        "nhan_vien_id",
        string="Người nhận/Phối hợp"
    )
    
    # Loại văn bản
    loai_van_ban_id = fields.Many2one(
        "loai_van_ban",
        string="Loại văn bản"
    )
    
    # Trạng thái
    state = fields.Selection([
        ('new', 'Mới nhận'),
        ('processing', 'Đang xử lý'),
        ('pending', 'Chờ duyệt'),
        ('done', 'Hoàn thành'),
        ('cancelled', 'Đã hủy')
    ], string="Trạng thái", default='new', required=True)
    
    # Mô tả
    mo_ta = fields.Text("Mô tả/Nội dung")
    ghi_chu = fields.Text("Ghi chú")
    ket_qua_xu_ly = fields.Text("Kết quả xử lý")
    
    @api.constrains('ngay_nhan', 'ngay_den_han', 'ngay_hoan_thanh')
    def _check_ngay(self):
        """Kiểm tra ngày hợp lệ"""
        for record in self:
            if record.ngay_den_han and record.ngay_nhan:
                if record.ngay_den_han < record.ngay_nhan:
                    raise ValidationError("Ngày đến hạn không thể trước ngày nhận!")
            if record.ngay_hoan_thanh and record.ngay_nhan:
                if record.ngay_hoan_thanh < record.ngay_nhan:
                    raise ValidationError("Ngày hoàn thành không thể trước ngày nhận!")
    
    @api.constrains('so_van_ban_den')
    def _check_so_van_ban_den_unique(self):
        """Kiểm tra số văn bản đến không trùng"""
        for record in self:
            if record.so_van_ban_den:
                existing = self.search([
                    ('so_van_ban_den', '=', record.so_van_ban_den),
                    ('id', '!=', record.id)
                ])
                if existing:
                    raise ValidationError(f"Số văn bản đến '{record.so_van_ban_den}' đã tồn tại!")
    
    def action_processing(self):
        """Chuyển sang đang xử lý"""
        self.write({'state': 'processing'})
    
    def action_pending(self):
        """Chuyển sang chờ duyệt"""
        if not self.nhan_vien_ky_id:
            raise ValidationError("Vui lòng chọn người ký trước khi chuyển sang chờ duyệt!")
        self.write({'state': 'pending'})
    
    def action_done(self):
        """Hoàn thành xử lý"""
        if not self.ngay_hoan_thanh:
            self.ngay_hoan_thanh = fields.Date.today()
        self.write({'state': 'done'})
    
    def action_cancel(self):
        """Hủy văn bản"""
        self.write({'state': 'cancelled'})

