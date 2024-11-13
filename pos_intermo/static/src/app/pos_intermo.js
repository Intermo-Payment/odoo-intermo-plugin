/** @odoo-module */

import { Payment } from "@point_of_sale/app/store/models";
import { patch } from "@web/core/utils/patch";


patch(Payment.prototype, {
    init_from_JSON(json) {
        super.init_from_JSON(...arguments);
        if(this.payment_method?.use_payment_terminal === 'intermo'){
            this.intermo_public_key = json.intermo_public_key;
            this.intermo_plugin_key = json.intermo_plugin_key;
            this.intermo_secret_key = json.intermo_secret_key;
            this.intermo_notify_url = json.intermo_notify_url;

        }
    },
    export_as_JSON() {
        const result = super.export_as_JSON(...arguments);
        if(result && this.payment_method?.use_payment_terminal === 'intermo'){
            return Object.assign(result, {
                intermo_public_key: this.intermo_public_key,
                intermo_plugin_key: this.intermo_plugin_key,
                intermo_secret_key: this.intermo_secret_key,
                intermo_notify_url: this.intermo_notify_url,
               });
        }
        return result
    },
});
