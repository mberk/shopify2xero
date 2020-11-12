import json
from pathlib import Path
from typing import List

import keyring
import shopify
from xero_python.accounting import AccountingApi
from xero_python.accounting.models.contacts import Contacts
from xero_python.api_client import ApiClient
from xero_python.api_client import Configuration
from xero_python.api_client.oauth2 import OAuth2Token
from xero_python.identity import IdentityApi

SHOPIFY_API_VERSION = '2020-10'


class Shopify2Xero:
    def __init__(self, xoauth_connection_name: str, shopify_shop_url: str, shopify_access_token: str):
        self.xoauth_connection_name = xoauth_connection_name
        self.shopify_shop_url = shopify_shop_url
        self.shopify_access_token = shopify_access_token

        with open(Path.home() / '.xoauth' / 'xoauth.json', 'r') as f:
            xoauth_config = json.load(f)

        self.xero_scopes = xoauth_config[xoauth_connection_name]['Scopes']

        xero_client_id = xoauth_config[xoauth_connection_name]['ClientId']
        xero_client_secret = keyring.get_password('com.xero.xoauth', xoauth_connection_name)

        oauth2_token = OAuth2Token(client_id=xero_client_id, client_secret=xero_client_secret)

        self.xero_api_client = ApiClient(
            configuration=Configuration(oauth2_token=oauth2_token),
            oauth2_token_saver=self.set_xero_oauth2_token,
            oauth2_token_getter=self.get_xero_oauth2_token
        )

    def get_xero_oauth2_token(self) -> dict:
        token = json.loads(
            keyring.get_password('com.xero.xoauth', f'{self.xoauth_connection_name}:token_set')
        )
        token['scope'] = self.xero_scopes
        return token

    def set_xero_oauth2_token(self, xero_oauth2_token: dict) -> None:
        keyring.set_password(
            'com.xero.xoauth',
            f'{self.xoauth_connection_name}:token_set',
            json.dumps(xero_oauth2_token)
        )

    def copy_customer(self):
        pass

    def get_all_shopify_customers(self) -> List[shopify.Customer]:
        with shopify.Session.temp(domain=self.shopify_shop_url, version=SHOPIFY_API_VERSION, token=self.shopify_access_token):
            return list(shopify.Customer.find(no_iter_next=False))

    def get_all_xero_contacts(self) -> Contacts:
        tenant_id = IdentityApi(self.xero_api_client).get_connections()[0].tenant_id
        return AccountingApi(self.xero_api_client).get_contacts(xero_tenant_id=tenant_id)
