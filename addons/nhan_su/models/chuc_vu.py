from odoo import models, fields, api

class ChucVu(models.Model):
    _name = 'chuc_vu'
    _description = 'Quản lý chức vụ'
    _rec_name = 'ten_chuc_vu'

    ma_chuc_vu = fields.Char("Mã chức vụ", required=True)
    ten_chuc_vu = fields.Char("Tên chức vụ", required=True)
    mo_ta = fields.Text("Mô tả công việc")

    # Liên kết: Một chức vụ thuộc về một phòng ban
    phong_ban_id = fields.Many2one('phong_ban', string="Thuộc phòng ban")
    
    # Liên kết ngược: Để biết chức vụ này có bao nhiêu nhân viên đang nắm giữ
    nhan_vien_ids = fields.One2many('nhan_vien', 'chuc_vu_id', string="Danh sách nhân viên")