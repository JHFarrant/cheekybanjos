import logging

from .core import BanjosAPIObject
from .menu import Menu
from .basket import Basket

logger = logging.getLogger(__name__)

class Restaurant(BanjosAPIObject):
    locationId = None
    deliveryTime = None
    acceptingOrders = None
    open = None
    locationName = None
    address = None
    contactNumber = None
    current_basket = None

    def __init__(self, _client, vals):
        super(Restaurant, self).__init__(_client, vals)
        self.load_menu()
        self.current_basket = Basket(self._client, {"restaurant": self})

    def refresh(self):
        resp = self._client._request("/v2/location/"+self.locationId)
        self._update_values(resp)
        logger.info("Restaurant and Menu reloaded")

    def load_menu(self):
        resp = self._client._request(F"/v2/location/{self.locationId}/menu/3")
        self.menu = Menu(self._client, resp["menus"][0])

    def new_basket(self):
        logger.debug("Creating new basket...")
        self.current_basket = Basket(self._client, {"restaurant": self})