# Generated by Django 4.1.7 on 2023-04-25 19:10

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('payApp', '0003_alter_orderdetails_payment_method'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderdetails',
            name='payment_method',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='payApp.paymentmethoddetails'),
        ),
    ]
