# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2016-10-29 23:42
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('groceries', '0015_auto_20161029_2325'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='shopper',
            name='email',
        ),
    ]
