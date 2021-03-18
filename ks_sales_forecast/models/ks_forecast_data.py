import base64
import json
import os
from datetime import datetime

import babel
import numpy as np
import pandas as pd
import pytz
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError, UserError
from odoo.tools import config
from statsmodels.tsa.ar_model import AutoReg
from statsmodels.tsa.arima_model import ARIMA
from statsmodels.tsa.arima_model import ARMA


class KsSalesForecast(models.Model):
    _name = 'ks.sales.forecast'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'ks_name'
    _order = 'id desc'
    _description = 'This model is to predict sales on the bases of historical data with trending and seasonal factor'

    ks_name = fields.Char('Name', tracking=True, default=lambda self: _('New'), readonly=True)
    ks_is_file = fields.Boolean(default=False, tracking=True)
    ks_file_type = fields.Selection([('csv', 'CSV'), ('xlx', 'Excel')], string=_('File Type'), default='csv',
                                    tracking=True)
    ks_import_file = fields.Binary(string=_('File'), tracking=True)
    ks_file_name = fields.Char(string=_('File Name'), tracking=True)
    ks_is_method_change = fields.Boolean(default=False, tracking=True)
    ks_forecast_method = fields.Selection([
        ('ar', 'Autoregression (AR)'),
        ('ma', 'Moving Average (MA)'),
        ('arma', 'Autoregressive Moving Average (ARMA)'),
        ('arima', 'Autoregressive Integrated Moving Average (ARIMA)'),
    ], tracking=True)
    ks_default_forecast_method = fields.Char(compute='ks_default_forecast_method_value', store=True)
    ks_model = fields.Many2one('ir.model', 'Model', default=lambda self: self.env.ref("sale.model_sale_order"),
                               readonly=True, invisible=True, tracking=True)
    ks_start_date = fields.Datetime(string=_('Start Date'), required=True, tracking=True)
    ks_end_date = fields.Datetime(string=_('End Date'), required=True, tracking=True)
    ks_forecast_base = fields.Selection([('all', 'All Products'), ('product', 'Specific Products')],
                                        string=_('Forecast Base'), default='product', tracking=True)
    ks_product_ids = fields.Many2many('product.product', invisible=True, tracking=True)
    ks_p = fields.Integer(string=_('P Coefficient (Auto Regressive)'))
    ks_d = fields.Integer(string=_('D Coefficient (Integrated)'))
    ks_q = fields.Integer(string=_('Q Coefficient (Moving Average)'))
    ks_forecast_unit = fields.Integer(string=_('Forecast Unit'), tracking=True, required=True, default=1)
    ks_forecast_period = fields.Selection([('day', 'Day'), ('month', 'Month'), ('year', 'Year')],
                                          string=_('Forecast Period'), default='month', tracking=True, required=True)
    ks_is_predicted = fields.Boolean()
    ks_chart_data = fields.Text(default=0)
    ks_graph_view = fields.Integer(default=1)

    @api.depends('ks_forecast_unit')
    @api.onchange('ks_forecast_unit')
    def ks_forecast_unit_method(self):
        if self.ks_forecast_unit < 1:
            raise ValidationError(_('Please Enter a positive non-zero number.'))

    @api.model
    def create(self, values):
        if 'ks_name' not in values or values['ks_name'] == _('New'):
            values['ks_name'] = self.env['ir.sequence'].next_by_code('ks.sales.forecast') or _('New')

        if not values.get('ks_is_method_change'):
            values.update(
                {'ks_default_forecast_method': self.env['ir.config_parameter'].sudo().get_param('ks_forecast_method')})
        elif values.get('ks_forecast_method'):
            values.update({'ks_default_forecast_method': values.get('ks_forecast_method')})
        return super(KsSalesForecast, self).create(values)

    def write(self, values):
        if values.get('ks_forecast_method'):
            values.update({'ks_default_forecast_method': values.get('ks_forecast_method')})
        return super(KsSalesForecast, self).write(values)

    @api.onchange('ks_start_date', 'ks_end_date')
    def ks_onchange_dates(self):
        if self.ks_start_date and self.ks_end_date:
            if not self.ks_start_date < self.ks_end_date:
                raise ValidationError('Start Date should be less then End Date')

    @api.onchange('ks_forecast_method', 'ks_is_method_change')
    def ks_default_forecast_method_value(self):
        for rec in self:
            if not rec.ks_is_method_change:
                rec.ks_default_forecast_method = self.env['ir.config_parameter'].sudo().get_param('ks_forecast_method')
            elif rec.ks_forecast_method:
                rec.ks_default_forecast_method = rec.ks_forecast_method

    def ks_predict_sales(self):
        vals = []
        if self.ks_is_file:
            temp_path = os.path.join(config.get('data_dir'), "temp")
            if not os.path.exists(temp_path):
                os.makedirs(temp_path)

            file_name = self.ks_file_name
            file_path = temp_path + '/' + file_name
            temp_file = open(file_path, 'wb')
            temp_file.write(base64.b64decode(self.ks_import_file))
            temp_file.close()

            previous_data = pd.read_csv(temp_file.name, index_col=['Date', 'Sales'])
            product_groups = previous_data.groupby(previous_data.Product).groups
            products = product_groups.keys()
            for product in products:
                sales_list = []
                product_id = self.env['product.product'].search([('name', '=', product)], limit=1)
                file_datas = product_groups[product].values
                for file_data in file_datas:
                    sales_list.append(float(file_data[1]))
                    sale_data = {
                        'ks_forecast_id': self.id,
                        'ks_date': datetime.strptime(file_data[0], tools.DEFAULT_SERVER_DATE_FORMAT),
                        'ks_value': float(file_data[1]),
                        'ks_product_id': product_id.id
                    }
                    vals.append(sale_data)
                sales_data = pd.read_csv(temp_file.name, index_col='Date', usecols=['Sales', 'Date'])
                forecast_method = self.env['ir.config_parameter'].sudo().get_param('ks_forecast_method')
                if self.ks_is_method_change:
                    forecast_method = self.ks_forecast_method
                data_frame = pd.DataFrame(sales_list)
                if forecast_method:
                    forecast_method_name = 'ks_%s_method' % forecast_method
                    if hasattr(self, forecast_method_name):
                        method = getattr(self, forecast_method_name)
                        results = method(product_groups[product])
                    # print(results)
                    for value, month in zip(results, results.index):
                        ks_date = datetime.strftime(month, tools.DEFAULT_SERVER_DATE_FORMAT)
                        forecast_data = {
                            'ks_forecast_id': self.id,
                            'ks_date': datetime.strptime(ks_date, tools.DEFAULT_SERVER_DATE_FORMAT),
                            'ks_value': value,
                            'ks_product_id': product_id.id
                        }
                        vals.append(forecast_data)
            self.env['ks.sales.forecast.result'].create(vals)
            # print(sales_data)
        else:
            end_date = self.ks_end_date
            query = """
                select
                    date_trunc(%(unit)s, so.date_order) as date,
                    sum(sol.price_subtotal),
                    sol.product_id
                from sale_order_line as sol
                    inner join sale_order as so
                        on sol.order_id = so.id
                where
                    date_order >= %(start_date)s and date_order <= %(end_date)s and sol.product_id in %(product_condition)s
                    group by date, sol.product_id
                    order by date
            """
            product_condition = tuple(self.env['product.product'].search([]).ids)
            if self.ks_forecast_base == 'product':
                product_condition = tuple(self.ks_product_ids.ids)

            if self.ks_forecast_period == 'month':
                if end_date.day > 15:
                    end_date = end_date + relativedelta(day=31)
                else:
                    end_date = end_date + relativedelta(day=1)

            self.env.cr.execute(query, {
                'unit': self.ks_forecast_period,
                'start_date': self.ks_start_date,
                'end_date': end_date,
                'product_condition': product_condition
            })
            result = self.env.cr.fetchall()
            # print(result)
            if len(result) == 0:
                raise UserError(_("Sales data is not available for these products"))
            data_dict = {}
            for data in result:
                keys = data_dict.keys()
                sale_data = {
                    'ks_forecast_id': self.id,
                    'ks_date': data[0],
                    'ks_value': float(data[1]),
                    'ks_product_id': data[2]
                }
                vals.append(sale_data)
                if data[2] in keys:
                    data_dict[data[2]]['date'].append(data[0])
                    data_dict[data[2]]['sales'].append(data[1])
                    data_dict[data[2]]['forecast_sales'].append(0.0)
                else:
                    data_dict[data[2]] = {'date': [], 'sales': [], 'forecast_sales': []}
                    data_dict[data[2]]['date'].append(data[0])
                    data_dict[data[2]]['sales'].append(data[1])
                    data_dict[data[2]]['forecast_sales'].append(0.0)

            product_keys = data_dict.keys()
            for product in product_keys:
                product_id = self.env['product.product'].browse(product)
                product_sales_data = data_dict[product]
                sales_list = product_sales_data.get('sales')
                forecast_method = self.env['ir.config_parameter'].sudo().get_param('ks_forecast_method')
                if self.ks_is_method_change:
                    forecast_method = self.ks_forecast_method
                data_frame = np.array(sales_list)
                if forecast_method and len(data_frame) > 8:
                    results = 0
                    try:
                        forecast_method_name = 'ks_%s_method' % forecast_method
                        if hasattr(self, forecast_method_name):
                            p = self.ks_p
                            q = self.ks_q
                            d = self.ks_d
                            method = getattr(self, forecast_method_name)
                            results = method(data_frame, p, q, d)
                    except Exception as e:
                        return self.env['ks.message.wizard'].ks_pop_up_message(names='Error', message=e)
                    for (i, value) in zip(range(0, len(results)), results):
                        i = i + 1
                        if self.ks_forecast_period == 'day':
                            ks_date = end_date + relativedelta(days=i)
                        elif self.ks_forecast_period == 'month':
                            ks_date = end_date + relativedelta(months=i)
                        else:
                            ks_date = end_date + relativedelta(years=i)
                        forecast_data = {
                            'ks_forecast_id': self.id,
                            'ks_date': ks_date,
                            'ks_value': value,
                            'ks_product_id': product_id.id
                        }
                        data_dict[product_id.id]['date'].append(ks_date)
                        data_dict[product_id.id]['sales'].append(0.0)
                        data_dict[product_id.id]['forecast_sales'].append(value)
                        vals.append(forecast_data)

                elif not len(data_frame) > 8:
                    raise UserError(
                        _('You do not have sufficient data for "%s" product. We need minimum 9 "%ss" data') % (
                            product_id.name, self.ks_forecast_period))
                else:
                    raise UserError(_('Please select a forecast method'))
            keys = data_dict.keys()
            final_dict = {}
            dict_data = {}
            if keys:
                dates = []
                for product in keys:
                    dates.extend(data_dict[product]['date'])
                dates = list(set(dates))
                dates.sort()
                labels = [self.format_label(values) for values in dates]
                final_dict.update({
                    'labels': labels,
                    'datasets': []
                })
                product_keys = data_dict.keys()
                for product in product_keys:
                    dict_data[product] = {
                        'sales': {},
                        'forecast_sales': {},
                    }
                    for final_date in dates:
                        if final_date in data_dict[product]['date']:
                            data_index = data_dict[product]['date'].index(final_date)
                            dict_data[product]['sales'][final_date] = data_dict[product]['sales'][data_index]
                            dict_data[product]['forecast_sales'][final_date] = data_dict[product]['forecast_sales'][
                                data_index]
                        else:
                            dict_data[product]['sales'][final_date] = 0.0
                            dict_data[product]['forecast_sales'][final_date] = 0.0
            if dict_data:
                product_keys = data_dict.keys()
                for product in product_keys:
                    product_id = self.env['product.product'].browse(product)
                    product_name = product_id.code + ' ' + product_id.name if product_id.code else product_id.name
                    final_dict['datasets'] = final_dict['datasets'] + [{
                        'data': list(dict_data[product]['sales'].values()),
                        'label': product_name + '/Previous',
                    }, {
                        'data': list(dict_data[product]['forecast_sales'].values()),
                        'label': product_name + '/Forecast'
                    }]
                self.ks_chart_data = json.dumps(final_dict)
            forecast_result = self.env['ks.sales.forecast.result']
            forecast_records = forecast_result.search([('ks_forecast_id', '=', self.id)])
            if forecast_records.ids:
                for forecast_record in forecast_records:
                    forecast_record.unlink()
                forecast_result.create(vals)
            else:
                forecast_result.create(vals)
            self.ks_is_predicted = True

    @api.model
    def format_label(self, value, ftype='datetime', display_format='MMMM yyyy'):
        if self.ks_forecast_period == 'day':
            display_format = 'dd MMMM yyyy'
        elif self.ks_forecast_period == 'year':
            display_format = 'yyyy'
        tz_convert = self._context.get('tz')
        locale = self._context.get('lang') or 'en_US'
        tzinfo = None
        if ftype == 'datetime':
            if tz_convert:
                value = pytz.timezone(self._context['tz']).localize(value)
                tzinfo = value.tzinfo
            return babel.dates.format_datetime(value, format=display_format, tzinfo=tzinfo, locale=locale)
        else:
            if tz_convert:
                value = pytz.timezone(self._context['tz']).localize(value)
                tzinfo = value.tzinfo
            return babel.dates.format_date(value, format=display_format, locale=locale)

    def ks_ar_method(self, data_frame, p=False, d=False, q=False):
        ks_ar_model = AutoReg(data_frame, lags=1)
        ks_fit_model = ks_ar_model.fit()
        forecast_period = self.ks_forecast_unit - 1
        forecast_value = ks_fit_model.predict(len(data_frame), len(data_frame) + forecast_period)
        return forecast_value

    def ks_ma_method(self, data_frame, p=False, d=False, q=False):
        ks_ma_model = ARMA(data_frame, order=(0, q))
        ks_fit_model = ks_ma_model.fit(disp=False)
        forecast_period = self.ks_forecast_unit - 1
        forecast_value = ks_fit_model.predict(len(data_frame), len(data_frame) + forecast_period)
        return forecast_value

    def ks_arma_method(self, data_frame, p=False, d=False, q=False):
        ks_arma_model = ARMA(data_frame, order=(p, q))
        ks_fit_model = ks_arma_model.fit(disp=False)
        forecast_period = self.ks_forecast_unit - 1
        forecast_value = ks_fit_model.predict(len(data_frame), len(data_frame) + forecast_period)
        return forecast_value

    def ks_arima_method(self, data_frame, p=False, d=False, q=False):
        ks_arima_model = ARIMA(data_frame, order=(p, d, q))
        ks_fit_model = ks_arima_model.fit(disp=False)
        forecast_period = self.ks_forecast_unit - 1
        forecast_value = ks_fit_model.predict(len(data_frame), len(data_frame) + forecast_period)
        return forecast_value

    def ks_auto_arima_method(self, data_frame, p=False, d=False, q=False):
        ks_arima_model = ARMA(data_frame, order=(2, 1))
        ks_fit_model = ks_arima_model.fit(disp=False)
        forecast_period = self.ks_forecast_unit - 1
        forecast_value = ks_fit_model.predict(len(data_frame), len(data_frame) + forecast_period)
        return forecast_value
