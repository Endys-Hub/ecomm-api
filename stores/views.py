from rest_framework import status, serializers
from rest_framework.views import APIView
from rest_framework.response import Response
from . models import *
from . serializers import *
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.urls import reverse
from django.conf import settings
import requests 

# CRUD for Category
class CategorysView(APIView):
    # Post(Create) and Get(Read-all/Retrieve-all)
    def post (self, request):
        try:
            serializers = CategorySerializer(data = request.data)
            if serializers.is_valid():
                serializers.save()
                return Response(serializers.data, status=status.HTTP_201_CREATED)
            return Response(serializers.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"Error":str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def get(self, request):
        try:
            categorys = Category.objects.all()
            serializers = CategorySerializer(categorys, many=True)
            return Response(serializers.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"Error":str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Get(Read-single/Retrieve-single)
class CategoryView(APIView):
    def get(self, request, id):
        try:
            category = Category.objects.get(id = id)
            serializers = CategorySerializer(category)
            return Response(serializers.data, status=status.HTTP_200_OK)        
        except Exception as e:
            return Response({"Error":str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Put(Update-single)
    def put(self, request, id):
        try:
            category = get_object_or_404(Category, id = id)
            serializers = CategorySerializer(category, data=request.data, partial = True)
            if serializers.is_valid():
                serializers.save()
                return Response(serializers.data, status=status.HTTP_201_CREATED)
            return Response(serializers.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"Error":str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)    

# Delete(Delete-single)
    def delete(self, request, id):
        try:
            category = get_object_or_404(Category, id = id)
            category.delete()
            return Response({"Message": f"{category.title} was deleted successfully"}, status=status.HTTP_200_OK)       
        except Exception as e:
            return Response({"Error":str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)    


# CRUD for Product
class ProductsView(APIView):
    # Post(Create) and Get(Read-all/Retrieve-all)
    def post (self, request):
        try:
            serializers = ProductSerializer(data = request.data)
            if serializers.is_valid():
                serializers.save()
                return Response(serializers.data, status=status.HTTP_201_CREATED)
            return Response(serializers.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"Error":str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def get(self, request):
        try:
            products = Product.objects.all()
            serializers = ProductSerializer(products, many=True)
            return Response(serializers.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"Error":str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Get(Read-single/Retrieve-single)
class ProductView(APIView):
    def get(self, request, id):
        try:
            product = Product.objects.get(id = id)
            serializers = ProductSerializer(product)
            return Response(serializers.data, status=status.HTTP_200_OK)        
        except Exception as e:
            return Response({"Error":str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Put(Update-single)
    def put(self, request, id):
        try:
            product = get_object_or_404(Product, id = id)
            serializers = ProductSerializer(product, data=request.data, partial = True)
            if serializers.is_valid():
                serializers.save()
                return Response(serializers.data, status=status.HTTP_201_CREATED)
            return Response(serializers.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"Error":str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)    

# Delete(Delete-single)
    def delete(self, request, id):
        try:
            product = get_object_or_404(Product, id = id)
            product.delete()
            return Response({"Message": f"{product.title} was deleted successfully"}, status=status.HTTP_200_OK)       
        except Exception as e:
            return Response({"Error":str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)         

# Add to Cart
class AddToCartView(APIView):
    def post(self, request, id):
       try:
         # Getting the product to add to cart
            product = get_object_or_404(Product, id=id)
            # Creating a cart based on session by getting Cart ID
            cart_id = request.session.get('cart_id', None)
            # Getting either actual price or discount price
            price = product.discount_price if product.discount_price else product.price


            while transaction.atomic():
                if cart_id:
                    # Get the cart
                    cart = Cart.objects.filter(id=cart_id).first()
                    if cart is None:
                        cart = Cart.objects.create(total=0)
                        request.session['cart_id'] = cart.id

                                # Add product to the cart
                    this_product_in_cart = cart.cartproduct_set.filter(product=product)
                    if request.user.is_authenticated and hasattr(request.user, 'profile'):          
                        cart.profile = request.user.profile
                        cart.save()
                    
                    if this_product_in_cart.exists():
                        cartproduct = this_product_in_cart.last()
                        cartproduct.quantity += 1
                        cartproduct.subtotal += price
                        cartproduct.save()
                        cart.total += price
                        cart.save()
                        return Response({"Message": "The items in your cart have increased"}, status=status.HTTP_200_OK)
                    else:
                        cartproduct = CartProduct.objects.create(cart=cart, product = product, quantity = 1, subtotal = price)
                        cartproduct.save()
                        cart.total += price
                        cart.save()
                        return Response ({"Message": "A new Item has been added to your cart"}, status=status.HTTP_200_OK)
                else:
                    # Create a new cart
                    cart = Cart.objects.create(total = 0)
                    request.session['cart_id'] = cart.id
                    cartproduct = CartProduct.objects.create(cart=cart, product = product, quantity = 1, subtotal = price)
                    cartproduct.save()
                    cart.total += price
                    cart.save()
                    return Response({"Message": " A new Item has been added to your cart"})
       except Exception as e:
           return Response({"Error":str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Get a User's Cart 
class MyCartView(APIView):
    def get(self, request):
        try:
            cart_id = request.session.get('cart_id', None)
            if cart_id:
                cart = get_object_or_404(Cart, id = cart_id)
                # Assign Cart to User
                if request.user.is_authenticated and hasattr(request.user, 'profile'):          
                    cart.profile = request.user.profile
                    cart.save()
                return Response({"Message": f"{cart.profile}"}, status=status.HTTP_200_OK)
            return Response({"Message": "Cart was not found"}, status=status.HTTP_400_BAD_REQUEST)       
        except Exception as e:
           return Response({"Error":str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Manage User's Cart - Increase / Decrease Quantity
class ManageCartView(APIView):
    def post(self, request, id):
        action = request.data.get('action')
        try:
            cart_obj = get_object_or_404(CartProduct, id=id)
            cart = cart_obj.cart
            price = cart_obj.product.discount_price if cart_obj.product.discount_price else cart_obj.product.price
        
            if action == "inc":
                cart_obj.quantity += 1
                cart_obj.subtotal += price
                cart_obj.save()
                cart.total += price
                cart.save()
                return Response({"Message": "Item has been Increased in the Cart"}, status=status.HTTP_200_OK)
            elif action == "dcr":
                cart_obj.quantity -= 1
                cart_obj.subtotal -= price
                cart_obj.save()
                cart.total -= price
                cart.save()
                if cart_obj.quantity == 0:
                    cart_obj.delete()
                return Response({"Message": "Item has been Decreased from the Cart"}, status=status.HTTP_200_OK)
            elif action == "rmv":
                cart.total -= cart_obj.subtotal
                cart.save()
                cart_obj.delete()
                return Response({"Message": "Item has been Removed from the Cart"}, status=status.HTTP_200_OK)
            else:
                return Response({"Message": "No Cart was Found"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
           return Response({"Error":str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Checkout
class CheckoutView(APIView):
    def post(self,request):
        cart_id = request.session.get('cart_id', None)
        if not cart_id:
            return Response({"Message": "Cart Not Found"})
        try:
            cart_obj = get_object_or_404(Cart, id = cart_id)
        except Exception as e:
           return Response({"Error":str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        serializers = CheckoutSerializer(data = request.data)
        if serializers.is_valid():
            order = serializers.save(
                cart = cart_obj,
                amount = cart_obj.total,
                subtotal = cart_obj.total,
                order_status = 'pending',
            )
            del request.session['cart_id'] # Attach cart to a registered user

            if order.payment_method == 'paystack':
                payment_url = reverse('payment', args = [order.id])
                return Response({"redirect url": payment_url}, status = status.HTTP_200_OK)
            return Response({"Message": "Order Created Successfully"})
        return Response(serializers.errors, status = status.HTTP_400_BAD_REQUEST)
            
# Payment
class PaymentView(APIView):
    def get(self, request, id):
        try:
            order = get_object_or_404(Order, id=id)
        except Order.DoesNotExist:
            return Response({"Error": "Order Not Found"}, status=status.HTTP_404_NOT_FOUND)

        url = "https://api.paystack.co/transaction/initialize"
        headers = {
            "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
            "Content-Type": "application/json"
        }
        data = {
            "amount": int(order.amount * 100),  # Kobo (not Naira)
            "email": order.email,
            "reference": order.ref
        }

        response = requests.post(url, headers=headers, json=data)
        response_data = response.json()

        if response_data.get('status'):
            paystack_url = response_data['data']['authorization_url']
            return Response(
                {
                    'order': order.id,
                    'total': order.amount,
                    'paystack_public_key': settings.PAYSTACK_PUBLIC_KEY,
                    'paystack_url': paystack_url
                },
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                {"message": "Payment Initialization Failed", "errors": response_data.get("message")},
                status=status.HTTP_400_BAD_REQUEST
            )

# Verify
class VerifyView(APIView):
    pass 

'''
class PaymentView(APIView):
    def get(self,request,id):
        try:
            order = get_object_or_404(Order, id=id)
        except Order.DoesNotExist:
           return Response({"Error": "Order Not Found"})
        # Creating pop-up for payment request
        url = "https://api.paystack.co/transaction/initialize"
        headers = {"Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}"}
        data = {
            "amount": int(order.amount * 100),
            "email": order.email,
            "reference": order.ref
        }
        response = requests.post(url, headers=headers, json=data)
        response_data = response.json()

        if response_data['status']:
            paystack_url = response_data['data']['authorization_url']
            return Response(
                {
                'order': order.id,
                'total': order.amount,
                'paystack_public_key': settings.PAYSTACK_PUBLIC_KEY,
                'paystack_url': paystack_url
            }, status=status.HTTP_200_OK
            )
        else:
            return Response({"message": "Payment Initialization Failed"}, status=status.HTTP_400_BAD_REQUEST)
'''