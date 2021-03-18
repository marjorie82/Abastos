# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.
##############################################################################

from odoo import api, fields, models, _
from datetime import datetime, date

class CrossoveredBudgetLine(models.Model):
    _inherit = 'crossovered.budget.lines'
    _rec_name = 'crossovered_budget_id'
    
    def get_currency_id(self):
        user_id = self.env.uid
        res_user_id = self.env['res.users'].browse(user_id)
        for line in self:
            line.currency_id = res_user_id.company_id.currency_id
    
    def _compute_invoice_quantity(self):
        for invoice in self:
            invoice_line_ids = self.env['account.move.line'].search([('product_id','=',invoice.product_id.id),('analytic_account_id','=',invoice.analytic_account_id.id)])
            if invoice_line_ids:
                for qty in invoice_line_ids:
                    invoice.actual_invoice_qty += qty.quantity
            else:
                invoice.actual_invoice_qty = 0.0
            
    def _compute_vendor_bill_quantity(self):
        for material in self:
            invoice_line_ids = self.env['account.move.line'].search([('product_id','=',material.product_id.id),('analytic_account_id','=',material.analytic_account_id.id)])
            if invoice_line_ids:
                for qty in invoice_line_ids:
                    if qty.purchase_line_id:
                        material.actual_vendor_bill_qty += qty.quantity
                    else:
                        material.actual_vendor_bill_qty = 0.0
            else:
                material.actual_vendor_bill_qty = 0.0
                
    def _compute_purchase_quantity(self):
        for material in self:
            purchase_order_line_ids = self.env['purchase.order.line'].search([('product_id','=',material.product_id.id),('account_analytic_id','=',material.analytic_account_id.id)])
            if purchase_order_line_ids:
                for qty in purchase_order_line_ids:
                    material.actual_purchase_qty += qty.product_qty
            else:
                material.actual_purchase_qty = 0.0

    @api.model
    def create(self,vals):
        result = super(CrossoveredBudgetLine, self).create(vals)        
        material_list = []
        jobcostsheet_obj = self.env['job.cost.sheet'].search([('id','=',vals.get('job_cost_sheet_id'))])
        product_obj = self.env['product.product'].search([('id','=',vals.get('product_id'))])
        crossovered_budget = self.env['crossovered.budget'].search([('id','=',vals.get('crossovered_budget_id'))])
        
        if vals.get('cost_type') == 'material':
            material_list.append((0,0,{
            'date' : datetime.now(),
            'job_type_id' : vals.get('job_type'),
            'product_id' : vals.get('product_id'),
            'unit_price' : product_obj.lst_price,
            'description' : vals.get('description'),
            'quantity' : vals.get('material_qty'),
            'actual_purchase_qty' : vals.get('actual_purchase_qty'),
            'actual_invoice_qty' : vals.get('actual_invoice_qty'),
            'uom_id' : vals.get('uom_id'),
            'currency_id' : vals.get('currency_id'),
            }))
            vals = {
                'create_date' : crossovered_budget.date_from,
                'close_date' : crossovered_budget.date_to,
                'budget_id' : vals.get('crossovered_budget_id'),
                'analytic_ids' : vals.get('analytic_account_id'),
                'create_by_id' : crossovered_budget.creating_user_id.id,
                'company_id' : crossovered_budget.company_id.id,
                'material_job_cost_line_ids' : material_list,
            }
        elif vals.get('cost_type') == 'labour':
            material_list.append((0,0,{
            'date' : datetime.now(),
            'job_type_id' : vals.get('job_type'),
            'product_id' : vals.get('product_id'),
            'unit_price' : product_obj.lst_price,
            'description' : vals.get('description'),
            'hours' : vals.get('lobour_hours'),
            'actual_purchase_qty' : vals.get('actual_purchase_qty'),
            'actual_invoice_qty' : vals.get('actual_invoice_qty'),
            'uom_id' : vals.get('uom_id'),
            'currency_id' : vals.get('currency_id'),
            }))
            vals = {
                'create_date' : crossovered_budget.date_from,
                'close_date' : crossovered_budget.date_to,
                'budget_id' : vals.get('crossovered_budget_id'),
                'analytic_ids' : vals.get('analytic_account_id'),
                'create_by_id' : crossovered_budget.creating_user_id.id,
                'company_id' : crossovered_budget.company_id.id,
                'labour_job_cost_line_ids' : material_list,
            }
        else:
            material_list.append((0,0,{
            'date' : datetime.now(),
            'job_type_id' : vals.get('job_type'),
            'product_id' : vals.get('product_id'),
            'unit_price' : product_obj.lst_price,
            'description' : vals.get('description'),
            'quantity' : vals.get('overhead_qty'),
            'actual_purchase_qty' : vals.get('actual_purchase_qty'),
            'actual_invoice_qty' : vals.get('actual_invoice_qty'),
            'uom_id' : vals.get('uom_id'),
            'currency_id' : vals.get('currency_id'),
            }))
            vals = {
                'create_date' : crossovered_budget.date_from,
                'close_date' : crossovered_budget.date_to,
                'budget_id' : vals.get('crossovered_budget_id'),
                'analytic_ids' : vals.get('analytic_account_id'),
                'create_by_id' : crossovered_budget.creating_user_id.id,
                'company_id' : crossovered_budget.company_id.id,
                'overhead_job_cost_line_ids' : material_list,
            }
        
        job_cost_id = jobcostsheet_obj.write(vals)  
        return result

    def write(self, vals):
        res = super(CrossoveredBudgetLine, self).write(vals)
        material_list = []
        jobcostsheet_obj = self.env['job.cost.sheet'].search([('id','=',self.job_cost_sheet_id.id)])
        product_obj = self.env['product.product'].search([('id','=',self.product_id.id)])
        crossovered_budget = self.env['crossovered.budget'].search([('id','=',self.crossovered_budget_id.id)])
        
        for line in self:
            if line.cost_type == 'material':
                material_list.append((0,0,{
                'date' : datetime.now(),
                'job_type_id' : line.job_type.id,
                'product_id' : line.product_id.id,
                'unit_price' : product_obj.lst_price,
                'description' : line.description,
                'quantity' : line.material_qty,
                'actual_purchase_qty' : line.actual_purchase_qty,
                'actual_invoice_qty' : line.actual_invoice_qty,
                'uom_id' : line.uom_id.id,
                'currency_id' : line.currency_id.id,
                }))
                vals = {
                    'create_date' : crossovered_budget.date_from,
                    'close_date' : crossovered_budget.date_to,
                    'budget_id' : line.crossovered_budget_id.id,
                    'analytic_ids' : line.analytic_account_id.id,
                    'create_by_id' : crossovered_budget.creating_user_id.id,
                    'company_id' : crossovered_budget.company_id.id,
                    'material_job_cost_line_ids' : material_list,
                }
            elif vals.get('cost_type') == 'labour':
                material_list.append((0,0,{
                'date' : datetime.now(),
                'job_type_id' : line.job_type.id,
                'product_id' : line.product_id.id,
                'unit_price' : product_obj.lst_price,
                'description' : line.description,
                'hours' : line.lobour_hours,
                'actual_purchase_qty' : line.actual_purchase_qty,
                'actual_invoice_qty' : line.actual_invoice_qty,
                'uom_id' : line.uom_id.id,
                'currency_id' : line.currency_id.id,
                }))
                vals = {
                    'create_date' : crossovered_budget.date_from,
                    'close_date' : crossovered_budget.date_to,
                    'budget_id' : line.crossovered_budget_id.id,
                    'analytic_ids' : line.analytic_account_id.id,
                    'create_by_id' : crossovered_budget.creating_user_id.id,
                    'company_id' : crossovered_budget.company_id.id,
                    'labour_job_cost_line_ids' : material_list,
                }
            else:
                material_list.append((0,0,{
                'date' : datetime.now(),
                'job_type_id' : line.job_type.id,
                'product_id' : line.product_id.id,
                'unit_price' : product_obj.lst_price,
                'description' : line.description,
                'quantity' : line.overhead_qty,
                'actual_purchase_qty' : line.actual_purchase_qty,
                'actual_invoice_qty' : line.actual_invoice_qty,
                'uom_id' : line.uom_id.id,
                'currency_id' : line.currency_id.id,
                }))
                vals = {
                    'create_date' : crossovered_budget.date_from,
                    'close_date' : crossovered_budget.date_to,
                    'budget_id' : line.crossovered_budget_id.id,
                    'analytic_ids' : line.analytic_account_id.id,
                    'create_by_id' : crossovered_budget.creating_user_id.id,
                    'company_id' : crossovered_budget.company_id.id,
                    'overhead_job_cost_line_ids' : material_list,
                }
            job_cost_id = jobcostsheet_obj.write(vals)
        return res


    job_cost_sheet_id = fields.Many2one('job.cost.sheet',string="Cost Sheet")
    cost_type = fields.Selection([('material','Material'),('labour','Labour'),('overhead','Overhead')],"Cost Type")
    job_type = fields.Many2one('job.type',string='Job Type')
    job_cost_line_id = fields.Many2one('job.cost.line',string='Job Cost Line')
    product_id = fields.Many2one("product.product", string="Product")
    uom_id = fields.Many2one('uom.uom','Unit Of Measure')
    description = fields.Char(string='Description')
    actual_purchase_qty = fields.Float(compute='_compute_purchase_quantity',string='Actual Purchased Quantity',default=0.0,store=True)
    actual_invoice_qty = fields.Float(compute='_compute_invoice_quantity',string='Actual Invoice Quantity',default=0.0,store=True)
    lobour_hours = fields.Float('Actual Labour Hours',default=0.0)
    material_qty = fields.Float('Material Planned Qty',default=0.0)
    overhead_qty = fields.Float('Overhead Planned Qty',default=0.0)
    actual_vendor_bill_qty = fields.Float(compute='_compute_vendor_bill_quantity',string='Actual Vendor Bill Quantity',default=0.0,store=True)
    currency_id = fields.Many2one("res.currency", compute='get_currency_id', string="Currency")
    
class CrossoveredBudget(models.Model):
    _inherit = 'crossovered.budget'
    
    def action_view_cost_sheet(self):
        self.ensure_one()
        return {
            'name': 'Cost Sheet',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'job.cost.sheet',
            'domain': [('budget_id', '=', self.id)],
        }

    def action_view_cost_sheet_line(self):
        self.ensure_one()
        return {
            'name': 'Cost Sheet Lines',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'crossovered.budget.lines',
            'domain': [('crossovered_budget_id', '=', self.id)],
        }
        
    job_cost_sheet_id = fields.Many2one('job.cost.sheet',string="Cost Sheet")
    cost_type = fields.Selection([('material','Material'),('labour','Labour'),('overhead','Overhead')],"Cost Type")
    job_type = fields.Many2one('job.type',string='Job Type')
    cost_sheet_count = fields.Integer(string="Count", copy=False)
        
class JobCostSheet(models.Model):
    _inherit = 'job.cost.sheet'
    
    budget_id = fields.Many2one('crossovered.budget',string="Project Budget")


