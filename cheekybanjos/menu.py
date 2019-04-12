import logging

from .core import BanjosAPIObject
from .exceptions import CheekyException

logger = logging.getLogger(__name__)

class Menu(BanjosAPIObject):
    id = None
    name = None
    revision = None
    categories = None

    def __init__(self, _client, vals):
        super(Menu, self).__init__(_client, vals)
        self.categories = [MenuCategory(self._client, category) for category in vals.get("categories", [])]

    def select(self, *search):
        return self._select(self.categories, search)

    # def quick_add(self, category_name, item_name, modifiers):
    #     item = self.select([category,item]
    #     basket.add_item(
    #         )
    #     chicken_butterfly = basket.add_item(butterfly_burger_portion)


class MenuCategory(BanjosAPIObject):
    id = None
    name = None
    description = None
    items = None
    tags = None
    uuid = None

    def __init__(self, _client, vals):
        super(MenuCategory, self).__init__(_client, vals)
        self.items = [MenuItem(self._client, item) for item in vals.get("items", [])]

    def select(self, *search):
        return self._select(self.items, search)
        
class MenuItem(BanjosAPIObject):
    id = None
    name = None
    customisationType = None
    portions = None
    tags = None
    uuid = None

    def __init__(self, _client, vals):
        super(MenuItem, self).__init__(_client, vals)
        self.portions = [MenuPortion(self._client, portion) for portion in vals.get("portions", [])]


class MenuPortion(BanjosAPIObject):
    id = None
    name = None
    ingredient = None
    items = None
    tags = None

    def __init__(self, _client, vals):
        super(MenuPortion, self).__init__(_client, vals)
        ingredient = vals.get("ingredient")
        if ingredient:
            self.ingredient = MenuIngredient(self._client, ingredient)
    
    def select(self, *search):
        if self.ingredient is None:
            raise CheekyException("Menu Portion has no Ingredient")
        return self.ingredient.select(*search)

class MenuIngredient(BanjosAPIObject):
    id = None
    name = None
    description = None
    addPrice = None
    modifiers = None
    contains = None
    nutrition = None
    slots = None
    stockLevel = None
    suitableFor = None
    tags = None

    def __init__(self, _client, vals):
        super(MenuIngredient, self).__init__(_client, vals)
        self.modifiers = [MenuModifier(self._client, modifier) for modifier in vals.get("modifiers", [])]

    def select(self, *search):
        return self._select(self.modifiers, search)

class MenuModifier(BanjosAPIObject):
    id = None
    name = None
    pickAtLeast = None
    pickAtMost = None
    pickOptions = None
    requirementType = None

    def __init__(self, _client, vals):
        super(MenuModifier, self).__init__(_client, vals)
        self.pickOptions = [MenuModifierPickOptions(self._client, option) for option in vals.get("pickOptions", [])]

    def select(self, *search):
        return self._select(self.pickOptions, search)

class MenuModifierPickOptions(BanjosAPIObject):
    id = None
    name = None
    stockLevel = None
    addPrice = None
    tags = None
    modifiers = None

    def __init__(self, _client, vals):
        super(MenuModifierPickOptions, self).__init__(_client, vals)
        self.modifiers = [MenuModifier(self._client, option) for option in vals.get("modifiers", [])]

    def select(self, *search):
        return self._select(self.modifiers, search)