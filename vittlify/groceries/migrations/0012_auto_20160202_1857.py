# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-02-03 00:57
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('groceries', '0011_auto_20160202_1850'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='shoppinglist',
            name='category',
        ),
        migrations.AddField(
            model_name='item',
            name='category',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='groceries.ShoppingListCategory'),
        ),
    ]