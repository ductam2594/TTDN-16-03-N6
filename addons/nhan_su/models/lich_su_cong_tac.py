from odoo import models, fields, api

class LichSuCongTac(models.Model):
    _name = 'lich_su_cong_tac'
    _description = 'Lịch sử công tác của nhân viên'
    _order = 'tu_ngay desc'
    # Liên kết: Bản ghi này thuộc về nhân viên nào
    nhan_vien_id = fields.Many2one('nhan_vien', string="Nhân viên", required=True)

    tu_ngay = fields.Date("Từ ngày", required=True)
    den_ngay = fields.Date("Đến ngày")
    vi_tri = fields.Char("Vị trí/Chức vụ")
    don_vi = fields.Char("Đơn vị/Phòng ban")
    mo_ta = fields.Text("Ghi chú chi tiết")