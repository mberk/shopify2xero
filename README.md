# shopify2xero

## Setup

### Xero

1. [Create a Xero App](https://github.com/XeroAPI/xero-python-oauth2-starter#create-a-xero-app)
2. Use [xoauth](https://github.com/XeroAPI/xoauth) to configure and store credentials
3. ...

### Shopify

1. ...

## Example Usage

### Reconciling a Shopify payout in Xero

**Before proceeding please see the [Known Issues](#known-issues). In particular, proceed with caution if your Shopify
payout includes refunds and/or your Shopify orders contain discounts**

Scenario:

* You have setup your bank feed in Xero and it's pulling in transactions for you to reconcile
* You have received a payout from Shopify that you want to reconcile
* In order to reconcile the payout, you will need a Xero invoice for each Shopify order in the payout
* To create a Xero invoice, you will need to create a Xero contact for the corresponding Shopify customer

The `shopify2xero` package aims to automate as much of this process as possible. You'll first have to:

* Add SKUs to each of the Shopify products in the orders associated with the payout
* Create corresponding Xero items (under Business > Products and Services on the Xero website) **where the item code
matches the Shopify SKU**

```python
from shopify2xero import Shopify2Xero
s2x = Shopify2Xero(xoauth_connection_name=..., shopify_shop_url=..., shopify_access_token=...)
s2x.copy_all_orders_for_payout(payout_date='2020-11-18')
```

```
2020-11-19 13:19:48,645 - shopify2xero - DEBUG - Copying order 0000000000001
2020-11-19 13:19:52,437 - shopify2xero - INFO - Created invoice INV-SHOPIFY-1001
2020-11-19 13:19:52,437 - shopify2xero - DEBUG - Copying order 0000000000002
2020-11-19 13:19:56,819 - shopify2xero - INFO - Created invoice INV-SHOPIFY-1002
2020-11-19 13:19:56,819 - shopify2xero - DEBUG - Copying order 0000000000003
2020-11-19 13:19:59,066 - shopify2xero - INFO - Created invoice INV-SHOPIFY-1003
2020-11-19 13:19:59,066 - shopify2xero - DEBUG - Copying order 0000000000004
2020-11-19 13:20:04,680 - shopify2xero - INFO - Created invoice INV-SHOPIFY-1004
PayoutSummary(date='2020-11-18', payout_amount='118.81', order_numbers=[1001, 1002, 1003, 1004], total_fees=3.4899999999999998)
```

Once this code has successfully run, everything should be in place for you to use the Xero website to reconcile the
payout.

**Note that any shipping costs in the Shopify orders will be assigned to the Xero account code 425** 

The return value of the `copy_all_orders_for_payout` method provides some summary information that may be useful when
doing the reconciliation:

* The `payout_amount` field should match the actual amount you received in the bank transaction. If it doesn't then your
orders probably contain discounts and you'll have to manually edit the invoices (for now)
* The `total_fees` field is a sanity check for when you create the adjustment during reconciliation

An example of how to actually do the reconciliation:

* Click "Find & Match" for the bank transaction
* Select the automatically generated invoices from the displayed set of unpaid invoices
* Click the `+Adjustments` button to create a bank fee transaction where the amount matches the Shopify fees you paid on
this payout

## Known Issues

* Handling Shopify discounts has not been thoroughly tested
* Refunds are not handled very well
* Shipping account code is hardcoded to `425`
* Taxes are probably not handled very well

Please create a GitHub issue if you encounter other problems or require a specific feature