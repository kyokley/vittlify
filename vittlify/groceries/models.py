from django.db import models
from django.utils.timezone import utc
from datetime import datetime

class Item(models.Model):
    name = models.CharField(max_length=200)
    shopping_list = models.ForeignKey('ShoppingList', related_name='items')
    date_added = models.DateTimeField(auto_now_add=True)
    date_edited = models.DateTimeField(auto_now=True)
    comments = models.TextField(default='', blank=True)
    _done = models.BooleanField(db_column='done', default=False)
    date_completed = models.DateTimeField(null=True, blank=True)

    class Meta:
        #unique_together = ('name', 'shopping_list')
        ordering = ('name',)

    def __str__(self):
        return 'id: {id} n: {name}'.format(id=self.id, name=self.name)

    def _get_done(self):
        return self._done
    def _set_done(self, val):
        if val:
            self.date_completed = datetime.utcnow().replace(tzinfo=utc)
        self._done = val
    done = property(fget=_get_done, fset=_set_done)

    @classmethod
    def recentlyCompletedByUser(cls, user):
        pass

class Shopper(models.Model):
    user = models.OneToOneField('auth.User')
    shopping_lists = models.ManyToManyField('ShoppingList', blank=True, through='ShoppingListMember', related_name='members')

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

    class Meta:
        ordering = ('date_added',)

    def __str__(self):
        return 'id: {id} n: {name} o: {username}'.format(id=self.id,
                                                         name=self.name,
                                                         username=self.owner.username)

    @property
    def has_comments(self):
        for item in self.items.all():
            if item.comments:
                return True
        else:
            return False

class ShoppingListMember(models.Model):
    shopper = models.ForeignKey('Shopper')
    shopping_list = models.ForeignKey('ShoppingList')

    def __str__(self):
        return '{list_name} is shared with shopper {shopper_name}'.format(
                    list_name=self.shopping_list.name,
                    shopper_name=self.shopper.username)
