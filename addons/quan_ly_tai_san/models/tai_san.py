# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import date, datetime
from dateutil.relativedelta import relativedelta

class TaiSan(models.Model):
    _name = 'tai_san'
    _description = 'Tài sản'
    _rec_name = 'ten_tai_san'
    _order = 'ngay_mua desc'

    # Thông tin cơ bản
    ten_tai_san = fields.Char(string="Tên tài sản", required=True)
    ma_tai_san = fields.Char(string="Mã tài sản", required=True, copy=False, readonly=True, default=lambda self: _('Mới'))
    loai_tai_san_id = fields.Many2one('loai_tai_san', string="Loại tài sản", required=True)
    mo_ta = fields.Text(string="Mô tả")
    
    # Thông tin mua sắm
    ngay_mua = fields.Date(string="Ngày mua", required=True, default=fields.Date.today)
    ngay_put_into_use = fields.Date(string="Ngày đưa vào sử dụng", required=True, default=fields.Date.today)
    # Hiển thị giá trị nguyên giá không có phần thập phân (ví dụ: 30.000.000 thay vì 30.000.000,00)
    gia_tri_nguyen_gia = fields.Float(string="Giá trị nguyên giá", required=True, digits=(16, 0))
    nha_cung_cap = fields.Char(string="Nhà cung cấp")
    so_seri = fields.Char(string="Số seri/Mã vạch")
    
    # Thông tin sử dụng
    nhan_vien_su_dung_id = fields.Many2one('nhan_vien', string="Nhân viên sử dụng")
    phong_ban_id = fields.Many2one('phong_ban', string="Phòng ban", related='nhan_vien_su_dung_id.phong_ban_id', store=True)
    vi_tri = fields.Char(string="Vị trí")
    trang_thai = fields.Selection([
        ('dang_su_dung', 'Đang sử dụng'),
        ('bao_tri', 'Bảo trì'),
        ('thanh_ly', 'Đã thanh lý'),
        ('mat', 'Mất'),
        ('hong', 'Hỏng')
    ], string="Trạng thái", default='dang_su_dung', required=True)
    
    # Thông tin khấu hao
    thoi_gian_khau_hao = fields.Integer(string="Thời gian khấu hao (tháng)", related='loai_tai_san_id.thoi_gian_khau_hao', store=True)
    ty_le_khau_hao = fields.Float(string="Tỷ lệ khấu hao (%)", related='loai_tai_san_id.ty_le_khau_hao', store=True)
    gia_tri_khau_hao_thang = fields.Float(
        string="Giá trị khấu hao/tháng",
        compute='_compute_gia_tri_khau_hao_thang',
        store=True,
        digits=(16, 0)
    )
    tong_khau_hao = fields.Float(
        string="Tổng khấu hao đã tính",
        compute='_compute_tong_khau_hao',
        store=False,
        digits=(16, 0)
    )
    gia_tri_con_lai = fields.Float(
        string="Giá trị còn lại",
        compute='_compute_gia_tri_con_lai',
        store=False,
        digits=(16, 0)
    )
    so_thang_da_khau_hao = fields.Integer(
        string="Số tháng đã khấu hao",
        compute='_compute_so_thang_da_khau_hao',
        store=False
    )
    
    # Company
    company_id = fields.Many2one(
        'res.company',
        string="Công ty",
        related='loai_tai_san_id.company_id',
        store=True,
        readonly=True
    )
    
    # Tài khoản kế toán - Cho phép override cho từng tài sản
    use_custom_accounts = fields.Boolean(
        string="Sử dụng tài khoản riêng",
        default=False,
        help="Nếu chọn, có thể cấu hình tài khoản riêng cho tài sản này thay vì dùng tài khoản của loại tài sản"
    )
    tai_khoan_tai_san_id = fields.Many2one(
        'account.account',
        string="Tài khoản Tài sản",
        domain="[('deprecated', '=', False), ('user_type_id.type', '=', 'asset')]",
        check_company=True,
        help="Tài khoản để ghi nhận giá trị tài sản. Nếu không chọn, sẽ dùng tài khoản của loại tài sản."
    )
    tai_khoan_khau_hao_id = fields.Many2one(
        'account.account',
        string="Tài khoản Khấu hao",
        domain="[('deprecated', '=', False), ('user_type_id.type', '=', 'asset')]",
        check_company=True,
        help="Tài khoản để ghi nhận khấu hao tích lũy. Nếu không chọn, sẽ dùng tài khoản của loại tài sản."
    )
    tai_khoan_chi_phi_id = fields.Many2one(
        'account.account',
        string="Tài khoản Chi phí",
        domain="[('deprecated', '=', False), ('user_type_id.type', 'in', ['expense', 'other'])]",
        check_company=True,
        help="Tài khoản để ghi nhận chi phí khấu hao hàng tháng. Nếu không chọn, sẽ dùng tài khoản của loại tài sản."
    )
    
    # Quan hệ
    khau_hao_ids = fields.One2many('khau_hao', 'tai_san_id', string="Lịch sử khấu hao")
    phieu_kiem_ke_chi_tiet_ids = fields.One2many('phieu_kiem_ke.chi_tiet', 'tai_san_id', string="Lịch sử Kiểm kê")
    bao_tri_sua_chua_ids = fields.One2many('bao_tri_sua_chua', 'tai_san_id', string="Lịch sử Bảo trì/Sửa chữa")
    thanh_ly_ids = fields.One2many('thanh_ly_tai_san', 'tai_san_id', string="Lịch sử Thanh lý")
    
    # Ảnh tài sản
    image_ids = fields.One2many('tai_san.image', 'tai_san_id', string="Ảnh sản phẩm")
    
    # Thông tin thanh lý
    ngay_thanh_ly = fields.Date(string="Ngày thanh lý")
    gia_tri_thanh_ly = fields.Float(string="Giá trị thanh lý", digits=(16, 2))
    
    # Thông tin bảo hành
    ngay_het_bao_hanh = fields.Date(string="Ngày hết bảo hành")
    tong_chi_phi_bao_tri = fields.Float(
        string="Tổng chi phí bảo trì",
        compute='_compute_tong_chi_phi_bao_tri',
        store=False,
        digits=(16, 2)
    )
    
    # AI Analysis Fields
    ai_maintenance_suggestion = fields.Html(
        string="Đề xuất Bảo trì AI",
        readonly=True,
        help="Phân tích và đề xuất bảo trì từ AI"
    )
    ai_liquidation_advice = fields.Html(
        string="Tư vấn Thanh lý AI",
        readonly=True,
        help="Phân tích và tư vấn thanh lý từ AI"
    )
    
    def _compute_tong_chi_phi_bao_tri(self):
        for record in self:
            record.tong_chi_phi_bao_tri = sum(
                record.bao_tri_sua_chua_ids.filtered(lambda b: b.state == 'done').mapped('chi_phi')
            )
    

    @api.depends('gia_tri_nguyen_gia', 'thoi_gian_khau_hao')
    def _compute_gia_tri_khau_hao_thang(self):
        for record in self:
            if record.thoi_gian_khau_hao > 0:
                record.gia_tri_khau_hao_thang = record.gia_tri_nguyen_gia / record.thoi_gian_khau_hao
            else:
                record.gia_tri_khau_hao_thang = 0.0

    def _compute_tong_khau_hao(self):
        for record in self:
            tong = sum(record.khau_hao_ids.filtered(lambda k: k.state == 'posted').mapped('so_tien_khau_hao'))
            record.tong_khau_hao = tong

    def _compute_gia_tri_con_lai(self):
        """Tính giá trị còn lại của tài sản
        
        Giá trị còn lại = Giá trị nguyên giá - Tổng khấu hao đã tính
        Đảm bảo giá trị còn lại không âm.
        """
        for record in self:
            record.gia_tri_con_lai = max(0.0, record.gia_tri_nguyen_gia - record.tong_khau_hao)

    def _compute_so_thang_da_khau_hao(self):
        for record in self:
            record.so_thang_da_khau_hao = len(record.khau_hao_ids.filtered(lambda k: k.state == 'posted'))
    
    def _get_tai_khoan_tai_san(self):
        """Lấy tài khoản tài sản thực tế được sử dụng"""
        self.ensure_one()
        if self.use_custom_accounts and self.tai_khoan_tai_san_id:
            return self.tai_khoan_tai_san_id
        return self.loai_tai_san_id.tai_khoan_tai_san_id
    
    def _get_tai_khoan_khau_hao(self):
        """Lấy tài khoản khấu hao thực tế được sử dụng"""
        self.ensure_one()
        if self.use_custom_accounts and self.tai_khoan_khau_hao_id:
            return self.tai_khoan_khau_hao_id
        return self.loai_tai_san_id.tai_khoan_khau_hao_id
    
    def _get_tai_khoan_chi_phi(self):
        """Lấy tài khoản chi phí thực tế được sử dụng"""
        self.ensure_one()
        if self.use_custom_accounts and self.tai_khoan_chi_phi_id:
            return self.tai_khoan_chi_phi_id
        return self.loai_tai_san_id.tai_khoan_chi_phi_id
    
    @api.onchange('loai_tai_san_id', 'use_custom_accounts')
    def _onchange_loai_tai_san_accounts(self):
        """Khi thay đổi loại tài sản hoặc bỏ chọn custom accounts, tự động điền tài khoản từ loại tài sản"""
        for record in self:
            if not record.use_custom_accounts and record.loai_tai_san_id:
                record.tai_khoan_tai_san_id = record.loai_tai_san_id.tai_khoan_tai_san_id
                record.tai_khoan_khau_hao_id = record.loai_tai_san_id.tai_khoan_khau_hao_id
                record.tai_khoan_chi_phi_id = record.loai_tai_san_id.tai_khoan_chi_phi_id
    
    @api.model
    def create(self, vals):
        """Khi tạo mới, tự động điền tài khoản từ loại tài sản nếu chưa có"""
        if vals.get('ma_tai_san', _('Mới')) == _('Mới'):
            vals['ma_tai_san'] = self.env['ir.sequence'].next_by_code('tai_san.sequence') or _('Mới')
        
        # Nếu không dùng custom accounts, tự động điền từ loại tài sản
        if not vals.get('use_custom_accounts') and vals.get('loai_tai_san_id'):
            loai_tai_san = self.env['loai_tai_san'].browse(vals['loai_tai_san_id'])
            if not vals.get('tai_khoan_tai_san_id'):
                vals['tai_khoan_tai_san_id'] = loai_tai_san.tai_khoan_tai_san_id.id
            if not vals.get('tai_khoan_khau_hao_id'):
                vals['tai_khoan_khau_hao_id'] = loai_tai_san.tai_khoan_khau_hao_id.id
            if not vals.get('tai_khoan_chi_phi_id'):
                vals['tai_khoan_chi_phi_id'] = loai_tai_san.tai_khoan_chi_phi_id.id
        
        return super(TaiSan, self).create(vals)
    
    def write(self, vals):
        """Khi cập nhật, tự động điền tài khoản từ loại tài sản nếu bỏ chọn custom accounts"""
        if 'use_custom_accounts' in vals and not vals['use_custom_accounts']:
            for record in self:
                if record.loai_tai_san_id:
                    vals.setdefault('tai_khoan_tai_san_id', record.loai_tai_san_id.tai_khoan_tai_san_id.id)
                    vals.setdefault('tai_khoan_khau_hao_id', record.loai_tai_san_id.tai_khoan_khau_hao_id.id)
                    vals.setdefault('tai_khoan_chi_phi_id', record.loai_tai_san_id.tai_khoan_chi_phi_id.id)
        
        # Nếu thay đổi loại tài sản và không dùng custom accounts, cập nhật tài khoản
        if 'loai_tai_san_id' in vals:
            for record in self:
                if not record.use_custom_accounts and vals.get('loai_tai_san_id'):
                    loai_tai_san = self.env['loai_tai_san'].browse(vals['loai_tai_san_id'])
                    vals.setdefault('tai_khoan_tai_san_id', loai_tai_san.tai_khoan_tai_san_id.id)
                    vals.setdefault('tai_khoan_khau_hao_id', loai_tai_san.tai_khoan_khau_hao_id.id)
                    vals.setdefault('tai_khoan_chi_phi_id', loai_tai_san.tai_khoan_chi_phi_id.id)
        
        return super(TaiSan, self).write(vals)

    @api.constrains('gia_tri_nguyen_gia', 'ngay_mua', 'ngay_put_into_use')
    def _check_gia_tri_va_ngay(self):
        for record in self:
            if record.gia_tri_nguyen_gia <= 0:
                raise ValidationError("Giá trị nguyên giá phải lớn hơn 0!")
            if record.ngay_put_into_use < record.ngay_mua:
                raise ValidationError("Ngày đưa vào sử dụng không thể trước ngày mua!")
    
    @api.constrains('tai_khoan_tai_san_id', 'tai_khoan_khau_hao_id', 'tai_khoan_chi_phi_id', 'company_id')
    def _check_tai_khoan_company(self):
        """Kiểm tra tài khoản phải cùng company với tài sản"""
        for record in self:
            if record.tai_khoan_tai_san_id and record.tai_khoan_tai_san_id.company_id != record.company_id:
                raise ValidationError(f"Tài khoản Tài sản phải thuộc cùng công ty với tài sản!")
            if record.tai_khoan_khau_hao_id and record.tai_khoan_khau_hao_id.company_id != record.company_id:
                raise ValidationError(f"Tài khoản Khấu hao phải thuộc cùng công ty với tài sản!")
            if record.tai_khoan_chi_phi_id and record.tai_khoan_chi_phi_id.company_id != record.company_id:
                raise ValidationError(f"Tài khoản Chi phí phải thuộc cùng công ty với tài sản!")

    def action_view_khau_hao(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Lịch sử khấu hao',
            'res_model': 'khau_hao',
            'view_mode': 'tree,form',
            'domain': [('tai_san_id', '=', self.id)],
            'context': {'default_tai_san_id': self.id},
        }

    def _get_gemini_api_key(self):
        """Get Gemini API Key from system parameter or use default"""
        api_key = self.env['ir.config_parameter'].sudo().get_param('quan_ly_tai_san.gemini_api_key', 'PASTE_YOUR_API_KEY_HERE')
        return api_key
    
    def _call_gemini_ai(self, prompt):
        """Call Google Gemini AI API"""
        try:
            import google.generativeai as genai
            
            api_key = self._get_gemini_api_key()
            if api_key == 'PASTE_YOUR_API_KEY_HERE' or not api_key:
                raise ValueError("Chưa cấu hình Gemini API Key. Vui lòng vào Quản lý Tài sản > Cấu hình > Cấu hình AI để nhập API Key")
            
            genai.configure(api_key=api_key)
            
            # List available models first
            try:
                available_models = genai.list_models()
                model_names = [m.name for m in available_models if 'generateContent' in m.supported_generation_methods]
                
                if not model_names:
                    raise ValidationError("Không tìm thấy model nào hỗ trợ generateContent. Vui lòng kiểm tra API Key.")
                
                # Use the first available model that supports generateContent
                # Prefer models with 'gemini' in the name
                preferred_models = [m for m in model_names if 'gemini' in m.lower()]
                if preferred_models:
                    model_name = preferred_models[0]
                else:
                    model_name = model_names[0]
                
                # Remove 'models/' prefix if present for GenerativeModel
                if model_name.startswith('models/'):
                    model_name = model_name.replace('models/', '')
                
                model = genai.GenerativeModel(model_name)
                response = model.generate_content(prompt)
                
                if response and response.text:
                    # Replace * with - for bullet points
                    result = response.text.replace('*', '-')
                    return result
                else:
                    raise ValidationError("Không nhận được phản hồi từ AI. Vui lòng thử lại.")
                    
            except Exception as list_error:
                # Fallback: try common model names
                fallback_models = ['gemini-pro', 'gemini-1.5-pro', 'gemini-1.5-flash']
                last_error = list_error
                
                for model_name in fallback_models:
                    try:
                        model = genai.GenerativeModel(model_name)
                        response = model.generate_content(prompt)
                        if response and response.text:
                            # Replace * with - for bullet points
                            result = response.text.replace('*', '-')
                            return result
                    except Exception as e:
                        last_error = e
                        continue
                
                # If all failed, show available models if we got them
                error_msg = f"Lỗi khi gọi AI: {str(last_error)}"
                try:
                    available_models = genai.list_models()
                    model_list = [m.name for m in available_models[:10]]
                    error_msg += f"\n\nCác model có sẵn: {', '.join(model_list)}"
                except:
                    pass
                
                raise ValidationError(error_msg)
                
        except ImportError:
            raise ValidationError("Thư viện google.generativeai chưa được cài đặt. Chạy: pip install google-generativeai")
        except ValidationError:
            raise
        except Exception as e:
            raise ValidationError(f"Lỗi khi gọi AI: {str(e)}")
    
    def action_predict_maintenance(self):
        """Predict maintenance using AI"""
        self.ensure_one()
        
        # Gather maintenance history
        maintenance_count = len(self.bao_tri_sua_chua_ids.filtered(lambda b: b.state == 'done'))
        total_maintenance_cost = self.tong_chi_phi_bao_tri
        
        # Calculate age in months
        today = date.today()
        age_months = (today.year - self.ngay_mua.year) * 12 + (today.month - self.ngay_mua.month)
        
        # Build prompt
        prompt = f"""Dựa trên thông tin tài sản sau, hãy dự đoán ngày bảo trì tiếp theo và đề xuất các thành phần cần kiểm tra. 
Hãy giữ câu trả lời ngắn gọn và chuyên nghiệp.

Thông tin tài sản:
- Tên: {self.ten_tai_san}
- Loại: {self.loai_tai_san_id.ten_loai if self.loai_tai_san_id else 'N/A'}
- Ngày mua: {self.ngay_mua.strftime('%d/%m/%Y') if self.ngay_mua else 'N/A'}
- Giá trị nguyên giá: {self.gia_tri_nguyen_gia:,.0f} VNĐ
- Tuổi tài sản: {age_months} tháng
- Số lần bảo trì đã thực hiện: {maintenance_count}
- Tổng chi phí bảo trì: {total_maintenance_cost:,.0f} VNĐ
- Trạng thái hiện tại: {dict(self._fields['trang_thai'].selection).get(self.trang_thai, self.trang_thai)}

Hãy phân tích và đưa ra:
1. Dự đoán ngày bảo trì tiếp theo
2. Các thành phần cần kiểm tra
3. Khuyến nghị bảo trì phòng ngừa
"""
        
        try:
            ai_response = self._call_gemini_ai(prompt)
            self.write({
                'ai_maintenance_suggestion': ai_response.replace('\n', '<br/>')
            })

            # Reload form so that the "Đề xuất Bảo trì AI" field is refreshed immediately
            return {
                'type': 'ir.actions.act_window',
                'name': _('Tài sản'),
                'res_model': 'tai_san',
                'view_mode': 'form',
                'res_id': self.id,
                'target': 'current',
                'context': dict(self.env.context or {}),
            }
        except Exception as e:
            raise ValidationError(f"Lỗi khi gọi AI: {str(e)}")
    
    def action_analyze_liquidation(self):
        """Analyze liquidation using AI"""
        self.ensure_one()
        
        # Calculate age in years
        today = date.today()
        age_years = (today - self.ngay_mua).days / 365.25 if self.ngay_mua else 0
        age_months = int((today.year - self.ngay_mua.year) * 12 + (today.month - self.ngay_mua.month)) if self.ngay_mua else 0
        
        # Get current values
        original_value = self.gia_tri_nguyen_gia
        depreciated_value = self.gia_tri_con_lai
        depreciation_amount = self.tong_khau_hao
        depreciation_percentage = (depreciation_amount / original_value * 100) if original_value > 0 else 0
        
        # Build prompt
        prompt = f"""Phân tích xem có nên thanh lý tài sản này ngay bây giờ không. 
Ước tính giá trị thị trường hiện tại dựa trên tuổi tài sản, dự đoán lãi/lỗ nếu bán ngay so với giữ thêm 1 năm nữa.

THÔNG TIN TÀI SẢN (DỮ LIỆU ĐÃ ĐƯỢC TÍNH SẴN, PHẢI DÙNG ĐÚNG):
- Tên: {self.ten_tai_san}
- Loại: {self.loai_tai_san_id.ten_loai if self.loai_tai_san_id else 'N/A'}
- Ngày mua: {self.ngay_mua.strftime('%d/%m/%Y') if self.ngay_mua else 'N/A'}
- Tuổi tài sản: {age_years:.1f} năm ({age_months} tháng)
- Giá trị nguyên giá ban đầu: {original_value:,.0f} VNĐ
- Giá trị đã khấu hao LUỸ KẾ: {depreciation_amount:,.2f} VNĐ (tương đương {depreciation_percentage:.2f}% giá trị ban đầu)
- Giá trị còn lại theo sổ sách: {depreciated_value:,.2f} VNĐ
- Ngày hiện tại: {today.strftime('%d/%m/%Y')}

YÊU CẦU QUAN TRỌNG:
- Nếu giá trị đã khấu hao > 0 thì PHẢI KHẲNG ĐỊNH RÕ tài sản ĐÃ ĐƯỢC KHẤU HAO, nêu rõ số tiền và tỷ lệ phần trăm.
- Tuyệt đối KHÔNG ĐƯỢC nói hoặc ngụ ý rằng tài sản 'chưa khấu hao' hay 'chưa ghi nhận khấu hao' nếu giá trị đã khấu hao > 0.
- Khi so sánh với giá trị nguyên giá, hãy nhấn mạnh rằng giá trị còn lại đã trừ phần khấu hao ở trên.

Hãy phân tích và đưa ra:
1. Ước tính giá trị thị trường hiện tại
2. So sánh lãi/lỗ nếu bán ngay vs giữ thêm 1 năm
3. Khuyến nghị có nên thanh lý ngay không
4. Lý do cụ thể
"""
        
        try:
            ai_response = self._call_gemini_ai(prompt)
            self.write({
                'ai_liquidation_advice': ai_response.replace('\n', '<br/>')
            })

            # Reload form so that the "Tư vấn Thanh lý AI" field is refreshed immediately
            return {
                'type': 'ir.actions.act_window',
                'name': _('Tài sản'),
                'res_model': 'tai_san',
                'view_mode': 'form',
                'res_id': self.id,
                'target': 'current',
                'context': dict(self.env.context or {}),
            }
        except Exception as e:
            raise ValidationError(f"Lỗi khi gọi AI: {str(e)}")

    @api.model
    def _cron_tinh_khau_hao_hang_thang(self):
        """Scheduled action: Tự động tính khấu hao hàng tháng
        
        Lưu ý: Method này được gọi từ cron job, Odoo tự động quản lý transaction.
        Không cần rollback thủ công vì Odoo sẽ tự động rollback khi có exception.
        """
        import logging
        import psycopg2
        _logger = logging.getLogger(__name__)
        
        try:
            # Kiểm tra connection còn hoạt động không
            if hasattr(self.env.cr, 'closed') and self.env.cr.closed:
                _logger.warning("Database connection đã bị đóng, bỏ qua tính khấu hao tự động")
                return
            
            # Kiểm tra connection bằng cách thử execute một query đơn giản
            try:
                self.env.cr.execute("SELECT 1")
            except (psycopg2.InterfaceError, psycopg2.OperationalError, AttributeError):
                _logger.warning("Database connection không khả dụng, bỏ qua tính khấu hao tự động")
                return
            
            # Tìm sổ nhật ký mặc định
            journal = self.env['account.journal'].search([
                ('type', '=', 'general'),
                ('company_id', '=', self.env.company.id),
                ('active', '=', True)
            ], limit=1)
            
            if not journal:
                _logger.warning(f"Không tìm thấy sổ nhật ký active để tính khấu hao tự động cho công ty {self.env.company.name}")
                return
            
            # Tháng khấu hao là tháng hiện tại
            today = date.today()
            thang_khau_hao = today.replace(day=1)
            
            # Tạo wizard và tính khấu hao
            wizard = self.env['tinh.khau.hao.wizard'].create({
                'thang_khau_hao': thang_khau_hao,
                'journal_id': journal.id,
                'auto_post': True
            })
            
            wizard.action_tinh_khau_hao()
            
            _logger.info(f"Đã tính khấu hao tự động cho tháng {thang_khau_hao.strftime('%m/%Y')}")
            
        except (psycopg2.InterfaceError, psycopg2.OperationalError) as e:
            # Lỗi connection - không log chi tiết vì đây là lỗi hệ thống
            # Odoo sẽ tự động retry cron job sau
            _logger.warning(f"Lỗi connection khi tính khấu hao tự động (sẽ retry sau): {type(e).__name__}")
            return
        except Exception as e:
            # Lỗi logic - log chi tiết để debug
            _logger.error(f"Lỗi khi tính khấu hao tự động: {str(e)}", exc_info=True)
            # Không raise exception để tránh làm crash cron job
            # Odoo sẽ tự động rollback transaction khi có exception
            return

