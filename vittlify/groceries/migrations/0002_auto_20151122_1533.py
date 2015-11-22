# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('groceries', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='item',
            name='got_quantity',
        ),
        migrations.RemoveField(
            model_name='item',
            name='needed_quantity',
        ),
        migrations.AddField(
            model_name='item',
            name='comments',
            field=models.TextField(default=b''),
        ),
        migrations.AddField(
            model_name='item',
            name='done',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='shopper',
            name='shopping_lists',
            field=models.ManyToManyField(to='groceries.ShoppingList'),
        ),
    ]
