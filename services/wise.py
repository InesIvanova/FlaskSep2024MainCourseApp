import uuid

import requests
from decouple import config


class WiseService:
    def __init__(self):
        self.main_url = config("WISE_URL")
        self.token = config("WISE_API_KEY")
        self.headers = {
            "Content-type": "application/json",
            "Authorization": f"Bearer {self.token}",
        }
        self.profile_id = config("WISE_PROFILE_ID")

    def create_quote(self, amount):
        url = self.main_url + "/v2/quotes/"
        body = {
            "sourceCurrency": "EUR",
            "targetCurrency": "BGN",
            "targetAmount": amount,
            "profile": self.profile_id,
        }

        resp = requests.post(url, headers=self.headers, json=body)
        return resp.json()

    def create_recipient(self, first_name, last_name, iban):
        url = self.main_url + "/v1/accounts"
        body = {
            "currency": "BGN",
            "type": "iban",
            "profile": self.profile_id,
            "accountHolderName": f"{first_name} {last_name}",
            "legalType": "PRIVATE",
            "details": {
                "iban": iban,
            },
        }

        resp = requests.post(url, headers=self.headers, json=body)
        return resp.json()

    def create_transfer(self, target_account_id, quote_id):
        customer_transaction_id = str(uuid.uuid4())

        url = self.main_url + "/v1/transfers"
        body = {
            "targetAccount": target_account_id,
            "quoteUuid": quote_id,
            "customerTransactionId": customer_transaction_id,
            "details": {},
        }
        resp = requests.post(url, headers=self.headers, json=body)
        return resp.json()

    def fund_transfer(self, transfer_id):
        url = f"{self.main_url}/v3/profiles/{self.profile_id}/transfers/{transfer_id}/payments"
        payload = {
            "type": "BALANCE"
         }
        resp = requests.post(url, headers=self.headers, json=payload)
        return resp.json()

    def cancel_transfer(self, transfer_id):
        url = f"{self.main_url}/v1/transfers/{transfer_id}/cancel"
        resp = requests.put(url, headers=self.headers)
        return resp.json()

