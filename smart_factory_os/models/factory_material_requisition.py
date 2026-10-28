# -*- coding: utf-8 -*-
# Part of Smart Factory OS by Muhammed Ezzat Hosni Hussen. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
from odoo.exceptions import UserError

class FactoryMaterialRequisition(models.Model):
    _name = 'factory.material.requisition'
    _description = 'Factory Shop Floor Material Requisition'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date desc, id desc'

    name = fields.Char(string='Requisition #', readonly=True, default=lambda self: _('New'))
    date = fields.Date(string='Request Date', default=fields.Date.context_today, required=True)
    requested_by = fields.Many2one('res.users', string='Requested By', default=lambda self: self.env.user, required=True)
    production_id = fields.Many2one('mrp.production', string='Manufacturing Batch')
    workcenter_id = fields.Many2one('mrp.workcenter', string='Target Production Line')

    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company, required=True)
    source_location_id = fields.Many2one(
        'stock.location',
        string='Source Raw Material Location',
        domain=[('usage', '=', 'internal')]
    )
    dest_location_id = fields.Many2one(
        'stock.location',
        string='Line Production Location',
        domain=[('usage', 'in', ['internal', 'production'])]
    )

    line_ids = fields.One2many(
        'factory.material.requisition.line',
        'requisition_id',
        string='Requested Materials'
    )

    state = fields.Selection([
        ('draft', 'Draft Request'),
        ('submitted', 'Awaiting Store Approval'),
        ('approved', 'Approved & Issued'),
        ('cancelled', 'Cancelled'),
    ], string='Status', default='draft', tracking=True)

    has_shortage = fields.Boolean(string='Has Shortage', compute='_compute_shortage', store=True)
    picking_id = fields.Many2one('stock.picking', string='Stock Transfer', readonly=True)
    notes = fields.Text(string='Requisition Notes')

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('factory.material.requisition') or _('REQ-%05d') % self.env['ir.sequence'].search_count([])
        return super().create(vals_list)

    @api.depends('line_ids.is_shortage')
    def _compute_shortage(self):
        for rec in self:
            rec.has_shortage = any(line.is_shortage for line in rec.line_ids)

    def action_submit(self):
        if not self.line_ids:
            raise UserError(_('Please add at least one material line before submitting.'))
        self.write({'state': 'submitted'})

    def action_approve_issue(self):
        """Approve and create stock movement or mark issued"""
        self.ensure_one()
        # Find default warehouse locations if not specified
        warehouse = self.env['stock.warehouse'].search([('company_id', '=', self.company_id.id)], limit=1)
        src_loc = self.source_location_id or (warehouse.lot_stock_id if warehouse else False)

        if not src_loc:
            # fallback internal location
            src_loc = self.env['stock.location'].search([('usage', '=', 'internal'), ('company_id', '=', self.company_id.id)], limit=1)

        dest_loc = self.dest_location_id
        if not dest_loc:
            dest_loc = self.env['stock.location'].search([('usage', '=', 'production'), ('company_id', '=', self.company_id.id)], limit=1) or src_loc

        # Try creating internal transfer picking if stock.picking type available
        picking_type = self.env['stock.picking.type'].search([
            ('code', '=', 'internal'),
            ('company_id', '=', self.company_id.id)
        ], limit=1)

        if picking_type and src_loc and dest_loc and src_loc != dest_loc:
            picking_vals = {
                'picking_type_id': picking_type.id,
                'location_id': src_loc.id,
                'location_dest_id': dest_loc.id,
                'origin': self.name,
                'company_id': self.company_id.id,
                'move_ids_without_package': [(0, 0, {
                    'name': line.product_id.display_name,
                    'product_id': line.product_id.id,
                    'product_uom_qty': line.quantity,
                    'product_uom': line.uom_id.id,
                    'location_id': src_loc.id,
                    'location_dest_id': dest_loc.id,
                    'company_id': self.company_id.id,
                }) for line in self.line_ids]
            }
            picking = self.env['stock.picking'].create(picking_vals)
            self.picking_id = picking.id

        self.write({'state': 'approved'})

    def action_create_purchase_rfq(self):
        """1-Click creation of purchase RFQ for any short materials"""
        self.ensure_one()
        short_lines = self.line_ids.filtered(lambda l: l.is_shortage)
        if not short_lines:
            raise UserError(_('No raw material shortages found in this requisition.'))

        # Find or pick default vendor
        vendor = self.env['res.partner'].search([('supplier_rank', '>', 0)], limit=1)
        if not vendor:
            vendor = self.env['res.partner'].create({'name': _('Factory Raw Material Supplier'), 'supplier_rank': 1})

        po_vals = {
            'partner_id': vendor.id,
            'company_id': self.company_id.id,
            'origin': _('Shortage for %s') % self.name,
            'order_line': [(0, 0, {
                'product_id': line.product_id.id,
                'name': line.product_id.name,
                'product_qty': line.shortage_qty if line.shortage_qty > 0 else line.quantity,
                'product_uom': line.uom_id.id,
                'price_unit': line.product_id.standard_price or 1.0,
                'date_planned': fields.Datetime.now(),
            }) for line in short_lines]
        }
        po = self.env['purchase.order'].create(po_vals)
        return {
            'name': _('Purchase Request Created'),
            'type': 'ir.actions.act_window',
            'res_model': 'purchase.order',
            'res_id': po.id,
            'view_mode': 'form',
        }


class FactoryMaterialRequisitionLine(models.Model):
    _name = 'factory.material.requisition.line'
    _description = 'Factory Material Requisition Line'

    requisition_id = fields.Many2one('factory.material.requisition', string='Requisition', ondelete='cascade', required=True)
    product_id = fields.Many2one('product.product', string='Raw Material / Component', required=True)
    quantity = fields.Float(string='Requested Qty', default=1.0, required=True)
    uom_id = fields.Many2one('uom.uom', string='Unit of Measure', related='product_id.uom_id', readonly=True)

    qty_available = fields.Float(string='Stock on Hand', compute='_compute_stock_levels')
    shortage_qty = fields.Float(string='Deficit Qty', compute='_compute_stock_levels')
    is_shortage = fields.Boolean(string='Shortage Flag', compute='_compute_stock_levels', store=True)

    @api.depends('product_id', 'quantity')
    def _compute_stock_levels(self):
        for rec in self:
            if rec.product_id:
                rec.qty_available = rec.product_id.qty_available
                deficit = rec.quantity - rec.qty_available
                rec.shortage_qty = deficit if deficit > 0 else 0.0
                rec.is_shortage = deficit > 0
            else:
                rec.qty_available = 0.0
                rec.shortage_qty = 0.0
                rec.is_shortage = False
