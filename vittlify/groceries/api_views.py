from groceries.serializers import (ItemSerializer,
                                   ShoppingListSerializer,
                                   Shopper,
                                   )
from groceries.models import (Item,
                              ShoppingList,
                              )
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authentication import BasicAuthentication, SessionAuthentication
from django.http import Http404

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
        item = self.get_item(pk)
        serializer = ItemSerializer(item, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request, format=None):
        serializer = ItemSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ShoppingListView(APIView):
    authentication_classes = (BasicAuthentication, SessionAuthentication)

    def get_shopping_list(self, pk):
        try:
            return ShoppingList.objects.get(pk=pk)
        except Item.DoesNotExist:
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

class ShoppingListMemberView(APIView):
    pass
