from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def new_order(request):
    return HttpResponse('not yet implemented')


@csrf_exempt
def add_item(request):
    return HttpResponse('not yet implemented')


def get_order_details(request, order_id):
    return HttpResponse('not yet implemented')


def get_order_status(request, order_id):
    return HttpResponse('not yet implemented')


@csrf_exempt
def register_payment_method(request):
    return HttpResponse('not yet implemented')


@csrf_exempt
def pay_for_order(request):
    return HttpResponse('not yet implemented')


@csrf_exempt
def cancel_order(request):
    return HttpResponse('not yet implemented')
