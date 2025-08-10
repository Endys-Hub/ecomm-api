from rest_framework import serializers
from . models import *

# Category Serializer
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

 # Product Serializer   
class ProductSerializer(serializers.ModelSerializer):    
    class Meta:
        model = Product
        fields = '__all__'

# Cart Serializer
class CartSerializer(serializers.ModelSerializer):    
    class Meta:
        model = Cart
        fields = '__all__'

# CartProduct Serializer
class CartProductSerializer(serializers.ModelSerializer):    
    class Meta:
        model = CartProduct
        fields = '__all__'

# Order Serializer
class OrderSerializer(serializers.ModelSerializer):    
    class Meta:
        model = Order
        fields = '__all__'

# Checkout Serializer
class CheckoutSerializer(serializers.ModelSerializer):    
    class Meta:
        model = Order
        exclude = ['amount', 'subtotal', 'cart']
        
        '''
        fields = '__all__'
        '''