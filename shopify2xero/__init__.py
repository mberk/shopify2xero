import json
from pathlib import Path
from typing import List

import keyring
import shopify
from xero_python.accounting import AccountingApi
from xero_python.accounting.models.contact import Contact
from xero_python.accounting.models.contacts import Contacts
from xero_python.accounting.models.invoice import Invoice
from xero_python.accounting.models.invoices import Invoices
from xero_python.accounting.models.item import Item
from xero_python.accounting.models.line_item import LineItem
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

        self.xero_tenant_id = IdentityApi(self.xero_api_client).get_connections()[0].tenant_id

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

    def copy_customer(self, customer_id: int, update: bool = False) -> None:
        customer = self.get_shopify_customer(customer_id)

        existing_contact = None
        if update:
            existing_contact = next(
                iter(
                    AccountingApi(self.xero_api_client).get_contacts(
                        xero_tenant_id=self.xero_tenant_id,
                        where=f'name="{customer.first_name} {customer.last_name}"'
                    ).contacts
                ),
                None
            )

        new_contact = Contact(
            name=f'{customer.first_name} {customer.last_name}',
            first_name=customer.first_name,
            last_name=customer.last_name,
            email_address=customer.email,
            is_customer=True,
            contact_number=str(customer_id)
        )

        if existing_contact is not None:
            AccountingApi(self.xero_api_client).update_contact(
                xero_tenant_id=self.xero_tenant_id,
                contact_id=existing_contact.contact_id,
                contacts=Contacts(contacts=[new_contact])
            )
        else:
            AccountingApi(self.xero_api_client).create_contacts(
                xero_tenant_id=self.xero_tenant_id,
                contacts=Contacts(contacts=[new_contact])
            )

    def get_all_shopify_customers(self) -> List[shopify.Customer]:
        with shopify.Session.temp(domain=self.shopify_shop_url, version=SHOPIFY_API_VERSION, token=self.shopify_access_token):
            return list(shopify.Customer.find(no_iter_next=False))

    def get_all_xero_contacts(self) -> List[Contact]:
        return AccountingApi(self.xero_api_client).get_contacts(xero_tenant_id=self.xero_tenant_id).contacts

    def get_all_xero_items(self) -> List[Item]:
        return AccountingApi(self.xero_api_client).get_items(xero_tenant_id=self.xero_tenant_id).items

    def get_shopify_customer(self, customer_id: int) -> shopify.Customer:
        with shopify.Session.temp(domain=self.shopify_shop_url, version=SHOPIFY_API_VERSION, token=self.shopify_access_token):
            return shopify.Customer.find(id_=customer_id)

    def get_shopify_order(self, order_id: int) -> shopify.Order:
        with shopify.Session.temp(domain=self.shopify_shop_url, version=SHOPIFY_API_VERSION, token=self.shopify_access_token):
            return shopify.Order.find(id_=order_id)
