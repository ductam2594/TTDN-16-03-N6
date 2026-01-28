# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from datetime import date

class ThanhLyTaiSan(models.Model):
    _name = 'thanh_ly_tai_san'
    _description = 'Thanh lý Tài sản'
    _rec_name = 'ma_phieu'
    _order = 'ngay_thanh_ly desc'

    ma_phieu = fields.Char(string="Mã phiếu", required=True, copy=False, readonly=True, default=lambda self: _('Mới'))
    tai_san_id = fields.Many2one('tai_san', string="Tài sản", required=True, domain="[('trang_thai', '!=', 'thanh_ly')]")
    ngay_thanh_ly = fields.Date(string="Ngày thanh lý", required=True, default=fields.Date.today)
    ly_do = fields.Text(string="Lý do thanh lý", required=True)
    
    # Giá trị (hiển thị không có phần thập phân để đồng bộ với toàn bộ module)
    gia_tri_con_lai = fields.Float(string="Giá trị còn lại", compute='_compute_gia_tri', store=False, digits=(16, 0))
    gia_tri_thanh_ly = fields.Float(string="Giá trị thanh lý", required=True, digits=(16, 0))
    lai_lo = fields.Float(string="Lãi/Lỗ", compute='_compute_lai_lo', store=False, digits=(16, 0))
    
    # Tài khoản kế toán
    tai_khoan_tien_id = fields.Many2one(
        'account.account',
        string="Tài khoản Tiền",
        domain="[('deprecated', '=', False), ('user_type_id.type', 'in', ['asset_cash', 'asset_current'])]"
    )
    tai_khoan_lai_lo_id = fields.Many2one(
        'account.account',
        string="Tài khoản Lãi/Lỗ",
        domain="[('deprecated', '=', False), ('user_type_id.type', 'in', ['income', 'expense'])]"
    )
    journal_id = fields.Many2one('account.journal', string="Sổ nhật ký", domain="[('type', '=', 'general')]")
    
    # Kế toán
    account_move_id = fields.Many2one('account.move', string="Bút toán kế toán", readonly=True)
    state = fields.Selection([
        ('draft', 'Nháp'),
        ('confirmed', 'Đã xác nhận'),
        ('done', 'Hoàn thành'),
        ('cancelled', 'Đã hủy')
    ], string="Trạng thái", default='draft', required=True)

    @api.model
    def create(self, vals):
        if vals.get('ma_phieu', _('Mới')) == _('Mới'):
            vals['ma_phieu'] = self.env['ir.sequence'].next_by_code('thanh_ly_tai_san.sequence') or _('Mới')
        return super(ThanhLyTaiSan, self).create(vals)

    @api.constrains('tai_san_id', 'gia_tri_thanh_ly', 'journal_id', 'tai_khoan_tien_id')
    def _check_thanh_ly(self):
        """Kiểm tra các điều kiện hợp lệ cho thanh lý"""
        for record in self:
            if not record.tai_san_id:
                continue
            
            # Kiểm tra tài sản không được thanh lý 2 lần
            if record.tai_san_id.trang_thai == 'thanh_ly' and record.state != 'done':
                raise ValidationError("Tài sản này đã được thanh lý!")
            
            # Kiểm tra giá trị thanh lý phải >= 0
            if record.gia_tri_thanh_ly < 0:
                raise ValidationError("Giá trị thanh lý không được âm!")
            
            # Kiểm tra journal nếu đã chọn
            if record.journal_id:
                if not record.journal_id.active:
                    raise ValidationError("Sổ nhật ký đã bị vô hiệu hóa!")
                if record.tai_san_id.company_id and record.journal_id.company_id != record.tai_san_id.company_id:
                    raise ValidationError("Sổ nhật ký phải thuộc cùng công ty với tài sản!")
            
            # Kiểm tra tài khoản tiền nếu đã chọn
            if record.tai_khoan_tien_id:
                if record.tai_san_id.company_id and record.tai_khoan_tien_id.company_id != record.tai_san_id.company_id:
                    raise ValidationError("Tài khoản Tiền phải thuộc cùng công ty với tài sản!")

    @api.depends('tai_san_id')
    def _compute_gia_tri(self):
        """Tính giá trị còn lại của tài sản tại thời điểm thanh lý"""
        for record in self:
            if record.tai_san_id:
                record.gia_tri_con_lai = record.tai_san_id.gia_tri_con_lai
            else:
                record.gia_tri_con_lai = 0.0

    @api.depends('gia_tri_thanh_ly', 'gia_tri_con_lai')
    def _compute_lai_lo(self):
        """Tính lãi/lỗ khi thanh lý
        
        Lãi/Lỗ = Giá trị thanh lý - Giá trị còn lại
        - Lãi: Giá trị thanh lý > Giá trị còn lại
        - Lỗ: Giá trị thanh lý < Giá trị còn lại
        """
        for record in self:
            record.lai_lo = record.gia_tri_thanh_ly - record.gia_tri_con_lai

    def action_confirm(self):
        self.write({'state': 'confirmed'})

    def action_done(self):
        """Hoàn thành thanh lý và tạo bút toán kế toán
        
        Thực hiện:
        1. Kiểm tra các điều kiện cần thiết
        2. Tạo bút toán kế toán thanh lý
        3. Cập nhật trạng thái tài sản thành 'thanh_ly'
        
        Raises:
            UserError: Nếu thiếu tài khoản hoặc sổ nhật ký
        """
        for record in self:
            if not record.tai_khoan_tien_id:
                raise UserError("Vui lòng chọn tài khoản Tiền!")
            if not record.journal_id:
                raise UserError("Vui lòng chọn sổ nhật ký!")
            if not record.journal_id.active:
                raise UserError("Sổ nhật ký đã bị vô hiệu hóa!")
            
            # Kiểm tra tài sản chưa được thanh lý
            if record.tai_san_id.trang_thai == 'thanh_ly':
                raise UserError("Tài sản này đã được thanh lý!")
            
            # Kiểm tra tài khoản kế toán của tài sản
            tai_khoan_tai_san = record.tai_san_id._get_tai_khoan_tai_san()
            tai_khoan_khau_hao = record.tai_san_id._get_tai_khoan_khau_hao()
            if not tai_khoan_tai_san:
                raise UserError(f"Tài sản '{record.tai_san_id.ten_tai_san}' chưa được cấu hình tài khoản tài sản!")
            
            # Tạo bút toán thanh lý
            record._create_liquidation_move()
            
            # Cập nhật trạng thái tài sản
            record.tai_san_id.write({
                'trang_thai': 'thanh_ly',
                'ngay_thanh_ly': record.ngay_thanh_ly,
                'gia_tri_thanh_ly': record.gia_tri_thanh_ly
            })
            
            record.write({'state': 'done'})

    def _create_liquidation_move(self):
        """Tạo bút toán thanh lý tài sản"""
        self.ensure_one()
        
        tai_san = self.tai_san_id
        tong_khau_hao = tai_san.tong_khau_hao
        gia_tri_nguyen_gia = tai_san.gia_tri_nguyen_gia
        
        line_ids = []
        
        # Nợ: Tiền mặt/Phải thu (giá trị thanh lý)
        line_ids.append((0, 0, {
            'account_id': self.tai_khoan_tien_id.id,
            'debit': self.gia_tri_thanh_ly,
            'credit': 0,
            'name': f"Thanh lý {tai_san.ten_tai_san}",
        }))
        
        # Lấy tài khoản thực tế được sử dụng
        tai_khoan_tai_san = tai_san._get_tai_khoan_tai_san()
        tai_khoan_khau_hao = tai_san._get_tai_khoan_khau_hao()
        
        # Nợ: Khấu hao tích lũy (tổng khấu hao)
        if tong_khau_hao > 0 and tai_khoan_khau_hao:
            line_ids.append((0, 0, {
                'account_id': tai_khoan_khau_hao.id,
                'debit': tong_khau_hao,
                'credit': 0,
                'name': f"Khấu hao tích lũy {tai_san.ten_tai_san}",
            }))
        
        # Có: Tài sản (giá trị nguyên giá)
        if tai_khoan_tai_san:
            line_ids.append((0, 0, {
                'account_id': tai_khoan_tai_san.id,
                'debit': 0,
                'credit': gia_tri_nguyen_gia,
                'name': f"Thanh lý {tai_san.ten_tai_san}",
            }))
        
        # Có/Lỗ: Thu nhập khác hoặc Chi phí khác (lãi/lỗ)
        if self.lai_lo != 0 and self.tai_khoan_lai_lo_id:
            if self.lai_lo > 0:  # Lãi
                line_ids.append((0, 0, {
                    'account_id': self.tai_khoan_lai_lo_id.id,
                    'debit': 0,
                    'credit': abs(self.lai_lo),
                    'name': f"Lãi thanh lý {tai_san.ten_tai_san}",
                }))
            else:  # Lỗ
                line_ids.append((0, 0, {
                    'account_id': self.tai_khoan_lai_lo_id.id,
                    'debit': abs(self.lai_lo),
                    'credit': 0,
                    'name': f"Lỗ thanh lý {tai_san.ten_tai_san}",
                }))
        
        move_vals = {
            'journal_id': self.journal_id.id,
            'date': self.ngay_thanh_ly,
            'ref': f"Thanh lý {tai_san.ten_tai_san} - {self.ma_phieu}",
            'line_ids': line_ids,
        }
        
        account_move = self.env['account.move'].create(move_vals)
        account_move._post()
        
        self.write({'account_move_id': account_move.id})

    def action_cancel(self):
        self.write({'state': 'cancelled'})



