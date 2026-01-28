from odoo import models, fields, api

class ChamCong(models.Model):
    _name = 'cham_cong'
    _description = 'Quản lý chấm công'
    _order = 'ngay_cham_cong desc'

    # Liên kết: Chấm công cho nhân viên nào
    nhan_vien_id = fields.Many2one('nhan_vien', string="Nhân viên", required=True)

    ngay_cham_cong = fields.Date("Ngày", default=fields.Date.today)
    gio_vao = fields.Float("Giờ vào")
    gio_ra = fields.Float("Giờ ra")
    
    # Tính tổng giờ làm (Tự động tính toán)
    tong_gio = fields.Float("Tổng giờ làm", compute='_tinh_tong_gio', store=True)

    trang_thai = fields.Selection([
        ('di_lam', 'Đi làm'),
        ('nghi_phep', 'Nghỉ phép'),
        ('nghi_khong_luong', 'Nghỉ không lương')
    ], string="Trạng thái", default='di_lam')

    @api.depends('gio_vao', 'gio_ra')
    def _tinh_tong_gio(self):
        for rec in self:
            if rec.gio_ra > rec.gio_vao:
                rec.tong_gio = rec.gio_ra - rec.gio_vao
            else:
                rec.tong_gio = 0.0