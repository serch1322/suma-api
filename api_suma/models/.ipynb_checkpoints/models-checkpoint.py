# -*- coding: utf-8 -*-

from odoo import api, fields, models, SUPERUSER_ID, _


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    @api.onchange('partner_id')
    def link_po(self):
        abcd = self.ids[0]
        url = "https://sumaenlinea.mx/cgi-bin/Odoo.EXE/COMPRAS?ACCION=IMPORTAR&ID=" + str(abcd)
        if url:
            return{
            "type": "ir.actions.act_url",
            "url": "%s" % url,
            "target": "new"
            }