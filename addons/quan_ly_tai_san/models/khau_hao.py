# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError
from datetime import date, datetime
from dateutil.relativedelta import relativedelta

class KhauHao(models.Model):
    _name = 'khau_hao'
    _description = 'Khấu hao Tài sản'
    _order = 'thang_khau_hao desc'
    _rec_name = 'display_name'

    tai_san_id = fields.Many2one('tai_san', string="Tài sản", required=True, ondelete='cascade')
    thang_khau_hao = fields.Date(string="Tháng khấu hao", required=True)
    so_tien_khau_hao = fields.Float(string="Số tiền khấu hao", required=True, digits=(16, 0))
    state = fields.Selection([
        ('draft', 'Nháp'),
        ('posted', 'Đã ghi sổ'),
        ('cancelled', 'Đã hủy')
    ], string="Trạng thái", default='draft', required=True)
    
    # Thông tin kế toán
    account_move_id = fields.Many2one('account.move', string="Bút toán kế toán", readonly=True)
    journal_id = fields.Many2one('account.journal', string="Sổ nhật ký", required=True)
    
    # Computed fields
    display_name = fields.Char(string="Tên hiển thị", compute='_compute_display_name', store=True)
    gia_tri_con_lai = fields.Float(string="Giá trị còn lại", compute='_compute_gia_tri_con_lai', store=False, digits=(16, 0))
    
    @api.depends('tai_san_id', 'thang_khau_hao')
    def _compute_display_name(self):
        for record in self:
            if record.tai_san_id and record.thang_khau_hao:
                month_str = record.thang_khau_hao.strftime('%m/%Y')
                record.display_name = f"{record.tai_san_id.ten_tai_san} - {month_str}"
            else:
                record.display_name = "Khấu hao"

    def _compute_gia_tri_con_lai(self):
        """Tính giá trị còn lại sau khi khấu hao
        
        Giá trị còn lại = Giá trị nguyên giá - Tổng khấu hao đã tính
        Nếu có khấu hao trước đó, tính dựa trên giá trị còn lại của khấu hao trước đó.
        """
        for record in self:
            if record.tai_san_id:
                # Tính giá trị còn lại tại thời điểm khấu hao này
                khau_hao_truoc = self.env['khau_hao'].search([
                    ('tai_san_id', '=', record.tai_san_id.id),
                    ('thang_khau_hao', '<', record.thang_khau_hao),
                    ('state', '=', 'posted')
                ], order='thang_khau_hao desc', limit=1)
                
                if khau_hao_truoc:
                    record.gia_tri_con_lai = khau_hao_truoc.gia_tri_con_lai - record.so_tien_khau_hao
                else:
                    record.gia_tri_con_lai = record.tai_san_id.gia_tri_nguyen_gia - record.so_tien_khau_hao
                
                # Đảm bảo giá trị còn lại không âm
                if record.gia_tri_con_lai < 0:
                    record.gia_tri_con_lai = 0.0
            else:
                record.gia_tri_con_lai = 0.0

    @api.constrains('thang_khau_hao', 'tai_san_id', 'so_tien_khau_hao', 'journal_id')
    def _check_thang_khau_hao(self):
        """Kiểm tra các điều kiện hợp lệ cho khấu hao"""
        for record in self:
            if not record.tai_san_id:
                continue
            
            # Kiểm tra số tiền khấu hao phải > 0
            if record.so_tien_khau_hao <= 0:
                raise ValidationError("Số tiền khấu hao phải lớn hơn 0!")
            
            # Kiểm tra không được khấu hao trước ngày đưa vào sử dụng
            if record.thang_khau_hao < record.tai_san_id.ngay_put_into_use:
                raise ValidationError(
                    f"Không thể khấu hao trước ngày đưa vào sử dụng ({record.tai_san_id.ngay_put_into_use.strftime('%d/%m/%Y')})!"
                )
            
            # Kiểm tra không được khấu hao trong tương lai (cho phép khấu hao tháng hiện tại)
            today = date.today()
            thang_hien_tai = today.replace(day=1)
            if record.thang_khau_hao > thang_hien_tai:
                raise ValidationError("Không thể khấu hao cho tháng trong tương lai!")
            
            # Kiểm tra không được khấu hao trùng tháng
            existing = self.env['khau_hao'].search([
                ('tai_san_id', '=', record.tai_san_id.id),
                ('thang_khau_hao', '=', record.thang_khau_hao),
                ('id', '!=', record.id),
                ('state', '!=', 'cancelled')
            ])
            if existing:
                raise ValidationError(f"Đã tồn tại khấu hao cho tháng {record.thang_khau_hao.strftime('%m/%Y')}!")
            
            # Kiểm tra journal phải cùng company với tài sản
            if record.journal_id and record.tai_san_id.company_id:
                if record.journal_id.company_id != record.tai_san_id.company_id:
                    raise ValidationError("Sổ nhật ký phải thuộc cùng công ty với tài sản!")
            
            # Kiểm tra journal phải active
            if record.journal_id and not record.journal_id.active:
                raise ValidationError("Sổ nhật ký đã bị vô hiệu hóa!")

    def action_post(self):
        """Ghi nhận khấu hao vào sổ cái kế toán
        
        Tạo bút toán kế toán với:
        - Nợ: Chi phí khấu hao (Expense account)
        - Có: Khấu hao tích lũy (Contra-asset account)
        
        Raises:
            UserError: Nếu trạng thái không phải draft hoặc thiếu tài khoản
        """
        for record in self:
            if record.state != 'draft':
                raise UserError("Chỉ có thể ghi sổ các bút toán ở trạng thái Nháp!")
            
            # Kiểm tra journal
            if not record.journal_id:
                raise UserError("Vui lòng chọn sổ nhật ký!")
            if not record.journal_id.active:
                raise UserError("Sổ nhật ký đã bị vô hiệu hóa!")
            
            # Lấy tài khoản thực tế được sử dụng
            tai_khoan_chi_phi = record.tai_san_id._get_tai_khoan_chi_phi()
            tai_khoan_khau_hao = record.tai_san_id._get_tai_khoan_khau_hao()
            
            if not tai_khoan_chi_phi:
                raise UserError(f"Tài sản '{record.tai_san_id.ten_tai_san}' chưa được cấu hình tài khoản chi phí khấu hao!")
            
            if not tai_khoan_khau_hao:
                raise UserError(f"Tài sản '{record.tai_san_id.ten_tai_san}' chưa được cấu hình tài khoản khấu hao!")
            
            # Kiểm tra số tiền khấu hao
            if record.so_tien_khau_hao <= 0:
                raise UserError("Số tiền khấu hao phải lớn hơn 0!")
            
            # Tạo bút toán kế toán
            move_vals = {
                'journal_id': record.journal_id.id,
                'date': record.thang_khau_hao,
                'ref': f"Khấu hao {record.tai_san_id.ten_tai_san} - {record.thang_khau_hao.strftime('%m/%Y')}",
                'line_ids': [
                    # Nợ: Chi phí khấu hao
                    (0, 0, {
                        'account_id': tai_khoan_chi_phi.id,
                        'debit': record.so_tien_khau_hao,
                        'credit': 0,
                        'name': f"Chi phí khấu hao {record.tai_san_id.ten_tai_san} - {record.thang_khau_hao.strftime('%m/%Y')}",
                    }),
                    # Có: Khấu hao tích lũy
                    (0, 0, {
                        'account_id': tai_khoan_khau_hao.id,
                        'debit': 0,
                        'credit': record.so_tien_khau_hao,
                        'name': f"Khấu hao tích lũy {record.tai_san_id.ten_tai_san} - {record.thang_khau_hao.strftime('%m/%Y')}",
                    }),
                ],
            }
            
            account_move = self.env['account.move'].create(move_vals)
            account_move._post()
            
            record.write({
                'state': 'posted',
                'account_move_id': account_move.id
            })
        
        return True

    def action_cancel(self):
        """Hủy khấu hao và đảo ngược bút toán kế toán"""
        for record in self:
            if record.state == 'posted' and record.account_move_id:
                # Đảo ngược bút toán
                if record.account_move_id.state == 'posted':
                    record.account_move_id.button_draft()
                    record.account_move_id.button_cancel()
            
            record.write({'state': 'cancelled'})
        
        return True

    def action_reset_to_draft(self):
        """Đặt lại về trạng thái nháp"""
        for record in self:
            if record.state == 'cancelled':
                record.write({'state': 'draft'})
        
        return True




