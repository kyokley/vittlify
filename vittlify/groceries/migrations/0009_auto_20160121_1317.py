# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('groceries', '0008_websockettoken'),
    ]

    operations = [
        migrations.AlterField(
            model_name='websockettoken',
            name='active',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterIndexTogether(
            name='websockettoken',
            index_together=set([('shopper', 'active')]),
        ),
    ]
