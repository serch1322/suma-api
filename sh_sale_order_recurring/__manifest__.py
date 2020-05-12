# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.
{
    "name" : "Sale Order Recurring",
    "author" : "Softhealer Technologies",
    "website": "https://www.softhealer.com",
    "support": "support@softhealer.com",    
    "category": "Sales",
    "summary": """sales recurring orders app, repeat order recurring module, generate monthly recurring, weekly regular order recurring, manually recurring order odoo""",
    "description": """
You can make recurring order for your regular customers using this module. For example, a consumer could set up an order to have particular goods in every three months. you can make recurring order using this module would let this purchase happen automatically on a regular schedule. You can also make recurring order manually from recurring order. You can set the schedule time.
sales recurring orders app, repeat order recurring module, generate monthly recurring, weekly regular order recurring, manually recurring order odoo                   
				   """,       
    "version":"13.0.1",
    "depends" : ["base","sale","sale_management"],
    "application" : True,
    "data" : [
                "security/ir.model.access.csv",
                "data/ir_sequence_data.xml",
                "data/cron_data.xml",
                "views/sale_recurring_view.xml",
                "views/sale_view.xml",              
            ],            
    "images": ["static/description/background.png",],              
    "auto_install":False,
    "installable" : True,
    "price": 30,
    "currency": "EUR"   
}
