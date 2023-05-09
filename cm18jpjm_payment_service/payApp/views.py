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
    order = models.OrderDetails.objects.create(total_price =0.00, payment_status=status.Status.ORDER_CREATED,
                                               payee_order_id=params.get("payee_order_id", False))

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
    try:
        ord = models.OrderDetails.objects.get(id=params.get('order_id'))
    except ObjectDoesNotExist:
        http_bad_req.content = "Order ID does not exist\n"
        http_bad_req.status_code = 404
        return http_bad_req

    models.ItemDetails.objects.create(order=ord, item_type=params.get("item_type"), item_price=params.get("item_price"),
                                      payee_item_id=params.get("payee_item_id"), metadata=params.get("metadata"))
    ord.total_price = ord.total_price + decimal.Decimal(params.get("item_price"))
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
    try:
        order = models.OrderDetails.objects.get(id=params["order_id"])
        pm = models.PaymentMethodDetails.objects.get(id=params["payment_method_id"])
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
    try:
        order = models.OrderDetails.objects.get(id=params["order_id"])
        pm = models.PaymentMethodDetails.objects.get(id=params["payment_method_id"])
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
