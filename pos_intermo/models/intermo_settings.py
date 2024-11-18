# from odoo import models, fields, api
# from odoo.exceptions import ValidationError
# import random

# class IntermoSettings(models.Model):
#     _name = 'intermo.settings'
#     _description = 'Intermo API Settings'
#     _rec_name = 'display_name'

#     name = fields.Char(default='Intermo Settings', readonly=True)
#     display_name = fields.Char(string='Display Name', compute='_compute_display_name', store=False)

#     # Fields for Sandbox and Production keys
#     sandbox_api_key = fields.Char(string="Sandbox API Key", required=True)
#     sandbox_secret_key = fields.Char(string="Sandbox Secret Key", required=True)
#     sandbox_auth_key = fields.Char(string="Sandbox Auth Token", required=True)

#     live_api_key = fields.Char(string="Live API Key", required=True)
#     live_secret_key = fields.Char(string="Live Secret Key", required=True)
#     live_auth_key = fields.Char(string="Live Auth Token", required=True)

#     # Auto-generated plugin key
#     plugin_key = fields.Char(
#         string="Plugin Key",
#         readonly=True,
#         default=lambda self: self._generate_plugin_key()
#     )

#     # Environment selection
#     environment = fields.Selection([
#         ('sandbox', 'Sandbox'),
#         ('production', 'Production'),
#     ], string="Environment", default='sandbox', required=True)

#     # Language selection
#     language = fields.Selection([
#         ('en', 'English'),
#         ('fr', 'French')
#     ], string="Language", default='en', required=True)

#     _sql_constraints = [
#         ('singleton_unique', 'unique(name)', 'Only one Intermo Settings record is allowed.')
#     ]

#     @api.model
#     def _generate_plugin_key(self):
#         """Generate a random 18-digit plugin key."""
#         return str(random.randint(10**17, (10**18)-1))

#     @api.depends()
#     def _compute_display_name(self):
#         for record in self:
#             record.display_name = "Intermo Settings"

#     @api.model
#     def get_or_create_singleton(self):
#         """Retrieve the singleton record, creating it if necessary."""
#         settings = self.search([], limit=1)
#         if settings:
#             return settings
#         else:
#             settings = super(IntermoSettings, self).create({
#             'name': 'Intermo Settings',
#             'environment': 'sandbox',
#             'language': 'en',
#             'sandbox_api_key': 'default_sandbox_api_key',
#             'sandbox_secret_key': 'default_sandbox_secret_key',
#             'sandbox_auth_key': 'default_sandbox_auth_key',
#             'live_api_key': 'default_live_api_key',
#             'live_secret_key': 'default_live_secret_key',
#             'live_auth_key': 'default_live_auth_key',
#             })
#         return settings

#     def get_active_keys(self):
#         """Return the API keys based on the current environment."""
#         if self.environment == 'sandbox':
#             return {
#                 'api_key': self.sandbox_api_key,
#                 'secret_key': self.sandbox_secret_key,
#                 'auth_key': self.sandbox_auth_key,
#                 'plugin_key': self.plugin_key,
#             }
#         elif self.environment == 'production':
#             return {
#                 'api_key': self.live_api_key,
#                 'secret_key': self.live_secret_key,
#                 'auth_key': self.live_auth_key,
#                 'plugin_key': self.plugin_key,
#             }
#         else:
#             raise ValidationError("Invalid environment selected.")
