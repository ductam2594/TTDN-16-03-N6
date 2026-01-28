# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import date
from odoo.exceptions import ValidationError

class VanBanDi(models.Model):
    _name = 'van_ban_di'
    _description = 'Bảng chứa thông tin văn bản đi'
    _rec_name = 'ten_van_ban'
    _order = 'ngay_gui desc, so_van_ban_di desc'

    so_van_ban_di = fields.Char("Số văn bản đi", required=True, copy=False)
    ten_van_ban = fields.Char("Tên văn bản", required=True)
    so_hieu_van_ban = fields.Char("Số hiệu văn bản", required=True)
    noi_nhan = fields.Char("Nơi nhận")
    
    # Thông tin ngày tháng
    ngay_gui = fields.Date("Ngày gửi", required=True, default=fields.Date.today)
    ngay_ky = fields.Date("Ngày ký")
    
    # Liên kết với nhân sự
    nhan_vien_soan_thao_id = fields.Many2one(
        "nhan_vien",
        string="Người soạn thảo"
    )
    nhan_vien_ky_id = fields.Many2one(
        "nhan_vien",
        string="Người ký",
        required=True
    )
    nhan_vien_phoi_hop_ids = fields.Many2many(
        "nhan_vien",
        "van_ban_di_nhan_vien_rel",
        "van_ban_di_id",
        "nhan_vien_id",
        string="Người phối hợp"
    )
    
    # Loại văn bản
    loai_van_ban_id = fields.Many2one(
        "loai_van_ban",
        string="Loại văn bản"
    )
    
    # Trạng thái
    state = fields.Selection([
        ('draft', 'Nháp'),
        ('pending', 'Chờ duyệt'),
        ('approved', 'Đã duyệt'),
        ('sent', 'Đã gửi'),
        ('cancelled', 'Đã hủy')
    ], string="Trạng thái", default='draft', required=True)
    
    # Mô tả
    mo_ta = fields.Text("Mô tả/Nội dung")
    ghi_chu = fields.Text("Ghi chú")
    
    @api.constrains('ngay_gui', 'ngay_ky')
    def _check_ngay(self):
        """Kiểm tra ngày hợp lệ"""
        for record in self:
            if record.ngay_ky and record.ngay_gui:
                if record.ngay_ky > record.ngay_gui:
                    raise ValidationError("Ngày ký không thể sau ngày gửi!")
    
    @api.constrains('so_van_ban_di')
    def _check_so_van_ban_di_unique(self):
        """Kiểm tra số văn bản đi không trùng"""
        for record in self:
            if record.so_van_ban_di:
                existing = self.search([
                    ('so_van_ban_di', '=', record.so_van_ban_di),
                    ('id', '!=', record.id)
                ])
                if existing:
                    raise ValidationError(f"Số văn bản đi '{record.so_van_ban_di}' đã tồn tại!")
    
    def action_draft(self):
        """Chuyển về nháp"""
        self.write({'state': 'draft'})
    
    def action_pending(self):
        """Gửi chờ duyệt"""
        if not self.nhan_vien_ky_id:
            raise ValidationError("Vui lòng chọn người ký trước khi gửi duyệt!")
        self.write({'state': 'pending'})
    
    def action_approve(self):
        """Duyệt văn bản"""
        self.write({'state': 'approved'})
    
    def action_send(self):
        """Gửi văn bản"""
        if self.state != 'approved':
            raise ValidationError("Chỉ có thể gửi văn bản đã được duyệt!")
        if not self.ngay_gui:
            self.ngay_gui = fields.Date.today()
        self.write({'state': 'sent'})
    
    def action_cancel(self):
        """Hủy văn bản"""
        self.write({'state': 'cancelled'})

