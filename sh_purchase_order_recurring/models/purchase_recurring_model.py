# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from odoo import api, fields, models, _
from odoo.exceptions import UserError, AccessError,ValidationError
from odoo.addons import decimal_precision as dp
from datetime import timedelta
from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT


class purchase_recurring(models.Model):
    _name = "purchase.recurring"
    _description = "purchase Order Recurring"
    _order = 'id desc'    
    
    name = fields.Char(string='purchase Recurring Reference', required=True, copy=False, readonly=True, index=True, default=lambda self: _('New'))  
    partner_id = fields.Many2one('res.partner', string='Vendor', required=True)
    start_date = fields.Date(string='Start date', index=True, copy=False, required = True,default=fields.Date.context_today,store = True)   
    active = fields.Boolean(string = 'Active', default=True)
    title = fields.Char(string = "Title")
    note = fields.Text(string = "Note")
    order_line = fields.One2many('purchase.recurring.line', 'purchase_recurring_id', string='Order Lines', copy=True, auto_join=True)    
    last_generated_date = fields.Date(string='Last date', index=True, copy=False)
    end_date = fields.Date(string='End date',copy=False)
 
    
    order_type = fields.Selection([
        ('rfq','Requests for Quotation'),
        ('po','Purchase Order'),
        ], string = "Order Type", default = "rfq")

    state = fields.Selection([
        ('draft', 'New'),
        ('confirm', 'Running'),
        ('pending', 'To Renew'),        
        ('done', 'Expired'),
        ('cancel', 'Cancelled'),                
    ], string='Status', required=True, copy=False, default='draft')
    
            
    #main recurring part
    recurring_interval = fields.Integer(string="Interval",default = 1,required=True)
    recurring_interval_unit =  fields.Selection([
        ('days','Days'),
        ('weeks','Weeks'),
        ('months','Months'),
        ('years','Years'),
        ],string="Interval Unit",default = "years",required=True)
    
    
    
    stop_recurring_interval = fields.Integer(string="Stop after") 
    stop_recurring_interval_unit =  fields.Selection([
        ('days','Days'),
        ('weeks','Weeks'),
        ('months','Months'),
        ('years','Years'),
        ],
        related = "recurring_interval_unit",
        string="Stop Interval Unit",required = True)    
    
    
    @api.onchange('stop_recurring_interval','recurring_interval_unit','start_date')
    def _onchange_stop_recurring_interval(self):
        if self and self.start_date:
            if self.stop_recurring_interval > 0:
                end_date = False
                st_date = fields.Date.from_string(self.start_date)
                if self.recurring_interval_unit == 'days':
                    end_date = st_date + relativedelta(days = self.stop_recurring_interval - 1)   
                elif self.recurring_interval_unit == 'weeks':
                    end_date = st_date + relativedelta(weeks = self.stop_recurring_interval - 1)    
                elif self.recurring_interval_unit == 'months':
                    end_date = st_date + relativedelta(months = self.stop_recurring_interval - 1)                                      
                elif self.recurring_interval_unit == 'years':
                    end_date =  st_date + relativedelta(years = self.stop_recurring_interval - 1) 
                
                if end_date:
                    self.end_date = end_date       
            else:
                self.end_date = False         
            
                 
    
    #compute no of purchase order in this recuring
    sh_purchase_recurring_count = fields.Integer(string='# of purchases', compute='sh_purchase_recurring_order_compute')
   
    
        
    def sh_purchase_recurring_order_compute(self):
        purchase_order_obj=self.env['purchase.order']
        if self:
            for rec in self:
                po_count = purchase_order_obj.sudo().search_count([
                                            ('sh_purchase_recurring_order_id','=',rec.id),
                                                ])
                rec.sh_purchase_recurring_count = po_count
            
    def action_view_recurring_order(self):
        if self:
            purchase_order_obj=self.env['purchase.order']
            search_recurring_orders = purchase_order_obj.sudo().search([
                            ('sh_purchase_recurring_order_id','=',self.id),
                                ])
            if search_recurring_orders:
                view = self.env.ref('purchase.purchase_order_tree')
                view_id = view and view.id or False                                   
                return {
                    'name'          :   'Recurring Orders',
                    'type'          :   'ir.actions.act_window',
                    'view_mode'     :   'tree,form',
                    'target'        :   'self', 
                    'res_model'     :   'purchase.order',
                    'view_id'       :   False,
                    'domain'        :   [('id','in',search_recurring_orders.ids)]
                    }                      
            
            
    
    
    @api.constrains('start_date', 'end_date')
    def _check_dates(self):
        if self.filtered(lambda c: c.end_date and c.start_date > c.end_date):
            raise ValidationError(_('start date must be less than end date.'))
        
    @api.constrains('stop_recurring_interval')
    def _check_stop_recurring_interval(self):
        if self.filtered(lambda c: c.stop_recurring_interval < 0):
            raise ValidationError(_('Stop after must be positive.'))        
        
    @api.constrains('recurring_interval')
    def _check_recurring_interval(self):
        if self.filtered(lambda c: c.recurring_interval < 0):
            raise ValidationError(_('Interval must be positive.'))   
                             
            
    @api.model
    def create(self, vals):       
        
        recurring_seq = self.env['ir.sequence'].next_by_code('sh.purchase.recurring.sequence')
        vals.update({'name' : recurring_seq})
        
        res =  super(purchase_recurring,self).create(vals)
        return res
    
    @api.model
    def recurring_order_cron(self):
        purchase_order_obj = self.env['purchase.order']  
        search_recur_orders = self.env['purchase.recurring'].search([
            ('state','=','confirm'),
            ('active','=',True),
            ])
        if search_recur_orders:
            for rec in search_recur_orders:
                next_date = False  
                if not rec.last_generated_date:
                    rec.last_generated_date = rec.start_date
                    next_date = fields.Date.from_string(rec.start_date)  
                else:   
                    last_generated_date = fields.Date.from_string(rec.last_generated_date)                
                    if rec.recurring_interval_unit == 'days':
                        next_date = last_generated_date + relativedelta(days = rec.recurring_interval)   
                    elif rec.recurring_interval_unit == 'weeks':
                        next_date = last_generated_date + relativedelta(weeks = rec.recurring_interval)    
                    elif rec.recurring_interval_unit == 'months':
                        next_date = last_generated_date + relativedelta(months = rec.recurring_interval)                                      
                    elif rec.recurring_interval_unit == 'years':
                        next_date = last_generated_date + relativedelta(years = rec.recurring_interval)      
    

                date_now = fields.Date.context_today(rec)
                date_now = fields.Date.from_string(date_now)          

                end_date = False               
                
                #for life time contract create
                if not rec.end_date:
                    end_date = next_date
                
                #for fixed time contract create
                if rec.end_date:
                    end_date = fields.Date.from_string(rec.end_date)   

                # we still need to make new quotation    
                if next_date <= date_now and next_date <= end_date:
                    purchase_order_vals = {}
                    purchase_order_vals.update({
                        'partner_id'                : rec.partner_id.id,
                        'date_order'                : next_date,
                        'sh_purchase_recurring_order_id': rec.id,
                        'origin'                    : rec.name,
                        })
                    order_line_list = []
                    if rec.order_line:
                        for line in rec.order_line:
                            if line.product_id and line.product_id.uom_po_id: 
                                order_line_vals = {
                                    'product_id'      : line.product_id.id,
                                    'price_unit'      : line.price_unit,
                                    'product_qty'     : line.product_qty,
                                    'product_uom'     : line.product_id.uom_id.id,
                                    'name'            : line.name,
                                    'date_planned'    : next_date,
                                }
                                order_line_list.append((0,0,order_line_vals))
                    if order_line_list:
                        purchase_order_vals.update({
                            'order_line' : order_line_list,
                            })
                    created_so = purchase_order_obj.create(purchase_order_vals)
                    if created_so:
                        rec.last_generated_date = next_date
                        
                        # Create RFQ or PO
                        if rec.order_type == 'po':
                            created_so.button_confirm()                        
                                
                # make state into done state and no require any more new quotation.
#                 last_gen_date = fields.Date.from_string(rec.last_generated_date)                 
                if rec.end_date and end_date <=  next_date:
                    rec.state = 'done'
                    
                                   
                
    def create_order_manually(self):
        self.ensure_one()
        purchase_order_obj = self.env['purchase.order']   
        if self:
            next_date = False  
            if not self.last_generated_date:
                self.last_generated_date = self.start_date
                next_date = fields.Date.from_string(self.start_date)  
            else:   
                last_generated_date = fields.Date.from_string(self.last_generated_date)                
                if self.recurring_interval_unit == 'days':
                    next_date = last_generated_date + relativedelta(days = self.recurring_interval)   
                elif self.recurring_interval_unit == 'weeks':
                    next_date = last_generated_date + relativedelta(weeks = self.recurring_interval)    
                elif self.recurring_interval_unit == 'months':
                    next_date = last_generated_date + relativedelta(months = self.recurring_interval)                                      
                elif self.recurring_interval_unit == 'years':
                    next_date = last_generated_date + relativedelta(years = self.recurring_interval)      
            
            end_date = False               
            
            #for life time contract create
            if not self.end_date:
                end_date = next_date
            
            #for fixed time contract create
            if self.end_date:
                end_date = fields.Date.from_string(self.end_date)                   
            
            # we still need to make new quotation    
            if next_date <= end_date:
                purchase_order_vals = {}
                purchase_order_vals.update({
                    'partner_id'                : self.partner_id.id,
                    'date_order'                : next_date,
                    'sh_purchase_recurring_order_id': self.id,
                    'origin'                    : self.name,
                    })
                order_line_list = []
                if self.order_line:
                    for line in self.order_line:
                        if line.product_id and line.product_id.uom_id: 
                            order_line_vals = {
                                'product_id'      : line.product_id.id,
                                'price_unit'      : line.price_unit,
                                'product_qty'     : line.product_qty,
                                'product_uom'     : line.product_id.uom_id.id,
                                'name'            : line.name,
                                'date_planned'    : next_date,
                            }
                            order_line_list.append((0,0,order_line_vals))
                if order_line_list:
                    purchase_order_vals.update({
                        'order_line' : order_line_list,
                        })
                created_so = purchase_order_obj.create(purchase_order_vals)
                if created_so:
                    self.last_generated_date = next_date
                    
                    # Create RFQ or PO
                    if self.order_type == 'po':
                        created_so.button_confirm()
                        
                        
                        

            # make state into done state and no require any more new quotation.
#             last_gen_date = fields.Date.from_string(self.last_generated_date)                 
            if self.end_date and end_date <=  next_date:
                self.state = 'done'
            
    
class purchase_recurring_line(models.Model):
    _name = "purchase.recurring.line"
    _description = "purchase Order Recurring Line"
    
    purchase_recurring_id = fields.Many2one('purchase.recurring', string='Order Reference', required=True, ondelete='cascade', index=True, copy=False)
    product_id = fields.Many2one('product.product', string='Product', domain=[('purchase_ok', '=', True)], change_default=True, required=True) 
    name = fields.Text(string='Description', required=True)
    price_unit = fields.Float(string='Unit Price', required=True, digits=dp.get_precision('Product Price'))   
    product_qty = fields.Float(string='Quantity', digits=dp.get_precision('Product Unit of Measure'), required=True)  

            
    
    
    @api.onchange('product_id')
    def product_id_change(self):
        if self:
            for rec in self:
                if rec.product_id:

                    product_lang = rec.product_id.with_context(
                        lang = rec.purchase_recurring_id.partner_id.lang,
                        partner_id = rec.purchase_recurring_id.partner_id.id,
                    )
                    rec.name = product_lang.display_name
                    if product_lang.description_purchase:
                        rec.name += '\n' + product_lang.description_purchase

                    rec.price_unit = rec.product_id.standard_price
             
                    
                    
                    
