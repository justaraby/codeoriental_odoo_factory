# -*- coding: utf-8 -*-
# Part of CodeOriental Smart Factory OS. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _

class FactoryShift(models.Model):
    _name = 'factory.shift'
    _description = 'Factory Shift Schedule'
    _order = 'sequence, start_hour'

    name = fields.Char(string='Shift Name', required=True, translate=True)
    code = fields.Char(string='Shift Code', required=True)
    sequence = fields.Integer(string='Sequence', default=10)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)

    start_hour = fields.Float(string='Start Time (24h)', default=8.0, help='e.g., 8.0 for 08:00 AM')
    end_hour = fields.Float(string='End Time (24h)', default=16.5, help='e.g., 16.5 for 04:30 PM')
    duration_hours = fields.Float(string='Working Hours', default=8.0)

    supervisor_id = fields.Many2one('res.users', string='Default Supervisor')
    worker_ids = fields.Many2many('hr.employee', string='Assigned Production Operators')
    worker_count = fields.Integer(string='Workers Count', compute='_compute_worker_count')

    active = fields.Boolean(default=True)
    color = fields.Integer(string='Color Index', default=4)

    @api.depends('worker_ids')
    def _compute_worker_count(self):
        for rec in self:
            rec.worker_count = len(rec.worker_ids)


class FactoryShiftLog(models.Model):
    _name = 'factory.shift.log'
    _description = 'Factory Shift Handover & Production Log'
    _inherit = ['mail.thread']
    _order = 'log_date desc, shift_id'

    name = fields.Char(string='Log Reference', readonly=True, default=lambda self: _('New'))
    log_date = fields.Date(string='Date', default=fields.Date.context_today, required=True)
    shift_id = fields.Many2one('factory.shift', string='Shift', required=True)
    supervisor_id = fields.Many2one('res.users', string='Shift Supervisor', default=lambda self: self.env.user, required=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)

    planned_units = fields.Float(string='Target Units', default=0.0)
    produced_units = fields.Float(string='Actual Output Units', default=0.0)
    scrap_units = fields.Float(string='Defective / Scrap Units', default=0.0)

    scrap_rate = fields.Float(string='Scrap Rate (%)', compute='_compute_rates', store=True)
    achievement_rate = fields.Float(string='Target Achievement (%)', compute='_compute_rates', store=True)

    downtime_minutes = fields.Float(string='Total Line Downtime (Minutes)', default=0.0)
    active_operators = fields.Integer(string='Operators Present', default=5)

    handover_notes = fields.Text(string='Shift Handover Notes & Instructions')
    safety_incidents = fields.Boolean(string='Any Safety / Quality Incident?', default=False)
    incident_details = fields.Text(string='Incident Details')

    state = fields.Selection([
        ('draft', 'In Progress'),
        ('submitted', 'Submitted / Handed Over'),
        ('approved', 'Plant Manager Approved'),
    ], string='Status', default='draft', tracking=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('factory.shift.log') or _('SFT-%s') % fields.Date.today()
        return super().create(vals_list)

    @api.depends('planned_units', 'produced_units', 'scrap_units')
    def _compute_rates(self):
        for rec in self:
            total_produced = rec.produced_units + rec.scrap_units
            if total_produced > 0:
                rec.scrap_rate = round((rec.scrap_units / total_produced) * 100.0, 2)
            else:
                rec.scrap_rate = 0.0

            if rec.planned_units > 0:
                rec.achievement_rate = round((rec.produced_units / rec.planned_units) * 100.0, 2)
            else:
                rec.achievement_rate = 100.0 if rec.produced_units > 0 else 0.0

    def action_submit(self):
        self.write({'state': 'submitted'})

    def action_approve(self):
        self.write({'state': 'approved'})
