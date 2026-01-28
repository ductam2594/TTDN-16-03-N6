# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import date
import re

class NhanVien(models.Model):
    _name = 'nhan_vien'  
    _description = 'Quản lý Nhân viên'
    _rec_name = 'ho_ten'

    # --- 1. THÔNG TIN CƠ BẢN ---
    ho_ten = fields.Char(string="Họ và tên", required=True)
    ngay_sinh = fields.Date(string="Ngày sinh", required=True)
    gioi_tinh = fields.Selection([
        ('nam', 'Nam'),
        ('nu', 'Nữ'),
        ('khac', 'Khác')
    ], string="Giới tính", default='nam')

    # --- 2. THÔNG TIN LIÊN HỆ & LƯƠNG (Đã thêm mới) ---
    email = fields.Char(string="Email")
    so_dien_thoai = fields.Char(string="Số điện thoại")
    luong = fields.Float(string="Mức lương")

    # --- 3. CÁC LIÊN KẾT (RELATIONS) ---
    phong_ban_id = fields.Many2one('phong_ban', string="Phòng ban")
    chuc_vu_id = fields.Many2one('chuc_vu', string="Chức vụ")
    
    # --- LIÊN KẾT VỚI VĂN BẢN ---
    van_ban_den_count = fields.Integer(
        string="Số văn bản phụ trách",
        compute="_compute_van_ban_den_count",
        store=False
    )

    # --- 4. FIELD TỰ ĐỘNG ---
    ma_dinh_danh = fields.Char(string="Mã định danh", readonly=True)
    tuoi = fields.Integer(string="Tuổi", compute='_compute_tuoi', store=True)

    # --- 5. LOGIC XỬ LÝ ---
    def _bo_dau_tieng_viet(self, text):
        if not text: return ""
        text = text.lower()
        text = re.sub(r'[àáạảãâầấậẩẫăằắặẳẵ]', 'a', text)
        text = re.sub(r'[èéẹẻẽêềếệểễ]', 'e', text)
        text = re.sub(r'[òóọỏõôồốộổỗơờớợởỡ]', 'o', text)
        text = re.sub(r'[ìíịỉĩ]', 'i', text)
        text = re.sub(r'[ùúụủũưừứựửữ]', 'u', text)
        text = re.sub(r'[ỳýỵỷỹ]', 'y', text)
        text = re.sub(r'[đ]', 'd', text)
        text = re.sub(r'[^a-z0-9 ]', '', text)
        return text.upper()

    @api.onchange('ho_ten', 'ngay_sinh')
    def _onchange_sinh_ma_dinh_danh(self):
        for r in self:
            if r.ho_ten and r.ngay_sinh:
                ten_khong_dau = self._bo_dau_tieng_viet(r.ho_ten)
                cac_tu = ten_khong_dau.split()
                chu_cai_dau = "".join([tu[0] for tu in cac_tu if tu])
                ngay_sinh_str = r.ngay_sinh.strftime('%d%m%Y')
                r.ma_dinh_danh = f"{chu_cai_dau}{ngay_sinh_str}"

    @api.depends('ngay_sinh')
    def _compute_tuoi(self):
        today = date.today()
        for r in self:
            if r.ngay_sinh:
                r.tuoi = today.year - r.ngay_sinh.year - (
                    (today.month, today.day) < (r.ngay_sinh.month, r.ngay_sinh.day)
                )
            else:
                r.tuoi = 0

    @api.onchange('luong')
    def _onchange_luong(self):
        """Xử lý định dạng lương khi nhập có dấu phẩy"""
        for r in self:
            if r.luong:
                # Nếu là string, loại bỏ dấu phẩy và khoảng trắng
                if isinstance(r.luong, str):
                    luong_str = str(r.luong).replace(',', '').replace(' ', '').strip()
                    try:
                        r.luong = float(luong_str)
                    except (ValueError, TypeError):
                        r.luong = 0.0
    
    @api.model_create_multi
    def create(self, vals_list):
        """Override create để xử lý lương có dấu phẩy"""
        for vals in vals_list:
            if 'luong' in vals and vals['luong']:
                if isinstance(vals['luong'], str):
                    vals['luong'] = float(str(vals['luong']).replace(',', '').replace(' ', '').strip() or 0)
        return super(NhanVien, self).create(vals_list)
    
    def write(self, vals):
        """Override write để xử lý lương có dấu phẩy"""
        if 'luong' in vals and vals['luong']:
            if isinstance(vals['luong'], str):
                vals['luong'] = float(str(vals['luong']).replace(',', '').replace(' ', '').strip() or 0)
        return super(NhanVien, self).write(vals)
    
    @api.depends()
    def _compute_van_ban_den_count(self):
        for rec in self:
            rec.van_ban_den_count = 0
            try:
                # Kiểm tra model có tồn tại trong registry không
                if self._check_model_exists('van_ban_den'):
                    van_ban_den_model = self.env["van_ban_den"]
                    rec.van_ban_den_count = van_ban_den_model.search_count([
                        ("nhan_vien_xu_ly_id", "=", rec.id)
                    ])
            except (KeyError, AttributeError):
                # Model chưa được load hoặc không tồn tại
                pass
            except Exception:
                pass
    
    def _check_model_exists(self, model_name):
        """Safely check if a model exists in the registry"""
        try:
            self.env[model_name]
            return True
        except KeyError:
            return False
    
    def action_open_van_ban_den(self):
        self.ensure_one()
        try:
            # Thử truy cập model để kiểm tra có tồn tại không
            if self._check_model_exists('van_ban_den'):
                return {
                    "type": "ir.actions.act_window",
                    "name": "Văn bản đến",
                    "res_model": "van_ban_den",
                    "view_mode": "tree,form",
                    "domain": [("nhan_vien_xu_ly_id", "=", self.id)],
                }
            return False
        except Exception:
            return False