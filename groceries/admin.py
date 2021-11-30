from django.contrib import admin
from .models import (Item,
                     Shopper,
                     ShoppingList,
                     ShoppingListMember,
                     NotifyAction,
                     ShoppingListCategory,
                     )

# Register your models here.
admin.site.register(Item)
admin.site.register(Shopper)
admin.site.register(ShoppingList)
admin.site.register(ShoppingListMember)
admin.site.register(NotifyAction)
admin.site.register(ShoppingListCategory)
