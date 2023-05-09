import decimal

from django.db import models
from . import status, item_types


class PaymentMethodDetails(models.Model):
    card_number = models.CharField(max_length=16)
    cvv = models.CharField(max_length=4)
    expiry_date = models.DateField()
    cardholder_name = models.CharField(max_length=30)


class OrderDetails(models.Model):
    total_price = models.DecimalField(decimal_places=2, max_digits=10, default=decimal.Decimal(0.00))
    payment_method = models.ForeignKey(PaymentMethodDetails, on_delete=models.PROTECT, null=True, blank=True)
    payment_status = models.IntegerField(default=int(status.Status.ORDER_CREATED))
    payee_order_id = models.IntegerField(blank=False)


class ItemDetails(models.Model):
    order = models.ForeignKey(OrderDetails, on_delete=models.CASCADE)
    item_type = models.CharField(max_length=100)
    payee_item_id = models.IntegerField(default=0)
    metadata = models.JSONField()
    item_price = models.DecimalField(decimal_places=2, max_digits=10, default=decimal.Decimal(0.00))
