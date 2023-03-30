from django.contrib import admin
from .models import PaymentMethodDetails, OrderDetails, ItemDetails

# Register your models here.
admin.site.register(PaymentMethodDetails)
admin.site.register(OrderDetails)
admin.site.register(ItemDetails)