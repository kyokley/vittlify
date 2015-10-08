from django.db import models

class GroceryList(models.Model):
    users = models.ManyToManyField('auth.user')

class Item(models.Model):
    name = models.CharField(max_length=200)
    quantity = models.IntegerField(default=1)
