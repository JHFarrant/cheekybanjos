import logging
import json

from .core import BanjosAPIObject
from .exceptions import CheekyException

logger = logging.getLogger(__name__)

class Checkout(BanjosAPIObject):
    userAddresses = None
    suggestedAddresses = None
    slots = None
    basket = None
    postCode = None
    locationId = None
    
    _selected_delivery_slot = None
    _selected_address = None
    _selected_card = None

    def __init__(self, _client, basket, vals):
        super(Checkout, self).__init__(_client, vals)
        self.basket = basket
        self.slots = [DeliverySlot(self._client, slot) for slot in vals.get("slots", [])]

    def select_delivery_slot(self, deliverySlot):
        self._selected_delivery_slot = deliverySlot

    def select_card(self, card):
        self._selected_card = card

    def select_address(self, address):
        self._selected_address = address

    def use_default_card(self):
        self.select_card(self._client.wallet.default_card)

    def use_default_address(self):
        self.select_address(self._client.addressBook.default_addresses)

    def use_asap_delivery_slot(self):
        if len(self.slots) < 1:
            raise CheekyException("No delivery slots available for this restaurant at the moment.")
        soonest_delivery_time = sorted(self.slots, key=lambda x: x.deliveryTime)[0]
        self.select_delivery_slot(soonest_delivery_time)

    def order_and_pay(self, csv, allowed_extras_limit=None):
        self.order(allowed_extras_limit)
        self.provision_payment()
        self.make_payment(csv)

    def order(self, allowed_extras_limit=None):
        if allowed_extras_limit is None:
            allowed_extras_limit = 2.5

        data = {"commit": True,
                "locationId": self.locationId,
                  "fulfillment": {
                        "deliveryTime": self._selected_delivery_slot.deliveryTime,
                        "type": "deliver",
                        "destination": {
                          "type": "saved_address",
                          "id": self._selected_address.id
                        }
                      }
                 }
        data["items"] = [ item.checkout_data() for item in self.basket.items]
        resp = self._client._request("/v1/order", method="POST", data=json.dumps(data))
        self.total = resp["total"]
        self.extras = resp["extras"]
        total_extras = sum([extra["price"] for extra in self.extras])
        if allowed_extras_limit < total_extras:
            raise CheekyException("Excessive extras over limit added. Change limit or adjust basket.")
        if self.total - total_extras != sum([item.pricePaid for item in self.basket.items]):
            raise CheekyException("Total price is not as expected acording to menu.")
        self.billId = resp["id"]

    def provision_payment(self):
        data = {
                  "billId": self.billId,
                  "cardId": 1,
                  "amounts": {
                    "totalExcludingTip": self.total,
                    "tip": 0,
                    "service": 0,
                    "decimal": True
                  }
                }
        resp = self._client._request("/payment-service/v2/payment/provision", method="POST", data=json.dumps(data))
        
        self.paymentHash = resp["hash"]

    def make_payment(self, csv):
        data ={
                  "hash": self.paymentHash,
                  "cvc": csv,
                  "orderId": self.billId
                }
        resp = self._client._request("/payment-service/v2/payment/make", method="POST", data=json.dumps(data))
        

    def track_order(self):
        resp = self._client._request(F"/payment-service/v5/order/{self.billId}")

class DeliverySlot(BanjosAPIObject):
    deliveryTime = None