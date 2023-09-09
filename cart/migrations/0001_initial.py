# Generated by Django 4.2.1 on 2023-09-02 15:38

from django.db import migrations, models
import django.db.models.deletion
import django_jalali.db.models
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('products', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Cart',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False, unique=True)),
                ('created_date', django_jalali.db.models.jDateTimeField(auto_now_add=True)),
                ('done', models.BooleanField(default=False)),
            ],
            options={
                'verbose_name': 'Carts',
                'verbose_name_plural': 'Carts',
            },
        ),
        migrations.CreateModel(
            name='Items',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.IntegerField(default=0)),
                ('cart', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='item', to='cart.cart')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='product', to='products.products')),
            ],
            options={
                'verbose_name': 'Items',
                'verbose_name_plural': 'Items',
            },
        ),
    ]