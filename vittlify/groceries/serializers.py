from rest_framework import serializers
from groceries.models import (Item,
                              ShoppingList,
                              )

class ItemSerializer(serializers.Serializer):
    pk = serializers.IntegerField(read_only=True)
    shopping_list_id = serializers.IntegerField()
    comments = serializers.CharField(required=False, allow_blank=True)
    done = serializers.BooleanField(default=False)

    def create(self, validated_data):
        return Item.objects.create(**validated_data)

    def update(self, instance, validated_data):
        shopping_list = ShoppingList.objects.get(pk=validated_data.get('shopping_list_id', instance.shopping_list.id))
        instance.shopping_list = shopping_list
        instance.comments = validated_data.get('comments', instance.comments)
        instance.done = validated_data.get('done', instance.done)
        instance.save()
        return instance
