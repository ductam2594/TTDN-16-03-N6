# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import date
from dateutil.relativedelta import relativedelta

class AiChatbot(models.TransientModel):
    _name = 'ai.chatbot'
    _description = 'AI Chatbot Assistant'

    user_question = fields.Text(
        string="Câu hỏi của bạn",
        required=True,
        help="Nhập câu hỏi về quản lý tài sản, khấu hao, hoặc các vấn đề khác"
    )
    ai_answer = fields.Html(
        string="Câu trả lời AI",
        readonly=True
    )

    def _get_gemini_api_key(self):
        """Get Gemini API Key from system parameter"""
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
    
    def _check_model_exists(self, model_name):
        """Safely check if a model exists in the registry"""
        try:
            self.env[model_name]
            return True
        except KeyError:
            return False
    
    def _get_database_summary(self):
        """Get comprehensive summary from all modules: quan_ly_tai_san, nhan_su, quan_ly_van_ban"""
        summary_parts = []
        today = date.today()
        
        # ========== 1. QUẢN LÝ TÀI SẢN ==========
        try:
            # Check if model exists
            if self._check_model_exists('tai_san'):
                tai_san_model = self.env['tai_san']
                all_assets = tai_san_model.search([])
                total_count = len(all_assets)
                total_original_value = sum(all_assets.mapped('gia_tri_nguyen_gia'))
                total_residual_value = sum(all_assets.mapped('gia_tri_con_lai'))
                total_depreciation = sum(all_assets.mapped('tong_khau_hao'))
                
                # Asset by status
                status_count = {}
                for asset in all_assets:
                    status = dict(asset._fields['trang_thai'].selection).get(asset.trang_thai, asset.trang_thai)
                    status_count[status] = status_count.get(status, 0) + 1
                
                # Asset by type
                loai_summary = []
                if self._check_model_exists('loai_tai_san'):
                    loai_tai_san_model = self.env['loai_tai_san']
                    for loai in loai_tai_san_model.search([]):
                        count = len(loai.tai_san_ids)
                        if count > 0:
                            loai_summary.append(f"  - {loai.ten_loai}: {count} tài sản")
                
                # Maintenance stats
                maintenance_count = 0
                total_maintenance_cost = 0
                if self._check_model_exists('bao_tri_sua_chua'):
                    bao_tri_model = self.env['bao_tri_sua_chua']
                    maintenance_records = bao_tri_model.search([('state', '=', 'done')])
                    maintenance_count = len(maintenance_records)
                    total_maintenance_cost = sum(maintenance_records.mapped('chi_phi'))
                
                # Depreciation records
                khau_hao_count = 0
                if self._check_model_exists('khau_hao'):
                    khau_hao_model = self.env['khau_hao']
                    khau_hao_count = khau_hao_model.search_count([('state', '=', 'posted')])
                
                # Detailed asset list with user information
                asset_details = []
                for asset in all_assets[:50]:  # Limit to 50 assets to avoid prompt too long
                    asset_info = f"  - {asset.ten_tai_san} (Mã: {asset.ma_tai_san})"
                    if asset.loai_tai_san_id:
                        asset_info += f", Loại: {asset.loai_tai_san_id.ten_loai}"
                    asset_info += f", Trạng thái: {dict(asset._fields['trang_thai'].selection).get(asset.trang_thai, asset.trang_thai)}"
                    
                    # Giá trị nguyên giá
                    asset_info += f", Giá trị nguyên giá: {asset.gia_tri_nguyen_gia:,.2f} VNĐ"
                    
                    # Thông tin khấu hao
                    if asset.ngay_put_into_use:
                        # Tính số tháng từ ngày đưa vào sử dụng đến hiện tại
                        today = date.today()
                        months_in_use = (today.year - asset.ngay_put_into_use.year) * 12 + (today.month - asset.ngay_put_into_use.month)
                        asset_info += f", Ngày đưa vào sử dụng: {asset.ngay_put_into_use.strftime('%d/%m/%Y')}"
                        asset_info += f", Đã sử dụng: {months_in_use} tháng"
                    
                    # Số tháng đã khấu hao
                    so_thang_khau_hao = len(asset.khau_hao_ids.filtered(lambda k: k.state == 'posted'))
                    asset_info += f", Số tháng đã khấu hao: {so_thang_khau_hao} tháng"
                    
                    # Giá trị khấu hao - format với 2 chữ số thập phân để không bị làm tròn sai
                    asset_info += f", Tổng khấu hao: {asset.tong_khau_hao:,.2f} VNĐ"
                    asset_info += f", Giá trị còn lại: {asset.gia_tri_con_lai:,.2f} VNĐ"
                    
                    # Lịch sử bảo trì/sửa chữa của tài sản
                    if self._check_model_exists('bao_tri_sua_chua'):
                        bao_tri_records = asset.bao_tri_sua_chua_ids.filtered(lambda b: b.state == 'done')
                        if bao_tri_records:
                            bao_tri_list = []
                            for bt in bao_tri_records:
                                loai_name = dict(bt._fields['loai_bao_tri'].selection).get(bt.loai_bao_tri, bt.loai_bao_tri)
                                ngay_str = bt.ngay_bao_tri.strftime('%d/%m/%Y') if bt.ngay_bao_tri else 'N/A'
                                chi_phi_str = f"{bt.chi_phi:,.0f}" if bt.chi_phi else "0"
                                mo_ta_str = f" - {bt.mo_ta}" if bt.mo_ta else ""
                                bao_tri_list.append(f"{loai_name} ({ngay_str}, {chi_phi_str} VNĐ{mo_ta_str})")
                            asset_info += f", Lịch sử bảo trì/sửa chữa: {len(bao_tri_records)} lần - " + "; ".join(bao_tri_list)
                        else:
                            asset_info += ", Lịch sử bảo trì/sửa chữa: Chưa có"
                    
                    if asset.nhan_vien_su_dung_id:
                        asset_info += f", Người sử dụng: {asset.nhan_vien_su_dung_id.ho_ten}"
                        if asset.nhan_vien_su_dung_id.phong_ban_id:
                            asset_info += f" (Phòng ban: {asset.nhan_vien_su_dung_id.phong_ban_id.ten_phong_ban})"
                    else:
                        asset_info += ", Chưa gán cho ai"
                    if asset.vi_tri:
                        asset_info += f", Vị trí: {asset.vi_tri}"
                    asset_details.append(asset_info)
                
                # Assets by user
                assets_by_user = {}
                for asset in all_assets:
                    if asset.nhan_vien_su_dung_id:
                        user_name = asset.nhan_vien_su_dung_id.ho_ten
                        if user_name not in assets_by_user:
                            assets_by_user[user_name] = []
                        assets_by_user[user_name].append(asset.ten_tai_san)
                
                user_assets_summary = []
                for user_name, asset_list in list(assets_by_user.items())[:20]:  # Limit to 20 users
                    user_assets_summary.append(f"  - {user_name}: {len(asset_list)} tài sản ({', '.join(asset_list[:3])}{'...' if len(asset_list) > 3 else ''})")
                
                summary_parts.append(f"""
=== QUẢN LÝ TÀI SẢN ===
Tổng quan:
- Tổng số tài sản: {total_count}
- Tổng giá trị nguyên giá: {total_original_value:,.2f} VNĐ
- Tổng giá trị còn lại: {total_residual_value:,.2f} VNĐ
- Tổng khấu hao đã tính: {total_depreciation:,.2f} VNĐ
- Số bút toán khấu hao đã ghi sổ: {khau_hao_count}

Phân loại theo trạng thái:
{chr(10).join([f"  - {status}: {count} tài sản" for status, count in status_count.items()]) if status_count else "  - Chưa có dữ liệu"}

Phân loại theo loại tài sản:
{chr(10).join(loai_summary) if loai_summary else "  - Chưa có dữ liệu"}

Bảo trì/Sửa chữa:
- Số lần bảo trì đã hoàn thành: {maintenance_count}
- Tổng chi phí bảo trì: {total_maintenance_cost:,.2f} VNĐ

Danh sách tài sản chi tiết (tối đa 50 tài sản đầu tiên):
{chr(10).join(asset_details) if asset_details else "  - Chưa có dữ liệu"}

Tài sản theo người sử dụng:
{chr(10).join(user_assets_summary) if user_assets_summary else "  - Chưa có tài sản nào được gán cho nhân viên"}
""")
            else:
                summary_parts.append("\n=== QUẢN LÝ TÀI SẢN ===\nModule chưa được cài đặt hoặc không có trong registry.\n")
        except Exception as e:
            summary_parts.append(f"\n=== QUẢN LÝ TÀI SẢN ===\nLỗi khi đọc dữ liệu: {str(e)}\n")
        
        # ========== 2. QUẢN LÝ NHÂN SỰ ==========
        try:
            # Check if model exists
            if self._check_model_exists('nhan_vien'):
                nhan_vien_model = self.env['nhan_vien']
                all_employees = nhan_vien_model.search([])
                total_employees = len(all_employees)
                
                # Employees by department
                dept_summary = []
                if self._check_model_exists('phong_ban'):
                    phong_ban_model = self.env['phong_ban']
                    for dept in phong_ban_model.search([]):
                        emp_count = len(dept.nhan_vien_ids)
                        if emp_count > 0:
                            dept_summary.append(f"  - {dept.ten_phong_ban}: {emp_count} nhân viên")
                
                # Employees by position
                position_summary = []
                if self._check_model_exists('chuc_vu'):
                    chuc_vu_model = self.env['chuc_vu']
                    position_count = {}
                    for emp in all_employees:
                        if emp.chuc_vu_id:
                            pos_name = emp.chuc_vu_id.name if hasattr(emp.chuc_vu_id, 'name') else str(emp.chuc_vu_id)
                            position_count[pos_name] = position_count.get(pos_name, 0) + 1
                    position_summary = [f"  - {pos}: {count} người" for pos, count in position_count.items()]
                
                # Age statistics
                avg_age = 0
                if total_employees > 0:
                    total_age = sum(all_employees.mapped('tuoi'))
                    avg_age = total_age / total_employees if total_age > 0 else 0
                
                # Salary statistics
                total_salary = sum([e.luong for e in all_employees if e.luong])
                avg_salary = total_salary / total_employees if total_employees > 0 and total_salary > 0 else 0
                
                # Detailed employee list
                employee_details = []
                for emp in all_employees[:50]:  # Limit to 50 employees
                    emp_info = f"  - {emp.ho_ten}"
                    if emp.phong_ban_id:
                        emp_info += f" (Phòng ban: {emp.phong_ban_id.ten_phong_ban})"
                    if emp.chuc_vu_id:
                        chuc_vu_name = emp.chuc_vu_id.name if hasattr(emp.chuc_vu_id, 'name') else str(emp.chuc_vu_id)
                        emp_info += f", Chức vụ: {chuc_vu_name}"
                    if emp.luong:
                        emp_info += f", Lương: {emp.luong:,.0f} VNĐ/tháng"
                    if emp.email:
                        emp_info += f", Email: {emp.email}"
                    if emp.so_dien_thoai:
                        emp_info += f", SĐT: {emp.so_dien_thoai}"
                    employee_details.append(emp_info)
                
                summary_parts.append(f"""
=== QUẢN LÝ NHÂN SỰ ===
Tổng quan:
- Tổng số nhân viên: {total_employees}
- Tuổi trung bình: {avg_age:.1f} tuổi
- Tổng quỹ lương: {total_salary:,.0f} VNĐ
- Lương trung bình: {avg_salary:,.0f} VNĐ/tháng

Phân loại theo phòng ban:
{chr(10).join(dept_summary) if dept_summary else "  - Chưa có dữ liệu"}

Phân loại theo chức vụ:
{chr(10).join(position_summary) if position_summary else "  - Chưa có dữ liệu"}

Danh sách nhân viên chi tiết (tối đa 50 nhân viên đầu tiên):
{chr(10).join(employee_details) if employee_details else "  - Chưa có dữ liệu"}
""")
            else:
                summary_parts.append("\n=== QUẢN LÝ NHÂN SỰ ===\nModule chưa được cài đặt hoặc không có trong registry.\n")
        except Exception as e:
            summary_parts.append(f"\n=== QUẢN LÝ NHÂN SỰ ===\nLỗi khi đọc dữ liệu: {str(e)}\n")
        
        # ========== 3. QUẢN LÝ VĂN BẢN ==========
        try:
            van_ban_den_count = 0
            van_ban_di_count = 0
            loai_van_ban_count = 0
            recent_den = 0
            recent_di = 0
            
            if self._check_model_exists('van_ban_den'):
                van_ban_den_model = self.env['van_ban_den']
                van_ban_den_count = van_ban_den_model.search_count([])
                # Recent documents (last 30 days)
                thirty_days_ago = date(today.year, today.month, today.day) - relativedelta(days=30)
                recent_den = van_ban_den_model.search_count([
                    ('create_date', '>=', thirty_days_ago.strftime('%Y-%m-%d'))
                ])
            
            if self._check_model_exists('van_ban_di'):
                van_ban_di_model = self.env['van_ban_di']
                van_ban_di_count = van_ban_di_model.search_count([])
                thirty_days_ago = date(today.year, today.month, today.day) - relativedelta(days=30)
                recent_di = van_ban_di_model.search_count([
                    ('create_date', '>=', thirty_days_ago.strftime('%Y-%m-%d'))
                ])
            
            if self._check_model_exists('loai_van_ban'):
                loai_van_ban_model = self.env['loai_van_ban']
                loai_van_ban_count = loai_van_ban_model.search_count([])
            
            summary_parts.append(f"""
=== QUẢN LÝ VĂN BẢN ===
Tổng quan:
- Tổng số văn bản đến: {van_ban_den_count}
- Tổng số văn bản đi: {van_ban_di_count}
- Số loại văn bản: {loai_van_ban_count}
- Văn bản đến trong 30 ngày gần đây: {recent_den}
- Văn bản đi trong 30 ngày gần đây: {recent_di}
""")
        except Exception as e:
            summary_parts.append(f"\n=== QUẢN LÝ VĂN BẢN ===\nLỗi khi đọc dữ liệu: {str(e)}\n")
        
        # Combine all summaries
        full_summary = "\n".join(summary_parts)
        return full_summary
    
    def _detect_anomalies(self):
        """Detect anomalies in asset maintenance costs"""
        anomalies = []
        tai_san_model = self.env['tai_san']
        
        all_assets = tai_san_model.search([])
        
        for asset in all_assets:
            if asset.gia_tri_nguyen_gia > 0:
                maintenance_ratio = (asset.tong_chi_phi_bao_tri / asset.gia_tri_nguyen_gia) * 100
                if maintenance_ratio > 30:
                    anomalies.append(
                        f"- Tài sản '{asset.ten_tai_san}' (Mã: {asset.ma_tai_san}): "
                        f"Chi phí bảo trì ({asset.tong_chi_phi_bao_tri:,.0f} VNĐ) chiếm {maintenance_ratio:.1f}% "
                        f"giá trị nguyên giá ({asset.gia_tri_nguyen_gia:,.0f} VNĐ). "
                        f"Đây là dấu hiệu tài sản có thể cần được đánh giá lại hoặc thanh lý."
                    )
        
        if anomalies:
            return "\n\nCẢNH BÁO - Phát hiện bất thường:\n" + "\n".join(anomalies)
        return ""
    
    def action_ask_bot(self):
        """Process user question with AI"""
        self.ensure_one()
        
        if not self.user_question:
            raise ValidationError("Vui lòng nhập câu hỏi!")
        
        # Gather context
        database_summary = self._get_database_summary()
        anomalies = self._detect_anomalies()
        
        # Build prompt
        prompt = f"""Bạn là Trợ lý Ảo Odoo chuyên về quản lý tài sản, nhân sự và văn bản.

BẠN CÓ QUYỀN TRUY CẬP DỮ LIỆU THỰC TẾ TỪ HỆ THỐNG:

{database_summary}
{anomalies}

CÂU HỎI CỦA NGƯỜI DÙNG: {self.user_question}

HƯỚNG DẪN TRẢ LỜI:
1. Trả lời bằng tiếng Việt, rõ ràng và chuyên nghiệp
2. SỬ DỤNG DỮ LIỆU THỰC TẾ từ hệ thống đã cung cấp ở trên để trả lời chính xác
3. Nếu câu hỏi liên quan đến số liệu cụ thể (số lượng tài sản, nhân viên, văn bản...), hãy trích dẫn số liệu từ dữ liệu trên
4. Nếu người dùng hỏi về quy trình, hãy cung cấp quy trình chuẩn chuyên nghiệp trong Odoo
5. Nếu câu hỏi về bảo trì/sửa chữa của tài sản (ví dụ: "PC có sửa chữa gì không", "PC đã bảo trì chưa"):
   - Tìm tài sản trong danh sách chi tiết theo tên hoặc mã (ví dụ: "PC", "TS00002")
   - Xem phần "Lịch sử bảo trì/sửa chữa" của tài sản đó trong dữ liệu
   - Nếu có lịch sử bảo trì/sửa chữa, PHẢI liệt kê chi tiết: loại (Bảo trì/Sửa chữa/Bảo dưỡng/Bảo hành), ngày, chi phí, mô tả (nếu có)
   - Nếu không có lịch sử, trả lời rõ ràng là "chưa có bảo trì/sửa chữa nào được ghi nhận"
   - PHẢI trả lời cụ thể và rõ ràng, không được nói chung chung như "có thể cần xem trong nhật ký"
6. Nếu câu hỏi về nhân viên/phòng ban, hãy sử dụng thông tin nhân sự từ hệ thống
7. Nếu câu hỏi về văn bản, hãy tham khảo dữ liệu văn bản đến/đi trong hệ thống
8. Nếu câu hỏi về khấu hao tài sản:
   - Tìm tài sản trong danh sách chi tiết theo tên hoặc mã (ví dụ: "PC", "TS00002")
   - QUAN TRỌNG: So sánh "Giá trị nguyên giá" với "Giá trị còn lại" để xác định tài sản đã khấu hao hay chưa
   - Nếu "Tổng khấu hao" > 0 VNĐ thì PHẢI nói rõ tài sản ĐÃ ĐƯỢC KHẤU HAO, không được nói "chưa khấu hao" hay "giá trị còn nguyên"
   - Sử dụng thông tin "Số tháng đã khấu hao: X tháng" để trả lời câu hỏi về số tháng đã khấu hao
   - Sử dụng "Tổng khấu hao: X,XX VNĐ" (với 2 chữ số thập phân) để trả lời về giá trị đã khấu hao - PHẢI dùng đúng số này từ dữ liệu
   - Sử dụng "Giá trị còn lại: X,XX VNĐ" (với 2 chữ số thập phân) để trả lời về giá trị hiện tại - PHẢI dùng đúng số này từ dữ liệu
   - Sử dụng "Ngày đưa vào sử dụng" và "Đã sử dụng: X tháng" để tính toán thời gian
   - TUYỆT ĐỐI KHÔNG được nói giá trị còn lại bằng giá trị nguyên giá nếu "Tổng khấu hao" > 0
9. Luôn cung cấp thông tin hữu ích và có thể áp dụng ngay
10. Nếu không tìm thấy thông tin cụ thể trong dữ liệu, hãy giải thích rõ ràng và đề xuất cách kiểm tra

VÍ DỤ CÁCH TRẢ LỜI:
- Câu hỏi: "PC đã được khấu hao bao nhiêu tháng rồi?"
  → Tìm trong danh sách tài sản chi tiết tài sản có tên chứa "PC" hoặc mã "TS00002"
  → Trả lời: "PC (Mã: TS00002) đã được khấu hao X tháng. Tổng khấu hao đã tính là X,XX VNĐ, giá trị còn lại là X,XX VNĐ (theo thông tin trong hệ thống)"

- Câu hỏi: "PC đã khấu hao bao nhiêu tiền rồi?"
  → Tìm trong danh sách tài sản chi tiết tài sản có tên chứa "PC"
  → Trả lời: "PC (Mã: TS00002) đã được khấu hao X,XX VNĐ. Giá trị nguyên giá là X,XX VNĐ, giá trị còn lại là X,XX VNĐ (theo thông tin trong hệ thống)"
  → QUAN TRỌNG: Nếu "Tổng khấu hao" > 0 thì PHẢI nói rõ là đã khấu hao, không được nói "chưa khấu hao" hay "giá trị còn nguyên"

- Câu hỏi: "PC có sửa chữa gì không?" hoặc "PC đã bảo trì chưa?"
  → Tìm trong danh sách tài sản chi tiết tài sản có tên chứa "PC" hoặc mã "TS00002"
  → Xem phần "Lịch sử bảo trì/sửa chữa" của PC đó
  → Nếu có: "PC (Mã: TS00002) đã có X lần bảo trì/sửa chữa: [liệt kê chi tiết từng lần: loại, ngày, chi phí, mô tả]"
  → Nếu không có: "PC (Mã: TS00002) chưa có lịch sử bảo trì/sửa chữa nào được ghi nhận trong hệ thống"
  → QUAN TRỌNG: PHẢI trả lời cụ thể và rõ ràng dựa trên dữ liệu "Lịch sử bảo trì/sửa chữa" trong danh sách tài sản chi tiết, không được nói chung chung

- Câu hỏi: "Lương của Nguyen Duy là bao nhiêu?"
  → Tìm trong danh sách nhân viên chi tiết người có tên "Nguyen Duy"
  → Trả lời: "Lương của Nguyen Duy là X,XXX,XXX VNĐ/tháng"

Hãy trả lời chi tiết dựa trên dữ liệu thực tế từ hệ thống.
"""
        
        try:
            ai_response = self._call_gemini_ai(prompt)
            
            # Format response with HTML
            formatted_response = ai_response.replace('\n', '<br/>')
            
            self.write({
                'ai_answer': formatted_response
            })
            
            return {
                'type': 'ir.actions.act_window',
                'name': 'Trợ lý ảo AI',
                'res_model': 'ai.chatbot',
                'view_mode': 'form',
                'target': 'new',
                'res_id': self.id,
                'context': {'form_view_initial_mode': 'readonly'}
            }
        except Exception as e:
            raise ValidationError(f"Lỗi khi gọi AI: {str(e)}")

