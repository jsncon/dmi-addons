# -*- coding: utf-8 -*-
import pytz
from datetime import datetime

from openerp import api, fields, models, _
from openerp.exceptions import ValidationError
#from openerp.addons import sale_stock as ss


class SaleOrder(models.Model):
    """
    """
	
    _inherit = "sale.order"
	# Not Remove For Future Reference
    #chamber_id = fields.Many2one(comodel_name='stock.warehouse', string='Chamber', compute='_compute_chamber_id', store=True, readonly=True)
	
    appointment_datetime = fields.Datetime(string="Appointment Datetime", compute='_compute_appointment_datetime', store=True)
    appointment_date = fields.Date(string="Appointment Date")
    appointment_time = fields.Selection([
            (8,'8 AM'),
            (10,'10 AM'),
            (12,'12 NN'),
            (14,'2 PM'),
            (16,'4 PM'),
        ], string='Appointment Time')
	
	# Not Remove For Future Reference
    #@api.multi	
    #@api.depends('chamber_id')
    #def _compute_chamber_id(self):
    #    """
    #    """
    #    for rec in self:
    #        rec.chamber_id = self.env['sale.order'].browse(rec.id).warehouse_id
		
		
    @api.depends('appointment_date','appointment_time','appointment_datetime')
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
		# Get user time zone if none use default: UTC
        #if not (self.appointment_date and self.appointment_time):
        #    return True
			
        #if self.env.user.partner_id.tz:
        #    order_time_zone = pytz.timezone(self.env.user.partner_id.tz)
        #else:
        #    order_time_zone = pytz.UTC
		    
	    # create time string
        #string_datetime = "%s %s:0:0" % (self.appointment_date,self.appointment_time)
        #format = '%Y-%m-%d %H:%M:%S'
		
		# create time object
        #order_time = datetime.strptime(string_datetime, format)
		
		# define the time of the time object
        #order_time = order_time_zone.localize(order_time)
        #order_time.replace(tzinfo=order_time_zone)
		
        #self.appointment_datetime = order_time.astimezone(pytz.UTC).strftime(format)
		
        self.note = str(self.warehouse_id)
		
        return True
