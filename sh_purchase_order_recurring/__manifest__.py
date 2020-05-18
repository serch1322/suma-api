# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.
{
    "name" : "Purchase Order Recurring",
    "author" : "Softhealer Technologies",
    "website": "https://www.softhealer.com",
    "support": "support@softhealer.com",    
    "category": "purchases",
    "summary": """
 Make Recurring Orders For Purchases, Auto Repeat Order For Purchase, Generate Monthly Regular Order Module, Manually Recurring Order, Purchase Order Recurring Module, Request For Quotation Recurring, RFQ Recurring App, PO Recurring Odoo

	""",
	"description": """
	You can make a recurring order for your regular vendors using this module. For example, set up an order to have particular goods in every three months. you can make recurring orders using this module would let this purchase happen automatically on a regular schedule. You can also make recurring orders manually from recurring orders or using cron. You can set the scheduled time.
 Purchase Order Recurring Odoo
 Make Recurring Orders For Purchases, Make Auto Repeat Orders For Purchase Module, Auto Generate Monthly Regular Order, Automatic Give Weekly Regular Order, Make Manually Recurring Order, Purchase Order Recurring, Request For Quotation Recurring, RFQ Recurring, PO Recurring Odoo
 Make Recurring Orders For Purchases, Auto Repeat Order For Purchase, Generate Monthly Regular Order Module, Weekly Regular Purchase Order, Manually Recurring Order, Purchase Order Recurring Module, Request For Quotation Recurring, RFQ Recurring App, PO Recurring Odoo

	""",
 
    "version":"13.0.1",
    "depends" : ["base","purchase"],
    "application" : True,
    "data" : [
                "security/ir.model.access.csv",
                "data/ir_sequence_data.xml",
                "data/cron_data.xml",
                "views/purchase_recurring_view.xml",
                "views/purchase_view.xml",              
            ],            
    "images": ["static/description/background.png",],              
    "auto_install":False,
    "installable" : True,
    "price": 40,
    "currency": "EUR"   
}
