// /** @odoo-module */

// import { AbstractAwaitablePopup } from "@point_of_sale/app/popup/abstract_awaitable_popup";
// import { _t } from "@web/core/l10n/translation";
// import { useState } from "@odoo/owl";

// export class PosIntermoPopup extends AbstractAwaitablePopup {
//     setup() {
//         super.setup();
//         this.state = useState({
//             error_message: "Waiting for payment...",
//             message_type: "info",
//             odoo_offline: this.props.odoo_offline || false, // Track Odoo offline state
//             selected_status: "pending", // Default dropdown status
//             paylink: this.props.paylink
//         });

//         const self = this;

//         // Periodically check payment status
//         setInterval(() => {
//             if (!this.state.odoo_offline) {
//                 const paymentStatus = self.env.services.pos.get_order().intermo_payment_status;
//                 if (paymentStatus === "payment_success") {
//                     self.state.error_message = "Payment Successful!";
//                     self.state.message_type = "success";
//                 }
//             }
//         }, 3000);
//     }

//     confirmPayment() {
//         const status = this.state.selected_status;

//         if (status === "success") {
//             // Update backend or perform necessary action for successful payment
//             this.env.services.pos.get_order().intermo_payment_status = "payment_success";

//             // Update the state to reflect the success
//             this.state.error_message = "Payment marked as Successful!";
//             this.state.message_type = "success";
//             // Close the popup
//             super.confirm();


//         } else if (status === "pending") {
//             // Update backend or perform necessary action for pending payment
//             this.env.services.pos.get_order().intermo_payment_status = "payment_pending";

//             // Update the state to reflect the pending status
//             this.state.error_message = "Payment is still pending.";
//             this.state.message_type = "info";

//             // Close the popup
//             super.confirm();
//         } else {
//             // Display error message if no valid status is selected
//             this.state.error_message = "Please select a valid status.";
//             this.state.message_type = "error";
//         }
//     }

//     cancelPayment() {
//         // Close the popup without performing any action
//         super.confirm(); // Close the popup properly
//     }

//     onStatusChange(event) {
//         // Update the selected status when the dropdown value changes
//         this.state.selected_status = event.target.value;
//     }

//     async confirm() {
//         if (this.state.odoo_offline) {
//             this.state.error_message = "Cannot proceed while Odoo is offline.";
//             this.state.message_type = "error";
//         } else if (this.env.services.pos.get_order().intermo_payment_status === "payment_success") {
//             super.confirm();
//         } else {
//             this.state.error_message = "Please wait, payment is not completed yet!";
//             this.state.message_type = "error";
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


// /** @odoo-module */

// import { AbstractAwaitablePopup } from "@point_of_sale/app/popup/abstract_awaitable_popup";
// import { _t } from "@web/core/l10n/translation";
// import { useState } from "@odoo/owl";

// export class PosIntermoPopup extends AbstractAwaitablePopup {
//     setup() {
//         super.setup();
//         this.state = useState({
//             error_message: "Waiting for payment...",
//             message_type: "info",
//             odoo_offline: this.props.odoo_offline || false,
//             selected_status: "pending",
//             paylink: this.props.paylink || "", // Paylink for offline mode
//         });

//         const self = this;

//         // Periodically check payment status
//         setInterval(() => {
//             if (!this.state.odoo_offline) {
//                 const paymentStatus = self.env.services.pos.get_order().intermo_payment_status;
//                 if (paymentStatus === "payment_success") {
//                     self.state.error_message = "Payment Successful!";
//                     self.state.message_type = "success";
//                 }
//             }
//         }, 3000);
//     }

//     confirmPayment() {
//         const status = this.state.selected_status;

//         if (status === "success") {
//             this.env.services.pos.get_order().intermo_payment_status = "payment_success";
//             this.state.error_message = "Payment marked as Successful!";
//             this.state.message_type = "success";
//             super.confirm();
//         } else if (status === "pending") {
//             this.env.services.pos.get_order().intermo_payment_status = "payment_pending";
//             this.state.error_message = "Payment is still pending.";
//             this.state.message_type = "info";
//             super.confirm();
//         } else {
//             this.state.error_message = "Please select a valid status.";
//             this.state.message_type = "error";
//         }
//     }

//     cancelPayment() {
//         super.confirm();
//     }

//     onStatusChange(event) {
//         this.state.selected_status = event.target.value;
//     }

//     async confirm() {
//         if (this.state.odoo_offline) {
//             this.state.error_message = "Cannot proceed while Odoo is offline.";
//             this.state.message_type = "error";
//         } else if (this.env.services.pos.get_order().intermo_payment_status === "payment_success") {
//             super.confirm();
//         } else {
//             this.state.error_message = "Please wait, payment is not completed yet!";
//             this.state.message_type = "error";
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
import { useState } from "@odoo/owl";

export class PosIntermoPopup extends AbstractAwaitablePopup {
    setup() {
        super.setup();
        this.state = useState({
            error_message: "Waiting for payment...",
            odoo_offline: this.props.odoo_offline || false,
            selected_status: "pending",
            paylink: this.props.paylink || "", // Paylink for online mode
        });
    }

    openPaylink() {
        if (this.state.paylink) {
            window.open(this.state.paylink, "_blank");
        } else {
            this.state.error_message = "Paylink is not available.";
        }
    }

    confirmPayment() {
        const status = this.state.selected_status;
        const order = this.env.services.pos.get_order();
        if (status === "success") {
            order.intermo_payment_status = "payment_success";
            this.state.error_message = "Payment marked as successful!";
            super.confirm();
        } else {
            order.intermo_payment_status = "payment_pending";
            this.state.error_message = "Payment is still pending.";
            super.confirm();
        }
    }

    cancelPayment() {
        super.confirm();
    }

    onStatusChange(event) {
        this.state.selected_status = event.target.value;
    }

    async confirm() {
        if (this.state.odoo_offline) {
            this.state.error_message = "Cannot proceed while offline.";
        } else if (this.env.services.pos.get_order().intermo_payment_status === "payment_success") {
            super.confirm();
        } else {
            this.state.error_message = "Payment is not completed yet!";
        }
    }

    static template = "pos_intermo.PosIntermoPopup";
    static defaultProps = {
        confirmText: "Ok",
        cancelText: "Cancel",
        title: "Confirm?",
        body: "",
    };
}
