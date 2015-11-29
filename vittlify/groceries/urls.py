from django.conf.urls import url
from . import (views,
               api_views,
               )

urlpatterns = [
    url(r'^$', views.home, name='home'),
    url(r'^signin/$', views.signin, name='signin'),
    url(r'^shopping_list_items/(?P<pk>[0-9]+)/$', api_views.ShoppingListItemsView.as_view(), name='shopping_list_items'),
    url(r'^item/(?P<pk>[0-9]+)/$', api_views.ItemView.as_view()),
]
