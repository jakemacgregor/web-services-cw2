import requests

# Tests each view in turn
if bool(input("Use pythonanywhere? (enter True if not using localhost)")):
    urlprefix = "http://cm18jpjm.pythonanywhere.com/"
else:
    urlprefix = "http://127.0.0.1:8000/"

# Create order
url = urlprefix + "order/new/"
req = {"payee_order_id": 123}
a = requests.post(url, json= req)
print(a.text)
_ = input("continue?")
order_id = a.json().get("order_id")

# Add an item
url = urlprefix + "order/add/"
req = {
    "order_id": int(order_id),
    "item_type": "TICKET",
    "item_price": 10.01,
    "payee_item_id": 1,
    "metadata": {
        "flight_data": "09/12/1999",
        "flight_no": "XYZ789",
        "departure_airport": "JFK",
        "arrival_airport": "LAX",
        "seat": "B3",
    },
}
a = requests.post(url, json = req)
print(a.text)
_ = input("continue?")

req = {
    "order_id": int(order_id),
    "item_type": "TICKET",
    "item_price": 17.71,
    "payee_item_id": 321,
    "metadata": {
        "flight_data": "11/02/1283",
        "flight_no": "ABC123",
        "departure_airport": "LHR",
        "arrival_airport": "MAN",
        "seat": "A1",
    },
}
a = requests.post(url, json = req)

# Get order
url = f"{urlprefix}order/{order_id}"
a = requests.get(url)
print(a.text)
_ = input("continue?")

# Get order status
url = f"{urlprefix}order/{order_id}/status"
a = requests.get(url)
print(a.text)
_ = input("continue?")

# Register payment method
url = f"{urlprefix}paymentmethod/new/"
req = {
    "card_number": "5355220012345678",
    "expiry_date": "06/27",
    "cvv": "065",
    "cardholder_name": "J MacGregor",
}
a = requests.post(url, json=req)
print(a.text)
_ = input("continue?")
payment_method_id = a.json().get("payment_method_id")

# Pay for an order
url = urlprefix + "order/pay/"
req = {
    "order_id": order_id,
    "payment_method_id": payment_method_id,
}
a = requests.post(url, json=req)
print(a.text)
url = f"{urlprefix}order/{order_id}"
a = requests.get(url)
print(a.text)
_ = input("continue?")

# Cancel the order
url = urlprefix + "order/cancel/"
a = requests.post(url, json=req)
print(a.text)
url = f"{urlprefix}order/{order_id}"
a = requests.get(url)
print(a.text)