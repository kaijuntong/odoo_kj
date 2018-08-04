from odoo import models, fields, api


class ExtendOhAppraisal(models.Model):
    _inherit = 'hr.appraisal'
    department_id = fields.Many2one(related='emp_id.department_id')
