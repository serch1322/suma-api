# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from odoo import api, fields, models, _
from odoo.exceptions import UserError, AccessError,ValidationError
# from odoo.addons import decimal_precision as dp
from datetime import timedelta
from datetime import datetime
from dateutil.relativedelta import relativedelta
# from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.osv import expression

class sale_recurring(models.Model):
    _name = "sale.recurring"
    _description = "Sale Order Recurring"
    _order = 'id desc'    
    
    name = fields.Char(string='Sale Recurring Reference', required=True, copy=False, readonly=True, index=True, default=lambda self: _('New'))  
    partner_id = fields.Many2one('res.partner', string='Customer', required=True)
    start_date = fields.Date(string='Start date', index=True, copy=False, required = True,default=fields.Date.context_today,store = True)   
    active = fields.Boolean(string = 'Active', default=True)
    title = fields.Char(string = "Title")
    note = fields.Text(string = "Note")
    order_line = fields.One2many('sale.recurring.line', 'sale_recurring_id', string='Order Lines', copy=True, auto_join=True)    
    last_generated_date = fields.Date(string='Last date', index=True, copy=False)
    end_date = fields.Date(string='End date',copy=False)
    

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
    
    
    
    def active_sr(self):
        if self:
            for rec in self:
                if not rec.active:
                    rec.active = True

    def archive_sr(self):
        if self:
            for rec in self:
                if rec.active:
                    rec.active = False                     
    
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
            
                 
    
    #compute no of sale order in this recuring
    sh_sale_recurring_count = fields.Integer(string='# of Sales', compute='sh_sale_recurring_order_compute')
   
    
        

    def sh_sale_recurring_order_compute(self):
        sale_order_obj=self.env['sale.order']
        if self:
            for rec in self:
                so_count = sale_order_obj.sudo().search_count([
                                            ('sh_sale_recurring_order_id','=',rec.id),
                                                ])
                rec.sh_sale_recurring_count = so_count
            

    def action_view_recurring_order(self):
        if self:
            sale_order_obj=self.env['sale.order']
            search_recurring_orders = sale_order_obj.sudo().search([
                            ('sh_sale_recurring_order_id','=',self.id),
                                ])
            if search_recurring_orders:
                view = self.env.ref('sale.view_quotation_tree')
                view_id = view and view.id or False                                   
                return {
                    'name'          :   'Recurring Orders',
                    'type'          :   'ir.actions.act_window',
                    'view_type'     :   'form',
                    'view_mode'     :   'tree,form',
                    'target'        :   'self', 
                    'res_model'     :   'sale.order',
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
        
        recurring_seq = self.env['ir.sequence'].next_by_code('sh.sale.recurring.sequence')
        vals.update({'name' : recurring_seq})
        
        res =  super(sale_recurring,self).create(vals)
        return res
    
    @api.model
    def recurring_order_cron(self):
        sale_order_obj = self.env['sale.order']  
        search_recur_orders = self.env['sale.recurring'].search([
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
                    sale_order_vals = {}
                    sale_order_vals.update({
                        'partner_id'                : rec.partner_id.id,
                        'date_order'                : next_date,
                        'sh_sale_recurring_order_id': rec.id,
                        'origin'                    : rec.name,
                        'payment_term_id'           : rec.partner_id.property_payment_term_id,
                        })
                    order_line_list = []
                    if rec.order_line:
                        for line in rec.order_line:
                            if line.product_id and line.product_id.uom_id: 
                                order_line_vals = {
                                    'product_id'      : line.product_id.id,
                                    'price_unit'      : line.price_unit,
                                    'product_uom_qty' : line.product_uom_qty,
                                    'discount'        : line.discount,
                                    'product_uom'     : line.product_id.uom_id.id,
                                    'name'            : line.name
                                }
                                order_line_list.append((0,0,order_line_vals))
                    if order_line_list:
                        sale_order_vals.update({
                            'order_line' : order_line_list,
                            })
                    created_so = sale_order_obj.create(sale_order_vals)
                    if created_so:
                        rec.last_generated_date = next_date
                                
                # make state into done state and no require any more new quotation.
#                 last_gen_date = fields.Date.from_string(rec.last_generated_date)                 
                if rec.end_date and end_date <=  next_date:
                    rec.state = 'done'
                    
                                   
                
    def create_order_manually(self):
        self.ensure_one()
        sale_order_obj = self.env['sale.order']   
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
                sale_order_vals = {}
                sale_order_vals.update({
                    'partner_id'                : self.partner_id.id,
                    'date_order'                : next_date,
                    'sh_sale_recurring_order_id': self.id,
                    'origin'                    : self.name,
                    'payment_term_id'           : rec.partner_id.property_payment_term_id,
                    })
                order_line_list = []
                if self.order_line:
                    for line in self.order_line:
                        if line.product_id and line.product_id.uom_id: 
                            order_line_vals = {
                                'product_id'      : line.product_id.id,
                                'price_unit'      : line.price_unit,
                                'product_uom_qty' : line.product_uom_qty,
                                'discount'        : line.discount,
                                'product_uom'     : line.product_id.uom_id.id,
                                'name'            : line.name
                            }
                            order_line_list.append((0,0,order_line_vals))
                if order_line_list:
                    sale_order_vals.update({
                        'order_line' : order_line_list,
                        })
                created_so = sale_order_obj.create(sale_order_vals)
                if created_so:
                    self.last_generated_date = next_date

            # make state into done state and no require any more new quotation.
#             last_gen_date = fields.Date.from_string(self.last_generated_date)                 
            if self.end_date and end_date <=  next_date:
                self.state = 'done'
            
    
class sale_recurring_line(models.Model):
    _name = "sale.recurring.line"
    _description = "Sale Order Recurring Line"
    
    sale_recurring_id = fields.Many2one('sale.recurring', string='Order Reference', required=True, ondelete='cascade', index=True, copy=False)
    product_id = fields.Many2one('product.product', string='Product', domain=[('sale_ok', '=', True)], change_default=True, ondelete='restrict', required=True)    
    name = fields.Text(string='Description', required=True)
    price_unit = fields.Float('Unit Price', required=True, digits='Product Price', default=0.0)        
    discount = fields.Float(string='Discount (%)', digits="Discount", default=0.0)   
    product_uom_qty = fields.Float(string='Quantity', digits='Product Unit of Measure', required=True, default=1.0)     
        
    
    @api.onchange('product_id')
    def product_id_change(self):
        if self:
            for rec in self:
                if rec.product_id:
                    name = rec.product_id.name_get()[0][1]
                    if rec.product_id.description_sale:
                        name += '\n' + rec.product_id.description_sale
                    rec.name = name
                    rec.price_unit = rec.product_id.lst_price
