# -*- coding: utf-8 -*-
# Part of CodeOriental Smart Factory OS. See LICENSE file for full copyright and licensing details.

{
    'name': 'Smart Factory Operating System | Turnkey Factory ERP & Shopfloor Hub',
    'version': '20.0.1.0.0',
    'category': 'Manufacturing/Manufacturing',
    'summary': 'Turnkey factory management without hiring an Odoo consultant: 1-Click Interactive Onboarding, Plant Command Center, Simplified Shopfloor Kiosk, 4-Pillar Batch Costing & Machine Downtime Log.',
    'description': """
Smart Factory Operating System (OS)
===================================
Transform standard Odoo into a complete, turnkey Manufacturing Operating System designed for factory owners, plant managers, and floor operators — without needing an Odoo consultant.

Key Features:
-------------
* **1-Click Interactive Factory Setup Wizard**: Select your industry (Food, Plastics, Metal, Textile, Chemicals, Furniture, Electronics, Job Shop) and automatically deploy pre-configured work centers, operational hourly rates, shift templates, and sample BOMs in 60 seconds.
* **Unified Plant Command Center (Dashboard)**: Real-time operational pulse displaying active batches, line availability (OEE), raw material shortages, output velocity, and daily manufacturing cost absorption.
* **Simplified Shopfloor Operator Mode**: Clean, touch-friendly interface designed for shopfloor tablets. Big buttons for batch execution, output logging, and defect reporting.
* **4-Pillar Live Batch Costing & Profitability Engine**: Instantly aggregates (1) Raw Materials, (2) Direct Labor, (3) Machinery & Energy, and (4) Factory Overhead. Calculates real unit cost, target minimum sale price, and gross profit margin % per batch.
* **Smart Material Requisitions & Shortage Prevention**: 1-click material requisition slips from BOM. Direct stock availability checking with 1-click Purchase RFQ generation for missing raw materials.
* **Machinery & Downtime Incident Tracking**: Real-time status cards (Running, Idle, Maintenance, Breakdown) with immediate operator breakdown alerts and automated downtime cost impact logs.
* **Shift Handover & Workforce Logs**: Daily output, achievement %, and scrap rate tracking with handover notes between incoming/outgoing supervisors.
* **Printable Factory Documents with Barcode**: Batch Job Traveler with Code128 barcode, Material Requisition Slips, and Batch Cost Sheets.

Compatibility:
--------------
* Odoo Community & Odoo Enterprise
* Odoo.sh & On-Premise deployments
    """,
    'author': 'CodeOriental',
    'website': 'https://codeoriental.com',
    'license': 'OPL-1',
    'price': 65.00,
    'currency': 'EUR',
    'depends': [
        'base',
        'mrp',
        'stock',
        'purchase',
        'hr',
        'mail',
    ],
    'data': [
        # Security
        'security/factory_security.xml',
        'security/ir.model.access.csv',
        # Data
        'data/factory_sequence.xml',
        'data/factory_industry_templates_data.xml',
        # Wizards
        'wizard/factory_onboarding_wizard_views.xml',
        'wizard/factory_quick_run_wizard_views.xml',
        'wizard/factory_downtime_wizard_views.xml',
        # Views
        'views/factory_dashboard_views.xml',
        'views/factory_production_views.xml',
        'views/factory_machine_views.xml',
        'views/factory_shift_views.xml',
        'views/factory_material_requisition_views.xml',
        'views/factory_cost_analysis_views.xml',
        'views/factory_industry_template_views.xml',
        'views/factory_menus.xml',
        # Reports
        'report/factory_reports.xml',
        'report/report_batch_traveler.xml',
        'report/report_material_requisition.xml',
        'report/report_cost_analysis.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'smart_factory_os/static/src/scss/factory_theme.scss',
        ],
    },
    'images': [
        'static/description/banner.png',
        'static/description/icon.png',
        'static/description/screenshot_dashboard.png',
        'static/description/screenshot_wizard.png',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
