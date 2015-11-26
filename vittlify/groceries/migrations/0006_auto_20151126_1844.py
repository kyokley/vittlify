# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('groceries', '0005_auto_20151122_1928'),
    ]

    operations = [
        migrations.AlterField(
            model_name='item',
            name='comments',
            field=models.TextField(default=b'', blank=True),
        ),
    ]
