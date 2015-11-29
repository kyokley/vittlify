from rest_framework import serializers
from groceries.models import (Item,
                              ShoppingList,
                              Shopper,
                              )

class ItemSerializer(serializers.Serializer):
    pk = serializers.IntegerField(read_only=True)
    shopping_list_id = serializers.IntegerField(required=False)
    comments = serializers.CharField(required=False, allow_blank=True)
    name = serializers.CharField(required=False)
    done = serializers.BooleanField(default=False)

    def create(self, validated_data):
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
        return ShoppingList.objects.create(**validated_data)

    def update(self, instance, validated_data):
        owner = Shopper.objects.get(pk=validated_data.get('owner_id', instance.owner.id))
        instance.owner = owner
        instance.name = validated_data.get('name', instance.name)
        instance.save()
        return instance
