from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)


class Survey(models.Model):
    _inherit = 'survey.user_input'

    department_id = fields.Many2one(related='appraisal_id.department_id', store=True)
    reviewer_id = fields.Many2one('hr.employee')

    @api.depends('token')
    def _compute_url(self):
        # Get the survey url
        url = '{}/{}'.format(self.survey_id.public_url, self.token)
        self.survey_url = url

    survey_url = fields.Char(compute='_compute_url')


class SurveySurvey(models.Model):
    _inherit = 'survey.survey'
    is_appraisal = fields.Boolean(string='Is Appraisal?', default=False)


class HrAppraisalForm(models.Model):
    _inherit = 'hr.appraisal'

    @api.multi
    def action_start_appraisal(self):
        """ This function will start the appraisal by sending emails to the corresponding employees
            specified in the appraisal"""
        send_count = 0
        appraisal_reviewers_list = self.fetch_appraisal_reviewer()
        for appraisal_reviewers, survey_id in appraisal_reviewers_list:
            for reviewers in appraisal_reviewers:
                url = survey_id.public_url
                response = self.env['survey.user_input'].create(
                    {'survey_id': survey_id.id, 'partner_id': reviewers.user_id.partner_id.id,
                     'appraisal_id': self.ids[0], 'deadline': self.appraisal_deadline, 'reviewer_id': reviewers.id,
                     'email': reviewers.user_id.email})
                token = response.token
                if token:
                    url = url + '/' + token
                    mail_content = "Dear " + reviewers.name + "," + "<br>Please fill out the following survey " \
                                                                    "related to " + self.emp_id.name + "<br>Click here to access the survey.<br>" + \
                                   str(url) + "<br>Post your response for the appraisal till : " + str(
                        self.appraisal_deadline)
                    values = {'model': 'hr.appraisal',
                              'res_id': self.ids[0],
                              'subject': survey_id.title,
                              'body_html': mail_content,
                              'parent_id': None,
                              'email_from': self.env.user.email or None,
                              'auto_delete': True,
                              }
                    values['email_to'] = reviewers.work_email
                    result = self.env['mail.mail'].create(values)._send()
                    if result is True:
                        send_count += 1
                        self.write({'tot_sent_survey': send_count})
                        rec = self.env['hr.appraisal.stages'].search([('sequence', '=', 2)])
                        self.state = rec.id
                        self.check_sent = True
                        self.check_draft = False
        if self.hr_emp and self.emp_survey_id:
            self.ensure_one()
            if not self.response_id:
                response = self.env['survey.user_input'].create(
                    {'survey_id': self.emp_survey_id.id, 'partner_id': self.emp_id.user_id.partner_id.id,
                     'appraisal_id': self.ids[0], 'deadline': self.appraisal_deadline,
                     'email': reviewers.user_id.email})
                self.response_id = response.id
            else:
                response = self.response_id
            return self.emp_survey_id.with_context(survey_token=response.token).action_start_survey()
