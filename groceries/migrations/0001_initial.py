# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Item',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=200)),
                ('date_added', models.DateTimeField(auto_now_add=True)),
                ('date_edited', models.DateTimeField(auto_now=True)),
                ('comments', models.TextField(default=b'', blank=True)),
                ('_done', models.BooleanField(default=False, db_column=b'done')),
                ('date_completed', models.DateTimeField(null=True, blank=True)),
            ],
            options={
                'ordering': ('name',),
            },
        ),
        migrations.CreateModel(
            name='Shopper',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
            ],
        ),
        migrations.CreateModel(
            name='ShoppingList',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(default=b'', max_length=200)),
                ('date_added', models.DateTimeField(auto_now_add=True)),
                ('date_edited', models.DateTimeField(auto_now=True)),
                ('owner', models.ForeignKey(on_delete=models.deletion.PROTECT, to='groceries.Shopper')),
            ],
            options={
                'ordering': ('date_added',),
            },
        ),
        migrations.CreateModel(
            name='ShoppingListMember',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('shopper', models.ForeignKey(on_delete=models.deletion.CASCADE, to='groceries.Shopper')),
                ('shopping_list', models.ForeignKey(on_delete=models.deletion.CASCADE, to='groceries.ShoppingList')),
            ],
        ),
        migrations.AddField(
            model_name='shopper',
            name='shopping_lists',
            field=models.ManyToManyField(related_name='members', through='groceries.ShoppingListMember', to='groceries.ShoppingList', blank=True),
        ),
        migrations.AddField(
            model_name='shopper',
            name='user',
            field=models.OneToOneField(on_delete=models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='item',
            name='shopping_list',
            field=models.ForeignKey(on_delete=models.deletion.CASCADE, related_name='items', to='groceries.ShoppingList'),
        ),
        migrations.AlterUniqueTogether(
            name='item',
            unique_together=set([('name', 'shopping_list')]),
        ),
    ]
