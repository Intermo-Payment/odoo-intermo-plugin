from odoo import models, fields, api, _
from odoo.exceptions import UserError

class IntermoOrderHistory(models.Model):
    _name = 'intermo.order.history'
    _description = 'Intermo Order History'

    transaction_id = fields.Char(string="Transaction ID", readonly=True)
    transaction_date = fields.Datetime(string="Transaction Date", readonly=True)
    amount = fields.Float(string="Amount", readonly=True)
    status = fields.Selection([
        ('completed', 'Completed'),
        ('pending', 'Pending'),
        ('failed', 'Failed')
    ], string="Status")
    pos_id = fields.Many2one('pos.order', string="POS Order", readonly=True)
    currency = fields.Char(string="Currency", readonly=False, default="XOF")
    merchant_info = fields.Char(string="POS Shop Name", readonly=True)

    @api.model
    def update_from_pos_order(self, pos_order):
        """
        Update or create a payment history record based on a POS order.
        """
        history_record = self.search([('pos_id', '=', pos_order.id)], limit=1)
        data = {
            'transaction_id': pos_order.pos_reference,
            'transaction_date': pos_order.date_order,
            'amount': pos_order.amount_total,
            'status': 'completed' if pos_order.state == 'done' else 'pending',
            'pos_id': pos_order.id,
            'currency': pos_order.pricelist_id.currency_id.name if pos_order.pricelist_id and pos_order.pricelist_id.currency_id else "XOF",
            'merchant_info': pos_order.session_id.config_id.name,
        }

        if history_record:
            history_record.write(data)
        else:
            self.create(data)

    def resync_payment_history(self):
        """
        Resync payment history by deleting all records and re-fetching from pos.order.
        """
        # Delete all existing records
        self.search([]).unlink()

        # Fetch all completed POS orders
        pos_orders = self.env['pos.order'].search([('state', '=', 'done')])
        for pos_order in pos_orders:
            self.update_from_pos_order(pos_order)

        return True

    def unlink(self):
        """Prevent manual deletion of records except during resync."""
        raise UserError(_("You cannot delete payment history records manually."))

# from odoo import models, fields, api, _

# class IntermoOrderHistory(models.Model):
#     _name = 'intermo.order.history'
#     _description = 'Intermo Order History'

#     transaction_id = fields.Char(string="Transaction ID", readonly=True)
#     transaction_date = fields.Datetime(string="Transaction Date", readonly=True)
#     amount = fields.Float(string="Amount", readonly=True)
#     status = fields.Selection([
#         ('completed', 'Completed'),
#         ('pending', 'Pending'),
#         ('failed', 'Failed')
#     ], string="Status")
#     pos_id = fields.Many2one('pos.order', string="POS Order", readonly=True)
#     currency = fields.Char(string="Currency", readonly=False, default="XOF")
#     merchant_info = fields.Char(string="POS Shop Name", readonly=True)
#     intermo_payment_link = fields.Char(string="Payment Link", readonly=True)
#     intermo_offline_status = fields.Boolean(string="Offline Payment", readonly=True)

#     @api.model
#     def update_from_pos_order(self, pos_order):
#         """
#         Update or create a payment history record based on a POS order.
#         """
#         history_record = self.search([('pos_id', '=', pos_order.id)], limit=1)
#         data = {
#             'transaction_id': pos_order.intermo_transaction_id or pos_order.pos_reference,
#             'transaction_date': pos_order.date_order,
#             'amount': pos_order.amount_total,
#             'status': pos_order.intermo_payment_status,
#             'pos_id': pos_order.id,
#             'currency': pos_order.pricelist_id.currency_id.name if pos_order.pricelist_id and pos_order.pricelist_id.currency_id else "XOF",
#             'merchant_info': pos_order.session_id.config_id.name,
#             'intermo_payment_link': pos_order.intermo_payment_link,
#             'intermo_offline_status': pos_order.intermo_offline_status,
#         }

#         if history_record:
#             history_record.write(data)
#         else:
#             self.create(data)
    
#     def resync_payment_history(self):
#         """
#         Resync payment history by deleting all records and re-fetching from pos.order.
#         """
#         # Delete all existing records
#         self.search([]).unlink()

#         # Fetch all POS orders with Intermo transactions
#         pos_orders = self.env['pos.order'].search([])
#         for pos_order in pos_orders:
#             self.update_from_pos_order(pos_order)

#         return True