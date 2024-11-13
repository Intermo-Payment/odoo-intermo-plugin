(function(global) {
	"use strict";

	const PaymentWidget = function(config) {
		this.config = config;
		this.apiUrl = 'http://localhost:7777/SandBox/v1/api/GetAccessToken';
		console.log("PaymentWidget initialized with config: ", config);
		this.init();
	};

	PaymentWidget.prototype.init = function() {
		const requiredFields = ['amount', 'publicApiKey', 'currency', 'referenceid', 'customername', 'customeremail', 'customerphone', 'callbackurl', 'notifyurl', 'pluginname', 'pluginversion', 'pluginkey', 'secretkey', 'isolang'];
		const missingFields = requiredFields.filter(field => !this.config[field]);

		if (missingFields.length > 0) {
			console.error("Required configuration missing: ", missingFields.join(', '));
			this.notifyParent('PAYMENT_ERROR', {
				message: 'Required configuration missing',
				details: missingFields
			});
			return;
		}

		this.widgetConfig = {
			amount: this.config.amount,
			publicApiKey: this.config.publicApiKey,
			sandbox: this.config.sandbox || true,
			currency: this.config.currency,
			referenceid: this.config.referenceid,
			customername: this.config.customername,
			customeremail: this.config.customeremail,
			customerphone: this.config.customerphone,
			callbackurl: this.config.callbackurl,
			notifyurl: this.config.notifyurl,
			pluginname: this.config.pluginname,
			pluginversion: this.config.pluginversion,
			serverless: this.config.serverless,
			pluginkey: this.config.pluginkey,
			secretkey: this.config.secretkey,
			isolang: this.config.isolang,
			location: 'Unknown',
			city: 'Unknown',
			timezone: 'UTC'
		};

		console.log("Widget Config: ", this.widgetConfig);
		this.getLocationDetails();
	};

	PaymentWidget.prototype.getLocationDetails = async function() {
		try {
			console.log("Fetching location details...");
			const response = await fetch('https://ipapi.co/json/');
			const locationData = await response.json();
			this.widgetConfig.location = locationData.country_name || 'Unknown';
			this.widgetConfig.city = locationData.city || 'Unknown';
			this.widgetConfig.timezone = locationData.timezone || 'UTC';
			console.log("Location details fetched: ", locationData);
		} catch (error) {
			console.error("Error fetching location details:", error);
			// this.notifyParent('PAYMENT_ERROR', {
			// 	message: 'Error fetching location details',
			// 	error: error.toString()
			// });
		}
	};

	PaymentWidget.prototype.fetchAccessToken = async function() {
		console.log("Fetching access token...");
		const {
			authToken
		} = this.config;
		const myHeaders = new Headers();
		myHeaders.append("Content-Type", "application/json");
		myHeaders.append("Authorization", `Bearer ${authToken}`);

		try {
			console.log("Fetching data...");
			const response = await fetch(this.apiUrl, {
				method: "POST",
				headers: myHeaders,
				body: JSON.stringify(this.widgetConfig),
			});

			if (!response.ok) {
				throw new Error('Failed to fetch access token: ' + response.statusText);
			}

			const responseData = await response.text();
			try {
				this.notifyParent('PAYMENT_INITIATED', {
					message: 'Payment initiated'
				});
				console.log("Access token fetched: ", responseData);
				return JSON.parse(responseData);
			} catch (error) {
				throw new Error('Invalid JSON response: ' + responseData);
			}
		} catch (error) {
			console.error("Error fetching access token:", error);
			this.notifyParent('PAYMENT_ERROR', {
				message: 'Failed to fetch access token',
				error: error.toString()
			});
			return null;
		}
	};

	PaymentWidget.prototype.initPaymentIframe = function(paymentLink) {
		console.log("Initializing payment iframe with link: ", paymentLink);
		const iframe = document.createElement("iframe");
		iframe.src = paymentLink;
		iframe.style.cssText = `
			display: block;
			height: 100vh;
			width: 100%;
			position: fixed;
			top: 0;
			left: 0;
			z-index: 9999;
			border: none;
		`;

		document.body.appendChild(iframe);

		window.addEventListener('message', (event) => {
			this.handlePaymentStatus(event.data);
		});
	};

	PaymentWidget.prototype.handlePaymentStatus = function(data) {
		console.log("Handling payment status: ", data.name);
		if (!data || !data.name) {
			console.log('Unknown payment status:', data);
			return;
		}

		const status = data.name;
        switch (status) {
            case 'PAYMENT_SUCCESS':
            case 'PAYMENT_ERROR':
            case 'PENDING_PAYMENT':
            case 'PAYMENT_EXPIRED':
                data.referenceid = this.widgetConfig.referenceid;
                this.notifyParent(data.name, data);
                if (status === 'PAYMENT_ERROR' || status === 'PAYMENT_EXPIRED') {
                    this.closeIframe();
                }
                break;
            default:
                //console.error('Unknown payment status:', status);
                break;
        }
	};

    PaymentWidget.prototype.closeIframe = function() {
        const iframe = document.querySelector("iframe");
        if (iframe) {
            iframe.parentNode.removeChild(iframe);
            console.log("Iframe closed.");
        }
    };

	PaymentWidget.prototype.sendPaymentDetailsToPlatform = function(data) {
		const paymentDetails = {
			status: data.name,
			paymentMethod: data.paymentMethod,
			currency: data.currency,
			amount: data.amount,
			transactionId: data.transactionId,
			referenceid: this.config.referenceid
		};

		console.log("Sending payment details to platform: ", paymentDetails);

		this.notifyParent(paymentDetails.status,data);


	};

	PaymentWidget.prototype.showSuccessMessage = function(data) {
		alert('Payment successful!');
		console.log(data);
	};

	PaymentWidget.prototype.showErrorMessage = function(data) {
		alert('Payment failed. Please try again.');
		console.log(data);
	};

	PaymentWidget.prototype.showPendingMessage = function(data) {
		alert('Payment is pending. Please wait.');
		console.log(data);
	};

	PaymentWidget.prototype.pay = async function() {
		console.log("Starting payment process...");
		const tokenResponse = await this.fetchAccessToken();
		if (tokenResponse && tokenResponse.paymentlink) {
			this.initPaymentIframe(tokenResponse.paymentlink);
		} else {
			console.error("Invalid response from fetchAccessToken:", tokenResponse);
		}
	};

	PaymentWidget.prototype.notifyParent = function(status, details) {
		console.log("Notifying parent with status: ", status, " and details: ", details);
		window.parent.postMessage({
			status,
			details
		}, "*");
	};

	global.PaymentWidget = PaymentWidget;

})(window);