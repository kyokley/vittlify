# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('groceries', '0001_initial'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='item',
            unique_together=set([]),
        ),
    ]
