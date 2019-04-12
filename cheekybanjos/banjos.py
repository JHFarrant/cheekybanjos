import logging
import json
import weakref

import requests

from .menu import *
from .basket import *
from .checkout import * 
from .restaurant import *
from .user import *
from .exceptions import CheekyException

logger = logging.getLogger(__name__)

class BanjosAPIClient():
    restaurant = None
    username = None
    password = None
    base_url = "https://get.nandos.co.uk/api"
    headers = None
    sessionId = None
    name = None
    wallet = None
    addressBook = None

    def __init__(self, username, password):
        self.login(username, password)
        self.get_wallet()
        self.get_addressBook()
        # pass

    def login(self, username, password):

        resp = self._request("/v1/login",
                             method="POST",
                             data=json.dumps({"username":username, "password":password}))
        self.sessionId = resp["sessionId"]
        self.name = resp["customerName"]
        logger.info("Logged in as "+ self.name)

    def _request(self,path,method="GET", params=None, data=None, extra_headers=None):
        if not self.sessionId:
            logger.debug("Retrieving new sessionID")
            self.sessionId = requests.post(self.base_url + "/v1/session").json()["sessionId"]
            logger.debug(F"New sessionID = {self.sessionId}")
        headers = {"sessionid": self.sessionId, "content-type":"application/json","Accept": "*/*"}
        if extra_headers: headers.update(extra_headers)
        logger.debug(self.base_url + path)
        logger.debug(headers)
        logger.debug(data)
        logger.debug(params)
        if method == "POST":
            resp = requests.post(self.base_url + path, data=data, headers=headers)
        else:
            resp = requests.get(self.base_url + path, params=params, headers=headers)
        logger.debug(resp.text)
        return resp.json()

    def find_restaurant(self, postcode, lat=0.0, lng=0.0):
        resp = self._request("/v2/location/search", params={"postcode":postcode,
                                                            "lat":lat,
                                                            "lng":lng})
        if not resp["deliveryEstimate"]:
            CheekyException("No local restaurant found...")
        else:
            self.postcode = postcode
            self.restaurant = Restaurant(self, resp["deliveryEstimate"])
            logger.info("Restaurant and Menu loaded")
        return self.restaurant

    def get_wallet(self):
        resp = self._request("/payment-service/v1/flyt/user/user_uuid/wallet")
        self.wallet = Wallet(self, resp)
        logger.info("Wallet loaded")

    def get_addressBook(self):
        resp = self._request("/payment-service/v1/flyt/user/user_uuid/addresses")
        self.addressBook = AddressBook(self, resp)
        logger.info("AddressBook loaded")
