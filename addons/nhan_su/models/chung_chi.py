from odoo import models, fields, api

class ChungChi(models.Model):
    _name = 'chung_chi'
    _description = 'Quản lý văn bằng chứng chỉ'

    # Liên kết: Chứng chỉ này của nhân viên nào
    nhan_vien_id = fields.Many2one('nhan_vien', string="Nhân viên", required=True)

    ten_chung_chi = fields.Char("Tên chứng chỉ", required=True)
    no_cap = fields.Char("Nơi cấp")
    ngay_cap = fields.Date("Ngày cấp")
    ngay_het_han = fields.Date("Ngày hết hạn")
    xep_loai = fields.Selection([
        ('gioi', 'Giỏi'),
        ('kha', 'Khá'),
        ('trung_binh', 'Trung bình')
    ], string="Xếp loại")