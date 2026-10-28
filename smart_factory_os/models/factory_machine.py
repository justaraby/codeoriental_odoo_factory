# -*- coding: utf-8 -*-
# Part of Smart Factory OS by Muhammed Ezzat Hosni Hussen. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
from odoo.exceptions import UserError

class FactoryMachine(models.Model):
    _name = 'factory.machine'
    _description = 'Factory Machine & Equipment'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name'

    name = fields.Char(string='Machine / Asset Name', required=True, tracking=True)
    code = fields.Char(string='Machine Code / Asset Tag', required=True, copy=False)
    serial_number = fields.Char(string='Serial Number')
    model_name = fields.Char(string='Model / Manufacturer')

    workcenter_id = fields.Many2one(
        'mrp.workcenter',
        string='Work Center / Production Line',
        required=True,
        tracking=True
    )
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.company,
        required=True
    )

    state = fields.Selection([
        ('running', 'Operational / Running'),
        ('idle', 'Standby / Idle'),
        ('maintenance', 'Scheduled Maintenance'),
        ('breakdown', 'Unplanned Breakdown'),
    ], string='Status', default='idle', tracking=True)

    hourly_cost = fields.Float(
        string='Machine Hourly Rate (€/hr)',
        default=35.0,
        help='Operating cost per hour including electricity, depreciation, and fluids.'
    )
    power_kw = fields.Float(string='Power Rating (kW)', default=15.0)

    installation_date = fields.Date(string='Installation Date')
    last_maintenance_date = fields.Date(string='Last Service Date')
    next_maintenance_date = fields.Date(string='Next Service Due', tracking=True)

    downtime_ids = fields.One2many(
        'factory.machine.downtime',
        'machine_id',
        string='Downtime Logs'
    )

    total_downtime_hours = fields.Float(
        string='Total Downtime (Hours)',
        compute='_compute_downtime_metrics',
        store=True
    )
    downtime_count = fields.Integer(
        string='Breakdown Count',
        compute='_compute_downtime_metrics',
        store=True
    )
    active = fields.Boolean(default=True)
    notes = fields.Text(string='Technical Notes / Operating Manual')

    @api.depends('downtime_ids.duration_hours', 'downtime_ids.state')
    def _compute_downtime_metrics(self):
        for rec in self:
            rec.total_downtime_hours = sum(rec.downtime_ids.mapped('duration_hours'))
            rec.downtime_count = len(rec.downtime_ids)

    def action_set_running(self):
        self.write({'state': 'running'})

    def action_set_idle(self):
        self.write({'state': 'idle'})

    def action_report_breakdown(self):
        """Open quick downtime reporting wizard"""
        return {
            'name': _('Report Machine Breakdown'),
            'type': 'ir.actions.act_window',
            'res_model': 'factory.downtime.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_machine_id': self.id,
                'default_workcenter_id': self.workcenter_id.id,
            }
        }

    def action_view_downtimes(self):
        self.ensure_one()
        return {
            'name': _('Downtime History - %s') % self.name,
            'type': 'ir.actions.act_window',
            'res_model': 'factory.machine.downtime',
            'view_mode': 'tree,form',
            'domain': [('machine_id', '=', self.id)],
            'context': {'default_machine_id': self.id},
        }


class FactoryMachineDowntime(models.Model):
    _name = 'factory.machine.downtime'
    _description = 'Factory Machine Downtime Incident'
    _inherit = ['mail.thread']
    _order = 'start_time desc'

    name = fields.Char(string='Incident Ref', readonly=True, default=lambda self: _('New'))
    machine_id = fields.Many2one('factory.machine', string='Machine', required=True)
    workcenter_id = fields.Many2one('mrp.workcenter', string='Work Center', required=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)

    reason = fields.Selection([
        ('breakdown', 'Mechanical / Electrical Breakdown'),
        ('tooling', 'Tooling / Die Changeover'),
        ('material', 'Raw Material Starvation / Shortage'),
        ('operator', 'Operator Absence / Shift Handover'),
        ('quality', 'Quality Defect Pause'),
        ('power', 'Power Outage / Utility Failure'),
        ('other', 'Other Reason'),
    ], string='Downtime Reason', required=True, default='breakdown')

    start_time = fields.Datetime(string='Start Time', default=fields.Datetime.now, required=True)
    end_time = fields.Datetime(string='Resolved Time')
    duration_hours = fields.Float(string='Duration (Hours)', compute='_compute_duration', store=True)

    cost_impact = fields.Float(
        string='Estimated Loss (€)',
        compute='_compute_cost_impact',
        store=True,
        help='Estimated lost production capacity cost during downtime.'
    )

    state = fields.Selection([
        ('open', 'Ongoing Breakdown'),
        ('resolved', 'Resolved / Back in Action'),
    ], string='Status', default='open', tracking=True)

    technician_notes = fields.Text(string='Remedy Action / Root Cause')

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('factory.machine.downtime') or _('INC-%05d') % self.env['ir.sequence'].search_count([])
        records = super().create(vals_list)
        for rec in records:
            if rec.state == 'open' and rec.machine_id:
                rec.machine_id.write({'state': 'breakdown'})
        return records

    @api.depends('start_time', 'end_time')
    def _compute_duration(self):
        for rec in self:
            if rec.start_time and rec.end_time:
                delta = rec.end_time - rec.start_time
                rec.duration_hours = round(delta.total_seconds() / 3600.0, 2)
            else:
                rec.duration_hours = 0.0

    @api.depends('duration_hours', 'machine_id.hourly_cost')
    def _compute_cost_impact(self):
        for rec in self:
            rec.cost_impact = round(rec.duration_hours * (rec.machine_id.hourly_cost or 30.0), 2)

    def action_resolve(self):
        self.ensure_one()
        now = fields.Datetime.now()
        self.write({
            'state': 'resolved',
            'end_time': self.end_time or now
        })
        if self.machine_id:
            self.machine_id.write({'state': 'running'})
