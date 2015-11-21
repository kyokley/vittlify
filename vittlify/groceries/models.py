from django.db import models

class Item(models.Model):
    name = models.CharField(max_length=200)
    needed_quantity = models.IntegerField(default=1)
    got_quantity = models.IntegerField(default=0)
    shopping_list = models.ForeignKey('ShoppingList')
    date_added = models.DateTimeField(auto_now_add=True)
    date_edited = models.DateTimeField(auto_now=True)

class Shopper(models.Model):
    user = models.OneToOneField('auth.User')

class ShoppingList(models.Model):
    owner = models.ForeignKey('Shopper')
    date_added = models.DateTimeField(auto_now_add=True)
    date_edited = models.DateTimeField(auto_now=True)
