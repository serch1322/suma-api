from odoo import models, fields, api
import datetime

class RemisionOrdenVenta(models.Model):
    _inherit = ['sale.order']

    state = fields.Selection(selection_add=[('remision', 'Remision'),('remision_pagada','Remision Pagada')])


    def status_remision(self):
        self.state = 'remision'

    def status_remision_pagada(self):
        self.state = 'remision_pagada'