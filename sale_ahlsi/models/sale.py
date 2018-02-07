# -*- coding: utf-8 -*-
from openerp import api, fields, models, _
from openerp.exceptions import ValidationError


class SaleOrder(models.Model):
    """
    """
	
    _inherit = "sale.order"
	
    appointment_datetime = fields.Datetime(string="Appointment Datetime")
    appointment_date = fields.Date(string="Appointment Date")
    appointment_time = fields.Selection([
            (8,'8 AM'),
            (10,'10 AM'),
            (12,'12 NN'),
            (14,'2 PM'),
            (16,'4 PM'),
        ], string='Time')
		

    @api.multi
    def action_test(self):
        """
        """
        self.ensure_one()
        self.note = "test"
        return True