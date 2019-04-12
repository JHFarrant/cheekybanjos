import logging

from .core import BanjosAPIObject
from .exceptions import CheekyException

logger = logging.getLogger(__name__)

class AddressBook(BanjosAPIObject):
    default = None
    addresses = None

    def __init__(self, _client, vals):
        super(AddressBook, self).__init__(_client, vals)
        self.addresses = [Address(self._client, address) for address in vals.get("addresses", [])]

    @property
    def default_addresses(self):
        if self.default is None:
            raise CheekyException("No default address is set. Go online to set a address.")
        default_addresses = [address for address in self.addresses if address.id == self.default]
        assert len(default_addresses) == 1
        return default_addresses[0]

class Address(BanjosAPIObject):
    id = None
    line1 = None
    line2 = None
    city = None
    postCode = None
    county = None
    location = None

class Wallet(BanjosAPIObject):
    default = None
    wallet = None

    def __init__(self, _client, vals):
        super(Wallet, self).__init__(_client, vals)
        self.wallet = [BankCard(self._client, card) for card in vals.get("wallet", [])]

    @property
    def default_card(self):
        if self.default is None:
            raise CheekyException("No default card set. Go online to set a default card.")
        default_card = [card for card in self.wallet if card.id == self.default]
        assert len(default_card) == 1
        return default_card[0]
    
class BankCard(BanjosAPIObject):
    id = None
    expiryMonth = None
    expiryYear = None
    last4Digits = None
    cardType = None
    nickname = None
    temporary = None
