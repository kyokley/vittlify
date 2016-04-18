# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('groceries', '0013_auto_20160202_1929'),
    ]

    operations = [
        migrations.AddField(
            model_name='shopper',
            name='theme',
            field=models.TextField(default=b'default'),
        ),
    ]
