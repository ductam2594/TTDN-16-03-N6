# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import UserError
from datetime import date, datetime
from dateutil.relativedelta import relativedelta

class TinhKhauHaoWizard(models.TransientModel):
    _name = 'tinh.khau.hao.wizard'
    _description = 'Tính khấu hao tự động'

    thang_khau_hao = fields.Date(
        string="Tháng khấu hao",
        required=True,
        default=lambda self: date.today().replace(day=1)
    )
    journal_id = fields.Many2one(
        'account.journal',
        string="Sổ nhật ký",
        required=True,
        domain="[('type', '=', 'general')]"
    )
    auto_post = fields.Boolean(
        string="Tự động ghi sổ",
        default=True,
        help="Nếu chọn, các bút toán khấu hao sẽ tự động được ghi sổ"
    )

    @api.constrains('thang_khau_hao', 'journal_id')
    def _check_wizard(self):
        """Kiểm tra các điều kiện hợp lệ cho wizard"""
        for record in self:
            if not record.thang_khau_hao:
                continue
            
            # Kiểm tra không được tính khấu hao cho tháng trong tương lai
            today = date.today()
            thang_hien_tai = today.replace(day=1)
            if record.thang_khau_hao > thang_hien_tai:
                raise ValidationError("Không thể tính khấu hao cho tháng trong tương lai!")
            
            # Kiểm tra journal
            if record.journal_id:
                if not record.journal_id.active:
                    raise ValidationError("Sổ nhật ký đã bị vô hiệu hóa!")
                if record.journal_id.type != 'general':
                    raise ValidationError("Sổ nhật ký phải là loại 'Chung' (General)!")

    def action_tinh_khau_hao(self):
        """Tính khấu hao cho tất cả tài sản trong tháng được chọn"""
        self.ensure_one()
        
        if not self.journal_id:
            raise UserError("Vui lòng chọn sổ nhật ký!")
        
        # Tính ngày cuối tháng để so sánh chính xác
        ngay_cuoi_thang = self.thang_khau_hao + relativedelta(months=1, days=-1)
        
        # Tìm tất cả tài sản đang sử dụng và đã đưa vào sử dụng trong tháng này hoặc trước đó
        tai_san_ids = self.env['tai_san'].search([
            ('trang_thai', '=', 'dang_su_dung'),
            ('ngay_put_into_use', '<=', ngay_cuoi_thang)
        ])
        
        if not tai_san_ids:
            raise UserError("Không có tài sản nào cần khấu hao trong tháng này!")
        
        created_count = 0
        posted_count = 0
        skipped_count = 0
        
        import logging
        _logger = logging.getLogger(__name__)
        
        for tai_san in tai_san_ids:
            # Kiểm tra tài khoản kế toán trước khi tạo khấu hao
            tai_khoan_chi_phi = tai_san._get_tai_khoan_chi_phi()
            tai_khoan_khau_hao = tai_san._get_tai_khoan_khau_hao()
            if not tai_khoan_chi_phi or not tai_khoan_khau_hao:
                _logger.warning(f"Tài sản {tai_san.ma_tai_san} ({tai_san.ten_tai_san}) chưa cấu hình đầy đủ tài khoản kế toán. Bỏ qua.")
                skipped_count += 1
                continue
            
            # Kiểm tra xem đã có khấu hao cho tháng này chưa
            existing = self.env['khau_hao'].search([
                ('tai_san_id', '=', tai_san.id),
                ('thang_khau_hao', '=', self.thang_khau_hao),
                ('state', '!=', 'cancelled')
            ])
            
            if existing:
                continue  # Đã có khấu hao cho tháng này
            
            # Kiểm tra xem tài sản đã hết thời gian khấu hao chưa
            so_thang_da_khau_hao = len(tai_san.khau_hao_ids.filtered(lambda k: k.state == 'posted'))
            if so_thang_da_khau_hao >= tai_san.thoi_gian_khau_hao:
                continue  # Đã khấu hao hết
            
            # Tính số tiền khấu hao
            so_tien_khau_hao = tai_san.gia_tri_khau_hao_thang
            
            # Kiểm tra giá trị còn lại
            tong_khau_hao = sum(tai_san.khau_hao_ids.filtered(lambda k: k.state == 'posted').mapped('so_tien_khau_hao'))
            gia_tri_con_lai = tai_san.gia_tri_nguyen_gia - tong_khau_hao
            
            # Nếu giá trị còn lại nhỏ hơn số tiền khấu hao, chỉ khấu hao phần còn lại
            if gia_tri_con_lai < so_tien_khau_hao:
                so_tien_khau_hao = gia_tri_con_lai
            
            if so_tien_khau_hao <= 0:
                continue
            
            # Tạo bản ghi khấu hao
            khau_hao = self.env['khau_hao'].create({
                'tai_san_id': tai_san.id,
                'thang_khau_hao': self.thang_khau_hao,
                'so_tien_khau_hao': so_tien_khau_hao,
                'journal_id': self.journal_id.id,
                'state': 'draft'
            })
            
            created_count += 1
            
            # Tự động ghi sổ nếu được chọn
            if self.auto_post:
                try:
                    khau_hao.action_post()
                    posted_count += 1
                except Exception as e:
                    # Log lỗi để debug
                    _logger.warning(f"Không thể ghi sổ khấu hao {khau_hao.id} cho tài sản {tai_san.ma_tai_san}: {str(e)}")
                    # Giữ ở trạng thái draft để xử lý sau
        
        message = f"Đã tạo {created_count} bút toán khấu hao. "
        if self.auto_post:
            message += f"Đã ghi sổ {posted_count} bút toán. "
        if skipped_count > 0:
            message += f"Bỏ qua {skipped_count} tài sản chưa cấu hình đầy đủ tài khoản."
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Thành công',
                'message': message,
                'type': 'success',
                'sticky': False,
            }
        }




