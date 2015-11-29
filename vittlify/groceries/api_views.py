from groceries.serializers import ItemSerializer
from groceries.models import (Item,
                              ShoppingList,
                              )
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import Http404

class ItemList(APIView):
    def get_items(self, pk):
        try:
            return ShoppingList.objects.get(pk=pk).items
        except ShoppingList.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        items = self.get_items(pk)
        serializer = ItemSerializer(items, many=True)
        return Response(serializer.data)
