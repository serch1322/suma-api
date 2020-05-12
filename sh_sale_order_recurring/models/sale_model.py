# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from odoo import models, fields,api

class sale_order(models.Model):
    _inherit = "sale.order"

    sh_sale_recurring_order_id = fields.Many2one("sale.recurring",string="Recurring Order")
    
    
    