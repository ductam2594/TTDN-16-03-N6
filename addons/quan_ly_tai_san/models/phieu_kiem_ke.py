# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import date

class PhieuKiemKe(models.Model):
    _name = 'phieu_kiem_ke'
    _description = 'Phiếu Kiểm kê Tài sản'
    _rec_name = 'ma_phieu'
    _order = 'ngay_kiem_ke desc'

    ma_phieu = fields.Char(string="Mã phiếu", required=True, copy=False, readonly=True, default=lambda self: _('Mới'))
    ngay_kiem_ke = fields.Date(string="Ngày kiểm kê", required=True, default=fields.Date.today)
    nguoi_kiem_ke_id = fields.Many2one('nhan_vien', string="Người kiểm kê", required=True)
    phong_ban_id = fields.Many2one('phong_ban', string="Phòng ban")
    mo_ta = fields.Text(string="Ghi chú")
    
    state = fields.Selection([
        ('draft', 'Nháp'),
        ('confirmed', 'Đã xác nhận'),
        ('done', 'Hoàn thành')
    ], string="Trạng thái", default='draft', required=True)
    
    chi_tiet_ids = fields.One2many('phieu_kiem_ke.chi_tiet', 'phieu_kiem_ke_id', string="Chi tiết kiểm kê")

    @api.model
    def create(self, vals):
        if vals.get('ma_phieu', _('Mới')) == _('Mới'):
            vals['ma_phieu'] = self.env['ir.sequence'].next_by_code('phieu_kiem_ke.sequence') or _('Mới')
        return super(PhieuKiemKe, self).create(vals)

    def action_confirm(self):
        self.write({'state': 'confirmed'})

    def action_done(self):
        self.write({'state': 'done'})


class PhieuKiemKeChiTiet(models.Model):
    _name = 'phieu_kiem_ke.chi_tiet'
    _description = 'Chi tiết Phiếu Kiểm kê'

    phieu_kiem_ke_id = fields.Many2one('phieu_kiem_ke', string="Phiếu kiểm kê", required=True, ondelete='cascade')
    tai_san_id = fields.Many2one('tai_san', string="Tài sản", required=True)
    trang_thai_thuc_te = fields.Selection([
        ('dang_su_dung', 'Đang sử dụng'),
        ('bao_tri', 'Bảo trì'),
        ('thanh_ly', 'Đã thanh lý'),
        ('mat', 'Mất'),
        ('hong', 'Hỏng')
    ], string="Trạng thái thực tế", required=True)
    ghi_chu = fields.Text(string="Ghi chú")
    co_su_khac_biet = fields.Boolean(string="Có sự khác biệt", compute='_compute_co_su_khac_biet', store=True)

    @api.depends('tai_san_id', 'trang_thai_thuc_te')
    def _compute_co_su_khac_biet(self):
        for record in self:
            if record.tai_san_id and record.trang_thai_thuc_te:
                record.co_su_khac_biet = record.tai_san_id.trang_thai != record.trang_thai_thuc_te
            else:
                record.co_su_khac_biet = False

