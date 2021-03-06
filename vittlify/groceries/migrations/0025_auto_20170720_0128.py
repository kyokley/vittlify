# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-07-20 01:28
from __future__ import unicode_literals

from django.db import migrations, models
import groceries.utils


class Migration(migrations.Migration):

    dependencies = [
        ('groceries', '0024_merge_20170706_0008'),
    ]

    operations = [
        migrations.AlterField(
            model_name='shopper',
            name='email_frequency',
            field=models.CharField(choices=[(b'daily', b'Daily'), (b'weekly', b'Weekly'), (None, b'No Emails')], default=b'daily', max_length=6, null=True),
        ),
        migrations.AlterField(
            model_name='shoppinglist',
            name='guid',
            field=models.CharField(default=groceries.utils.createToken, max_length=32, unique=True),
        ),
    ]
