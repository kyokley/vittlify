from django.db import models
from django.utils.timezone import utc
from datetime import datetime
from email_template import EMAIL_TEMPLATE

RECENTLY_COMPLETED_DAYS = 14
LARGE_INT = 999999999

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
        else:
            self.date_completed = None
        self._done = val
    done = property(fget=_get_done, fset=_set_done)

    @classmethod
    def recentlyCompletedByShopper(cls, shopper):
        items = cls.objects.raw('''
                        SELECT item.* FROM groceries_item AS item
                        INNER JOIN groceries_shoppinglistmember AS slm
                        ON slm.shopping_list_id = item.shopping_list_id
                        WHERE slm.shopper_id = %s
                        AND item.date_completed IS NOT NULL
                        AND item.date_completed > now() - INTERVAL '%s days';
                           ''', (shopper.id, RECENTLY_COMPLETED_DAYS))
        return items

class Shopper(models.Model):
    user = models.OneToOneField('auth.User')
    shopping_lists = models.ManyToManyField('ShoppingList', blank=True, through='ShoppingListMember', related_name='members')
    email = models.EmailField(null=True, blank=True)

    @property
    def username(self):
        return self.user.username

    def __str__(self):
        return 'id: {id} u: {name}'.format(id=self.id, name=self.user.username)

    def as_dict(self):
        return {'id': self.id}

    def generateEmail(self):
        actionTemplate = '\n'
        for shopping_list in self.shopping_lists.all():
            actionTemplate += '<h1>%s</h1>\n' % shopping_list.name

            actions = list(NotifyAction.objects
                                       .filter(shopping_list=shopping_list)
                                       .filter(sent=False)
                                       .all())

            for action in actions:
                actionTemplate += '<ul><li>%s</li></ul>\n' % action.getActionRecord()
        template = EMAIL_TEMPLATE.format(actions=actionTemplate)
        return template

class RecentlyCompletedShoppingList(object):
    def __init__(self,
                 owner,
                 name='Finished'
                 ):
        self.id = LARGE_INT
        self.owner = owner if isinstance(owner, Shopper) else Shopper.objects.filter(user=owner).first()
        self.name = name
        self.displayItems = [x for x in Item.recentlyCompletedByShopper(self.owner)]

class ShoppingList(models.Model):
    owner = models.ForeignKey('Shopper', related_name='owned_lists')
    name = models.CharField(max_length=200, default='')
    date_added = models.DateTimeField(auto_now_add=True)
    date_edited = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('date_added',)

    def __str__(self):
        return 'id: {id} n: {name} o: {username}'.format(id=self.id,
                                                         name=self.name,
                                                         username=self.owner.username)

    def as_dict(self):
        return {'owner': self.owner.as_dict(),
                'name': self.name,
                'id': self.id,
                }

    @property
    def has_comments(self):
        for item in self.items.all():
            if item.comments:
                return True
        else:
            return False

    def displayItems(self):
        return self.items.filter(_done=False)

class ShoppingListMember(models.Model):
    shopper = models.ForeignKey('Shopper')
    shopping_list = models.ForeignKey('ShoppingList')

    def __str__(self):
        return '{list_name} is shared with shopper {shopper_name}'.format(
                    list_name=self.shopping_list.name,
                    shopper_name=self.shopper.username)

    def as_dict(self):
        return {'shopper': self.shopper.as_dict(),
                'shopping_list': self.shopping_list.as_dict(),
                'id': self.id}

class NotifyAction(models.Model):
    item = models.ForeignKey('Item', null=True)
    shopping_list = models.ForeignKey('ShoppingList', null=True)
    shopper = models.ForeignKey('Shopper', null=False)
    action = models.TextField(default='', blank=True)
    sent = models.BooleanField(null=False, default=False, db_index=True)
    date_added = models.DateTimeField(auto_now_add=True)
    date_edited = models.DateTimeField(auto_now=True)

    def __str__(self):
        return 'S: {shopper_name} Act: {action} Snt: {sent} Added: {date_added} Edited: {date_edited}'.format(
                shopper_name=self.shopper.username,
                action=self.action,
                sent=self.sent,
                date_added=self.date_added,
                date_edited=self.date_edited)

    def getActionRecord(self):
        return 'At %s, %s' % (self.date_added.strftime('%H:%M'),
                              self.action)
