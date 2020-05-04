 -*- coding: utf-8 -*-
 from odoo import http


 class SumaBoton(http.Controller):
     @http.route('/suma_boton/suma_boton/', auth='public')
     def index(self, **kw):
         return "Hello, world"

     @http.route('/suma_boton/suma_boton/objects/', auth='public')
     def list(self, **kw):
         return http.request.render('suma_boton.listing', {
             'root': '/suma_boton/suma_boton',
             'objects': http.request.env['suma_boton.suma_boton'].search([]),
         })

     @http.route('/suma_boton/suma_boton/objects/<model("suma_boton.suma_boton"):obj>/', auth='public')
     def object(self, obj, **kw):
         return http.request.render('suma_boton.object', {
             'object': obj
         })
