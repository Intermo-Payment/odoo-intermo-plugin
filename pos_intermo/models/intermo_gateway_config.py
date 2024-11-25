from odoo import models, fields, api, _
import random
import string


class IntermoGatewayConfig(models.Model):
    _name = 'intermo.gateway.config'
    _description = 'Intermo Gateway Configuration'

    mode = fields.Selection([
        ('sandbox', 'Sandbox'),
        ('live', 'Production'),
    ], string='Mode', default='sandbox')

    language = fields.Selection([
        ('en', 'English'),
        ('fr', 'French'),
    ], string='Language', default='en')

    generated_secret_token = fields.Char(
        string='Plugin Key',
        readonly=True,
        copy=False
    )

    # Sandbox keys
    sandbox_authentication_key = fields.Char(string='Sandbox Authentication Key')
    sandbox_public_key = fields.Char(string='Sandbox Public Key')
    sandbox_secret = fields.Char(string='Sandbox Secret')

    # Production keys
    production_authentication_key = fields.Char(string='Production Authentication Key')
    production_public_key = fields.Char(string='Production Public Key')
    production_secret = fields.Char(string='Production Secret')

    is_payment_method_configured = fields.Boolean(
        string="Is Payment Method Active",
        compute="_compute_payment_method_status",
        store=False
    )

    @api.model
    def create(self, vals):
        existing = self.search([], limit=1)
        if existing:
            existing.write(vals)
            return existing
        else:
            if not vals.get('generated_secret_token'):
                vals['generated_secret_token'] = self.generate_secret_token()
            record = super(IntermoGatewayConfig, self).create(vals)
            record._configure_payment_method()
            return record

    def write(self, vals):
        res = super(IntermoGatewayConfig, self).write(vals)
        self._configure_payment_method()
        return res

    @api.model
    def default_get(self, fields_list):
        res = super(IntermoGatewayConfig, self).default_get(fields_list)
        existing = self.search([], limit=1)
        if existing:
            defaults = existing.read(fields_list)[0]
            res.update(defaults)
        else:
            res['generated_secret_token'] = self.generate_secret_token()
        return res

    @api.model
    def generate_secret_token(self):
        chars = string.ascii_letters + string.digits
        token = ''.join(random.choice(chars) for _ in range(12))
        return token

    @api.model
    def name_get(self):
        return [(record.id, "Intermo API Key Configuration") for record in self]

    def _configure_payment_method(self):
        payment_method = self.env['pos.payment.method'].search([('name', '=', 'Intermo Payment')], limit=1)
        if not payment_method:
            journal = self.env['account.journal'].search([('type', '=', 'bank')], limit=1)
            if not journal:
                journal = self.env['account.journal'].create({
                    'name': 'Default Bank',
                    'type': 'bank',
                    'code': 'BNK1',
                    'company_id': self.env.company.id,
                    'active': True,
                })
            self.env['pos.payment.method'].create({
                'name': 'Intermo Payment',
                'use_payment_terminal': 'intermo',
                'journal_id': journal.id,
                'is_cash_count': False,
            })

    @api.depends('sandbox_public_key', 'production_public_key')
    def _compute_payment_method_status(self):
        for record in self:
            payment_method = self.env['pos.payment.method'].search([('name', '=', 'Intermo Payment')], limit=1)
            record.is_payment_method_configured = bool(payment_method)
