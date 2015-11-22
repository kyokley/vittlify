# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('groceries', '0002_auto_20151122_1533'),
    ]

    operations = [
        migrations.AlterField(
            model_name='item',
            name='comments',
            field=models.TextField(default=''),
        ),
        migrations.AlterField(
            model_name='shopper',
            name='shopping_lists',
            field=models.ManyToManyField(blank=True, to='groceries.ShoppingList'),
        ),
    ]
