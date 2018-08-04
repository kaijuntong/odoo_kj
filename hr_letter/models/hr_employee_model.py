from odoo import api, fields, models


class Employees(models.Model):
    _inherit = ['hr.employee']

    letter_ids = fields.One2many(
        'hr.letter',
        'employee_id',
        'Letter'
    )
