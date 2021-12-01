# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2015-12-24 21:01
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('groceries', '0002_auto_20151212_2207'),
    ]

    operations = [
        migrations.AddField(
            model_name='shopper',
            name='email',
            field=models.EmailField(blank=True, max_length=254, null=True),
        ),
        migrations.AlterField(
            model_name='shoppinglist',
            name='owner',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='owned_lists', to='groceries.Shopper'),
        ),
    ]