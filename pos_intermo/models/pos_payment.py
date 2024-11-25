from odoo import api, models, fields



class PosPayment(models.Model):

    _inherit = "pos.payment"

    intermo_public_key = fields.Char('Intermo Public Key')
    intermo_plugin_key = fields.Char('Intermo Plugin Key')
    intermo_secret_key = fields.Char('Intermo Secret Key')
    intermo_notify_url = fields.Char('Intermo Notify URL')

class PosPaymentTxn(models.Model):

    _name = "pos.payment.txn"


    name = fields.Char(string="Name")
    status = fields.Char(string="Status")



class PosOrder(models.Model):

    _inherit = 'pos.order'


    intermo_payment_status = fields.Char(string="Payment Status")

    def _export_for_ui(self, order):
        res = super()._export_for_ui(order)
        print("==================2=-2=2=2=2", order)
        res['intermo_payment_status'] = order.intermo_payment_status
        return res


    @api.model
    def _payment_fields(self, order, ui_paymentline):
        payment_fields = super()._payment_fields(order, ui_paymentline)
        payment_fields.update({
                'intermo_public_key': ui_paymentline.get('intermo_public_key'),
                'intermo_plugin_key': ui_paymentline.get('intermo_plugin_key'),
                'intermo_secret_key': ui_paymentline.get('intermo_secret_key'),
                'intermo_notify_url': ui_paymentline.get('intermo_notify_url'),

            })
        return payment_fields
