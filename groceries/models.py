import hashlib
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import padding, ed25519, ec, dsa
from cryptography.exceptions import InvalidSignature
from django.db import models
from django.db.models import Q
from django.utils.timezone import utc, localtime
from django.contrib.auth.models import User
from datetime import datetime, timedelta
from .email_template import EMAIL_TEMPLATE
from groceries.utils import createToken

RECENTLY_COMPLETED_DAYS = 14
LARGE_INT = 999999999
ACTIVE_TOKENS = 5

RSA_PRIVATE_BEGIN = '-----BEGIN RSA PRIVATE KEY-----'
RSA_PRIVATE_END = '-----END RSA PRIVATE KEY-----'


class Item(models.Model):
    name = models.CharField(max_length=200)
    shopping_list = models.ForeignKey('ShoppingList', related_name='items', on_delete=models.CASCADE)
    date_added = models.DateTimeField(auto_now_add=True)
    date_edited = models.DateTimeField(auto_now=True)
    comments = models.TextField(default='', blank=True)
    _done = models.BooleanField(db_column='done', default=False)
    date_completed = models.DateTimeField(null=True, blank=True)
    _category = models.ForeignKey('ShoppingListCategory', null=True, db_column='category', on_delete=models.SET_NULL)
    guid = models.CharField(max_length=32, default=createToken, unique=True, null=False)

    class Meta:
        unique_together = ('name', 'shopping_list')
        ordering = ('name',)

    @classmethod
    def new(cls,
            name,
            shopping_list,
            comments='',
            ):
        trimmed_name = name.strip()
        existing = (cls.objects
                       .filter(shopping_list=shopping_list)
                       .filter(name__iexact=trimmed_name)
                       .filter(_done=False)
                       .first())
        if existing:
            return existing

        new_item = cls()
        new_item.name = trimmed_name
        new_item.shopping_list = shopping_list
        new_item.comments = comments
        new_item.save()
        return new_item

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

    def move(self, shopping_list, shopper):
        if (shopper not in shopping_list.members.all() or
                shopper not in self.shopping_list.members.all()):
            raise Exception('User is not authorized to move this item')

        self.shopping_list = shopping_list

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

    def recentlyCompleted(self):
        return self.done and self.date_completed > datetime.now().replace(tzinfo=utc) - timedelta(days=RECENTLY_COMPLETED_DAYS)

    @classmethod
    def get_by_guid(cls, guid, shopper=None):
        query = Q(guid__istartswith=guid) | Q(name__istartswith=guid)
        if not shopper:
            return cls.objects.get(query)
        else:
            return (cls.objects
                       .filter(shopping_list__shoppinglistmember__shopper=shopper)
                       .get(query))


class Shopper(models.Model):
    DAILY = 'daily'
    WEEKLY = 'weekly'
    EMAIL_FREQUENCY_CHOICES = ((DAILY, 'Daily'),
                               (WEEKLY, 'Weekly'),
                               (None, 'No Emails'),
                               )
    user = models.OneToOneField('auth.User', on_delete=models.CASCADE)
    shopping_lists = models.ManyToManyField('ShoppingList', blank=True, through='ShoppingListMember', related_name='members')
    email_frequency = models.CharField(max_length=6,
                                       choices=EMAIL_FREQUENCY_CHOICES,
                                       default=DAILY,
                                       null=True,
                                       blank=True)
    theme = models.TextField(default='default', blank=False, null=False)

    @classmethod
    def new(cls,
            username=None,
            password=None,
            email=None,
            user=None,
            email_frequency=WEEKLY,
            ):
        if not (user or (username and email)):
            raise ValueError('Either a user object or username and email must be provided')

        obj = cls()

        if not user:
            user = User()
            user.username = username
            user.email = email
            if password:
                user.set_password(password)
            user.save()

        obj.user = user
        obj.email_frequency = email_frequency
        obj.save()
        return obj

    def _get_username(self):
        return self.user.username

    def _set_username(self, username):
        self.user.username = username

    username = property(fget=_get_username, fset=_set_username)

    def _get_email(self):
        return self.user.email

    def _set_email(self, email):
        self.user.email = email

    email = property(fget=_get_email, fset=_set_email)

    def __str__(self):
        return 'id: {id} u: {name}'.format(id=self.id, name=self.user.username)

    def as_dict(self):
        return {'id': self.id}

    def generateEmail(self):
        if self.email_frequency:
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

    @classmethod
    def get_by_username(cls, username):
        user = User.objects.filter(username__iexact=username).first()
        return cls.objects.filter(user=user).first()


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
    owner = models.ForeignKey('Shopper', related_name='owned_lists', on_delete=models.PROTECT)
    name = models.CharField(max_length=200, default='')
    date_added = models.DateTimeField(auto_now_add=True)
    date_edited = models.DateTimeField(auto_now=True)
    guid = models.CharField(max_length=32, default=createToken, unique=True, null=False)

    class Meta:
        ordering = ('date_added',)

    @classmethod
    def new(cls,
            name,
            owner):
        obj = cls()
        obj.name = name
        obj.owner = owner
        obj.save()
        return obj

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

    @classmethod
    def get_by_guid(cls, guid, shopper=None):
        query = Q(guid__istartswith=guid) | Q(name__istartswith=guid)
        if not shopper:
            return cls.objects.get(query)
        else:
            return (cls.objects
                       .filter(shoppinglistmember__shopper=shopper)
                       .get(query))


class ShoppingListMember(models.Model):
    shopper = models.ForeignKey('Shopper', on_delete=models.CASCADE)
    shopping_list = models.ForeignKey('ShoppingList', on_delete=models.CASCADE)

    def __str__(self):
        return '{list_name} is shared with shopper {shopper_name}'.format(
                    list_name=self.shopping_list.name,
                    shopper_name=self.shopper.username)

    def as_dict(self):
        return {'shopper': self.shopper.as_dict(),
                'shopping_list': self.shopping_list.as_dict(),
                'id': self.id}


class NotifyAction(models.Model):
    item = models.ForeignKey('Item', null=True, on_delete=models.CASCADE)
    shopping_list = models.ForeignKey('ShoppingList', null=True, on_delete=models.SET_NULL)
    shopper = models.ForeignKey('Shopper', null=False, on_delete=models.CASCADE)
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
    shopper = models.ForeignKey('Shopper', null=False, blank=False, on_delete=models.CASCADE)
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
    shopping_list = models.ForeignKey('ShoppingList', related_name='categories', null=False, blank=False, on_delete=models.CASCADE)
    name = models.CharField(max_length=200, null=False, blank=False, default='None')
    date_added = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('date_added',)
        unique_together = ('name', 'shopping_list')
        verbose_name_plural = 'Shopping list categories'

    @classmethod
    def new(cls,
            name,
            shopping_list):
        trimmed_name = name.strip().title()
        existing = cls.objects.filter(shopping_list=shopping_list).filter(name__iexact=trimmed_name).first()

        if existing:
            return existing

        new_category = cls()
        new_category.shopping_list = shopping_list
        new_category.name = trimmed_name
        new_category.save()
        return new_category

    def __str__(self):
        return 'id: {id} l: {shopping_list} n: {name}'.format(id=self.id,
                                                              shopping_list=self.shopping_list.name,
                                                              name=self.name,
                                                              )

    @classmethod
    def get_shopping_list_category_by_name(cls, name, shopping_list):
        trimmed_name = name.strip()

        if trimmed_name.lower() == 'none':
            return None

        category = cls.objects.filter(shopping_list=shopping_list).filter(name__iexact=trimmed_name).first()

        if not category:
            raise cls.DoesNotExist('Could not find provided category %s' % name)

        return category


class SshKey(models.Model):
    shopper = models.ForeignKey('Shopper', null=False, blank=False, on_delete=models.CASCADE)
    title = models.TextField(null=False, blank=False)
    ssh_format = models.TextField(null=False, blank=False)
    date_added = models.DateTimeField(auto_now_add=True)
    date_edited = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('shopper', 'title')

    def __str__(self):
        return 'id: {id} u: {username} t: {title} f: {fingerprint}'.format(id=self.id,
                                                                           title=self.title,
                                                                           username=self.shopper.username,
                                                                           fingerprint=self.fingerprint(),
                                                                           )

    @classmethod
    def new(cls,
            shopper,
            title,
            ssh_format):
        if RSA_PRIVATE_BEGIN in ssh_format or RSA_PRIVATE_END in ssh_format:
            raise ValueError('Only SSH formatted public keys are allowed')

        new_key = cls()
        new_key.shopper = shopper
        new_key.ssh_format = ssh_format
        new_key.title = title
        new_key.rsaObj

        return new_key

    def hash_md5(self):
        """ Calculate md5 fingerprint.
        Shamelessly copied from http://stackoverflow.com/questions/6682815/deriving-an-ssh-fingerprint-from-a-public-key-in-python
        For specification, see RFC4716, section 4.
        """
        fp_plain = hashlib.md5(self.ssh_format.encode()).hexdigest()  # nosec
        return "MD5&nbsp;" + ':'.join(a + b for a, b in zip(fp_plain[::2], fp_plain[1::2]))
    fingerprint = hash_md5

    @property
    def rsaObj(self):
        return serialization.load_ssh_public_key(self.ssh_format.encode(), default_backend())

    def verify(self, message, signature):
        try:
            if isinstance(self.rsaObj, (ed25519.Ed25519PublicKey,
                                        ec.EllipticCurvePublicKey,
                                        dsa.DSAPublicKey)):
                self.rsaObj.verify(signature,
                                   message,
                                   )

            else:
                self.rsaObj.verify(signature,
                                   message,
                                   padding.PSS(mgf=padding.MGF1(hashes.SHA512()),
                                               salt_length=padding.PSS.MAX_LENGTH),
                                   hashes.SHA512())

            return True
        except InvalidSignature:
            return False
