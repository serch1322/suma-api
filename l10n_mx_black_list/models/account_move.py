# -*- coding: utf-8 -*-
from odoo import api, fields, models, fields, _
from odoo.exceptions import ValidationError

class account_move(models.Model):
    _inherit = "account.move"

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        if self.env['l10n.mx.black_list'].search([('name', '=', self.partner_id.vat)], limit=1):
            raise ValidationError(_('RFC in the black list'))
