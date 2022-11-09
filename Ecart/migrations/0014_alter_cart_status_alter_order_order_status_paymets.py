# Generated by Django 4.1.2 on 2022-11-09 05:13

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Ecart', '0013_alter_cart_status_alter_order_order_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cart',
            name='status',
            field=models.IntegerField(choices=[(1, 'pending'), (2, 'success'), (0, 'failed')], default=1),
        ),
        migrations.AlterField(
            model_name='order',
            name='order_status',
            field=models.IntegerField(choices=[(1, 'pending'), (2, 'success'), (0, 'failed')], default=1),
        ),
        migrations.CreateModel(
            name='Paymets',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('transaction_id', models.CharField(max_length=200)),
                ('payment_satus', models.CharField(max_length=200)),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Ecart.order')),
            ],
        ),
    ]