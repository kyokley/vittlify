from rest_framework import serializers
from groceries.models import (Item,
                              ShoppingList,
                              Shopper,
                              ShoppingListMember,
                              WebSocketToken,
                              ShoppingListCategory,
                              SshKey,
                              )

class ItemSerializer(serializers.Serializer):
    pk = serializers.IntegerField(read_only=True)
    shopping_list_id = serializers.IntegerField(required=False)
    comments = serializers.CharField(required=False, allow_blank=True)
    name = serializers.CharField(required=False)
    done = serializers.BooleanField(default=False)
    category_id = serializers.IntegerField(required=False, allow_null=True)
    category_name = serializers.CharField(read_only=True)
    guid = serializers.CharField(read_only=True)

    def create(self, validated_data):
        if not validated_data.get('name'):
            raise ValueError('Name must be provided for a new Item object')
        if not validated_data.get('shopping_list_id'):
            raise ValueError('Shopping_list_id must be provided for a new Item object')
        validated_data['name'] = validated_data['name'].strip()
        category = None
        if 'category_id' in validated_data:
            if validated_data.get('category_id'):
                category = ShoppingListCategory.objects.get(pk=validated_data.get('category_id'))
            del validated_data['category_id']

        item =  Item.objects.create(**validated_data)
        item.category = category
        item.save()
        return item

    def update(self, instance, validated_data):
        shopping_list = ShoppingList.objects.get(pk=validated_data.get('shopping_list_id', instance.shopping_list.id))
        instance.shopping_list = shopping_list
        if not validated_data.get('category_id'):
            category = None
        else:
            category = ShoppingListCategory.objects.get(pk=validated_data.get('category_id'))
        instance.category = category
        instance.comments = validated_data.get('comments', instance.comments)
        instance.name = validated_data.get('name', instance.name)
        instance.done = validated_data.get('done', instance.done)

        if not instance.name or not instance.shopping_list:
            raise Exception("Missing data")
        instance.save()
        return instance

class ShoppingListCategorySerializer(serializers.ModelSerializer):
    pk = serializers.IntegerField(read_only=True)
    name = serializers.CharField(required=True)
    shopping_list = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = ShoppingListCategory
        fields = ('pk', 'name', 'shopping_list')

    def create(self, validated_data):
        if not validated_data.get('name'):
            raise ValueError('Name must be provided for a new ShoppingListCategory object')
        if not validated_data.get('shopping_list_id'):
            raise ValueError('ShoppingLlistId must be provided for a new ShoppingListCategory object')
        new_category = ShoppingListCategory.new(**validated_data)
        return new_category

class ShoppingListSerializer(serializers.Serializer):
    pk = serializers.IntegerField(read_only=True)
    owner_id = serializers.IntegerField()
    name = serializers.CharField()
    categories = ShoppingListCategorySerializer(many=True, read_only=True)
    guid = serializers.CharField(read_only=True)

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
    email_frequency = serializers.CharField(required=False, allow_null=True)

    class Meta:
        model = Shopper
        fields = ('shopping_lists', 'email', 'user', 'email_frequency', 'theme')

    def update(self, instance, validated_data):
        instance.email = validated_data.get('email', instance.email)
        instance.email_frequency = validated_data.get('email_frequency', instance.email_frequency)
        instance.theme = validated_data.get('theme', instance.theme)
        instance.save()
        return instance

class ShoppingListMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShoppingListMember
        fields = '__all__'

class WebSocketTokenSerializer(serializers.ModelSerializer):
    guid = serializers.CharField(read_only=True)
    active = serializers.BooleanField(required=False)
    shopper = ShopperSerializer(read_only=True)

    class Meta:
        model = WebSocketToken
        fields = ('guid', 'active', 'shopper')

    def update(self, instance, validated_data):
        shopper = Shopper.objects.get(pk=validated_data.get('shopper', instance.shopper.id))
        instance.shopper = shopper
        instance.active = validated_data.get('active')
        instance.save()
        return instance

class SshKeySerializer(serializers.ModelSerializer):
    class Meta:
        model = SshKey
        fields = ('shopper', 'title', 'ssh_format')

    def create(self, validated_data):
        key = SshKey.new(**validated_data)
        key.save()
        return key
