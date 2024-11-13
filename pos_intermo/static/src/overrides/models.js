/** @odoo-module */
import { register_payment_method } from "@point_of_sale/app/store/pos_store";
import { PaymentIntermo } from '@pos_intermo/app/payment_intermo';

register_payment_method('intermo', PaymentIntermo);
