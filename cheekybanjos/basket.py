import logging
import json

from .core import *
from .checkout import Checkout

logger = logging.getLogger(__name__)

class Basket(BanjosAPIObject):
    items = None
    restaurant = None
    checkout = None

    def __init__(self, _client, vals):
        self.items = []
        super(Basket, self).__init__(_client, vals)

    def add_item(self, portion):
        vals = {"id": portion.id,
               "portionId": portion.id,
               "name":portion.name,
               "stockLevel":portion.ingredient.stockLevel,
               "originalPrice": portion.ingredient.addPrice,
               "_ingredient":portion.ingredient}
        item = BasketItem(self._client, vals)
        self.items.append(item)
        logger.info(F"Item {item.name} added to basket at price {item.pricePaid}")
        return item

    def checkout(self, asap=True, default_address=True, default_card=True):
        checkout_data = self._get_checkout_prefill() 
        self.checkout = Checkout(self._client, self, checkout_data)
        self.checkout.locationId = self._client.restaurant.locationId
        if default_address: 
            self.checkout.use_default_address()
        if default_card:
            self.checkout.use_default_card()
        if asap:
            self.checkout.use_asap_delivery_slot()
        return self.checkout

    def _get_checkout_prefill(self):
        data = {"postCode": self._client.postcode,
                "locationId": self._client.restaurant.locationId,
                "deliveryTime": self._client.restaurant.deliveryTime
                 }

        data["items"] = [ item.checkout_data() for item in self.items]
        resp = self._client._request("/v1/checkout/prefill", method="POST", data=json.dumps(data))
        return resp

    def __str__(self):
        ret = "####### BASKET #######\n"
        for item in self.items:
            ret += item.name + "       " + str(item.pricePaid) + "\n"
            for mod in item.modifiers: 
                ret += "     " + mod.name + "\n"
                for po in mod.pickOptions:
                    ret += "         " + po.name + "\n"
                    for mod in po.modifiers:
                        ret += "             " + mod.name + "\n"
                        for po in mod.pickOptions:
                            ret += "                  " + po.name + "\n"
        return ret



class BasketItem(BanjosAPIObject):
    id = None
    portionId = None
    name = None
    originalPrice = None
    modifiers = None
    stockLevel = None
    _ingredient = None

    @property
    def pricePaid(self):
        return self.originalPrice + sum([mod.get_addPrice() for mod in self.modifiers])


    def __init__(self, _client, vals):
        self.modifiers = []
        super(BasketItem, self).__init__(_client, vals)

    def add_modifier(self, modifier):
        if type(modifier) == str:
            modifier = self._ingredient.select(modifier)
        vals = {"id":modifier.id,
                "modifierId":modifier.id,
                "name":modifier.name,
                "_modifier": modifier}
        basket_item_modifier = BasketItemModifier(self._client, vals)
        self.validate_modifier(basket_item_modifier)
        self.modifiers.append(basket_item_modifier)
        logger.info(F"Item {self.name} modified with {modifier.name}")
        return basket_item_modifier

    def validate_modifier(self, basket_item_modifier):
        #TODO: Check for duplicated modifiers
        return True

    def checkout_data(self):
        data = dict(vars(self))
        [data.pop(key) for key in list(data.keys()) if key.startswith("_")]
        data["pricePaid"] = self.pricePaid

        if len(self.modifiers) > 0: 
            data["modifiers"] = [ mod.checkout_data() for mod in self.modifiers ]
        else:
            data.pop("modifiers")
        return data

class BasketItemModifier(BanjosAPIObject):
    id = None
    _modifier = None
    modifierId = None
    name = None
    pickOptions = None

    def __init__(self, _client, vals):
        self.pickOptions = []
        super(BasketItemModifier, self).__init__(_client, vals)

    def add_pickOption(self, pickOption):
        if type(pickOption) == str:
            pickOption = self._modifier.select(pickOption)
        vals = {"id": pickOption.id,
                "name": pickOption.name,
                "stockLevel": pickOption.stockLevel,
                "addPrice": pickOption.addPrice or 0.0,
                "_pickOption": pickOption}
        basket_item_pickOption = BasketItemModifierPickOption(self._client, vals)
        self.validate_pickOption(basket_item_pickOption)
        self.pickOptions.append(basket_item_pickOption)
        logger.info(F"Option {pickOption.name} chosen for modifier {self.name}")
        return basket_item_pickOption

    def add_pickOptions(self, *args):
        for pickOption in args:
            self.add_pickOption(pickOption)

    def validate_pickOption(self, basket_item_pickOption):
        #TODO: Check against modifier rules
        return True
    
    def checkout_data(self):
        data = dict(vars(self))
        [data.pop(key) for key in list(data.keys()) if key.startswith("_")]

        data["selected"] = True
        data["pickOptions"] = [ po.checkout_data() for po in self.pickOptions ]
        return data

    def get_addPrice(self):
        return sum([po.get_addPrice() for po in self.pickOptions])

class BasketItemModifierPickOption(BanjosAPIObject):
    id = None
    name = None
    stockLevel = None
    selected = True
    modifiers = None
    addPrice = None
    _pickOption = None

    def __init__(self, _client, vals):
        self.addPrice = 0.0
        self.modifiers = []
        super(BasketItemModifierPickOption, self).__init__(_client, vals)

    def add_modifier(self, modifier):
        if type(modifier) == str:
            modifier = self._pickOption.select(modifier)
        vals = {"id": modifier.id,
                "modifierId": modifier.id,
                "name": modifier.name,
                "_modifier": modifier}
        item_modifier = BasketItemModifier(self._client, vals)
        self.modifiers.append(item_modifier)
        return item_modifier

    def checkout_data(self):
        data = dict(vars(self))
        [data.pop(key) for key in list(data.keys()) if key.startswith("_")]
        data["selected"] = True
        if len(self.modifiers) > 0: 
            data["modifiers"] = [ mod.checkout_data() for mod in self.modifiers ]
        else:
            data.pop("modifiers")
        if self.addPrice == 0.0:
            data.pop("addPrice")
        return data

    def get_addPrice(self):
        return self.addPrice + sum([mod.get_addPrice() for mod in self.modifiers]) 
