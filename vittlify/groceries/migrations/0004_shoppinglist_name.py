# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('groceries', '0003_auto_20151122_1835'),
    ]

    operations = [
        migrations.AddField(
            model_name='shoppinglist',
            name='name',
            field=models.CharField(default='', max_length=200),
        ),
    ]
