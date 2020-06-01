# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from odoo import models, fields,api

class purchase_order(models.Model):
    _inherit = "purchase.order"

    sh_purchase_recurring_order_id = fields.Many2one("purchase.recurring",string="Recurring Order")
    
    
    