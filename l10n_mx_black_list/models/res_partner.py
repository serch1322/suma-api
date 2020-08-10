from odoo import api, fields, models, fields, _
from odoo.exceptions import ValidationError


class res_partner(models.Model):
    _inherit = "res.partner"

    @api.model
    def create(self, vals):
        if self.env['l10n.mx.black_list'].search([('name', '=', vals['vat'])], limit=1):
            raise ValidationError(_('RFC in the black list'))
        else:
            record = super(res_partner, self).create(vals)
            return record
