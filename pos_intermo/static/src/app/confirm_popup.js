// /** @odoo-module */

// import { AbstractAwaitablePopup } from "@point_of_sale/app/popup/abstract_awaitable_popup";
// import { _t } from "@web/core/l10n/translation";
// import { useState } from "@odoo/owl";

// export class PosIntermoPopup extends AbstractAwaitablePopup {

//     setup(){
//         super.setup();
//         this.state = useState({
//             error_message:'Waiting for payment...',
//             message_type: 'info',
//         });
//         const self = this
//         setInterval(() => {
//              if(self.env.services.pos.get_order().intermo_payment_status == 'payment_success'){
//                 self.state.error_message = "Payment Successful!";
//                 self.state.message_type = "success";
//              }
//         }, 3000);
//     }

//     async confirm() {
//         if(this.env.services.pos.get_order().intermo_payment_status == 'payment_success'){
//             super.confirm()
//         }else{
//             this.state.error_message = 'Please wait, payment is not completed yet!';
//             this.state.message_type = 'error';
//         }
//     }

//     static template = "pos_intermo.PosIntermoPopup";
//     static defaultProps = {
//         confirmText: _t("Ok"),
//         cancelText: _t("Cancel"),
//         title: _t("Confirm?"),
//         body: "",
//     };
// }


/** @odoo-module */

import { AbstractAwaitablePopup } from "@point_of_sale/app/popup/abstract_awaitable_popup";
import { _t } from "@web/core/l10n/translation";
import { useState } from "@odoo/owl";

export class PosIntermoPopup extends AbstractAwaitablePopup {
    setup() {

        // Access the QR code data
        const qrCodeData = this.props.body;
        console.log("QR Code Data:", qrCodeData);
        super.setup();
        this.state = useState({
            error_message: "Waiting for payment...",
            message_type: "info",
            odoo_offline: false, // Track Odoo offline state

        });

        const self = this;
        // this.checkOdooConnection();

        // Periodically check payment status
        setInterval(() => {
            if (!this.state.odoo_offline) {
                const paymentStatus = self.env.services.pos.get_order().intermo_payment_status;
                if (paymentStatus === "payment_success") {
                    self.state.error_message = "Payment Successful!";
                    self.state.message_type = "success";
                }
            }
        }, 3000);
    }

    // async checkOdooConnection() {
    //     try {
    //         const response = await this.env.services.rpc({
    //             model: "res.users",
    //             method: "search_read",
    //             args: [],
    //             kwargs: { limit: 1 },
    //         });
    //         if (!response || response.length === 0) {
    //             this.state.odoo_offline = true;
    //         } else {
    //             this.state.odoo_offline = false;
    //         }
    //     } catch (error) {
    //         console.error("Error checking Odoo connection:", error);
    //         this.state.odoo_offline = true;
    //     }
    // }


    async confirm() {
        if (this.state.odoo_offline) {
            this.state.error_message = "Cannot proceed while Odoo is offline.";
            this.state.message_type = "error";
        } else if (this.env.services.pos.get_order().intermo_payment_status === "payment_success") {
            super.confirm();
        } else {
            this.state.error_message = "Please wait, payment is not completed yet!";
            this.state.message_type = "error";
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
