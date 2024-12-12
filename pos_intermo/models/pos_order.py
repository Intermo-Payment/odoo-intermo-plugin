from odoo import models, api

class PosOrder(models.Model):
    _inherit = 'pos.order'

    @api.model
    def create(self, values):
        """
        Automatically update payment history when a new POS order is created.
        """
        order = super(PosOrder, self).create(values)
        self.env['intermo.order.history'].update_from_pos_order(order)
        return order

    def write(self, values):
        """
        Update payment history when a POS order is modified.
        """
        result = super(PosOrder, self).write(values)
        for order in self:
            self.env['intermo.order.history'].update_from_pos_order(order)
        return result

# from odoo import models, fields, api

# class PosOrder(models.Model):
#     _inherit = 'pos.order'

#     intermo_payment_status = fields.Selection(
#         [('completed', 'Completed'), ('pending', 'Pending'), ('failed', 'Failed')],
#         string="Intermo Payment Status",
#         default='pending',
#         help="Payment status for Intermo transactions."
#     )
#     intermo_transaction_id = fields.Char(
#         string="Intermo Transaction ID",
#         help="The transaction ID from Intermo."
#     )
#     intermo_payment_link = fields.Char(
#         string="Intermo Payment Link",
#         help="The payment link generated for this order."
#     )
#     intermo_offline_status = fields.Boolean(
#         string="Is Offline Payment",
#         default=False,
#         help="Indicates whether the payment was made offline."
#     )

#     @api.model
#     def create(self, values):
#         """
#         Override to sync Intermo payments with `intermo.order.history`.
#         """
#         order = super(PosOrder, self).create(values)
#         if 'intermo_transaction_id' in values or 'intermo_payment_status' in values:
#             self.env['intermo.order.history'].update_from_pos_order(order)
#         return order

#     def write(self, values):
#         """
#         Override to update Intermo payment synchronization.
#         """
#         result = super(PosOrder, self).write(values)
#         if any(key in values for key in ['intermo_transaction_id', 'intermo_payment_status']):
#             for order in self:
#                 self.env['intermo.order.history'].update_from_pos_order(order)
#         return result
