# -*- coding: utf-8 -*-
import pytz
from datetime import datetime

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
        ], string='Appointment Time')

    #@api.depends('appointment_date','appointment_time')
    def _compute_appointment_datetime(self):
        """
        """
		
        for rec in self:
		    # Get user time zone if none use default: UTC
            if not (rec.appointment_date and rec.appointment_time):
                continue
			
            if self.env.user.partner_id.tz:
                order_time_zone = pytz.timezone(self.env.user.partner_id.tz)
            else:
                order_time_zone = pytz.UTC
		    
		    # create time string
            string_datetime = "%s %s:0:0" % (rec.appointment_date,rec.appointment_time)
            format = '%Y-%m-%d %H:%M:%S'
		
		    # create time object
            order_time = datetime.strptime(string_datetime, format)
		
		    # define the time of the time object
            order_time = order_time_zone.localize(order_time)
            order_time.replace(tzinfo=order_time_zone)
		
            rec.appointment_datetime = order_time.astimezone(pytz.UTC).strftime(format)

    @api.multi
    def action_test(self):
        """
        """
        self.ensure_one()
        #self.appointment_datetime = "%s %s:0:0" % (self.appointment_date,self.appointment_time) 
		    # Get user time zone if none use default: UTC
        if not (self.appointment_date and self.appointment_time):
            return True
			
        if self.env.user.partner_id.tz:
            order_time_zone = pytz.timezone(self.env.user.partner_id.tz)
        else:
            order_time_zone = pytz.UTC
		    
	    # create time string
        string_datetime = "%s %s:0:0" % (self.appointment_date,self.appointment_time)
        format = '%Y-%m-%d %H:%M:%S'
		
		# create time object
        order_time = datetime.strptime(string_datetime, format)
		
		# define the time of the time object
        order_time = order_time_zone.localize(order_time)
        order_time.replace(tzinfo=order_time_zone)
		
        self.appointment_datetime = order_time.astimezone(pytz.UTC).strftime(format)
        #self.note = str(self.appointment_datetime)
        #self.note = str(self.env.user.partner_id.tz)
        return True
		