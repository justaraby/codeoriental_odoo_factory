# -*- coding: utf-8 -*-
# Part of Smart Factory OS by Muhammed Ezzat Hosni Hussen. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
from odoo.exceptions import UserError

class FactoryOnboardingWizard(models.TransientModel):
    _name = 'factory.onboarding.wizard'
    _description = 'Interactive Factory Quick Setup Wizard'

    template_id = fields.Many2one(
        'factory.industry.template',
        string='Factory Industry Type',
        required=True,
        help='Pick the industry profile that best matches your factory operations.'
    )
    company_id = fields.Many2one(
        'res.company',
        string='Target Company',
        default=lambda self: self.env.company,
        required=True
    )

    create_workcenters = fields.Boolean(
        string='Auto-create Standard Work Centers & Lines',
        default=True
    )
    create_shifts = fields.Boolean(
        string='Configure Standard Production Shifts',
        default=True
    )
    shift_count = fields.Selection([
        ('1', '1 Shift (Daytime 8 Hours)'),
        ('2', '2 Shifts (Day + Evening 16 Hours)'),
        ('3', '3 Shifts (24/7 Continuous Operation)'),
    ], string='Daily Shift Schedule', default='2')

    create_demo_products = fields.Boolean(
        string='Create Sample Product & Bill of Materials (BOM)',
        default=True,
        help='Generates sample raw materials, finished product, and pre-linked BOM so you can test production immediately.'
    )
    sample_product_name = fields.Char(
        string='Sample Finished Product Name',
        default='Sample Manufactured Item'
    )

    factory_overhead_rate = fields.Float(
        string='Estimated Factory Overhead (%)',
        default=15.0,
        help='Default overhead allocation for plant rent, utilities, indirect costs.'
    )

    @api.onchange('template_id')
    def _onchange_template_id(self):
        if self.template_id:
            self.factory_overhead_rate = self.template_id.default_overhead_rate or 15.0
            if self.template_id.code == 'FOOD':
                self.sample_product_name = 'Organic Artisanal Bread 500g'
            elif self.template_id.code == 'PLASTIC':
                self.sample_product_name = 'PET Plastic Bottle 1 Liter'
            elif self.template_id.code == 'METAL':
                self.sample_product_name = 'Precision Steel Bracket 100mm'
            elif self.template_id.code == 'TEXTILE':
                self.sample_product_name = 'Cotton Crewneck T-Shirt Size L'
            elif self.template_id.code == 'CHEMICAL':
                self.sample_product_name = 'Liquid Dish Detergent 1L'
            elif self.template_id.code == 'FURNITURE':
                self.sample_product_name = 'Solid Oak Office Desk'
            elif self.template_id.code == 'ELECTRONICS':
                self.sample_product_name = 'Smart Sensor Module v1'
            else:
                self.sample_product_name = 'Custom Fabricated Assembly'

    def action_deploy_factory(self):
        """Zero-Consultant Factory Automation Engine"""
        self.ensure_one()

        created_wcs = []
        # 1. Create Work Centers from Industry Template
        if self.create_workcenters and self.template_id.line_ids:
            for line in self.template_id.line_ids:
                existing = self.env['mrp.workcenter'].search([
                    ('name', '=', line.name),
                    ('company_id', '=', self.company_id.id)
                ], limit=1)
                if not existing:
                    wc = self.env['mrp.workcenter'].create({
                        'name': line.name,
                        'code': line.code,
                        'company_id': self.company_id.id,
                        'costs_hour': line.hourly_cost,
                        'time_efficiency': line.time_efficiency,
                        'note': line.default_notes,
                    })
                    created_wcs.append(wc)

                    # Also create a default Machine linked to this work center
                    self.env['factory.machine'].create({
                        'name': _('Line 1 - %s Machine') % line.name,
                        'code': _('MAC-%s-01') % line.code,
                        'workcenter_id': wc.id,
                        'company_id': self.company_id.id,
                        'hourly_cost': line.hourly_cost,
                        'state': 'running',
                    })
                else:
                    created_wcs.append(existing)

        # 2. Create Shifts
        if self.create_shifts:
            shift_defs = [
                ('Morning Shift (08:00 - 16:00)', 'SFT-MORN', 8.0, 16.0, 8.0, 1),
                ('Evening Shift (16:00 - 00:00)', 'SFT-EVE', 16.0, 24.0, 8.0, 2),
                ('Night Shift (00:00 - 08:00)', 'SFT-NGT', 0.0, 8.0, 8.0, 3),
            ]
            count = int(self.shift_count or 2)
            for i in range(count):
                name, code, start, end, dur, seq = shift_defs[i]
                existing_shift = self.env['factory.shift'].search([
                    ('code', '=', code),
                    ('company_id', '=', self.company_id.id)
                ], limit=1)
                if not existing_shift:
                    self.env['factory.shift'].create({
                        'name': name,
                        'code': code,
                        'start_hour': start,
                        'end_hour': end,
                        'duration_hours': dur,
                        'sequence': seq,
                        'company_id': self.company_id.id,
                    })

        # 3. Create Sample Products & BOM if requested
        if self.create_demo_products:
            # Create Category: Finished Goods & Raw Materials
            cat_fg = self.env['product.category'].search([('name', '=', 'Finished Manufactured Goods')], limit=1)
            if not cat_fg:
                cat_fg = self.env['product.category'].create({'name': 'Finished Manufactured Goods'})

            cat_raw = self.env['product.category'].search([('name', '=', 'Raw Materials & Components')], limit=1)
            if not cat_raw:
                cat_raw = self.env['product.category'].create({'name': 'Raw Materials & Components'})

            # Create Raw Materials
            uom_unit = self.env.ref('uom.product_uom_unit', raise_if_not_found=False) or self.env['uom.uom'].search([], limit=1)
            uom_kg = self.env.ref('uom.product_uom_kgm', raise_if_not_found=False) or uom_unit

            raw_1 = self.env['product.product'].create({
                'name': _('Raw Material A - Primary Grade'),
                'categ_id': cat_raw.id,
                'is_storable': True,
                'uom_id': uom_kg.id,
                'uom_po_id': uom_kg.id,
                'standard_price': 4.50,
            })
            raw_2 = self.env['product.product'].create({
                'name': _('Packaging & Label Material'),
                'categ_id': cat_raw.id,
                'is_storable': True,
                'uom_id': uom_unit.id,
                'uom_po_id': uom_unit.id,
                'standard_price': 0.85,
            })

            # Create Finished Product
            finished_prod = self.env['product.product'].create({
                'name': self.sample_product_name or _('Factory Finished Good'),
                'categ_id': cat_fg.id,
                'is_storable': True,
                'uom_id': uom_unit.id,
                'uom_po_id': uom_unit.id,
                'list_price': 25.00,
                'standard_price': 12.00,
            })

            # Create BOM
            bom_vals = {
                'product_tmpl_id': finished_prod.product_tmpl_id.id,
                'product_qty': 1.0,
                'type': 'normal',
                'company_id': self.company_id.id,
                'bom_line_ids': [
                    (0, 0, {'product_id': raw_1.id, 'product_qty': 2.0}),
                    (0, 0, {'product_id': raw_2.id, 'product_qty': 1.0}),
                ]
            }
            # Link workcenter operation if we have workcenters
            if created_wcs:
                bom_vals['operation_ids'] = [(0, 0, {
                    'name': _('Primary Processing & Assembly'),
                    'workcenter_id': created_wcs[0].id,
                    'time_cycle': 15.0,  # 15 minutes
                })]

            self.env['mrp.bom'].create(bom_vals)

        # Notify success and redirect to Command Center
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Factory Setup Complete!'),
                'message': _('Your factory operating environment for [%s] is fully ready. Work centers, shifts, and production rules are active.') % self.template_id.name,
                'type': 'success',
                'sticky': False,
                'next': {
                    'type': 'ir.actions.act_window',
                    'name': _('Smart Factory Command Center'),
                    'res_model': 'factory.dashboard',
                    'view_mode': 'form',
                    'target': 'current',
                }
            }
        }
