/** @odoo-module */

import { patch } from "@web/core/utils/patch";
import { _t } from "@web/core/l10n/translation";
import { PaymentInterface } from "@point_of_sale/app/payment/payment_interface";
import { Order } from "@point_of_sale/app/store/models";
import { AlertDialog } from "@web/core/confirmation_dialog/confirmation_dialog";
import { PosIntermoPopup } from "@pos_intermo/app/confirm_popup";

const REQUEST_TIMEOUT = 10000;

export class PaymentIntermo extends PaymentInterface {
    setup() {
        super.setup(...arguments);

    }
    async send_payment_request(cid) {

        await super.send_payment_request(...arguments);
        var self = this;


        self.url_link = await self._process_intermo(cid);
        self.intermoInterval = setInterval(async () => {
            await self._waitForPaymentConfirmation();
        }, 10000);
        self.IntermoPopup = await self.env.services.popup.add(PosIntermoPopup, {
            title: _t('Intermo Payment Gateway'),
            body: self.url_link.qr_code,
            testmsg: self.url_link.offline_mode,
            odoo_offline: self.url_link.offline_mode,
            paylink:self.url_link.paylink
        });
        if (self.pos.get_order().intermo_payment_status == 'payment_success') {
            clearInterval(self.intermoInterval);
            await self.pos.get_order().selected_paymentline.set_payment_status("done");
            return true;

        }
        else {
            clearInterval(self.intermoInterval);
            await self.pos.get_order().selected_paymentline.set_payment_status("retry");
            return false;
        }
    }

    pending_intermo_line() {
        return this.pos.getPendingPaymentLine("intermo");
    }


    _call_intermo(data, action) {

        return this.env.services.orm.silent
            .call("pos.payment.method",
                action,
                [[this.payment_method.id], data]
            )
            .catch(this._handle_odoo_connection_failure.bind(this));
    }
    //
    _handle_odoo_connection_failure(data = {}) {
        // handle timeout
        const line = this.pending_intermo_line();
        if (line) {
            line.set_payment_status("retry");
        }
        this._showError(
            _t(
                "Could not connect to the Odoo server, please check your internet connection and try again."
            )
        );

        return Promise.reject(data); // prevent subsequent onFullFilled's from being called
    }


    async send_payment_cancel(order, cid) {
        console.log("=====================w-wwpwwwpewewp");
        await super.send_payment_cancel(...arguments);
        const paymentLine = this.pos.get_order()?.selected_paymentline;
        paymentLine.set_payment_status('retry');
        return true;
    }

    async _process_intermo(cid) {
        const order = this.pos.get_order();
        const line = order.paymentlines.find((paymentLine) => paymentLine.cid === cid);

        if (line.amount < 0) {
            this._showError(_t("Cannot process transactions with negative amount."));
            return Promise.resolve();
        }

        const orderId = order.name.replace(" ", "").replaceAll("-", "").toUpperCase();
        const referencePrefix = this.pos.config.name.replace(/\s/g, "").slice(0, 4);
        localStorage.setItem("referenceId", referencePrefix + "/" + orderId + "/" + crypto.randomUUID().replaceAll("-", ""));
        let baseUrl = window.location.origin + '/pos_intermo/notification';
        let updatedUrl = `${baseUrl}?order_id=${order.pos_session_id}`;

        var customername = "";
        var customeremail = "";
        var customerphone = "+";
        if (order.partner) {
            customername = order.partner.name;
            customeremail = order.partner.email;
            customerphone = order.partner.phone;
        }
        if (!order.reference) {
            order.set_reference(order.name);
        }
        var x = order.reference;
        var y = "";
        if (x.includes("#")) {
            y = x.split("#");
            x = y[0] + "#" + (parseInt(y[1]) + 1);
        } else {
            x = x + "#1";
        }
        order.set_reference(x);

        // Fetch the configuration dynamically
        const config = await this.env.services.orm.call("intermo.gateway.config", "search_read", [], {
            fields: [
                "mode", "sandbox_authentication_key", "sandbox_public_key", "sandbox_secret",
                "production_authentication_key", "production_public_key", "production_secret",
                "generated_secret_token", "language"
            ],
            limit: 1,
        });

        if (config.length === 0) {
            this._showError(_t("Intermo configuration is missing. Please set it up in the Intermo Gateway Config settings."));
            return;
        }

        const intermoConfig = config[0];
        const isSandbox = intermoConfig.mode === "sandbox";
        const publicKey = isSandbox ? intermoConfig.sandbox_public_key : intermoConfig.production_public_key;
        const secretKey = isSandbox ? intermoConfig.sandbox_secret : intermoConfig.production_secret;
        const pluginKey = intermoConfig.generated_secret_token;
        const language = intermoConfig.language;

        const data = {
            'amount': line.amount,
            "referenceid": x,
            "publicApiKey": publicKey,
            "sandbox": isSandbox,
            "currency": order.pos.currency.name,
            "customername": customername,
            "customeremail": customeremail,
            "customerphone": customerphone,
            "callbackurl": updatedUrl,
            "notifyurl": updatedUrl,
            "pluginname": "Odoo",
            "pluginversion": "v1.1.0",
            "serverless": false,
            "pluginkey": pluginKey,
            "secretkey": secretKey,
            "isolang": language || "en"
        };

        console.log("================---data--------", data);

        const url_link = await this._call_intermo(data, 'intermo_make_payment_request');
        order.jwt_token = url_link.jwt_token;
        order.url_link = url_link;
        order.url_link.offline_mode = url_link.offline_mode

        console.log("================---url_link--------", url_link);
        return url_link;
    }

    async _waitForPaymentConfirmation() {
        const self = this;
        const order = self.pos.get_order();

        // Skip confirmation check in offline mode
        if (order.url_link && order.url_link.offline_mode ) {
            console.log("Payment is in offline mode. Skipping status check.");
            return;
        }

        console.log("Checking payment status in online mode...");

        try {
            // Check for transaction in the database
            const payment_trx = await self.pos.orm.call("pos.payment.txn", "search_read", [], {
                fields: ["name", "status"],
                domain: [["name", "=", order.name]],
            });

            if (payment_trx.length > 0) {
                order.intermo_payment_status = payment_trx[0]["status"];
                console.log("Transaction found in database:", order.intermo_payment_status);
            } else {
                // If no transaction is found, check via Intermo API
                let tmp_payment_method_id = null;
                order.paymentlines.forEach((pl) => {
                    if (pl.payment_method.use_payment_terminal === "intermo") {
                        tmp_payment_method_id = pl.payment_method.id;
                    }
                });

                if (tmp_payment_method_id) {
                    const payment_status_check = await self.pos.orm.call(
                        "pos.payment.method",
                        "intermo_get_payment_status",
                        [tmp_payment_method_id, order.jwt_token]
                    );
                    console.log("Fetched payment status from intermo_get_payment_status:", payment_status_check);
                    order.intermo_payment_status = payment_status_check;
                }
            }
        } catch (error) {
            console.error("Error during payment status check:", error);
            order.intermo_payment_status = "unknown";
        }
    }



    _showError(error_msg, title) {
        this.env.services.dialog.add(AlertDialog, {
            title: title || _t("Intermo Error"),
            body: error_msg,
        });
    }
}

patch(Order.prototype, {
    set_reference(reference) {
        this.assert_editable();
        this.reference = reference;
    },
    export_as_JSON() {
        const json = super.export_as_JSON();
        json.reference = this.reference;
        return json;
    },
    init_from_JSON(json) {
        super.init_from_JSON(...arguments);
        this.reference = json.reference;
    },
});


