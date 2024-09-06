import logging
import pprint
import time
from datetime import datetime

from dateutil.relativedelta import relativedelta

from odoo import api, models
from odoo.exceptions import UserError, ValidationError

from odoo.addons.payment import utils as payment_utils

_logger = logging.getLogger(__name__)


class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'

    def _get_specific_processing_values(self, processing_values):
        """ Override of `payment` to return provider-specific processing values.

        :param dict processing_values: The generic and specific processing values of the transaction.
        :return: The provider-specific processing values.
        :rtype: dict
        """
        # Skeleton function: No actual processing
        res = super()._get_specific_processing_values(processing_values)
        if self.provider_code != 'dummy':
            return res

        # Return empty or dummy data
        return {
            'dummy_key_id': 'dummy_key',
            'dummy_customer_id': 'dummy_customer_id',
            'is_tokenize_request': False,
            'dummy_order_id': 'dummy_order_id',
        }

    def _dummy_create_customer(self):
        """ Create and return a Dummy Customer object.

        :return: The created Dummy Customer.
        :rtype: dict
        """
        # Skeleton function: No actual processing
        return {'id': 'dummy_customer_id'}

    @api.model
    def _validate_phone_number(self, phone):
        """ Validate and format the phone number.

        :param str phone: The phone number to validate.
        :return str: The formatted phone number.
        :raise ValidationError: If the phone number is missing or incorrect.
        """
        # Skeleton function: No actual processing
        return phone

    def _dummy_create_order(self, customer_id=None):
        """ Create and return a Dummy Order object to initiate the payment.

        :param str customer_id: The ID of the Dummy Customer object to assign to the Order.
        :return: The created Dummy Order.
        :rtype: dict
        """
        # Skeleton function: No actual processing
        return {'id': 'dummy_order_id'}

    def _dummy_prepare_order_payload(self, customer_id=None):
        """ Prepare the payload for the dummy order request.

        :param str customer_id: The ID of the Dummy Customer object.
        :return: The request payload.
        :rtype: dict
        """
        # Skeleton function: No actual processing
        return {}

    def _send_payment_request(self):
        """ Override of `payment` to send a dummy payment request.

        :return: None
        """
        # Skeleton function: No actual processing
        super()._send_payment_request()
        if self.provider_code != 'dummy':
            return

        # Dummy log for skeleton
        _logger.info("Dummy payment request sent for transaction with reference %s", self.reference)

    def _send_refund_request(self, amount_to_refund=None):
        """ Override of `payment` to send a dummy refund request.

        :param float amount_to_refund: The amount to refund.
        :return: The refund transaction created to process the refund request.
        :rtype: recordset of `payment.transaction`
        """
        # Skeleton function: No actual processing
        refund_tx = super()._send_refund_request(amount_to_refund=amount_to_refund)
        if self.provider_code != 'dummy':
            return refund_tx

        # Dummy log for skeleton
        _logger.info("Dummy refund request sent for transaction with reference %s", self.reference)

        return refund_tx

    def _send_capture_request(self, amount_to_capture=None):
        """ Override of `payment` to send a dummy capture request.

        :return: None
        """
        # Skeleton function: No actual processing
        super()._send_capture_request(amount_to_capture=amount_to_capture)
        if self.provider_code != 'dummy':
            return

        # Dummy log for skeleton
        _logger.info("Dummy capture request sent for transaction with reference %s", self.reference)

    def _send_void_request(self, amount_to_void=None):
        """ Override of `payment` to explain that it is impossible to void a Dummy transaction.

        :return: None
        """
        # Skeleton function: No actual processing
        super()._send_void_request(amount_to_void=amount_to_void)
        if self.provider_code != 'dummy':
            return

        _logger.info("Dummy void request sent for transaction with reference %s", self.reference)

    def _get_tx_from_notification_data(self, provider_code, notification_data):
        """ Override of `payment` to find the transaction based on dummy data.

        :param str provider_code: The code of the provider that handled the transaction
        :param dict notification_data: The normalized notification data sent by the provider
        :return: The transaction if found
        :rtype: recordset of `payment.transaction`
        """
        # Skeleton function: No actual processing
        return super()._get_tx_from_notification_data(provider_code, notification_data)

    def _process_notification_data(self, notification_data):
        """ Override of `payment` to process the transaction based on dummy data.

        :param dict notification_data: The notification data sent by the provider
        :return: None
        """
        # Skeleton function: No actual processing
        super()._process_notification_data(notification_data)
        if self.provider_code != 'dummy':
            return

        _logger.info("Dummy notification data processed for transaction with reference %s", self.reference)

    def _razorpay_tokenize_from_notification_data(self, notification_data):
        """ Create a new token based on the notification data.

        :param dict notification_data: The notification data built with dummy objects.
        :return: None
        """
        # Skeleton function: No actual processing
        pass

    def _razorpay_create_refund_tx_from_notification_data(self, source_tx, notification_data):
        """ Create a refund transaction based on dummy data.

        :param recordset source_tx: The source transaction for which a refund is initiated.
        :param dict notification_data: The notification data sent by the provider.
        :return: The newly created refund transaction.
        :rtype: recordset of `payment.transaction`
        """
        # Skeleton function: No actual processing
        return source_tx

