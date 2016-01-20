from groceries.serializers import (ItemSerializer,
                                   ShoppingListSerializer,
                                   ShopperSerializer,
                                   )
from groceries.models import (Item,
                              ShoppingList,
                              Shopper,
                              NotifyAction,
                              )
from groceries.auth import UnsafeSessionAuthentication
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authentication import BasicAuthentication, SessionAuthentication
from django.http import Http404
from config.settings import ALEXA_LIST
from groceries.utils import queryDictToDict
import requests

class ShoppingListItemsView(APIView):
    def get_items(self, pk):
        try:
            return ShoppingList.objects.get(pk=pk).items
        except ShoppingList.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        items = self.get_items(pk)
        serializer = ItemSerializer(items, many=True)
        return Response(serializer.data)

class ItemView(APIView):
    authentication_classes = (BasicAuthentication, SessionAuthentication)

    def get_item(self, pk):
        try:
            return Item.objects.get(pk=pk)
        except Item.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        item = self.get_item(pk)
        serializer = ItemSerializer(item)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        modified_done = modified_comments = False
        item = self.get_item(pk)
        serializer = ItemSerializer(item, data=request.data)
        if serializer.is_valid():
            if ('done' in serializer.validated_data and
                    serializer.validated_data.get('done') != item.done):
                na = NotifyAction()
                na.shopper = Shopper.objects.filter(user=request.user).first()
                na.shopping_list = item.shopping_list
                na.item = item
                if serializer.validated_data.get('done'):
                    template = '{item_name} has been completed by {username}'
                else:
                    template = '{item_name} has been uncompleted by {username}'
                na.action = template.format(
                                item_name=item.name,
                                username=na.shopper.username)
                na.save()

                modified_done = True

            if ('comments' in serializer.validated_data and
                    serializer.validated_data.get('comments') != item.comments):
                modified_comments = True
            serializer.save()

            data = {'list_id': item.shopping_list.id,
                    'checked': item.done,
                    'comments': item.comments,
                    'name': item.name,
                    'modified_done': modified_done,
                    'modified_comments': modified_comments}
            node_resp = requests.put('http://localhost:3000/item/%s' % item.id, data=data)
            node_resp.raise_for_status()

            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request, format=None):
        serializer = ItemSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()

            item = serializer.instance
            na = NotifyAction()
            na.shopper = Shopper.objects.filter(user=request.user).first()
            na.shopping_list = item.shopping_list
            na.item = item
            template = '{item_name} has been added to {shopping_list} by {username}'
            na.action = template.format(
                            item_name=item.name,
                            username=na.shopper.username,
                            shopping_list=item.shopping_list.name)
            na.save()

            data = {'item_id': item.id,
                    'list_id': item.shopping_list.id,
                    'name': item.name,
                    'comments': item.comments}
            node_resp = requests.post('http://localhost:3000/item', data=data)
            node_resp.raise_for_status()

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UnsafeItemView(ItemView):
    authentication_classes = (UnsafeSessionAuthentication,)

    def post(self, request, format=None):
        data = queryDictToDict(request.data)
        data['shopping_list_id'] = ALEXA_LIST
        serializer = ItemSerializer(data=data)
        if serializer.is_valid():
            serializer.save()

            item = serializer.instance
            na = NotifyAction()
            na.shopper = item.shopping_list.owner
            na.shopping_list = item.shopping_list
            na.item = item
            template = '{item_name} has been added by {username}'
            na.action = template.format(
                            item_name=item.name,
                            username=na.shopper.username,
                            shopping_list=item.shopping_list.name)
            na.save()
            data = {'item_id': item.id,
                    'list_id': item.shopping_list.id,
                    'name': item.name,
                    'comments': item.comments}

            node_resp = requests.post('http://localhost:3000/item', data=data)
            node_resp.raise_for_status()

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, format=None):
        name = request.data['name']
        shopping_list = ShoppingList.objects.get(pk=ALEXA_LIST)
        items = (Item.objects.filter(shopping_list=shopping_list)
                             .filter(name=name)
                             .all())
        for item in items:
            na = NotifyAction()
            na.shopper = shopping_list.owner
            na.shopping_list = shopping_list
            na.item = item
            template = '{item_name} has been completed by {username}'
            na.action = template.format(
                            item_name=item.name,
                            username=na.shopper.username)
            na.save()

            item.done = True
            item.save()
        return Response(status=status.HTTP_200_OK)

class ShoppingListView(APIView):
    authentication_classes = (BasicAuthentication, SessionAuthentication)

    def get_shopping_list(self, pk):
        try:
            return ShoppingList.objects.get(pk=pk)
        except ShoppingList.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        shopper = Shopper.objects.filter(user=request.user).first()
        shopping_list = self.get_shopping_list(pk)
        if shopper != shopping_list.owner:
            raise ValueError('Shopper is not the owner of this list')
        serializer = ShoppingListSerializer(shopping_list)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        shopper = Shopper.objects.filter(user=request.user).first()
        if request.data['owner_id'] != shopper.id:
            raise ValueError('Cannot create shopping list owned by another user')
        shopping_list = self.get_shopping_list(pk)
        serializer = ShoppingListSerializer(shopping_list, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request, format=None):
        shopper = Shopper.objects.filter(user=request.user).first()
        owner_id = request.data.get('owner_id') or shopper.id
        if int(owner_id) != shopper.id:
            raise ValueError('Cannot create shopping list owned by another user')
        serializer = ShoppingListSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        shopping_list = self.get_shopping_list(pk)
        shopping_list.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class ShopperView(APIView):
    authentication_classes = (BasicAuthentication, SessionAuthentication)

    def get_shopper(self, pk):
        try:
            return Shopper.objects.get(pk=pk)
        except Shopper.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        shopper = self.get_shopper(pk=pk)
        serializer = ShopperSerializer(shopper)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        shopper = self.get_shopper(pk=pk)
        serializer = ShopperSerializer(shopper, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class WebSocketTokenView(APIView):
    authentication_classes = (UnsafeSessionAuthentication,)

    def post(self, request, format=None):
        data = queryDictToDict(request.data)
        data['shopping_list_id'] = ALEXA_LIST
        serializer = ItemSerializer(data=data)
        if serializer.is_valid():
            serializer.save()

            item = serializer.instance
            na = NotifyAction()
            na.shopper = item.shopping_list.owner
            na.shopping_list = item.shopping_list
            na.item = item
            template = '{item_name} has been added by {username}'
            na.action = template.format(
                            item_name=item.name,
                            username=na.shopper.username,
                            shopping_list=item.shopping_list.name)
            na.save()
            data = {'item_id': item.id,
                    'list_id': item.shopping_list.id,
                    'name': item.name,
                    'comments': item.comments}

            node_resp = requests.post('http://localhost:3000/item', data=data)
            node_resp.raise_for_status()

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
