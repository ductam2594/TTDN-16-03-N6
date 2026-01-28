# -*- coding: utf-8 -*-
from odoo import models, fields, api

class NhanVienExtend(models.Model):
    _inherit = 'nhan_vien'

    tai_san_ids = fields.One2many(
        'tai_san',
        'nhan_vien_su_dung_id',
        string="Tài sản đang sử dụng"
    )
    so_luong_tai_san = fields.Integer(
        string="Số lượng tài sản",
        compute='_compute_so_luong_tai_san',
        store=False
    )
    tong_gia_tri_tai_san = fields.Float(
        string="Tổng giá trị tài sản",
        compute='_compute_tong_gia_tri_tai_san',
        store=False,
        digits=(16, 0)
    )

    @api.depends('tai_san_ids')
    def _compute_so_luong_tai_san(self):
        for record in self:
            record.so_luong_tai_san = len(record.tai_san_ids.filtered(lambda ts: ts.trang_thai == 'dang_su_dung'))

    @api.depends('tai_san_ids')
    def _compute_tong_gia_tri_tai_san(self):
        for record in self:
            tai_san_dang_su_dung = record.tai_san_ids.filtered(lambda ts: ts.trang_thai == 'dang_su_dung')
            record.tong_gia_tri_tai_san = sum(tai_san_dang_su_dung.mapped('gia_tri_nguyen_gia'))

    def action_view_tai_san(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Tài sản đang sử dụng',
            'res_model': 'tai_san',
            'view_mode': 'tree,form',
            'domain': [('nhan_vien_su_dung_id', '=', self.id)],
            'context': {'default_nhan_vien_su_dung_id': self.id},
        }






