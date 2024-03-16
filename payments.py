import os  # os.environ.get('variable_name')
import time
import math
import base64
import requests
from datetime import datetime
from requests.auth import HTTPBasicAuth


# from yourapp.settings import env  # environment for Django or use the os option too

class MpesaHandler:
    now = None
    shortcode = None
    consumer_key = None
    consumer_secret = None
    access_token_url = None
    access_token = None
    access_token_expiration = None
    stk_push_url = None
    my_callback_url = None
    query_status_url = None
    timestamp = None
    passkey = None

    def __init__(self, till):
        self.headers = None
        self.till = till
        self.now = datetime.now()
        self.shortcode = till # os.environ.get(till)  # env("SAF_SHORTCODE")
        self.consumer_key = "OZHUaBKuvC39cAPU7AAZGV5PzDkB7GxGBYXSDo3cy6XZqyQm"  # os.environ.get("OZHUaBKuvC39cAPU7AAZGV5PzDkB7GxGBYXSDo3cy6XZqyQm")
        self.consumer_secret = "yCTAw0VG24oacEEE0W9RfQVHAtdYsPU2Bn95zcU4kG3DanAi7V0cHEAfFZkDYfGZ"  # os.environ.get("yCTAw0VG24oacEEE0W9RfQVHAtdYsPU2Bn95zcU4kG3DanAi7V0cHEAfFZkDYfGZ")
        self.access_token_url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
        self.passkey = "bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919"  # os.environ.get("bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919")
        self.stk_push_url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"  # os.environ.get("https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest")
        self.query_status_url = "https://sandbox.safaricom.co.ke/mpesa/stkpushquery/v1/query" # os.environ.get("https://sandbox.safaricom.co.ke/mpesa/stkpushquery/v1/query")
        self.my_callback_url = "https://sandbox.safaricom.co.ke/mpesa/" # os.environ.get("https://sandbox.safaricom.co.ke/mpesa/")
        self.password = self.generate_password()

        try:
            self.access_token = self.get_mpesa_access_token()

            if self.access_token is None:
                raise Exception("Request for access token failed")
            else:
                self.access_token_expiration = time.time() + 3599

        except Exception as e:
            # log this errors
            print(str(e))

    def get_mpesa_access_token(self):
        try:
            res = requests.get(
                self.access_token_url,
                auth=HTTPBasicAuth(self.consumer_key, self.consumer_secret),
            )
            token = res.json()['access_token']

            self.headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
        except Exception as e:
            print(str(e), "error getting access token")
            raise e

        return token

    def generate_password(self):
        self.timestamp = self.now.strftime("%Y%m%d%H%M%S")
        '''
        print("Till:", self.till)
        print("Consumer Key:", self.consumer_key)
        print("Consumer Secret:", self.consumer_secret)
        print("Access Token URL:", self.access_token_url)
        print("Passkey:", self.passkey)
        print("STK Push URL:", self.stk_push_url)
        print("Query Status URL:", self.query_status_url)
        print("Callback URL:", self.my_callback_url)
        '''
        password_str = self.shortcode + self.passkey + self.timestamp
        password_bytes = password_str.encode()

        return base64.b64encode(password_bytes).decode("utf-8")

    def make_stk_push(self, payload):
        amount = payload['amount']
        phone_number = payload['phone_number']

        push_data = {
            "BusinessShortCode": self.shortcode,
            "Password": self.password,
            "Timestamp": self.timestamp,
            "TransactionType": "CustomerPayBillOnline",
            "Amount": math.ceil(float(amount)),
            "PartyA": phone_number,
            "PartyB": self.shortcode,
            "PhoneNumber": phone_number,
            "CallBackURL": self.my_callback_url,
            "AccountReference": "REMM METERS",
            "TransactionDesc": "description of the transaction",
        }

        response = requests.post(
            self.stk_push_url,
            json=push_data,
            headers=self.headers)

        response_data = response.json()

        return response_data

    def query_transaction_status(self, checkout_request_id):
        query_data = {
            "BusinessShortCode": self.shortcode,
            "Password": self.password,
            "Timestamp": self.timestamp,
            "CheckoutRequestID": checkout_request_id
        }

        response = requests.post(
            self.query_status_url,
            json=query_data,
            headers=self.headers
        )

        response_data = response.json()

        return response_data
