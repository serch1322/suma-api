# -*- coding: utf-8 -*-
# Developed by Bizople Solutions Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.
{
    'name': 'Outgoing SMTP Mail Server Per User',
    'summary': """ It sends an e-mail from particular user's outgoing SMTP mail server.
                Use your own smtp server for sending mail from Odoo.
                    """,
    'description': """Set an outgoing SMTP mail server for particular user.
                        smtp server, mail server, user email, user mail, 
                        user outgoing mail, outgoing mail server,
                        mail server configuration, email configuration,
                        smtp mail,how to configure mail server,smtp outgoing mail, 
                        company email, user wise email, mail setup,
                        different mail server for user,different smtp mail server for user""",
    'category': 'Mail',
    'version': '14.0.1.0',
    'author': 'Bizople Solutions Pvt. Ltd.',
    'website': 'https://www.bizople.com/',
    'sequence':1,
    'depends': [
        'base',
        'mail'
    ],
    'data': [
        'views/ir_mail_server_view.xml',
        'views/res_users_view.xml',
    ],

    'images': [
       'static/description/banner.png',
       'static/description/icon.png'
    ],
    'license': 'OPL-1',
    'price': 15,
    'installable': True,
    'application': True,
    'auto_install': False,
    'currency': 'EUR'
}
