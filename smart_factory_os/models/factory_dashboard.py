# -*- coding: utf-8 -*-
# Part of CodeOriental Smart Factory OS. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _

class FactoryDashboard(models.Model):
    _name = 'factory.dashboard'
    _description = 'Smart Factory Command Center Hub'

    name = fields.Char(string='Dashboard', default='Plant Command Center')
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)

    # Production KPIs
    active_orders_count = fields.Integer(string='Active Batches', compute='_compute_kpis')
    completed_today_count = fields.Integer(string='Batches Done Today', compute='_compute_kpis')
    units_produced_today = fields.Float(string='Units Output Today', compute='_compute_kpis')

    # Machine & Asset Health KPIs
    total_machines = fields.Integer(string='Total Machinery', compute='_compute_kpis')
    running_machines = fields.Integer(string='Running Lines', compute='_compute_kpis')
    breakdown_machines = fields.Integer(string='Faulted / Breakdown', compute='_compute_kpis')
    machine_utilization_pct = fields.Float(string='Line Availability (%)', compute='_compute_kpis')

    # Material & Shortages
    pending_requisitions = fields.Integer(string='Pending Requisitions', compute='_compute_kpis')
    shortage_alerts_count = fields.Integer(string='Material Shortages', compute='_compute_kpis')

    # Quality & Scrap
    today_scrap_units = fields.Float(string='Today Scrap Units', compute='_compute_kpis')
    avg_scrap_rate_pct = fields.Float(string='Scrap Rate (%)', compute='_compute_kpis')

    # Cost absorption
    today_factory_cost = fields.Float(string='Estimated Factory Cost Today (€)', compute='_compute_kpis')

    def _compute_kpis(self):
        today = fields.Date.today()
        for rec in self:
            # Production
            active_mrp = self.env['mrp.production'].search([
                ('company_id', '=', rec.company_id.id),
                ('state', 'in', ['confirmed', 'progress', 'to_close'])
            ])
            rec.active_orders_count = len(active_mrp)

            done_today = self.env['mrp.production'].search([
                ('company_id', '=', rec.company_id.id),
                ('state', '=', 'done'),
                ('date_finished', '>=', fields.Datetime.to_datetime(today))
            ])
            rec.completed_today_count = len(done_today)
            rec.units_produced_today = sum(done_today.mapped('qty_producing'))

            # Machines
            machines = self.env['factory.machine'].search([('company_id', '=', rec.company_id.id)])
            rec.total_machines = len(machines)
            rec.running_machines = len(machines.filtered(lambda m: m.state == 'running'))
            rec.breakdown_machines = len(machines.filtered(lambda m: m.state == 'breakdown'))
            if rec.total_machines > 0:
                rec.machine_utilization_pct = round((rec.running_machines / rec.total_machines) * 100.0, 1)
            else:
                rec.machine_utilization_pct = 100.0

            # Shortages
            reqs = self.env['factory.material.requisition'].search([
                ('company_id', '=', rec.company_id.id),
                ('state', 'in', ['draft', 'submitted'])
            ])
            rec.pending_requisitions = len(reqs)
            rec.shortage_alerts_count = len(reqs.filtered(lambda r: r.has_shortage))

            # Scrap
            scraps = self.env['stock.scrap'].search([
                ('company_id', '=', rec.company_id.id),
                ('date_done', '>=', fields.Datetime.to_datetime(today))
            ])
            rec.today_scrap_units = sum(scraps.mapped('scrap_qty'))
            total_prod = rec.units_produced_today + rec.today_scrap_units
            if total_prod > 0:
                rec.avg_scrap_rate_pct = round((rec.today_scrap_units / total_prod) * 100.0, 2)
            else:
                rec.avg_scrap_rate_pct = 0.0

            # Today cost
            rec.today_factory_cost = round(sum(done_today.mapped('cost_total_batch')), 2)

    # 1-Click Navigation Actions
    def action_open_active_orders(self):
        return {
            'name': _('Active Manufacturing Batches'),
            'type': 'ir.actions.act_window',
            'res_model': 'mrp.production',
            'view_mode': 'tree,form,calendar',
            'domain': [('state', 'in', ['confirmed', 'progress', 'to_close'])],
        }

    def action_open_machines(self):
        return {
            'name': _('Factory Machinery & Asset Status'),
            'type': 'ir.actions.act_window',
            'res_model': 'factory.machine',
            'view_mode': 'kanban,tree,form',
        }

    def action_open_shortages(self):
        return {
            'name': _('Raw Material Shortages'),
            'type': 'ir.actions.act_window',
            'res_model': 'factory.material.requisition',
            'view_mode': 'tree,form',
            'domain': [('has_shortage', '=', True)],
        }

    def action_open_onboarding_wizard(self):
        return {
            'name': _('Interactive Factory Onboarding Wizard'),
            'type': 'ir.actions.act_window',
            'res_model': 'factory.onboarding.wizard',
            'view_mode': 'form',
            'target': 'new',
        }

    def action_open_quick_run_wizard(self):
        return {
            'name': _('Launch Instant Production Batch'),
            'type': 'ir.actions.act_window',
            'res_model': 'factory.quick.run.wizard',
            'view_mode': 'form',
            'target': 'new',
        }
