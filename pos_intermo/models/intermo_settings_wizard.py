# from odoo import models, fields, api

# class IntermoSettingsWizard(models.TransientModel):
#     _name = 'intermo.settings.wizard'
#     _description = 'Intermo Settings Wizard'

#     # Fields that mirror those in IntermoSettings
#     sandbox_api_key = fields.Char(string="Sandbox API Key", required=True)
#     sandbox_secret_key = fields.Char(string="Sandbox Secret Key", required=True)
#     sandbox_auth_key = fields.Char(string="Sandbox Auth Token", required=True)

#     live_api_key = fields.Char(string="Live API Key", required=True)
#     live_secret_key = fields.Char(string="Live Secret Key", required=True)
#     live_auth_key = fields.Char(string="Live Auth Token", required=True)

#     environment = fields.Selection([
#         ('sandbox', 'Sandbox'),
#         ('production', 'Production'),
#     ], string="Environment", required=True)

#     language = fields.Selection([
#         ('en', 'English'),
#         ('fr', 'French')
#     ], string="Language", required=True)

#     @api.model
#     def default_get(self, fields):
#         """Load values from IntermoSettings singleton."""
#         res = super(IntermoSettingsWizard, self).default_get(fields)
#         settings = self.env['intermo.settings'].get_or_create_singleton()
#         for field in fields:
#             if hasattr(settings, field):
#                 res[field] = getattr(settings, field)
#         return res

#     def save_settings(self):
#         """Save changes from the wizard back to IntermoSettings."""
#         settings = self.env['intermo.settings'].get_or_create_singleton()
#         for field in self._fields:
#             if hasattr(settings, field):
#                 setattr(settings, field, self[field])
#         settings.invalidate_cache()
