import json
from groceries.serializers import (ItemSerializer,
                                   ShoppingListSerializer,
                                   ShopperSerializer,
                                   WebSocketTokenSerializer,
                                   ShoppingListCategorySerializer,
                                   SshKeySerializer,
                                   )
from groceries.models import (Item,
                              ShoppingList,
                              Shopper,
                              NotifyAction,
                              ShoppingListMember,
                              WebSocketToken,
                              SshKey,
                              )
from groceries.auth import (UnsafeSessionAuthentication,
                            LocalSessionAuthentication,
                            SshSessionAuthentication,
                            )
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authentication import BasicAuthentication, SessionAuthentication
from django.http import (Http404,
                         )
from django.core.exceptions import PermissionDenied, MultipleObjectsReturned
from config.settings import (ALEXA_LIST,
                             NODE_SERVER,
                             )
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

    def get_item(self, pk, user):
        shopper = Shopper.objects.filter(user=user).first()

        try:
            item = Item.objects.get(pk=pk)
            if item.shopping_list not in shopper.shopping_lists.all():
                raise PermissionDenied
            return item
        except Item.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        item = self.get_item(pk, request.user)
        serializer = ItemSerializer(item)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        modified_category = modified_done = modified_comments = False
        item = self.get_item(pk, request.user)
        request_data = queryDictToDict(request.data)
        request_data['category_id'] = request_data.get('category_id') or None
        serializer = ItemSerializer(item, data=request_data)
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

            if ('category_id' in serializer.validated_data and
                    serializer.validated_data.get('category_id') != item.category_id):
                modified_category = True
            serializer.save()

            data = {'list_id': item.shopping_list.id,
                    'category_id': item.category and item.category.id or '',
                    'category_name': item.category and item.category.name or 'None',
                    'checked': item.done,
                    'comments': item.comments,
                    'name': item.name,
                    'modified_done': modified_done,
                    'modified_comments': modified_comments,
                    'modified_category': modified_category}

            shopping_list_members = ShoppingListMember.objects.filter(shopping_list=item.shopping_list).all()
            for shopping_list_member in shopping_list_members:
                socket_tokens = WebSocketToken.objects.filter(shopper=shopping_list_member.shopper).filter(active=True).all()
                for socket_token in socket_tokens:
                    data['socket_token'] = socket_token.guid
                    node_resp = requests.put('%s/item/%s' % (NODE_SERVER,
                                                             item.id), data=data)
                    node_resp.raise_for_status()

            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request, format=None):
        serializer = ItemSerializer(data=request.data)

        if serializer.is_valid():
            shopping_list = ShoppingList.objects.get(pk=serializer.validated_data['shopping_list_id'])
            shopper = Shopper.objects.filter(user=request.user).first()
            if shopping_list not in shopper.shopping_lists.all():
                raise PermissionDenied
            serializer.save()

            item = serializer.instance
            na = NotifyAction()
            na.shopper = shopper
            na.shopping_list = item.shopping_list
            na.item = item
            template = '{item_name} has been added to {shopping_list} by {username}'
            na.action = template.format(
                            item_name=item.name,
                            username=na.shopper.username,
                            shopping_list=item.shopping_list.name)
            na.save()

            data = {'item_id': item.id,
                    'category_id': item.category and item.category.id or '',
                    'category_name': item.category and item.category.name or 'None',
                    'list_id': item.shopping_list.id,
                    'name': item.name,
                    'comments': item.comments}

            shopping_list_members = ShoppingListMember.objects.filter(shopping_list=item.shopping_list).all()
            for shopping_list_member in shopping_list_members:
                socket_tokens = WebSocketToken.objects.filter(shopper=shopping_list_member.shopper).filter(active=True).all()
                for socket_token in socket_tokens:
                    data['socket_token'] = socket_token.guid
                    node_resp = requests.post('%s/item' % NODE_SERVER, data=data)
                    node_resp.raise_for_status()

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UnsafeItemView(ItemView):
    authentication_classes = (UnsafeSessionAuthentication,)

    def post(self, request, format=None):
        data = queryDictToDict(request.data)
        data['shopping_list_id'] = ALEXA_LIST
        data['name'] = data['name'].title()
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
                    'category_id': item.category and item.category.id or '',
                    'category_name': item.category and item.category.name or 'None',
                    'name': item.name,
                    'comments': item.comments}

            shopping_list_members = ShoppingListMember.objects.filter(shopping_list=item.shopping_list).all()
            for shopping_list_member in shopping_list_members:
                socket_tokens = WebSocketToken.objects.filter(shopper=shopping_list_member.shopper).filter(active=True).all()
                for socket_token in socket_tokens:
                    data['socket_token'] = socket_token.guid
                    node_resp = requests.post('%s/item' % NODE_SERVER, data=data)
                    node_resp.raise_for_status()

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # If Alexa ever supports completing items, this will be useful
    # until then, just leaving this commented out
    #def put(self, request, format=None):
        #name = request.data['name']
        #shopping_list = ShoppingList.objects.get(pk=ALEXA_LIST)
        #items = (Item.objects.filter(shopping_list=shopping_list)
                             #.filter(name=name)
                             #.all())
        #for item in items:
            #na = NotifyAction()
            #na.shopper = shopping_list.owner
            #na.shopping_list = shopping_list
            #na.item = item
            #template = '{item_name} has been completed by {username}'
            #na.action = template.format(
                            #item_name=item.name,
                            #username=na.shopper.username)
            #na.save()
#
            #item.done = True
            #item.save()
        #return Response(status=status.HTTP_200_OK)

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
            raise ValueError('Cannot modify shopping list owned by another user')
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
    authentication_classes = (LocalSessionAuthentication,)
    def get_token(self, guid):
        try:
            return WebSocketToken.objects.filter(guid=guid).first()
        except WebSocketToken.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        socket_token = self.get_token(pk)
        serializer = WebSocketTokenSerializer(socket_token)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        socket_token = self.get_token(pk)
        serializer = WebSocketTokenSerializer(socket_token, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ShoppingListCategoryView(APIView):
    authentication_classes = (BasicAuthentication, SessionAuthentication)

    def post(self, request, format=None):
        serializer = ShoppingListCategorySerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class SshKeyView(APIView):
    authentication_classes = (BasicAuthentication, SessionAuthentication)

    def get(self, request, pk, format=None):
        shopper = Shopper.objects.filter(user=request.user).first()
        serializer = SshKeySerializer(shopper.sshkey_set.all(), many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        shopper = Shopper.objects.filter(user=request.user).first()
        serializer = SshKeySerializer(data={'shopper': shopper.id,
                                            'title': request.data['title'],
                                            'ssh_format': request.data['ssh_format']})

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        shopper = Shopper.objects.filter(user=request.user).first()
        sshkey = SshKey.objects.get(pk=pk)
        if sshkey.shopper.id != shopper.id:
            raise ValueError('Cannot delete SSH key not owned by the current user')
        sshkey.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

def check_authenticated_user(func):
    def wraps(*args, **kwargs):
        request = args[1]
        if not request.user.is_authenticated():
            return Response('Auth failed', status=status.HTTP_401_UNAUTHORIZED)
        return func(*args, **kwargs)
    return wraps


class CliShoppingListItemsView(ShoppingListItemsView):
    authentication_classes = (SshSessionAuthentication,)

    @check_authenticated_user
    def get(self, request, format=None):
        message = json.loads(request.data['message'])
        shopper = Shopper.objects.filter(user=request.user).first()

        if message['endpoint'].lower() == 'all lists':
            serializer = ShoppingListSerializer(shopper.shopping_lists, many=True)
        elif message['endpoint'].lower() == 'list':
            guid = message['guid']
            try:
                shopping_list = ShoppingList.get_by_guid(guid, shopper=shopper)
            except MultipleObjectsReturned:
                return Response('Provided guid matched multiple lists', status=status.HTTP_409_CONFLICT)
            except ShoppingList.DoesNotExist:
                return Response('Provided guid did not match any lists', status=status.HTTP_404_NOT_FOUND)

            if shopping_list in shopper.shopping_lists.all():
                serializer = ShoppingListSerializer(shopping_list)
        elif message['endpoint'].lower() == 'list items':
            guid = message['guid']
            try:
                shopping_list = ShoppingList.get_by_guid(guid, shopper=shopper)
            except MultipleObjectsReturned:
                return Response('Provided guid matched multiple lists', status=status.HTTP_409_CONFLICT)
            except ShoppingList.DoesNotExist:
                return Response('Provided guid did not match any lists', status=status.HTTP_404_NOT_FOUND)
            if shopping_list in shopper.shopping_lists.all():
                serializer = ItemSerializer(shopping_list.items.filter(_done=False), many=True)
        elif message['endpoint'].lower() == 'item':
            guid = message['guid']
            try:
                item = Item.get_by_guid(guid, shopper=shopper)
            except MultipleObjectsReturned:
                return Response('Provided guid matched multiple items', status=status.HTTP_409_CONFLICT)
            except Item.DoesNotExist:
                return Response('Provided guid did not match any items', status=status.HTTP_404_NOT_FOUND)
            serializer = ItemSerializer(item)
        elif message['endpoint'].lower() == 'completed':
            serializer = ItemSerializer([x for x in Item.recentlyCompletedByShopper(shopper)], many=True)
        elif message['endpoint'].lower() == 'list all items':
            guid = message['guid']
            try:
                shopping_list = ShoppingList.get_by_guid(guid, shopper=shopper)
            except MultipleObjectsReturned:
                return Response('Provided guid matched multiple lists', status=status.HTTP_409_CONFLICT)
            except ShoppingList.DoesNotExist:
                return Response('Provided guid did not match any lists', status=status.HTTP_404_NOT_FOUND)
            if shopping_list in shopper.shopping_lists.all():
                serializer = ItemSerializer([x for x in shopping_list.items.all() if not x.done or x.recentlyCompleted()], many=True)
        return Response(serializer.data)

    @check_authenticated_user
    def put(self, request, format=None):
        message = json.loads(request.data['message'])
        shopper = Shopper.objects.filter(user=request.user).first()

        guid = message['guid']

        try:
            item = Item.get_by_guid(guid, shopper=shopper)
            if message['endpoint'].lower() == 'complete':
                item.done = True
            elif message['endpoint'].lower() == 'uncomplete':
                item.done = False
            elif message['endpoint'].lower() == 'modify':
                item.comments = message['comments']
            item.save()
        except MultipleObjectsReturned:
            return Response('Provided guid matched multiple items', status=status.HTTP_409_CONFLICT)
        except Item.DoesNotExist:
            return Response('Provided guid did not match any items', status=status.HTTP_404_NOT_FOUND)

        serializer = ItemSerializer(item)
        return Response(serializer.data)

    @check_authenticated_user
    def post(self, request):
        message = json.loads(request.data['message'])
        shopper = Shopper.objects.filter(user=request.user).first()

        if message['endpoint'].lower() == 'add item':
            guid = message['guid']
            name = message['name']
            comments = message.get('comments', '')

            try:
                shopping_list = ShoppingList.get_by_guid(guid, shopper=shopper)
            except MultipleObjectsReturned:
                return Response('Provided guid matched multiple lists', status=status.HTTP_409_CONFLICT)
            except ShoppingList.DoesNotExist:
                return Response('Provided guid did not match any lists', status=status.HTTP_404_NOT_FOUND)

            item = Item.new(name, shopping_list, comments=comments)
            item.save()

            serializer = ItemSerializer(item)
            return Response(serializer.data)
