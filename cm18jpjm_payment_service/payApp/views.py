import datetime
import json

from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from models import *
from status import Status


@csrf_exempt
def new_order(request):
    http_bad_req = HttpResponseBadRequest()
    http_bad_req["Content-Type"] = 'text/plain'

    if request.method != "POST":
        http_bad_req.content = "POST request expected\n"
        http_bad_req.status_code = 405
        return http_bad_req

    order = OrderDetails.objects.create(total_price=0.00, payment_status=Status.ORDER_CREATED)
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

    params = request.POST
    try:
        order = OrderDetails.objects.get(id=params["order_id"])
    except ObjectDoesNotExist:
        http_bad_req.content = "Order ID does not exist\n"
        http_bad_req.status_code = 404
        return http_bad_req

    ItemDetails.objects.create(order=order.id, item_name=params["item_name"], item_price=params["item_price"])
    response = HttpResponse()
    response["Content-Type"] = 'text/plain'
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
        order = OrderDetails.objects.get(id=order_id)
    except ObjectDoesNotExist:
        http_bad_req.content = "Order ID does not exist\n"
        http_bad_req.status_code = 404
        return http_bad_req

    items = ItemDetails.objects.filter(order=order.id)
    item_list = ""
    for i in items:
        item_list.join(f"{i['item_name']}; ")
    payload = {"order_id": order.id, "order_item_quantity": len(items), "order_value": order.total_price,
               "order_payment_status": order.payment_status, "items":item_list}
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
        order = OrderDetails.objects.get(id=order_id)
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

    params = request.POST

    # TODO: timestamps
    pm = PaymentMethodDetails.objects.create(card_number=params["card_number"], cvv=params["cvv"],
                                             cardholder_name=params["cardholder_name"],
                                             expiry_date=datetime.date.today())
    payload = {"payment_method_id": pm.id}
    response = HttpResponse(json.dumps(payload))
    response["Content-Type"] = 'application/json'
    response.status_code = 200
    response.reason_phrase = "OK"


@csrf_exempt
def pay_for_order(request):
    http_bad_req = HttpResponseBadRequest()
    http_bad_req["Content-Type"] = 'text/plain'

    if request.method != "POST":
        http_bad_req.content = "POST request expected\n"
        http_bad_req.status_code = 405
        return http_bad_req

    params = request.POST
    try:
        order = OrderDetails.objects.get(id=params["order_id"])
        pm = PaymentMethodDetails.objects.get(id=params["payment_method_id"])
    except ObjectDoesNotExist:
        http_bad_req.content = "ID does not exist\n"
        http_bad_req.status_code = 404
        return http_bad_req

    order.payment_method = pm.id
    order.payment_status = Status.PENDING
    order.save()

    response = HttpResponse()
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

    params = request.POST
    try:
        order = OrderDetails.objects.get(id=params["order_id"])
        pm = PaymentMethodDetails.objects.get(id=params["payment_method_id"])
    except ObjectDoesNotExist:
        http_bad_req.content = "ID does not exist\n"
        http_bad_req.status_code = 404
        return http_bad_req

    order.payment_status = Status.CANCELLED
    order.save()

    response = HttpResponse()
    response["Content-Type"] = 'text/plain'
    response.status_code = 200
    response.reason_phrase = "OK"
    return response