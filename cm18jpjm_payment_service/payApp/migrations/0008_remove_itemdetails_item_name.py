# Generated by Django 4.1.7 on 2023-05-09 16:02

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('payApp', '0007_alter_orderdetails_payee_order_id'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='itemdetails',
            name='item_name',
        ),
    ]
