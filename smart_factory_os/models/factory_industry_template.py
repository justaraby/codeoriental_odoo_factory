# -*- coding: utf-8 -*-
# Part of CodeOriental Smart Factory OS. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _

class FactoryIndustryTemplate(models.Model):
    _name = 'factory.industry.template'
    _description = 'Factory Industry Preset Profile'
    _order = 'sequence, name'

    name = fields.Char(string='Industry Name', required=True, translate=True)
    code = fields.Char(string='Industry Code', required=True)
    sequence = fields.Integer(string='Sequence', default=10)
    icon = fields.Char(string='Icon (FontAwesome / Emoji)', default='fa-industry')
    description = fields.Text(string='Description', translate=True)
    active = fields.Boolean(default=True)

    # Defaults for factory setup
    default_overhead_rate = fields.Float(
        string='Default Overhead Factor (%)',
        default=15.0,
        help='Estimated factory overhead (electricity, facility rent, indirect expenses) applied to batches.'
    )
    default_scrap_tolerance = fields.Float(
        string='Scrap Tolerance Threshold (%)',
        default=3.0,
        help='Trigger an alert if scrap rate exceeds this percentage.'
    )
    shift_system = fields.Selection([
        ('single', 'Single Shift (8 Hours)'),
        ('double', 'Two Shifts (16 Hours)'),
        ('triple', 'Continuous 24/7 (3 Shifts)'),
    ], string='Recommended Shift Structure', default='double')

    line_ids = fields.One2many(
        'factory.industry.line',
        'template_id',
        string='Work Center Presets'
    )

    workcenter_count = fields.Integer(
        string='Work Centers Count',
        compute='_compute_workcenter_count'
    )

    @api.depends('line_ids')
    def _compute_workcenter_count(self):
        for rec in self:
            rec.workcenter_count = len(rec.line_ids)


class FactoryIndustryLine(models.Model):
    _name = 'factory.industry.line'
    _description = 'Factory Work Center Preset Line'
    _order = 'sequence, id'

    template_id = fields.Many2one(
        'factory.industry.template',
        string='Industry Template',
        ondelete='cascade',
        required=True
    )
    name = fields.Char(string='Work Center Name', required=True, translate=True)
    sequence = fields.Integer(string='Sequence', default=10)
    code = fields.Char(string='Code', required=True)
    hourly_cost = fields.Float(string='Hourly Operating Cost (€)', default=25.0)
    capacity = fields.Float(string='Default Capacity / Hr', default=100.0)
    time_efficiency = fields.Float(string='Efficiency (%)', default=100.0)
    requires_maintenance = fields.Boolean(string='Machine Tracking', default=True)
    default_notes = fields.Char(string='Standard Operating Procedure Note', translate=True)
