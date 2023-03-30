from django.db import models


class PaymentMethodDetails(models.Model):
    card_number = models.BigIntegerField
    cvv = models.IntegerField
    expiry_date = models.DateField
    cardholder_name = models.CharField(max_length=30)


class OrderDetails(models.Model):
    total_price = models.DecimalField
    payment_method = models.ForeignKey(PaymentMethodDetails, on_delete=models.PROTECT)
    payment_status = models.IntegerField


class ItemDetails(models.Model):
    order = models.ForeignKey(OrderDetails, on_delete=models.CASCADE)
    item_name = models.CharField(max_length=30)
    item_price = models.DecimalField

