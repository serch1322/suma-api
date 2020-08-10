# -*- coding: utf-8 -*-
from odoo import _, api, fields, models, fields
import csv
import requests


class l10n_mx_black_list(models.Model):
    _name = 'l10n.mx.black_list'
    _description = 'l10n MX black list'


    no = fields.Char(
        string="No.",
        required=True,
        index=True,
    )
    name = fields.Char(
        string="RFC",
        required=True,
        index=True,
    )
    contributor_name = fields.Char(
        required=True,
    )
    contributor_situation = fields.Char(
        required=True,
    )

    def get_data(self):
        urls = [
            'http://omawww.sat.gob.mx/cifras_sat/Documents/Presuntos.csv',
            'http://omawww.sat.gob.mx/cifras_sat/Documents/Definitivos.csv'
        ]
        with requests.Session() as session:
            for files in urls:
                download = session.get(files)
                decoded_content = str(download.content, 'cp1252')
                data = csv.reader(decoded_content.splitlines())
                for _ in range(3):
                    next(data, None)
                self.unlink()
                for line in data:
                    self.create({
                        'no': line[0],
                        'name': line[1],
                        'contributor_name': line[2],
                        'contributor_situation': line[3]
                    })
