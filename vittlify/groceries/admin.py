from django.contrib import admin
from .models import (Item,
                     Shopper,
                     ShoppingList,
                     )

# Register your models here.
admin.site.register(Item)
admin.site.register(Shopper)
admin.site.register(ShoppingList)
