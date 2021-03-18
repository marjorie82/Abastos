from odoo import fields, models, _


class KsResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    ks_forecast_method = fields.Selection([
        ('ar', 'Autoregression (AR)'),
        ('ma', 'Moving Average (MA)'),
        ('arma', 'Autoregressive Moving Average (ARMA)'),
        ('arima', 'Autoregressive Integrated Moving Average (ARIMA)'),
        # ('sarima', 'Seasonal Autoregressive Integrated Moving-Average (SARIMA)'),
        # ('sarimax', 'Seasonal Autoregressive Integrated Moving-Average with Exogenous Regressors (SARIMAX)'),
        # ('var', 'Vector Autoregression (VAR)'),
        # ('varma', 'Vector Autoregression Moving-Average (VARMA)'),
        # ('varmax', 'Vector Autoregression Moving-Average with Exogenous Regressors (VARMAX)'),
        # ('ses', 'Simple Exponential Smoothing (SES)'),
        # ('hwes', 'Holt Winter’s Exponential Smoothing (HWES)')
    ])

    def get_values(self):
        ks_res = super(KsResConfigSettings, self).get_values()
        ks_res.update(
            ks_forecast_method=self.env['ir.config_parameter'].sudo().get_param('ks_forecast_method'),
        )
        return ks_res

    def set_values(self):
        super(KsResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].sudo().set_param('ks_forecast_method', self.ks_forecast_method)
