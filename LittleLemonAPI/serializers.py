from .models import Category, MenuItem , Cart , Order , OrderItem
from rest_framework import serializers
from django.contrib.auth.models import User

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class MenuItemSerializer(serializers.ModelSerializer):
    category = serializers.StringRelatedField()
    category_id = serializers.IntegerField(write_only=True)
    class Meta:
        model = MenuItem
        fields = [ 'title',  'price','featured', 'category', 'category_id']

class CartSerializer(serializers.ModelSerializer):
    menuitem = serializers.StringRelatedField()
    class Meta:
        model = Cart
        fields = ['menuitem_id','menuitem', 'quantity', 'unit_price' , 'price'] 

    def get_price(self, obj):
        return obj.unit_price * obj.quantity
    

class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'

class OrderPUTSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['status']

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']

