# Generated by Django 4.1.2 on 2022-11-02 04:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Ecart', '0010_remove_product_in_stock_product_in_stocks'),
    ]

    operations = [
        migrations.AddField(
            model_name='cart',
            name='status',
            field=models.CharField(choices=[('pending', 'pending'), ('success', 'success'), ('failed', 'failed')], default='pending', max_length=60),
        ),
        migrations.AlterField(
            model_name='order',
            name='order_status',
            field=models.CharField(choices=[('pending', 'pending'), ('success', 'success'), ('failed', 'failed')], default='pending', max_length=60),
        ),
    ]
