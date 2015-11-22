# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('groceries', '0004_shoppinglist_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='item',
            name='shopping_list',
            field=models.ForeignKey(related_name='items', to='groceries.ShoppingList'),
        ),
    ]
