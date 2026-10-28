# -*- coding: utf-8 -*-
# Part of Smart Factory OS by Muhammed Ezzat Hosni Hussen. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _

class FactoryDowntimeWizard(models.TransientModel):
    _name = 'factory.downtime.wizard'
    _description = 'Report Machine Breakdown Incident'

    machine_id = fields.Many2one('factory.machine', string='Machine / Equipment', required=True)
    workcenter_id = fields.Many2one('mrp.workcenter', string='Work Center', required=True)
    reason = fields.Selection([
        ('breakdown', 'Mechanical / Electrical Breakdown'),
        ('tooling', 'Tooling / Die Changeover'),
        ('material', 'Raw Material Starvation / Shortage'),
        ('operator', 'Operator Absence / Shift Handover'),
        ('quality', 'Quality Defect Pause'),
        ('power', 'Power Outage / Utility Failure'),
        ('other', 'Other Reason'),
    ], string='Downtime Reason', required=True, default='breakdown')

    start_time = fields.Datetime(string='Breakdown Occurred At', default=fields.Datetime.now, required=True)
    technician_notes = fields.Text(string='Symptom & Operator Observations')

    def action_confirm_breakdown(self):
        self.ensure_one()
        incident = self.env['factory.machine.downtime'].create({
            'machine_id': self.machine_id.id,
            'workcenter_id': self.workcenter_id.id,
            'reason': self.reason,
            'start_time': self.start_time,
            'technician_notes': self.technician_notes,
            'state': 'open',
        })
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Breakdown Incident Logged!'),
                'message': _('Machine [%s] status marked as FAULTED. Maintenance alert triggered.') % self.machine_id.name,
                'type': 'danger',
                'sticky': False,
            }
        }
