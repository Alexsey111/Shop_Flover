from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model

User = get_user_model()

class Category(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='products/')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')

    def __str__(self):
        return self.name

# Определите остальные модели
class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def update_total_price(self):
        total = sum(item.quantity * item.product.price for item in self.items.all())
        self.total_price = total
        self.save()

    def __str__(self):
        return f"Cart {self.id} for {self.user.username}"

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} of {self.product.name} in cart of {self.cart.user.username}"

class DeliveryMethod(models.Model):
    name = models.CharField(max_length=100)
    cost = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.name

class PaymentMethod(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', _('Pending')),
        ('completed', _('Completed')),
        ('cancelled', _('Cancelled')),
    ]

    DELIVERY_CHOICES = [
        ('standard', _('Standard Delivery')),
        ('express', _('Express Delivery')),
        ('pickup', _('Pickup')),
    ]

    PAYMENT_CHOICES = [
        ('credit_card', _('Credit Card')),
        ('paypal', _('PayPal')),
        ('cash_on_delivery', _('Cash on Delivery')),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    delivery_option = models.CharField(max_length=20, choices=DELIVERY_CHOICES, default='standard')
    payment_option = models.CharField(max_length=20, choices=PAYMENT_CHOICES, default='credit_card')

    def update_total_price(self):
        self.total_price = sum(item.product.price * item.quantity for item in self.orderitem_set.all())
        self.save()

    def __str__(self):
        return f"Order {self.id} by {self.user.username}, Status: {self.get_status_display()}, Total Price: {self.total_price}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='orderitem_set', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.quantity} of {self.product.name}"

class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    review = models.TextField()
    rating = models.PositiveIntegerField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        if self.rating < 1 or self.rating > 5:
            raise ValidationError(_('Rating must be between 1 and 5.'))

    def __str__(self):
        return f"Review by {self.user.username} for {self.product.name}"

class Report(models.Model):
    date = models.DateField()
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    profit = models.DecimalField(max_digits=10, decimal_places=2)
    expenses = models.DecimalField(max_digits=10, decimal_places=2)
    sales_data = models.JSONField(blank=True, null=True)

    def __str__(self):
        return f"Report for {self.date}"


class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, unique=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    telegram_username = models.CharField(max_length=255, blank=True, null=True)
    chat_id = models.BigIntegerField(null=True, blank=True)

    def __str__(self):
        return self.user.username