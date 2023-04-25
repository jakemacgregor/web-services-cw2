import decimal

from django.db import models
from . import status


class PaymentMethodDetails(models.Model):
    card_number = models.BigIntegerField()
    cvv = models.IntegerField()
    expiry_date = models.DateField()
    cardholder_name = models.CharField(max_length=30)


class OrderDetails(models.Model):
    total_price = models.DecimalField(decimal_places=2, max_digits=10, default=decimal.Decimal(0.00))
    payment_method = models.ForeignKey(PaymentMethodDetails, on_delete=models.PROTECT, null=True, blank=True)
    payment_status = models.IntegerField(default=int(status.Status.ORDER_CREATED))
    payee_order_id = models.IntegerField(default=0)


class ItemDetails(models.Model):
    order = models.ForeignKey(OrderDetails, on_delete=models.CASCADE)
    item_name = models.CharField(max_length=30)
    item_price = models.DecimalField(decimal_places=2, max_digits=10, default=decimal.Decimal(0.00))
