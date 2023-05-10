import datetime
import decimal
import json

from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.forms.models import model_to_dict
from . import models
from . import status


@csrf_exempt
def new_order(request):
    http_bad_req = HttpResponseBadRequest()
    http_bad_req["Content-Type"] = 'text/plain'
    if request.method != "POST":
        http_bad_req.content = "POST request expected\n"
        http_bad_req.status_code = 405
        return http_bad_req

    params = json.loads(request.body)
    payee_order_id = params.get("payee_order_id")
    if payee_order_id is None:
        http_bad_req.content = "payee_order_id missing\n"
        http_bad_req.status_code = 405
        return http_bad_req

    order = models.OrderDetails.objects.create(total_price=0.00, payment_status=status.Status.ORDER_CREATED,
                                               payee_order_id=payee_order_id)

    payload = {"order_id": order.id}
    response = HttpResponse(json.dumps(payload))
    response["Content-Type"] = 'application/json'
    response.status_code = 200
    response.reason_phrase = "OK"

    return response


@csrf_exempt
def add_item(request):
    http_bad_req = HttpResponseBadRequest()
    http_bad_req["Content-Type"] = 'text/plain'
    if request.method != "POST":
        http_bad_req.content = "POST request expected\n"
        http_bad_req.status_code = 405
        return http_bad_req

    params = json.loads(request.body)
    order_id = params.get('order_id', False)
    item_type = params.get('item_type', False)
    item_price = params.get('item_price', False)
    payee_item_id = params.get('payee_item_id', False)
    metadata = params.get('metadata', False)
    if not (order_id and item_type and item_price and payee_item_id and metadata):
        http_bad_req.content = "Missing parameter\n"
        http_bad_req.status_code = 405
        return http_bad_req

    try:
        ord = models.OrderDetails.objects.get(id=order_id)
    except ObjectDoesNotExist:
        http_bad_req.content = "Order ID does not exist\n"
        http_bad_req.status_code = 404
        return http_bad_req

    models.ItemDetails.objects.create(order=ord, item_type=item_type, item_price=item_price,
                                      payee_item_id=payee_item_id, metadata=metadata)
    ord.total_price = ord.total_price + decimal.Decimal(item_price)
    ord.save()

    response = HttpResponse(json.dumps({"error_code": ""}))
    response["Content-Type"] = 'application/json'
    response.status_code = 200
    response.reason_phrase = "OK"
    return response


def get_order_details(request, order_id):
    http_bad_req = HttpResponseBadRequest()
    http_bad_req["Content-Type"] = 'text/plain'
    if request.method != "GET":
        http_bad_req.content = "GET request expected\n"
        http_bad_req.status_code = 405
        return http_bad_req

    try:
        order = models.OrderDetails.objects.get(id=order_id)
    except ObjectDoesNotExist:
        http_bad_req.content = "Order ID does not exist\n"
        http_bad_req.status_code = 404
        return http_bad_req

    items = models.ItemDetails.objects.filter(order=order.id)
    item_list = []
    for i in items:
        d = model_to_dict(i)
        d["item_price"] = float(d["item_price"])
        item_list.append(d)
    print(item_list)
    payload = {"order_id": order.id, "order_item_quantity": len(items), "order_value": float(order.total_price),
               "order_payment_status": order.payment_status, "items": item_list}
    response = HttpResponse(json.dumps(payload))
    response["Content-Type"] = 'application/json'
    response.status_code = 200
    response.reason_phrase = "OK"

    return response


def get_order_status(request, order_id):
    http_bad_req = HttpResponseBadRequest()
    http_bad_req["Content-Type"] = 'text/plain'
    if request.method != "GET":
        http_bad_req.content = "GET request expected\n"
        http_bad_req.status_code = 405
        return http_bad_req

    try:
        order = models.OrderDetails.objects.get(id=order_id)
    except ObjectDoesNotExist:
        http_bad_req.content = "Order ID does not exist\n"
        http_bad_req.status_code = 404
        return http_bad_req

    payload = {"status": order.payment_status}
    response = HttpResponse(json.dumps(payload))
    response["Content-Type"] = 'application/json'
    response.status_code = 200
    response.reason_phrase = "OK"

    return response


@csrf_exempt
def register_payment_method(request):
    http_bad_req = HttpResponseBadRequest()
    http_bad_req["Content-Type"] = 'text/plain'
    if request.method != "POST":
        http_bad_req.content = "POST request expected\n"
        http_bad_req.status_code = 405
        return http_bad_req

    params = json.loads(request.body)
    expiry_date = params.get('expiry_date', False)
    card_number = params.get('card_number', False)
    cvv = params.get('cvv', False)
    cardholder_name = params.get('cardholder_name', False)
    if not (expiry_date and card_number and cvv and cardholder_name):
        http_bad_req.content = "Missing parameter\n"
        http_bad_req.status_code = 405
        return http_bad_req

    exp = datetime.datetime.strptime(params["expiry_date"], "%m/%y")
    pm = models.PaymentMethodDetails.objects.create(card_number=params["card_number"], cvv=params["cvv"],
                                                    cardholder_name=params["cardholder_name"],
                                                    expiry_date=exp)
    payload = {"payment_method_id": pm.id}
    response = HttpResponse(json.dumps(payload))
    response["Content-Type"] = 'application/json'
    response.status_code = 200
    response.reason_phrase = "OK"

    return response


@csrf_exempt
def pay_for_order(request):
    http_bad_req = HttpResponseBadRequest()
    http_bad_req["Content-Type"] = 'text/plain'
    if request.method != "POST":
        http_bad_req.content = "POST request expected\n"
        http_bad_req.status_code = 405
        return http_bad_req

    params = json.loads(request.body)
    order_id = params.get('order_id')
    payment_method_id = params.get('payment_method_id')
    if not (order_id and payment_method_id):
        http_bad_req.content = "Missing parameter\n"
        http_bad_req.status_code = 405
        return http_bad_req

    try:
        order = models.OrderDetails.objects.get(id=order_id)
        pm = models.PaymentMethodDetails.objects.get(id=payment_method_id)
    except ObjectDoesNotExist:
        http_bad_req.content = "ID does not exist\n"
        http_bad_req.status_code = 404
        return http_bad_req

    if order.payment_status == status.Status.SUCCESSFUL or order.payment_status == status.Status.CANCELLED:
        http_bad_req.content = "Order already paid for or cancelled\n"
        http_bad_req.status_code = 405
        return http_bad_req

    order.payment_method = pm
    order.payment_status = status.Status.PENDING
    order.save()

    response = HttpResponse(json.dumps({"error_code": ""}))
    response["Content-Type"] = 'text/plain'
    response.status_code = 200
    response.reason_phrase = "OK"
    return response


@csrf_exempt
def cancel_order(request):
    http_bad_req = HttpResponseBadRequest()
    http_bad_req["Content-Type"] = 'text/plain'
    if request.method != "POST":
        http_bad_req.content = "POST request expected\n"
        http_bad_req.status_code = 405
        return http_bad_req

    params = json.loads(request.body)
    order_id = params.get('order_id')
    payment_method_id = params.get('payment_method_id')
    if not (order_id and payment_method_id):
        http_bad_req.content = "Missing parameter\n"
        http_bad_req.status_code = 405
        return http_bad_req

    try:
        order = models.OrderDetails.objects.get(id=order_id)
        pm = models.PaymentMethodDetails.objects.get(id=payment_method_id)
    except ObjectDoesNotExist:
        http_bad_req.content = "ID does not exist\n"
        http_bad_req.status_code = 404
        return http_bad_req

    order.payment_status = status.Status.CANCELLED
    order.save()

    response = HttpResponse(json.dumps({"error_code": ""}))
    response["Content-Type"] = 'text/plain'
    response.status_code = 200
    response.reason_phrase = "OK"
    return response
