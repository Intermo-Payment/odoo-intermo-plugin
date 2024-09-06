odoo.define('pos_intermo.PaymentScreen', function (require) {
    'use strict';

    const PaymentScreen = require('point_of_sale.PaymentScreen');
    const Registries = require('point_of_sale.Registries');

    const IntermoPaymentScreen = PaymentScreen =>
        class extends PaymentScreen {
            async _finalizeValidation() {
                const currentOrder = this.env.pos.get_order();
                const paymentLines = currentOrder.get_paymentlines();
                
                // Check if Intermo payment method is selected
                const intermoPaymentMethod = paymentLines.some(line => line.payment_method.use_intermo);

                if (intermoPaymentMethod) {
                    // Logic to display the summary screen
                    this.showPopup('ConfirmPopup', {
                        title: this.env._t('Order Summary'),
                        body: this._getOrderSummary(),
                    });
                } else {
                    await super._finalizeValidation();
                }
            }

            // Helper method to get the order summary details
            _getOrderSummary() {
                const order = this.env.pos.get_order();
                let summary = '';

                order.get_orderlines().forEach(line => {
                    summary += `${line.product.display_name} - ${line.quantity} x ${line.price.toFixed(2)}\n`;
                });

                summary += `\nTotal: ${order.get_total_with_tax().toFixed(2)}`;

                return summary;
            }
        };

    Registries.Component.extend(PaymentScreen, IntermoPaymentScreen);

    return IntermoPaymentScreen;
});
