from django.db import models

class Item(models.Model):
    name = models.CharField(max_length=200)
    shopping_list = models.ForeignKey('ShoppingList')
    date_added = models.DateTimeField(auto_now_add=True)
    date_edited = models.DateTimeField(auto_now=True)
    comments = models.TextField()
    done = models.BooleanField()

class Shopper(models.Model):
    user = models.OneToOneField('auth.User')

class ShoppingList(models.Model):
    owner = models.ForeignKey('Shopper')
    date_added = models.DateTimeField(auto_now_add=True)
    date_edited = models.DateTimeField(auto_now=True)
