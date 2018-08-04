from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)


class Letter(models.Model):
    _name = 'hr.letter'

    employee_id = fields.Many2one('hr.employee', string="Employee name", index=True)
    particular = fields.Text(string='Particular')
    received_date = fields.Date(string='Received Date')
    time = fields.Datetime(string="Time")
    ref_no = fields.Char(string="Ref No",readonly=True)
    company = fields.Char(string="Company")
    issue_date = fields.Date(string='Issue Date')
    # type_of_letter = fields.Selection(
    #     list(zip(
    #         ('authorization', 'certificate_of_employment', 'confirmation_letter', 'reference_letter',
    #          'resignation_letter', 'termination_letter', 'warning_letter'),
    #         ('Authorization', 'Certificate of employment', 'Confirmation Letter', 'Reference Letter',
    #          'Resignation Letter', 'Termination Letter', 'Warning Letter')
    #     ))
    # )

    type_of_letter = fields.Many2one('hr.letter.type', string="Type of letter", index=True, store='True')

    department_id = fields.Many2one(
        string='Department',
        related='employee_id.department_id',
        store='True'
    )

    start_date = fields.Date(string='Start Date')
    end_date = fields.Date(string='End Date')
    reason = fields.Text(string='Reason')

    def name_get(self):
        result = []
        for record in self:
            result.append(
                [record.id, '{} - {}'.format(record.employee_id.name, record.type_of_letter.name)]
            )
        return result

    @api.multi
    def letter_send_action(self):
        self.ensure_one()
        template = self.env.ref('hr_letter.email_template_hr_letter', False)
        compose_form = self.env.ref('mail.email_compose_message_wizard_form', False)
        ctx = dict(
            default_model='hr.letter',
            default_res_id=self.id,
            default_use_template=bool(template),
            default_template_id=template and template.id or False,
            default_composition_mode='comment',
            mark_invoice_as_sent=True,
            force_email=True
        )

        return {
            'name': 'Compose Email',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form.id, 'form')],
            'view_id': compose_form.id,
            'target': 'new',
            'context': ctx,
        }

    @api.model
    def create(self,vals):
        vals['ref_no'] = self.env['ir.sequence'].next_by_code('hr.letter.sequence')
        return super(Letter,self).create(vals)



class TypeLetter(models.Model):
    _name = 'hr.letter.type'

    _description = 'Letter Type'
    _order = 'sequence, id'

    name = fields.Char(string='Letter Type', required=True)
    sequence = fields.Integer(help="Gives the sequence when displaying a list of Letter Type.", default=10)

    # letter_ids = fields.One2many('hr.letter', 'type_of_letter', 'Letters')
