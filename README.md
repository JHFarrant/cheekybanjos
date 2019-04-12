![](https://travis-ci.org/JHFarrant/cheekybanjos.svg?branch=master)

# Cheeky Banjos (Unofficial Nandos Delivery Python Client)

### For people who need chicken and don't have time to leave the terminal

## Quick Start

* You first need an account a nandos delivery account. https://get.nandos.co.uk/
* Set a default address and a default bank card

```python
from cheekybanjos import BanjosAPIClient

client = BanjosAPIClient("example@gmail.com", "chicken123")
restaurant = client.find_restaurant("SW1 1AA")
basket = restaurant.current_basket

# Find menu item in menu
menu_item = restaurant.menu.select("Burgers", "Butterfly Burger").portions[0]

# Add menu item to basket
butterfly_burger = basket.add_item(menu_item)
# Add Sauce (Mandatory)
butterfly_burger.add_modifier("PERi-ometer").add_pickOption("Medium")
# Choose how many sides (Mandatory)
butterfly_burger.add_modifier("Specials Choice").add_pickOption("2 Regular Sides").add_modifier("2 Regular Sides").add_pickOptions("PERi-Salted Chips", "Garlic Bread")


print(basket)

# Checkout
checkout = basket.checkout(asap=True, default_address=True, default_card=True)
# Provide Credit Card CVS
checkout.order_and_pay("123")
```


## Todo

- [x] Basic Tests
- [ ] Validation of modifier pick options based on menu parameters
- [ ] PIP package
