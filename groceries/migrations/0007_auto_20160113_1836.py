# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-01-14 00:36
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('groceries', '0006_auto_20151227_0443'),
    ]

    operations = [
        migrations.AddField(
            model_name='notifyaction',
            name='weekly_sent',
            field=models.BooleanField(db_index=True, default=False),
        ),
        migrations.AddField(
            model_name='shopper',
            name='email_frequency',
            field=models.CharField(choices=[('daily', 'Daily'), ('weekly', 'Weekly')], default='daily', max_length=6),
        ),
    ]
