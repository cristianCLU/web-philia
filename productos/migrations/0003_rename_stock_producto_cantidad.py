# Generated by Django 4.1.2 on 2024-08-03 23:10

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('productos', '0002_carrito_remove_venta_cantidad_remove_venta_producto_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='producto',
            old_name='stock',
            new_name='cantidad',
        ),
    ]
