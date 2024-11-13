/** @odoo-module */

import { AbstractAwaitablePopup } from "@point_of_sale/app/popup/abstract_awaitable_popup";
import { _t } from "@web/core/l10n/translation";
import { useState } from "@odoo/owl";

export class PosIntermoPopup extends AbstractAwaitablePopup {

    setup(){
        super.setup();
        this.state = useState({
            error_message:'Waiting for payment...',
            message_type: 'info',
        });
        const self = this
        setInterval(() => {
             if(self.env.services.pos.get_order().intermo_payment_status == 'payment_success'){
                self.state.error_message = "Payment Successful!";
                self.state.message_type = "success";
             }
        }, 3000);
    }

    async confirm() {
        if(this.env.services.pos.get_order().intermo_payment_status == 'payment_success'){
            super.confirm()
        }else{
            this.state.error_message = 'Please wait, payment is not completed yet!';
            this.state.message_type = 'error';
        }
    }

    static template = "pos_intermo.PosIntermoPopup";
    static defaultProps = {
        confirmText: _t("Ok"),
        cancelText: _t("Cancel"),
        title: _t("Confirm?"),
        body: "",
    };
}
