# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import date, datetime
from dateutil.relativedelta import relativedelta

class BaoTriSuaChua(models.Model):
    _name = 'bao_tri_sua_chua'
    _description = 'Bảo trì & Sửa chữa Tài sản'
    _rec_name = 'ma_phieu'
    _order = 'ngay_bao_tri desc'

    ma_phieu = fields.Char(string="Mã phiếu", required=True, copy=False, readonly=True, default=lambda self: _('Mới'))
    tai_san_id = fields.Many2one('tai_san', string="Tài sản", required=True)
    loai_bao_tri = fields.Selection([
        ('bao_tri', 'Bảo trì'),
        ('sua_chua', 'Sửa chữa'),
        ('bao_duong', 'Bảo dưỡng'),
        ('bao_hanh', 'Bảo hành')
    ], string="Loại", required=True, default='bao_tri')
    
    ngay_bao_tri = fields.Date(string="Ngày bảo trì/sửa chữa", required=True, default=fields.Date.today)
    ngay_hoan_thanh = fields.Date(string="Ngày hoàn thành")
    nguoi_thuc_hien_id = fields.Many2one('nhan_vien', string="Người thực hiện")
    nha_cung_cap_id = fields.Char(string="Nhà cung cấp dịch vụ")
    
    mo_ta = fields.Text(string="Mô tả vấn đề")
    giai_phap = fields.Text(string="Giải pháp")
    # Chi phí bảo trì/sửa chữa (không hiển thị phần thập phân để đồng bộ với các giá trị tiền khác)
    chi_phi = fields.Float(string="Chi phí", digits=(16, 0))
    
    # Tài khoản kế toán
    tai_khoan_chi_phi_id = fields.Many2one(
        'account.account',
        string="Tài khoản Chi phí",
        domain="[('deprecated', '=', False), ('user_type_id.type', 'in', ['expense', 'other'])]"
    )
    tai_khoan_doi_ung_id = fields.Many2one(
        'account.account',
        string="Tài khoản Đối ứng",
        domain="[('deprecated', '=', False), ('user_type_id.type', 'in', ['asset_cash', 'asset_current', 'liability_payable'])]",
        help="Tài khoản để ghi nhận phải trả hoặc tiền mặt (ví dụ: Phải trả nhà cung cấp, Tiền mặt...)"
    )
    journal_id = fields.Many2one('account.journal', string="Sổ nhật ký", domain="[('type', '=', 'general')]")
    
    # Kế toán
    account_move_id = fields.Many2one('account.move', string="Bút toán kế toán", readonly=True)
    state = fields.Selection([
        ('draft', 'Nháp'),
        ('in_progress', 'Đang thực hiện'),
        ('done', 'Hoàn thành'),
        ('cancelled', 'Đã hủy')
    ], string="Trạng thái", default='draft', required=True)

    @api.model
    def create(self, vals):
        if vals.get('ma_phieu', _('Mới')) == _('Mới'):
            vals['ma_phieu'] = self.env['ir.sequence'].next_by_code('bao_tri_sua_chua.sequence') or _('Mới')
        return super(BaoTriSuaChua, self).create(vals)

    def action_start(self):
        self.write({'state': 'in_progress'})

    def action_done(self):
        for record in self:
            record.write({
                'state': 'done',
                'ngay_hoan_thanh': fields.Date.today()
            })
            
            # Nếu có chi phí và tài khoản, tự động tạo bút toán
            if record.chi_phi > 0 and record.tai_khoan_chi_phi_id and record.tai_khoan_doi_ung_id and record.journal_id:
                record._create_account_move()

    def _create_account_move(self):
        """Tạo bút toán kế toán cho chi phí bảo trì/sửa chữa"""
        self.ensure_one()
        
        if not self.tai_khoan_doi_ung_id:
            raise ValidationError("Vui lòng chọn Tài khoản Đối ứng để tạo bút toán!")
        
        move_vals = {
            'journal_id': self.journal_id.id,
            'date': self.ngay_bao_tri,
            'ref': f"{self.loai_bao_tri} {self.tai_san_id.ten_tai_san} - {self.ma_phieu}",
            'line_ids': [
                # Nợ: Chi phí bảo trì/sửa chữa
                (0, 0, {
                    'account_id': self.tai_khoan_chi_phi_id.id,
                    'debit': self.chi_phi,
                    'credit': 0,
                    'name': f"Chi phí {self.loai_bao_tri} {self.tai_san_id.ten_tai_san}",
                }),
                # Có: Phải trả/Tiền mặt
                (0, 0, {
                    'account_id': self.tai_khoan_doi_ung_id.id,
                    'debit': 0,
                    'credit': self.chi_phi,
                    'name': f"Thanh toán {self.loai_bao_tri} {self.tai_san_id.ten_tai_san}",
                }),
            ],
        }
        
        account_move = self.env['account.move'].create(move_vals)
        account_move._post()
        
        self.write({'account_move_id': account_move.id})

    def action_cancel(self):
        self.write({'state': 'cancelled'})



