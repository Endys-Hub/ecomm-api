from django.db import models
import uuid
import secrets
from users.models import UserProfile
from . paystack import Paystack

# Category
class Category(models.Model):
    title = models.CharField(max_length=50)
    image = models.ImageField()
    created = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.title


# Products
SIZE_CHOICES = (
    ('36-40', '36-40'),
    ('41-45', '41-45'),
    ('46-47', '46-47'),
)

class Product(models.Model):
    title = models.CharField(max_length=50)
    description = models.TextField()
    price = models.BigIntegerField()
    discount_price = models.BigIntegerField(null=True, blank=True)
    category = models.ForeignKey('Category', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='product')
    photo1 = models.ImageField(upload_to='product', null=True, blank=True)
    photo2 = models.ImageField(upload_to='product', null=True, blank=True)
    photo3 = models.ImageField(upload_to='product', null=True, blank=True)
    photo4 = models.ImageField(upload_to='product', null=True, blank=True)
    brand = models.CharField(max_length=50)
    size = models.CharField(max_length=50, choices=SIZE_CHOICES)
    product_code = models.UUIDField(unique=True, default=uuid.uuid4)
    review = models.TextField()
    rating = models.BigIntegerField(default=0)
    is_available = models.BooleanField(default=True)
    in_stock = models.IntegerField()
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.product_code:
            self.product_code = uuid.uuid4()
        super().save(*args, **kwargs)    

    
# Cart
class Cart(models.Model):

    profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE, null=True, blank=True)
    total = models.BigIntegerField(default=0)
    created = models.DateTimeField(auto_now_add=True, null=True)
    def __str__(self):
        return f'cart {self.id} - total {self.total}'


# Cart_products
class CartProduct(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.BigIntegerField()
    subtotal = models.PositiveBigIntegerField()
    created = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f'Cart Product - {self.cart.id} - {self.quantity}'



# Order
ORDER_STATUS = (
    ('pending', 'pending'),
    ('approved', 'approved'),
    ('complete', 'complete'),
    ('cancelled', 'cancelled'),
)
PAYMENT_METHOD = (
    ('paystack', 'paystack'),
    ('paypal', 'paypal'),
    ('stripe', 'stripe'),
    ('transfer', 'transfer'),
)
class Order(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    order_by = models.CharField(max_length=255)
    shipping_address = models.TextField()
    mobile = models.CharField(max_length=12)
    email = models.EmailField()
    amount = models.PositiveBigIntegerField()
    subtotal = models.PositiveBigIntegerField()
    order_status = models.CharField(max_length=12, default='pending', choices=ORDER_STATUS)
    payment_completed = models.BooleanField(default=False, null=True, blank=True)
    payment_method = models.CharField(max_length=12, default='paystack', choices=PAYMENT_METHOD)
    ref = models.CharField(max_length=255, null=True, blank=True, unique=True)

    def __str__(self):
        return self.order_by

    # Auto-save    
    def save(self, *args, **kwargs):
        ref = secrets.token_urlsafe(50)
        obj_with_same_ref = Order.objects.filter(ref = ref)
        if not obj_with_same_ref:
            self.ref = ref 
        super().save(*args, **kwargs)   

    # Converting from Dollar/Naira to Cents/Kobo
    def amount_value(self, request)->int:
        return self.amount * 100

# Verify Payments    
def verify_payment(self):
    paystack = Paystack()
    status, result = paystack.verify_payment(self.ref)

    if status and result.get('status') == 'success':
        # Ensuring amount tallies
        if result['amount'] / 100 == self.amount:
            self.payment_completed = True                                                         #if self.cart:
            self.save()
            return True     
        if self.payment_completed == True:
            del self.cart
            self.save()
            return True    
        return False
'''
def verify_payment(self):
    paystack = Paystack()
    status, result = paystack.verify_payment(self.ref)

    if status and result.get('status') == 'success':
        # Ensuring amount tallies
        if result['amount']/ 100 == self.amount:
            self.payment_completed = True
            del self.cart
            self.save()
            return True
        if self.payment_completed == True:
            del self.cart
            self.save()
            return True    
        return False
'''        