# Generated by Django 4.1.2 on 2022-11-01 04:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Ecart', '0006_remove_cart_tax'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='order_price',
            field=models.IntegerField(null=True),
        ),
    ]
