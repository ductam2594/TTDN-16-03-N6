# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class AiConfigWizard(models.TransientModel):
    _name = 'ai.config.wizard'
    _description = 'Cấu hình AI - Gemini API Key'

    gemini_api_key = fields.Char(
        string="Gemini API Key",
        required=True,
        help="Nhập API Key từ Google AI Studio (https://makersuite.google.com/app/apikey)"
    )
    
    @api.model
    def default_get(self, fields_list):
        """Load current API key if exists"""
        res = super(AiConfigWizard, self).default_get(fields_list)
        current_key = self.env['ir.config_parameter'].sudo().get_param(
            'quan_ly_tai_san.gemini_api_key', 
            'PASTE_YOUR_API_KEY_HERE'
        )
        res['gemini_api_key'] = current_key
        return res
    
    def action_save_config(self):
        """Save API key to system parameters"""
        self.ensure_one()
        
        if not self.gemini_api_key or self.gemini_api_key.strip() == '':
            raise ValidationError("Vui lòng nhập Gemini API Key!")
        
        # Save to system parameter
        self.env['ir.config_parameter'].sudo().set_param(
            'quan_ly_tai_san.gemini_api_key',
            self.gemini_api_key.strip()
        )
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Thành công',
                'message': 'Đã lưu API Key thành công!',
                'type': 'success',
                'sticky': False,
            }
        }


