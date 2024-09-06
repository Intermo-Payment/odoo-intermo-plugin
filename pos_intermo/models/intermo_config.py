from odoo import models, fields, api

class IntermoConfig(models.Model):
    _name = 'intermo.config'
    _description = 'Intermo Configuration'

    auth_key = fields.Char(string="Auth Key", required=True)
    secret_key = fields.Char(string="Secret Key", required=True)
    public_key = fields.Char(string="Public Key", required=True)

    def set_values(self):
        self.ensure_one()
        self.env['ir.config_parameter'].sudo().set_param('intermo.auth_key', self.auth_key)
        self.env['ir.config_parameter'].sudo().set_param('intermo.secret_key', self.secret_key)
        self.env['ir.config_parameter'].sudo().set_param('intermo.public_key', self.public_key)

    @api.model
    def create(self, vals):
        record = super(IntermoConfig, self).create(vals)
        record.set_values()
        return record

    def write(self, vals):
        res = super(IntermoConfig, self).write(vals)
        self.set_values()
        return res

    @api.model
    def load_values(self):
        return {
            'auth_key': self.env['ir.config_parameter'].sudo().get_param('intermo.auth_key', default=''),
            'secret_key': self.env['ir.config_parameter'].sudo().get_param('intermo.secret_key', default=''),
            'public_key': self.env['ir.config_parameter'].sudo().get_param('intermo.public_key', default=''),
        }

    @api.model
    def default_get(self, fields_list):
        res = super(IntermoConfig, self).default_get(fields_list)
        res.update(self.load_values())
        return res

    def name_get(self):
        """Override the name_get method to display a custom name"""
        result = []
        for record in self:
            name = "Intermo Payment Gateway Configuration"
            result.append((record.id, name))
        return result




# from odoo import models, fields, api

# class IntermoConfig(models.TransientModel):
#     _name = 'intermo.config'
#     _description = 'Intermo Configuration'

#     auth_key = fields.Char(string="Auth Key", required=True)
#     secret_key = fields.Char(string="Secret Key", required=True)
#     public_key = fields.Char(string="Public Key", required=True)

#     def set_values(self):
#         self.env['ir.config_parameter'].sudo().set_param('intermo.auth_key', self.auth_key)
#         self.env['ir.config_parameter'].sudo().set_param('intermo.secret_key', self.secret_key)
#         self.env['ir.config_parameter'].sudo().set_param('intermo.public_key', self.public_key)

#     @api.model
#     def get_values(self):
#         return {
#             'auth_key': self.env['ir.config_parameter'].sudo().get_param('intermo.auth_key'),
#             'secret_key': self.env['ir.config_parameter'].sudo().get_param('intermo.secret_key'),
#             'public_key': self.env['ir.config_parameter'].sudo().get_param('intermo.public_key'),
#         }


# from odoo import models, fields, api

# class IntermoConfigSettings(models.TransientModel):
#     _inherit = 'res.config.settings'

#     auth_key = fields.Char(string="Auth Key", default=lambda self: self._get_default_value('intermo.auth_key'))
#     secret_key = fields.Char(string="Secret Key", default=lambda self: self._get_default_value('intermo.secret_key'))
#     public_key = fields.Char(string="Public Key", default=lambda self: self._get_default_value('intermo.public_key'))

#     def set_values(self):
#         super(IntermoConfigSettings, self).set_values()
#         self.env['ir.config_parameter'].sudo().set_param('intermo.auth_key', self.auth_key)
#         self.env['ir.config_parameter'].sudo().set_param('intermo.secret_key', self.secret_key)
#         self.env['ir.config_parameter'].sudo().set_param('intermo.public_key', self.public_key)

#     @api.model
#     def _get_default_value(self, param_name):
#         return self.env['ir.config_parameter'].sudo().get_param(param_name)
