# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Budget for Job Contracting and Construction Projects in odoo',
    'version': '13.0.0.3',
    'category': 'Budget',
    'author': 'Browseinfo',
    'website': 'https://www.browseinfo.in',
    'summary': 'Construction Projects budget for project job costing budget management budget integration with Construction budget contracting budget job costing with budget integration Construction material planning Construction budget planning for job costing accounting',
    'description': """
        Project Job Costing and Job Cost Sheet.job contract, job contracting, Construction job , contracting job , contract estimation cost estimation project estimation , 
        This modules helps to manage contracting,Job Costing and Job Cost Sheet inculding dynamic material request
        This modules helps to manage contracting,Job Costing and Job Cost Sheet inculding dynamic material request , budget estimation for construction project , project budget estimation 
		Construction Project budget estimation,  budget management Construction Project , budget estimate for contract
        Project Contracting , budget costing , budget estimation , project budget , contract budgeting , construction budget
        Project costing , cost calculation Job Contract , project estiamation 
        project cost sheet
            Send Estimation to your Customers for materials, labour, overheads details in job estimation.
        Estimation for Jobs - Material / Labour / Overheads
        Material Esitmation
        Job estimation
        labour estimation
        Overheads estimation
        BrowseInfo developed a new odoo/OpenERP module apps.
        This module use for Real Estate Management, Construction management, Building Construction,
        Material Line on JoB Estimation
        Labour Lines on Job Estimation.
        Overhead Lines on Job Estimation.
        create Quotation from the Job Estimation.
        overhead on job estimation
        Construction Projects
        Budgets
        Notes
        Materials
        Material Request For Job Orders
        Add Materials
        Job Orders
        Create Job Orders
        Job Order Related Notes
        Issues Related Project
        Vendors
        Vendors / Contractors

        Construction Management
        Construction Activity
        Construction Jobs
        Job Order Construction
        Job Orders Issues
        Job Order Notes
        Construction Notes
        Job Order Reports
        Construction Reports
        Job Order Note
        Construction app
        Project Report
        Task Report
        Construction Project - Project Manager
        real estate property
        propery management
        bill of material
        Material Planning On Job Order

        Bill of Quantity On Job Order
        Bill of Quantity construction
        Project job costing on manufacturing
    BrowseInfo developed a new odoo/OpenERP module apps.
    Material request is an instruction to procure a certain quantity of materials by purchase , internal transfer or manufacturing.So that goods are available when it require.
    Material request for purchase, internal transfer or manufacturing
    Material request for internal transfer
    Material request for purchase order
    Material request for purchase tender
    Material request for tender
    Material request for manufacturing order.
    product request, subassembly request, raw material request, order request
    product change request on constuction project
    Budget for Job Contracting and Construction Projects
    budget for constuction project
    budget for projects
    budhget for job costing
    budget for project job costing
    project job costing budget management
    constuction budget management
    constuction project budget management
    constuction project with budget management
    job costing with budget management
""",

    "price": 39,
    "currency": 'EUR',
    'live_test_url':'https://youtu.be/VDLbkD9E3qA',
    'depends': ['bi_odoo_job_costing_management','bi_material_purchase_requisitions','bi_account_budget'],
    'data': [
        'views/budget_view.xml',
    ],
    'installable': True,
    'auto_install': False,
    "images":['static/description/Banner.png'],
}
