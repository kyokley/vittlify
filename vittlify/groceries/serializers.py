from rest_framework import serializers
from groceries.models import (Item,
                              ShoppingList,
                              Shopper,
                              ShoppingListMember,
                              WebSocketToken,
                              )

class ItemSerializer(serializers.Serializer):
    pk = serializers.IntegerField(read_only=True)
    shopping_list_id = serializers.IntegerField(required=False)
    comments = serializers.CharField(required=False, allow_blank=True)
    name = serializers.CharField(required=False)
    done = serializers.BooleanField(default=False)

    def create(self, validated_data):
        if not validated_data.get('name'):
            raise ValueError('Name must be provided for a new Item object')
        if not validated_data.get('shopping_list_id'):
            raise ValueError('Shopping_list_id must be provided for a new Item object')
        validated_data['name'] = validated_data['name'].strip()
        return Item.objects.create(**validated_data)

    def update(self, instance, validated_data):
        shopping_list = ShoppingList.objects.get(pk=validated_data.get('shopping_list_id', instance.shopping_list.id))
        instance.shopping_list = shopping_list
        instance.comments = validated_data.get('comments', instance.comments)
        instance.name = validated_data.get('name', instance.name)
        instance.done = validated_data.get('done', instance.done)

        if not instance.name or not instance.shopping_list:
            raise Exception("Missing data")
        instance.save()
        return instance

class ShoppingListSerializer(serializers.Serializer):
    pk = serializers.IntegerField(read_only=True)
    owner_id = serializers.IntegerField()
    name = serializers.CharField()

    def create(self, validated_data):
        if not validated_data.get('name'):
            raise ValueError('Name must be provided for a new ShoppingList object')
        if not validated_data.get('owner_id'):
            raise ValueError('OwnerId must be provided for a new ShoppingList object')
        new_list = ShoppingList.objects.create(**validated_data)
        ShoppingListMember.objects.create(**{'shopper': new_list.owner,
                                             'shopping_list': new_list})
        return new_list

    def update(self, instance, validated_data):
        owner = Shopper.objects.get(pk=validated_data.get('owner_id', instance.owner.id))
        instance.owner = owner
        instance.name = validated_data.get('name', instance.name)
        instance.save()
        return instance

class ShopperSerializer(serializers.ModelSerializer):
    shopping_lists = ShoppingListSerializer(many=True, read_only=True)
    email = serializers.EmailField(required=False)
    user = serializers.CharField(read_only=True)
    email_frequency = serializers.CharField(required=False)

    class Meta:
        model = Shopper

    def update(self, instance, validated_data):
        instance.email = validated_data.get('email')
        instance.email_frequency = validated_data.get('email_frequency')
        instance.save()
        return instance

class ShoppingListMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShoppingListMember

class WebSocketTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = WebSocketToken
