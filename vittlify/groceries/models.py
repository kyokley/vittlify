from django.db import models
from django.utils.timezone import utc, localtime
from datetime import datetime
from email_template import EMAIL_TEMPLATE
from groceries.utils import createToken

RECENTLY_COMPLETED_DAYS = 14
LARGE_INT = 999999999
ACTIVE_TOKENS = 5

class Item(models.Model):
    name = models.CharField(max_length=200)
    shopping_list = models.ForeignKey('ShoppingList', related_name='items')
    date_added = models.DateTimeField(auto_now_add=True)
    date_edited = models.DateTimeField(auto_now=True)
    comments = models.TextField(default='', blank=True)
    _done = models.BooleanField(db_column='done', default=False)
    date_completed = models.DateTimeField(null=True, blank=True)
    _category = models.ForeignKey('ShoppingListCategory', null=True, db_column='category')

    class Meta:
        #unique_together = ('name', 'shopping_list')
        ordering = ('name',)

    def __str__(self):
        return 'id: {id} n: {name}'.format(id=self.id, name=self.name)

    def _get_category(self):
        return self._category
    def _set_category(self, val):
        if val and val.shopping_list != self.shopping_list:
            raise Exception('Invalid category for this item')
        self._category = val
    category = property(fget=_get_category, fset=_set_category)

    def _get_category_id(self):
        return self.category and self.category.id
    def _set_category_id(self, val):
        if val:
            category = ShoppingListCategory.objects.get(pk=val)
        else:
            category = None
        self.category = category
    category_id = property(fget=_get_category_id, fset=_set_category_id)

    def _get_category_name(self):
        return self.category and self.category.name
    category_name = property(fget=_get_category_name)

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
    DAILY = 'daily'
    WEEKLY = 'weekly'
    EMAIL_FREQUENCY_CHOICES = ((DAILY, 'Daily'),
                               (WEEKLY, 'Weekly'),
                               )
    user = models.OneToOneField('auth.User')
    shopping_lists = models.ManyToManyField('ShoppingList', blank=True, through='ShoppingListMember', related_name='members')
    email = models.EmailField(null=True, blank=True)
    email_frequency = models.CharField(max_length=6,
                                       choices=EMAIL_FREQUENCY_CHOICES,
                                       default=DAILY)

    @property
    def username(self):
        return self.user.username

    def __str__(self):
        return 'id: {id} u: {name}'.format(id=self.id, name=self.user.username)

    def as_dict(self):
        return {'id': self.id}

    def generateEmail(self):
        actionTemplate = ''
        for shopping_list in self.shopping_lists.all():
            actions = NotifyAction.objects.filter(shopping_list=shopping_list)

            if self.receive_daily_email():
                actions = actions.filter(sent=False)
            elif self.receive_weekly_email():
                actions = actions.filter(weekly_sent=False)

            actions = list(actions.order_by('date_added').all())

            if actions:
                actionTemplate += '<h1>%s</h1>\n' % shopping_list.name
                for action in actions:
                    actionTemplate += '<ul><li>%s</li></ul>\n' % action.getActionRecord(display_day=self.receive_weekly_email())
        template = None
        if actionTemplate:
            template = EMAIL_TEMPLATE.format(actions=actionTemplate)
        return template

    def receive_daily_email(self):
        return self.email_frequency == self.DAILY

    def receive_weekly_email(self):
        return self.email_frequency == self.WEEKLY

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
    def has_categories(self):
        return bool(self.categories.count())

    @property
    def has_comments(self):
        for item in self.items.all():
            if item.comments:
                return True
        else:
            return False

    def displayItems(self):
        return self.items.filter(_done=False)

    def count(self):
        return self.items.filter(_done=False).count()

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
    weekly_sent = models.BooleanField(null=False, default=False, db_index=True)
    date_added = models.DateTimeField(auto_now_add=True)
    date_edited = models.DateTimeField(auto_now=True)

    def __str__(self):
        return 'S: {shopper_name} Act: {action} Snt: {sent} Weekly_Snt: {weekly_sent} Added: {date_added} Edited: {date_edited}'.format(
                shopper_name=self.shopper.username,
                action=self.action,
                sent=self.sent,
                weekly_sent=self.weekly_sent,
                date_added=self.date_added,
                date_edited=self.date_edited)

    def getActionRecord(self, display_day=False):
        if not display_day:
            return 'At %s, %s' % (localtime(self.date_added).strftime('%I:%M%p'),
                                  self.action)
        else:
            return 'At %s on %s, %s' % (localtime(self.date_added).strftime('%I:%M%p'),
                                        localtime(self.date_added).strftime('%a %b %d'),
                                        self.action)

class WebSocketToken(models.Model):
    guid = models.CharField(max_length=32, default=createToken, unique=True)
    shopper = models.ForeignKey('Shopper', null=False, blank=False)
    active = models.BooleanField(null=False, default=True)
    date_added = models.DateTimeField(auto_now_add=True)
    date_edited = models.DateTimeField(auto_now=True)

    class Meta:
        index_together = ['shopper', 'active']

    def __str__(self):
        return 'id: %s guid: %s u: %s act: %s added: %s edited: %s' % (self.id,
                                                                       self.guid,
                                                                       self.shopper.username,
                                                                       self.active,
                                                                       self.date_added,
                                                                       self.date_edited)

    @classmethod
    def removeOldTokens(cls, shopper):
        tokens = list(cls.objects.filter(shopper=shopper).order_by('-date_added'))
        if len(tokens) < ACTIVE_TOKENS:
            return

        for token in tokens[5:]:
            token.delete()

class ShoppingListCategory(models.Model):
    shopping_list = models.ForeignKey('ShoppingList', related_name='categories', null=False, blank=False)
    name = models.CharField(max_length=200, null=False, blank=False, default='None')
    date_added = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('date_added',)
        unique_together = ('name', 'shopping_list')
        verbose_name_plural = 'Shopping list categories'

    def __str__(self):
        return 'id: {id} l: {shopping_list} n: {name}'.format(id=self.id,
                                                              shopping_list=self.shopping_list.name,
                                                              name=self.name,
                                                              )
