# -*- coding: utf-8 -*-
# Part of Smart Factory OS by Muhammed Ezzat Hosni Hussen. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
from odoo.exceptions import UserError

class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    factory_batch_code = fields.Char(
        string='Batch Tracking Code',
        copy=False,
        default=lambda self: self.env['ir.sequence'].next_by_code('factory.batch.code') or f"BATCH-{fields.Date.today()}"
    )
    factory_shift_id = fields.Many2one(
        'factory.shift',
        string='Production Shift',
        tracking=True
    )
    factory_supervisor_id = fields.Many2one(
        'res.users',
        string='Floor Supervisor',
        default=lambda self: self.env.user,
        tracking=True
    )
    factory_machine_ids = fields.Many2many(
        'factory.machine',
        string='Assigned Machinery'
    )

    # 4-Pillar Batch Costing & Profitability
    cost_raw_materials = fields.Float(
        string='Raw Materials Cost (€)',
        compute='_compute_factory_costs',
        store=True,
        digits='Product Price'
    )
    cost_direct_labor = fields.Float(
        string='Direct Labor Cost (€)',
        compute='_compute_factory_costs',
        store=True,
        digits='Product Price'
    )
    cost_machine_power = fields.Float(
        string='Machine & Energy Cost (€)',
        compute='_compute_factory_costs',
        store=True,
        digits='Product Price'
    )
    overhead_rate_pct = fields.Float(
        string='Factory Overhead Factor (%)',
        default=15.0,
        help='Percentage applied over direct costs for facility rent, indirect labor, water & administration.'
    )
    cost_factory_overhead = fields.Float(
        string='Factory Overhead Cost (€)',
        compute='_compute_factory_costs',
        store=True,
        digits='Product Price'
    )
    cost_total_batch = fields.Float(
        string='Total Batch Cost (€)',
        compute='_compute_factory_costs',
        store=True,
        digits='Product Price'
    )
    cost_per_unit = fields.Float(
        string='Real Unit Production Cost (€)',
        compute='_compute_factory_costs',
        store=True,
        digits='Product Price'
    )
    target_margin_pct = fields.Float(
        string='Target Gross Margin (%)',
        default=30.0
    )
    suggested_sale_price = fields.Float(
        string='Target Minimum Selling Price (€)',
        compute='_compute_factory_costs',
        store=True,
        digits='Product Price'
    )
    actual_product_price = fields.Float(
        string='Catalog List Price (€)',
        related='product_id.list_price',
        readonly=True
    )
    batch_margin_pct = fields.Float(
        string='Estimated Batch Margin (%)',
        compute='_compute_factory_costs',
        store=True
    )

    # Scrap & Quality Management
    scrap_units = fields.Float(
        string='Scrap / Waste Qty',
        compute='_compute_scrap_metrics',
        store=True
    )
    scrap_ratio_pct = fields.Float(
        string='Scrap Rate (%)',
        compute='_compute_scrap_metrics',
        store=True
    )
    is_scrap_alert = fields.Boolean(
        string='Scrap Alert',
        compute='_compute_scrap_metrics',
        store=True
    )
    scrap_threshold_pct = fields.Float(
        string='Scrap Alert Threshold (%)',
        default=3.0
    )

    qc_inspected = fields.Boolean(string='QC Inspected', default=False, tracking=True)
    qc_passed = fields.Boolean(string='Quality Passed', default=False, tracking=True)
    qc_inspector_id = fields.Many2one('res.users', string='QC Inspector')
    qc_inspection_notes = fields.Char(string='Inspection Remarks')

    requisition_count = fields.Integer(
        string='Requisitions Count',
        compute='_compute_requisition_count'
    )

    @api.depends('move_raw_ids', 'move_raw_ids.quantity', 'move_raw_ids.product_id',
                 'workorder_ids.duration', 'qty_producing', 'product_qty', 'overhead_rate_pct',
                 'target_margin_pct', 'factory_machine_ids')
    def _compute_factory_costs(self):
        for order in self:
            # 1. Raw Materials Cost
            mat_cost = 0.0
            for move in order.move_raw_ids:
                # Use standard_price of product or move unit price
                unit_price = move.product_id.standard_price or 0.0
                qty_used = move.quantity if move.quantity > 0 else move.product_uom_qty
                mat_cost += (unit_price * qty_used)
            order.cost_raw_materials = round(mat_cost, 2)

            # 2. Labor Cost: estimated from work orders duration (in minutes / 60 * avg labor rate)
            total_duration_hours = sum(order.workorder_ids.mapped('duration')) / 60.0
            labor_rate_per_hour = 18.0  # standard operator rate
            order.cost_direct_labor = round(total_duration_hours * labor_rate_per_hour, 2)

            # 3. Machine Cost: machine hourly rates * total workcenter durations
            machine_cost = 0.0
            if order.factory_machine_ids:
                total_mach_rate = sum(order.factory_machine_ids.mapped('hourly_cost'))
                machine_cost = total_duration_hours * (total_mach_rate or 25.0)
            else:
                machine_cost = total_duration_hours * 25.0
            order.cost_machine_power = round(machine_cost, 2)

            # 4. Factory Overhead Cost
            direct_cost = order.cost_raw_materials + order.cost_direct_labor + order.cost_machine_power
            order.cost_factory_overhead = round(direct_cost * (order.overhead_rate_pct / 100.0), 2)

            # Total and per unit
            order.cost_total_batch = round(direct_cost + order.cost_factory_overhead, 2)
            qty = order.qty_producing if order.qty_producing > 0 else order.product_qty
            if qty > 0:
                order.cost_per_unit = round(order.cost_total_batch / qty, 2)
            else:
                order.cost_per_unit = 0.0

            # Suggested Price for Target Margin
            if order.cost_per_unit > 0 and order.target_margin_pct < 100:
                order.suggested_sale_price = round(order.cost_per_unit / (1.0 - (order.target_margin_pct / 100.0)), 2)
            else:
                order.suggested_sale_price = order.cost_per_unit

            # Estimated Margin vs Catalog List Price
            list_price = order.product_id.list_price or 0.0
            if list_price > 0 and order.cost_per_unit > 0:
                order.batch_margin_pct = round(((list_price - order.cost_per_unit) / list_price) * 100.0, 1)
            else:
                order.batch_margin_pct = 0.0

    @api.depends('scrap_ids.scrap_qty', 'qty_producing', 'product_qty')
    def _compute_scrap_metrics(self):
        for order in self:
            total_scrap = sum(order.scrap_ids.mapped('scrap_qty'))
            order.scrap_units = total_scrap
            total_output = (order.qty_producing or order.product_qty or 1.0) + total_scrap
            if total_output > 0:
                rate = round((total_scrap / total_output) * 100.0, 2)
                order.scrap_ratio_pct = rate
                order.is_scrap_alert = rate > order.scrap_threshold_pct
            else:
                order.scrap_ratio_pct = 0.0
                order.is_scrap_alert = False

    def _compute_requisition_count(self):
        for order in self:
            order.requisition_count = self.env['factory.material.requisition'].search_count([('production_id', '=', order.id)])

    def action_view_requisitions(self):
        self.ensure_one()
        return {
            'name': _('Material Requisitions - %s') % self.name,
            'type': 'ir.actions.act_window',
            'res_model': 'factory.material.requisition',
            'view_mode': 'list,form',
            'domain': [('production_id', '=', self.id)],
            'context': {
                'default_production_id': self.id,
                'default_requested_by': self.env.user.id,
            }
        }

    def action_quick_material_requisition(self):
        """1-Click creation of Material Requisition based on BOM raw materials"""
        self.ensure_one()
        if not self.move_raw_ids:
            raise UserError(_('No raw materials found in this production order.'))

        req_vals = {
            'production_id': self.id,
            'requested_by': self.env.user.id,
            'date': fields.Date.today(),
            'notes': _('Auto-generated requisition for Batch %s (%s)') % (self.factory_batch_code, self.product_id.display_name),
            'line_ids': [(0, 0, {
                'product_id': move.product_id.id,
                'quantity': move.product_uom_qty,
            }) for move in self.move_raw_ids]
        }
        req = self.env['factory.material.requisition'].create(req_vals)
        return {
            'name': _('Material Requisition Created'),
            'type': 'ir.actions.act_window',
            'res_model': 'factory.material.requisition',
            'res_id': req.id,
            'view_mode': 'form',
        }

    def action_pass_quality(self):
        """1-Click Quality Sign-off"""
        self.ensure_one()
        self.write({
            'qc_inspected': True,
            'qc_passed': True,
            'qc_inspector_id': self.env.user.id,
            'qc_inspection_notes': _('Passed by %s on %s') % (self.env.user.name, fields.Date.today())
        })

    def action_shopfloor_produce_one_click(self):
        """Simple 1-click batch completion for floor operators"""
        self.ensure_one()
        if self.state in ['draft', 'confirmed']:
            if hasattr(self, 'action_confirm'):
                self.action_confirm()
        # Set quantity producing to target if empty
        if not self.qty_producing or self.qty_producing == 0:
            self.qty_producing = self.product_qty

        # Mark done if standard method exists
        try:
            return self.button_mark_done()
        except Exception:
            # Fallback for various odoo versions
            pass
        return True
