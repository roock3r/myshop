import requests
import logging

class BelizeBankPaymentGatewayError(Exception):
    def __init__(self, code, message):
        self.code = code
        self.message = message
        super().__init__(self.format_message())

    def format_message(self):
        return f"Error Code: {self.code} - Message: {self.message}"

class BelizeBankPaymentGateway:
    BASE_URL_TEST = 'https://sandbox.belizebank.com/payment/rest'
    BASE_URL_PROD = '{prod-url}'

    def __init__(self, username, password, mode='test'):
        self.username = username
        self.password = password
        self.mode = mode
        self.base_url = self.BASE_URL_TEST if mode == 'test' else self.BASE_URL_PROD
        self.logger = logging.getLogger(__name__)

    def _make_request(self, endpoint, data):
        url = f"{self.base_url}/{endpoint}"
        response = requests.post(url, data=data)
        print('response data:', response.json())
        return self._handle_response(response)

    def _handle_response(self, response):
        response_data = response.json()
        if response.status_code != 200 or "errorCode" in response_data and response_data["errorCode"] != "0":
            error_code = response_data.get("errorCode")
            error_message = response_data.get("errorMessage", "Unknown error")
            self.logger.error(f"Failed request: {error_code} - {error_message}")
            raise BelizeBankPaymentGatewayError(error_code, error_message)
        return response_data

    def authorize_payment(self, amount, order_number, return_url, description=None, client_id=None, email=None):
        payload = {
            "userName": self.username,
            "password": self.password,
            "amount": amount,
            "orderNumber": order_number,
            "returnUrl": return_url,
            "description": description,
            "clientId": client_id,
            "email": email,
        }
        print('payload:', payload)
        return self._make_request('register.do', payload)

    def pre_authorize_payment(self, amount, order_number, return_url, description=None, client_id=None, email=None):
        payload = {
            "userName": self.username,
            "password": self.password,
            "amount": amount,
            "orderNumber": order_number,
            "returnURL": return_url,
            "description": description,
            "clientId": client_id,
            "email": email,
        }
        return self._make_request('registerPreAuth.do', payload)

    def capture_pre_authorization(self, order_id, amount):
        payload = {
            "userName": self.username,
            "password": self.password,
            "orderId": order_id,
            "amount": amount,
        }
        return self._make_request('deposit.do', payload)

    def reverse_payment(self, order_id):
        payload = {
            "userName": self.username,
            "password": self.password,
            "orderId": order_id,
        }
        return self._make_request('reverse.do', payload)

    def refund_payment(self, order_id, amount):
        payload = {
            "userName": self.username,
            "password": self.password,
            "orderId": order_id,
            "amount": amount,
        }
        return self._make_request('refund.do', payload)

    def get_payment_status(self, order_id):
        payload = {
            "userName": self.username,
            "password": self.password,
            "orderId": order_id,
        }
        return self._make_request('getOrderStatusExtended.do', payload)
