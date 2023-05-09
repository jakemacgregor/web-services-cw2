import requests

# Tests each view in turn

# Create order
url = "http://127.0.0.1:8000/order/new/"
req = {"payee_order_id": 123}
a = requests.post(url, json= req)
print(a.text)
_ = input("continue?")
order_id = a.json().get("order_id")

# Add an item
url = "http://127.0.0.1:8000/order/add/"
req = {
    "order_id": int(order_id),
    "item_type": "TICKET",
    "item_price": 10.01,
    "payee_item_id": 1,
    "metadata": {
        "flight_data": "12/04/1923",
    },
}
a = requests.post(url, json = req)
print(a.text)
_ = input("continue?")

# Get order
url = f"http://127.0.0.1:8000/order/{order_id}"
a = requests.get(url)
print(a.text)
_ = input("continue?")

# Get order status
url = f"http://127.0.0.1:8000/order/{order_id}/status"
a = requests.get(url)
print(a.text)
_ = input("continue?")

# Register payment method
url = "http://127.0.0.1:8000/paymentmethod/new/"
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
url = "http://127.0.0.1:8000/order/pay/"
req = {
    "order_id": order_id,
    "payment_method_id": payment_method_id,
}
a = requests.post(url, json=req)
print(a.text)
url = f"http://127.0.0.1:8000/order/{order_id}"
a = requests.get(url)
print(a.text)
_ = input("continue?")

# Cancel the order
url = "http://127.0.0.1:8000/order/cancel/"
a = requests.post(url, json=req)
print(a.text)
url = f"http://127.0.0.1:8000/order/{order_id}"
a = requests.get(url)
print(a.text)