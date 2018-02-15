# -*- coding: utf-8 -*-
from openerp import api, fields, models, _
from openerp.exceptions import ValidationError

"""
part - A product which is a spare parts of a 'unit'
unit - A product which can be a whole machinery or a power tool
"""

class SparePartsBorrow(models.Model):
    """ 
    """
    _name = 'stock.parts.borrow'
	
    
    name = fields.Char(string='Order Reference', required=True, copy=False, readonly=True, states={'draft': [('readonly', False)]}, index=True, default=lambda self: _('New'))
    unrevisioned_name = fields.Char(string='Order Reference', copy=True, readonly=True)
    # In this Case (A Kahoy Order) this means (Re-Kahoy)
    revised = fields.Boolean(string="Revised Order")
    revision_number = fields.Integer(string="Revision", copy=False)
	
	# Kahoy Dependent 
    unit_id = fields.Many2one(comodel_name='product.product',string='Unit', required=True)
    unit_uom = fields.Many2one(comodel_name='product.uom', string='Unit of Measure',compute='_compute_unit_uom', readonly=False)
    unit_procurement_group_id = fields.Many2one(comodel_name='procurement.group', string='Parts Procurement Group', readonly=True, ondelete='cascade')
    reverse_unit_procurement_group_id = fields.Many2one(comodel_name='procurement.group', string='Parts Procurement Group', readonly=True, ondelete='cascade')
    serial_id = fields.Many2one(comodel_name='stock.production.lot', string='Serial Number', compute='_compute_serial_id',readonly=True)
	# End
    from_location_id = fields.Many2one(comodel_name='stock.warehouse', string='From Location', required=True, readonly=True)
    to_location_id = fields.Many2one(comodel_name='stock.warehouse', string='To Location', required=True, readonly=True)
    part_procurement_group_id = fields.Many2one(comodel_name='procurement.group', string='Parts Procurement Group', readonly=True, ondelete='cascade')
    reverse_part_procurement_group_id = fields.Many2one(comodel_name='procurement.group', string='Parts Procurement Group', readonly=True, ondelete='cascade')
    request_by = fields.Many2one(comodel_name='res.users', string='Request by', readonly=True)
    confirm_by = fields.Many2one(comodel_name='res.users', string='Confirmed by', readonly=True)
    company_id = fields.Many2one(comodel_name='res.company', string='Company', default=lambda self: self.env.user.company_id.id, readonly=True)
    current_revision_id = fields.Many2one(comodel_name='stock.parts.borrow', string='Current Revision', readonly=True)
	
	# Kahoy Dependent
    unit_picking_ids = fields.One2many(comodel_name='stock.picking',string="Parts Lists",compute='_compute_unit_picking_ids',store=False,readonly=True,ondelete='cascade')
    reverse_unit_picking_ids = fields.One2many(comodel_name='stock.picking',string="Parts Lists",compute='_compute_reverse_unit_picking_ids',store=False,readonly=True,ondelete='cascade')
	# End
    list_ids = fields.One2many(comodel_name='stock.parts.borrow.list',inverse_name='order_id',string="Parts Lists",readonly=True,copy=False,ondelete='cascade')
    picking_ids = fields.One2many(comodel_name='stock.picking',string="Parts Lists",compute='_compute_picking_ids',store=False,readonly=True,ondelete='cascade')
    reverse_picking_ids = fields.One2many(comodel_name='stock.picking',string="Parts Lists",compute='_compute_reverse_picking_ids',store=False,readonly=True,ondelete='cascade')
    old_revision_ids = fields.One2many(comodel_name='stock.parts.borrow',inverse_name='current_revision_id',string="Old Revisions",readonly=True,ondelete='cascade')
	
    old_list_ids = fields.Many2many(comodel_name='stock.parts.borrow.list',string="Old Test Revisions",relation='stock_borrow_order_to_list_rel',readonly=True,copy=True,ondelete='cascade')
	
    created_date = fields.Date(string="Date Requested",default=fields.Date.today,readonly=True)
    confirm_date = fields.Date(string="Date Confirmed",readonly=True)

    state = fields.Selection([
            ('draft','Draft'),
            ('request','Requesting'),
            ('confirm','Confirmed'),
            ('wait_transfer','Waiting for Transfer'),
            ('kahoy','Kahoy'),
            ('assembly','Assembling'),
            ('done','Done'),
            ('wait_return','Waiting for Product Returns'),
            ('cancel','Canceled'),
        ], string='Status',readonly=True, default='draft',
        track_visibility='onchange', copy=False)
		
    note = fields.Text(string='Notes')
	
    @api.multi
    @api.depends('unit_id')
    def _compute_unit_uom(self):
        """ Kahoy Dependent
        """
        for rec in self:
            rec.unit_uom = rec.unit_id.uom_id	

    @api.multi
    @api.depends('serial_id','unit_picking_ids','unit_picking_ids.move_lines.quant_ids','unit_picking_ids.move_lines.quant_ids.lot_id')
    def _compute_serial_id(self):
        """
        """
        for rec in self:
            for pick in (self.unit_picking_ids).sorted(key=lambda pick: pick.id, reverse=True):
                if pick.state in ['done']:
                    for quant in pick.move_lines.quant_ids:
                        if quant.lot_id:
					        self.serial_id = quant.lot_id
					        return True

	
    @api.multi
    @api.depends('picking_ids')
    def _compute_picking_ids(self):
        """
        """
        for order in self:
            if not order.part_procurement_group_id:
                continue
            order.picking_ids = self.env['stock.picking'].search([('group_id', '=', order.part_procurement_group_id.id)])
			
    @api.multi
    @api.depends('reverse_picking_ids')
    def _compute_reverse_picking_ids(self):
        """
        """
        for order in self:
            if not order.reverse_part_procurement_group_id:
                continue
            order.reverse_picking_ids = self.env['stock.picking'].search([('group_id', '=', order.reverse_part_procurement_group_id.id)])

    @api.multi
    @api.depends('unit_picking_ids')
    def _compute_unit_picking_ids(self):
        """ Kahoy Dependent
        """
        for order in self:
            if not order.unit_procurement_group_id:
                continue
            order.unit_picking_ids = self.env['stock.picking'].search([('group_id', '=', order.unit_procurement_group_id.id)])	
			
    @api.multi
    @api.depends('reverse_unit_picking_ids')
    def _compute_reverse_unit_picking_ids(self):
        """ Kahoy Dependent
        """
        for order in self:
            if not order.reverse_unit_procurement_group_id:
                continue
            order.reverse_unit_picking_ids = self.env['stock.picking'].search([('group_id', '=', order.reverse_unit_procurement_group_id.id)])	

    @api.constrains('from_location_id', 'to_location_id')
    def _check_from_location_id(self):
        """
        """
        if self.from_location_id == self.to_location_id:
		    raise ValidationError(_('Both From and To Locations Must Be Different!'))
		
    @api.model
    def create(self,vals):
        """
        """
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('kahoy.order') or _('New')
	    return super(SparePartsBorrow, self).create(vals)
		
    @api.multi
    def action_request(self):
        """
        """
        self.ensure_one()
        if len(self.list_ids) < 1:
		    raise ValidationError(_('Please Add Parts to Be Burrowed!'))
        self.write({'request_by':self.env.uid,'state':'request'})
        return True

    @api.multi
    def action_confirm(self):
        """
        """
        self.ensure_one()
        if len(self.list_ids) < 1:
		    raise ValidationError(_('Please Add Parts to Be Burrowed!'))
        self.write({'confirm_by':self.env.uid,'confirm_date':fields.Date.today(),'state':'wait_transfer'})
        self._action_ship_create()
		
        part_list_recs = self.env['stock.parts.borrow.list'].browse([l.id for l in self.list_ids])
        part_list_recs.write({'state': 'under_process'})
        return True
		

    @api.multi
    def action_view_delivery(self):
	
        self.ensure_one()
    
        #compute the number of delivery orders to display
        pick_ids = []
        pick_ids += [picking.id for picking in self.picking_ids]
        pick_ids += [picking.id for picking in self.unit_picking_ids]
        pick_ids += [picking.id for picking in self.reverse_picking_ids]
        pick_ids += [picking.id for picking in self.reverse_unit_picking_ids]	
		
        if len(pick_ids) > 0:
            context = self._context.copy()
            view = self.env.ref('stock.action_picking_tree_all').read(context = context)
            view[0]['domain'] = "[('id','in',[" + ','.join(map(str, pick_ids)) + "])]"
            return view[0]
        else:
            return True
		
    @api.multi
    def action_assembly(self):
        """ Kahoy Dependent
        """
        self.ensure_one()
        self._action_ship_create(reverse=True)
        self.write({'state':'assembly'})
        return True
		
    @api.multi
    def action_order_cancel(self):
        """
        """
        self.ensure_one()
		
        if len(self.old_list_ids) < 1:
            raise ValidationError(_('Cannot Cancel Without Kahoy Parts'))
        
        self._action_ship_create(reverse=True)
		
        self.write({'state': 'wait_return'})
        return True
		
    @api.multi
    def action_rekahoy(self):
        """
        Revised here means Re-Kahoy
        """
        self.ensure_one()
		
        self.revised = False
        self.copy_quotation()
        self.state = "draft"
        self.revised = True
		
		
        return True
		
    @api.multi
    def action_test(self):
        """ TEST PURPOSES ONLY
        """
        self.ensure_one()
		
        if len(self.old_list_ids) < 1:
            raise ValidationError(_('Cannot Cancel Without Kahoy Parts'))
			
        self.note = str(len(self.old_list_ids))
			
        return True
		
    def _prepare_procurement_group(self,order):
        return {
            'name' : order.name, #if not kahoy str(order.custom_stocktransfer_reference)+ '-1', 
            'partner_id': '',
            'move_type':'direct'
        }		
		
    def _prepare_order_line_procurement(self, order, line, group_id=False, kahoy=False, reverse=False):   
        """ 
        If kahoy: We will prepare the 'unit' that will go to the "Destination Warehouse"
                  and the 'parts' go to the "Source Warehouse"
        """
        route_obj = self.env['stock.location.route']
        if reverse:
            kahoy = not kahoy
        if kahoy:
            routes = route_obj.search([('supplied_wh_id', '=', order.to_location_id.id), ('supplier_wh_id', '=', order.from_location_id.id)])
            warehouse_obj = self.env['stock.warehouse'].browse(order.to_location_id.id)
        else:
            routes = route_obj.search([('supplied_wh_id', '=', order.from_location_id.id), ('supplier_wh_id', '=', order.to_location_id.id)])
            warehouse_obj = self.env['stock.warehouse'].browse(order.from_location_id.id)
		# We only reverse to source and destination of stocks not the Products
        if reverse:
            kahoy = not kahoy
        return {
            'location_id' : warehouse_obj.lot_stock_id.id,
            'route_ids' : [(6, 0, [route.id for route in routes])],
            'warehouse_id' : ((order.from_location_id.id or False) if kahoy else (order.to_location_id.id or False))
                if reverse else ((order.to_location_id.id or False) if kahoy else (order.from_location_id.id or False)),
            'origin' : order.name,
            'name' : _('Kahoy Unit for %s') % order.name if kahoy else _('Kahoy Parts for %s') % order.name, #line.product_description, 
            'date_planned' : order.confirm_date,
            'product_id' : order.unit_id.id if kahoy else line.product_id.id,
            'product_qty' : 1.00 if kahoy else line.qty,
            'product_uom' : order.unit_uom.id if kahoy else line.product_uom.id,
            'product_uos_qty' : 1.00 if kahoy else line.qty,
            'product_uos' : order.unit_uom.id if kahoy else line.product_uom.id,
            'company_id' : order.company_id.id,
            'partner_dest_id' : '',#order.partner_id.id,
            'group_id' : group_id
        }
		
    @api.multi
    def _action_ship_create(self, reverse=False):
        """ 
        Create Stock movements of unit and parts
        For Unit: From "Source Warehouse" To "Destination Warehouse"
        For Parts: From "Destination Location" To "Source Location"
        if revese: It will interchange the 'From' and 'To' Location.
        """
        ProcurementOrder = self.env['procurement.order'] # empty recordset
        for order in self:
            part_vals = self._prepare_procurement_group(order)
            unit_vals = self._prepare_procurement_group(order)
            if not order.unrevisioned_name:
                order.unrevisioned_name = order.name
			
            if reverse:
                if not order.reverse_part_procurement_group_id:
                    order.reverse_part_procurement_group_id = self.env["procurement.group"].create(part_vals)
                    part_group_id = order.reverse_part_procurement_group_id.id
                else:
                    part_group_id = reverse_part_procurement_group_id
                if not order.reverse_unit_procurement_group_id:
                    order.reverse_unit_procurement_group_id = self.env["procurement.group"].create(unit_vals)
                    unit_group_id = order.reverse_unit_procurement_group_id.id
                else:
                    unit_group_id = order.reverse_unit_procurement_group_id.id
            else:
                if not order.part_procurement_group_id:
                    order.part_procurement_group_id = self.env["procurement.group"].create(part_vals)
                    part_group_id = order.part_procurement_group_id.id
                else:
                    part_group_id = order.part_procurement_group_id.id
                if not order.unit_procurement_group_id:
                    order.unit_procurement_group_id = self.env["procurement.group"].create(unit_vals)
                    unit_group_id = order.unit_procurement_group_id.id
                else:
                    unit_group_id = order.unit_procurement_group_id.id
					
			# For parts Procurement
			# if reverse prepare the already kahoy parts
			# else the order lines
            if reverse:
                part_list = order.old_list_ids
            else:
                part_list = order.list_ids
            for line in part_list:
                vals = self._prepare_order_line_procurement(order, line, group_id=part_group_id, reverse=reverse)
                new_proc = self.env["procurement.order"].create(vals)
                ProcurementOrder += new_proc
            # For Unit Procurement
			# do not prepare if revised(Re-kahoy)
			# prepare if reverse
            if not order.revised or reverse:
                unit_vals = self._prepare_order_line_procurement(order, line, group_id=unit_group_id, kahoy=True, reverse=reverse)
                new_proc = self.env["procurement.order"].create(unit_vals)
                ProcurementOrder += new_proc
        ProcurementOrder.run()
		
        return True

    @api.multi		
    def _create_cancel_return_list(self):
        """ 
        This create a stock movement of return of 'done' operations.
        before going to 'assembly' state
        """
        self.ensure_one()
        return_line_obj = self.env['stock.parts.borrow.return.list']
        uom_obj = self.env['product.uom']
        for picking in self.picking_ids:
            if picking.state in ['done']:
                for line in picking.move_lines:
                    line_product_uom_id = line.product_id.uom_id
                    line_uom_id = line.product_uom
                    line_src_usage = line.location_id.usage
                    line_dst_usage = line.location_id.usage
					
                    if line_src_usage == line_dst_usage:
                        continue
                    elif line_src_usage in ['internal']:
                        qty = uom_obj._compute_qty_obj(line_uom_id,line.product_qty,line_product_uom_id,)
                    elif line_dst_usage in ['internal']:
                        qty = -uom_obj._compute_qty_obj(line_uom_id,line.product_qty,line_product_uom_id,)
						
                    if self.return_list_ids:
                        isinlist = False
                        for returnline in self.return_list_ids:
                            if returnline.product_id == line.product_id:
                                vals = {
                                    'on_confirmed_qty': returnline.on_confirmed_qty + qty,
									'on_canceled_qty': returnline.on_canceled_qty + qty
								}
                                returnline.write(vals)
                                isinlist = True
								
                        if isinlist == False:
                            vals = {
                                    'product_id': line.product_id.id,
                                    'on_confirmed_qty': qty,
                                    'product_uom': line.product_id.uom_id.id,
                                    'on_canceled_qty': qty,
                                    'order_id': order.id
                            }
                            return_line_obj.create(vals)
                    if not self.return_list_ids:
                        vals = {
                                'product_id': line.product_id.id,
                                'on_confirmed_qty': qty,
                                'product_uom': line.product_id.uom_id.id,
                                'on_canceled_qty': qty,
                                'order_id': order.id
                        }
                        return_line_obj.create(vals)
						
            for returnline in self.return_list_ids:
                for line in list_ids:
                    line_product_uom_id = line.product_id.uom_id
                    line_uom_id = line.product_uom
					
                    qty = uom_obj._compute_qty_obj(sm_uom_id,line.product_uom_qty, sol_uom_id)
                    returnline.write({'on_confirmed_qty': returnline.on_confirmed_qty - qty})
					
            for returnline in self.return_list_ids:
                if returnline.on_confirmed_qty < 0:
                    returnline.write({'returnline.on_confirmed_qty': 0})

        return True
			
    def create_procurement_reverse(self):
        """
        This create stock movement for returning products
        Unit goes to 'Destination Location (Kahoy)' to 'Source Location'
        Parts goes to 'Source Location' to 'Destination Location'
        In order to cancel out negative stock of 'Kahoy Warehouse'
        This is called after first batch of transfer. see class(StockPicking)
        """
        self._action_ship_create(reverse=True)
		
    @api.multi
    def update_kahoy_list(self):
        """
        Add the part on 'Already Kahoy Parts' list. A list that need to be return
        when the order is for assembly or cancel.
        """
        self.ensure_one()
		
        update_m2m_list = []
        for list in self.list_ids:
            update_m2m_list.append((4,list.id))
			
        self.old_list_ids = update_m2m_list
		
    @api.model
    def copy(self):
        """
        """

        default = ({'state':'cancel'})
		
        return super(SparePartsBorrow, self).copy(default=default)
		
    @api.multi
    def copy_quotation(self):
        """
        """
        self.ensure_one()
		
		# Prepare the older name
        temp_name = self.name
		
		# Create a Duplicate
        copy_rec = self.copy()
		
		# Set the Duplicate name to older name and link to the current record
        copy_rec.name = temp_name
        copy_rec.current_revision_id = self.id
		
		# Link Part List to the Duplicate
        update_list = []
        for list in self.list_ids:
            update_list.append((1,list.id,{'order_id': copy_rec.id}))
        copy_rec.list_ids = update_list
		
		# Set new name for the current record
        temp_num = self.revision_number
        self.revision_number = temp_num + 1
        temp_rev_name = "%s-REV-%02d" % (self.unrevisioned_name,self.revision_number)
        self.name = temp_rev_name
		
        view = self.env.ref('stock_unit_spare_parts_borrowing.stock_parts_borrow_view_form').read()
		
        if view:
            #return view[0]
            return {
                'type': 'ir.actions.act_window',
                'name': _('Kahoy Order'),
                'res_model': 'stock.parts.borrow',
                'res_id': copy_rec.id,
                'view_type': 'form',
                'view_mode': 'form',
                'view_id': view[0]['id'],
                'target': 'current',
                'nodestroy': True,
            }
        else:
            #self.note = str(view)
            return False
		
class SparePartsBorrowList(models.Model):
    """
    """
    _name = 'stock.parts.borrow.list'

    order_id = fields.Many2one(comodel_name='stock.parts.borrow',string='Order')
    old_order_id = fields.Many2one(comodel_name='stock.parts.borrow',string='Old Order')
    product_id = fields.Many2one(comodel_name='product.product',string='Product', required=True)
    product_uom = fields.Many2one(comodel_name='product.uom',string='Unit of Measure',compute='_compute_product_uom' ,readonly=True, states={'draft': [('readonly', False)]})
    request_by = fields.Many2one(comodel_name='res.users', string='Request by', readonly=True)
    confirm_by = fields.Many2one(comodel_name='res.users', string='Confirmed by', readonly=True)

    qty =  fields.Float(string='Quantity', digits=(16,2), default=1.00, required=True)
	
    confirm_date = fields.Date(string="Confirmed On",readonly=True)
	
    state = fields.Selection([
            ('draft', 'Draft'),
            ('under_process', 'Under Process'),
            ('done', 'Done'),
            ('cancel', 'Canceled')], string='Status', default='draft', required=True, copy=False)

    @api.multi
    @api.depends('product_id','product_uom')
    def _compute_product_uom(self):
        """
        """
        for rec in self:
            rec.product_uom = rec.product_id.uom_id	

class StockPicking(models.Model):
    _inherit = "stock.picking"
    
    @api.model
    def do_transfer(self):
        res = super(StockPicking, self).do_transfer()
        for rec in self:
            picking_obj = rec
        kahoy_order_id = self.env['stock.parts.borrow'].search([('|'),
			('unit_procurement_group_id', '=', picking_obj.group_id.id ),
			('part_procurement_group_id', '=', picking_obj.group_id.id ),
			('state', 'not in', ['cancel'])])
        if not kahoy_order_id:			
            kahoy_order_id = self.env['stock.parts.borrow'].search([('|'),
				('reverse_part_procurement_group_id', '=', picking_obj.group_id.id ),
				('reverse_unit_procurement_group_id', '=', picking_obj.group_id.id ),
				('state', 'not in', ['cancel'])])
        if kahoy_order_id:
		
            if picking_obj.group_id.id in (kahoy_order_id.unit_procurement_group_id.id, kahoy_order_id.reverse_unit_procurement_group_id.id):
                serial_ok = False
                for pack in picking_obj.pack_operation_ids:
                    if pack.lot_id.id == kahoy_order_id.serial_id.id:
                        serial_ok = True
                if not serial_ok:
                    raise ValidationError(_('Please Enter Same Serial Number: %s') % kahoy_order_id.serial_id.name)
            
            for picking in kahoy_order_id.picking_ids + kahoy_order_id.unit_picking_ids + \
						kahoy_order_id.reverse_picking_ids + kahoy_order_id.reverse_unit_picking_ids:
                if picking.state not in ('done', 'cancel'):
                    return True
            if kahoy_order_id.state in ['wait_transfer']:
                #kahoy_order_id.create_procurement_reverse()
                kahoy_order_id.update_kahoy_list()
                kahoy_order_id.list_ids.write({'state':'done'})
                return kahoy_order_id.write({'state': 'kahoy'})
            elif kahoy_order_id.state in ['assembly']:
                return kahoy_order_id.write({'state': 'done'})
            elif kahoy_order_id.state in ['wait_return']:
                kahoy_order_id.list_ids.write({'state':'cancel'})
                return kahoy_order_id.write({'state': 'cancel'})

        return True
	
    @api.multi	
    @api.model
    def action_cancel(self):
        """
        Probhibits to cancel a related Stock Transfer on Kahoy Orders
        """
        for rec in self:
           picking_obj = rec
        
        kahoy_order_id = self.env['stock.parts.borrow'].search([('|'),
			('unit_procurement_group_id', '=', picking_obj.group_id.id ),
			('part_procurement_group_id', '=', picking_obj.group_id.id ),
			('state', 'not in', ['cancel'])])
        if not kahoy_order_id:			
            kahoy_order_id = self.env['stock.parts.borrow'].search([('|'),
				('reverse_part_procurement_group_id', '=', picking_obj.group_id.id ),
				('reverse_unit_procurement_group_id', '=', picking_obj.group_id.id ),
				('state', 'not in', ['cancel'])])
        if kahoy_order_id:
            raise ValidationError(_('Forbidden to Cancel This Tranfer \n Reason: Related to Kahoy Orders'))
        
			
        return super(StockPicking, self).action_cancel()
