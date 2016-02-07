from django.conf.urls import url
from . import (views,
               api_views,
               )

urlpatterns = [
    url(r'^$', views.home, name='home'),
    url(r'^signin/$', views.signin, name='signin'),
    url(r'^signout/$', views.signout, name='signout'),
    url(r'^settings/$', views.settings, name='settings'),
    url(r'^shopping_list_items/(?P<pk>[0-9]+)/$', api_views.ShoppingListItemsView.as_view(), name='shopping_list_items'),
    url(r'^item/(?P<pk>[0-9]+)/$', api_views.ItemView.as_view()),
    url(r'^item/$', api_views.ItemView.as_view()),
    url(r'^unsafe_item/$', api_views.UnsafeItemView.as_view()),
    url(r'^shopping_list/(?P<pk>[0-9]+)/$', api_views.ShoppingListView.as_view(), name='shopping_list-detail'),
    url(r'^shopping_list/$', api_views.ShoppingListView.as_view()),
    url(r'^shopper/(?P<pk>[0-9]+)/$', api_views.ShopperView.as_view()),
    url(r'^shopper/$', api_views.ShopperView.as_view()),
    url(r'^shared_lists/(?P<shopper_id>[0-9]+)/$', views.shared_lists),
    url(r'^shared_list_member/(?P<shopper_id>[0-9]+)/(?P<list_id>[0-9]+)/$', views.shared_list_member_json),
    url(r'^socket/(?P<pk>[0-9a-z]+)/$', api_views.WebSocketTokenView.as_view(), name='socket'),
    url(r'^category/$', api_views.ShoppingListCategoryView.as_view()),
]
