from django.db import models

class Item(models.Model):
    name = models.CharField(max_length=200)
    shopping_list = models.ForeignKey('ShoppingList', related_name='items')
    date_added = models.DateTimeField(auto_now_add=True)
    date_edited = models.DateTimeField(auto_now=True)
    comments = models.TextField(default='')
    done = models.BooleanField(default=False)

    def __str__(self):
        return 'id: {id} n: {name}'.format(id=self.id, name=self.name)

class Shopper(models.Model):
    user = models.OneToOneField('auth.User')
    shopping_lists = models.ManyToManyField('ShoppingList', blank=True)

    @property
    def username(self):
        return self.user.username

    def __str__(self):
        return 'id: {id} u: {name}'.format(id=self.id, name=self.user.username)

class ShoppingList(models.Model):
    owner = models.ForeignKey('Shopper')
    name = models.CharField(max_length=200, default='')
    date_added = models.DateTimeField(auto_now_add=True)
    date_edited = models.DateTimeField(auto_now=True)

    def __str__(self):
        return 'id: {id} n: {name} o: {username}'.format(id=self.id,
                                                         name=self.name,
                                                         username=self.owner.username)
