import unittest
import pytest
import requests_mock

from cheekybanjos import BanjosAPIClient
from cheekybanjos.exceptions import CheekyException

import tests.mocks as mocks

class TestFullOrder(unittest.TestCase):

	def test_full_order(self):
		with requests_mock.Mocker() as mocker_context:
			mocker_context.post("https://get.nandos.co.uk/api/v1/session", status_code=200, text="""{"sessionId": "1234"}""")
			mocker_context.get("https://get.nandos.co.uk/api/payment-service/v1/flyt/user/user_uuid/addresses", status_code=200, text=mocks.GET_ADDRESS_JSON)
			mocker_context.get("https://get.nandos.co.uk/api/payment-service/v1/flyt/user/user_uuid/wallet", status_code=200, text=mocks.GET_WALLET_JSON)
			mocker_context.post("https://get.nandos.co.uk/api/v1/login", status_code=200, text=mocks.POST_LOGIN_JSON)
			client = BanjosAPIClient("user@example.com", "Chicken123")
		
		with requests_mock.Mocker() as mocker_context:
			mocker_context.get("https://get.nandos.co.uk/api/v2/location/search", status_code=200, text=mocks.GET_LOCATION_SEARCH_JSON)
			mocker_context.get("https://get.nandos.co.uk/api/v2/location/735/menu/3", status_code=200, text=mocks.GET_MENU_JSON)

			restaurant = client.find_restaurant("SW1A 1AA")

		basket = restaurant.current_basket

		chicken_butterfly_portion = restaurant.menu.categories[8].items[7].portions[0]

		cat = restaurant.menu.select("PERi-PERi")
		print(chicken_butterfly_portion.name)
		print(restaurant.menu.select("PERi-PERi").select("Chicken Butterfly").portions[0])

		self.assertEqual(restaurant.menu.select("PERi-PERi", "Chicken Butterfly"),restaurant.menu.select("PERi-PERi").select("Chicken Butterfly"))
		self.assertEqual(chicken_butterfly_portion,restaurant.menu.select("PERi-PERi", "Chicken Butterfly").portions[0])

		
		sauce_mod = chicken_butterfly_portion.ingredient.modifiers[0]
		self.assertEqual(sauce_mod, chicken_butterfly_portion.select("PERi-ometer"))
		
		medium_sauce_option = sauce_mod.pickOptions[2]
		self.assertEqual(medium_sauce_option, sauce_mod.select("Medium"))

		sides_mod = chicken_butterfly_portion.ingredient.modifiers[1]
		self.assertEqual(sides_mod, chicken_butterfly_portion.select("Butterfly Chicken Choice"))

		print(sides_mod.name)
		print([x.name for x in sides_mod.pickOptions])
		
		two_sides_option = sides_mod.pickOptions[1]
		self.assertEqual(two_sides_option, sides_mod.select("With 2 Regular Sides"))


		print(two_sides_option.name)

		two_sides_option_modifier = two_sides_option.modifiers[0]
		print(two_sides_option_modifier.name)
		print([x.name for x in two_sides_option_modifier.pickOptions])

		peri_chips_option = two_sides_option_modifier.pickOptions[1]
		print(peri_chips_option.name)

		garlic_bread_option = two_sides_option_modifier.pickOptions[5]
		print(garlic_bread_option.name)


		# Add item to basket
		chicken_butterfly = basket.add_item(chicken_butterfly_portion)
		# Add modifers on item
		# sauce
		chicken_butterfly.add_modifier(sauce_mod).add_pickOption(medium_sauce_option)
		# with 2 sides
		chicken_butterfly.add_modifier(sides_mod).add_pickOption(two_sides_option).add_modifier(two_sides_option_modifier).add_pickOptions(peri_chips_option, garlic_bread_option)

		# Checkout
		with requests_mock.Mocker() as mocker_context:

			mocker_context.post("https://get.nandos.co.uk/api/v1/checkout/prefill", status_code=200, text=mocks.POST_CHECKOUT_PREFILL_JSON)
			checkout = basket.checkout(asap=True, default_address=True, default_card=True)
		
		with requests_mock.Mocker() as mocker_context:
			mocker_context.post("https://get.nandos.co.uk/api/v1/order", status_code=200, text=mocks.POST_ORDER_JSON)
			mocker_context.post("https://get.nandos.co.uk/api/payment-service/v2/payment/provision", status_code=200, text=mocks.POST_PAYMENT_PROVISION_JSON)
			mocker_context.post("https://get.nandos.co.uk/api/payment-service/v2/payment/make", status_code=200, text=mocks.POST_PAYMENT_MAKE_JSON)

			with pytest.raises(CheekyException, match=r'Excessive extras over limit added\. Change limit or adjust basket\.'):
				checkout.order_and_pay("123")

			checkout.order_and_pay("123", allowed_extras_limit=6.0)
			

