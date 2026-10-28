# -*- coding: utf-8 -*-
# Part of CodeOriental Smart Factory OS. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
from odoo.exceptions import UserError

class FactoryQuickRunWizard(models.TransientModel):
    _name = 'factory.quick.run.wizard'
    _description = 'Instant Factory Production Batch Launcher'

    product_id = fields.Many2one(
        'product.product',
        string='Finished Product to Produce',
        domain=[('bom_ids', '!=', False)],
        required=True
    )
    product_qty = fields.Float(string='Target Production Quantity', default=100.0, required=True)
    uom_id = fields.Many2one('uom.uom', string='Unit of Measure', related='product_id.uom_id', readonly=True)

    bom_id = fields.Many2one('mrp.bom', string='Bill of Materials', compute='_compute_bom', readonly=False, store=True)
    shift_id = fields.Many2one('factory.shift', string='Assigned Shift')
    supervisor_id = fields.Many2one('res.users', string='Floor Supervisor', default=lambda self: self.env.user, required=True)
    date_start = fields.Datetime(string='Scheduled Start Time', default=fields.Datetime.now)

    auto_issue_materials = fields.Boolean(
        string='Auto-generate Raw Material Requisition Slip',
        default=True
    )

    @api.depends('product_id')
    def _compute_bom(self):
        for rec in self:
            if rec.product_id:
                rec.bom_id = self.env['mrp.bom']._bom_find(rec.product_id)[rec.product_id]
            else:
                rec.bom_id = False

    def action_launch_batch(self):
        self.ensure_one()
        if self.product_qty <= 0:
            raise UserError(_('Production quantity must be greater than zero.'))

        # Create MRP production
        mo_vals = {
            'product_id': self.product_id.id,
            'product_qty': self.product_qty,
            'product_uom_id': self.uom_id.id,
            'bom_id': self.bom_id.id if self.bom_id else False,
            'date_start': self.date_start,
            'factory_shift_id': self.shift_id.id if self.shift_id else False,
            'factory_supervisor_id': self.supervisor_id.id,
        }
        mo = self.env['mrp.production'].create(mo_vals)

        # Confirm MO to populate raw moves
        if hasattr(mo, 'action_confirm'):
            mo.action_confirm()

        # Auto create requisition if enabled
        if self.auto_issue_materials and mo.move_raw_ids:
            try:
                mo.action_quick_material_requisition()
            except Exception:
                pass

        return {
            'name': _('Active Batch: %s') % mo.factory_batch_code,
            'type': 'ir.actions.act_window',
            'res_model': 'mrp.production',
            'res_id': mo.id,
            'view_mode': 'form',
        }
