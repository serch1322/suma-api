# -*- coding: utf-8 -*-
{
    'name': "api_suma",

    'summary': "Conectar sumaenlinea con Odoo v13" """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': "Conectar sumaenlinea con Odoo v13" """
        Long description of module's purpose
    """,

    'author': "IT Reingenierias",
    'website': "http://www.itreingenierias.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Purchase',
    'version': '1.0',

    # any module necessary for this one to work correctly
    'depends': ['purchase'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
    ],
    # only loaded in demonstration mode,
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
