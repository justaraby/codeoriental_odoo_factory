# -*- coding: utf-8 -*-
# Part of Smart Factory OS by Muhammed Ezzat Hosni Hussen. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, tools, _

class FactoryCostAnalysis(models.Model):
    _name = 'factory.cost.analysis'
    _description = 'Factory Batch Cost & Margin Analysis'
    _auto = False
    _order = 'date_planned_start desc'

    production_id = fields.Many2one('mrp.production', string='Manufacturing Order', readonly=True)
    batch_code = fields.Char(string='Batch Code', readonly=True)
    product_id = fields.Many2one('product.product', string='Finished Product', readonly=True)
    product_tmpl_id = fields.Many2one('product.template', string='Product Template', readonly=True)
    company_id = fields.Many2one('res.company', string='Company', readonly=True)
    date_planned_start = fields.Datetime(string='Start Date', readonly=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('progress', 'In Progress'),
        ('to_close', 'To Close'),
        ('done', 'Done'),
        ('cancel', 'Cancelled'),
    ], string='Status', readonly=True)

    product_qty = fields.Float(string='Planned Qty', readonly=True)
    qty_produced = fields.Float(string='Produced Qty', readonly=True)

    cost_raw_materials = fields.Float(string='Material Cost (€)', readonly=True)
    cost_direct_labor = fields.Float(string='Labor Cost (€)', readonly=True)
    cost_machine_power = fields.Float(string='Machine Cost (€)', readonly=True)
    cost_factory_overhead = fields.Float(string='Overhead Cost (€)', readonly=True)
    cost_total_batch = fields.Float(string='Total Cost (€)', readonly=True)
    cost_per_unit = fields.Float(string='Unit Cost (€)', readonly=True)

    actual_revenue = fields.Float(string='Theoretical Revenue (€)', readonly=True)
    gross_profit = fields.Float(string='Gross Profit (€)', readonly=True)
    margin_pct = fields.Float(string='Margin (%)', readonly=True)

    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""
            CREATE OR REPLACE VIEW %s AS (
                SELECT
                    mp.id AS id,
                    mp.id AS production_id,
                    mp.factory_batch_code AS batch_code,
                    mp.product_id AS product_id,
                    pp.product_tmpl_id AS product_tmpl_id,
                    mp.company_id AS company_id,
                    mp.date_start AS date_planned_start,
                    mp.state AS state,
                    mp.product_qty AS product_qty,
                    COALESCE(mp.qty_producing, mp.product_qty) AS qty_produced,
                    COALESCE(mp.cost_raw_materials, 0.0) AS cost_raw_materials,
                    COALESCE(mp.cost_direct_labor, 0.0) AS cost_direct_labor,
                    COALESCE(mp.cost_machine_power, 0.0) AS cost_machine_power,
                    COALESCE(mp.cost_factory_overhead, 0.0) AS cost_factory_overhead,
                    COALESCE(mp.cost_total_batch, 0.0) AS cost_total_batch,
                    COALESCE(mp.cost_per_unit, 0.0) AS cost_per_unit,
                    (COALESCE(mp.qty_producing, mp.product_qty) * COALESCE(pp.list_price, 0.0)) AS actual_revenue,
                    ((COALESCE(mp.qty_producing, mp.product_qty) * COALESCE(pp.list_price, 0.0)) - COALESCE(mp.cost_total_batch, 0.0)) AS gross_profit,
                    CASE 
                        WHEN (COALESCE(mp.qty_producing, mp.product_qty) * COALESCE(pp.list_price, 0.0)) > 0 
                        THEN ROUND(((((COALESCE(mp.qty_producing, mp.product_qty) * COALESCE(pp.list_price, 0.0)) - COALESCE(mp.cost_total_batch, 0.0)) / (COALESCE(mp.qty_producing, mp.product_qty) * COALESCE(pp.list_price, 0.0))) * 100)::numeric, 1)
                        ELSE 0.0
                    END AS margin_pct
                FROM mrp_production mp
                JOIN product_product pp ON mp.product_id = pp.id
            )
        """ % self._table)
