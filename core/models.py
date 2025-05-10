# Create your models here.
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

class User(AbstractUser):  # Using Django's AbstractUser for customization
    budget = models.FloatField(default=1000.0)
    created_at = models.DateTimeField(default=timezone.now)
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        help_text=(
            'The groups this user belongs to. A user will get all permissions '
            'granted to each of their groups.'
        ),
        related_name="core_user_groups",  # ADD THIS LINE
        related_query_name="user",
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name="core_user_permissions",  # ADD THIS LINE
        related_query_name="user",
    )

    def __str__(self):
        return self.username

class Restaurant(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)  # Allow null and blank
    logo_path = models.ImageField(upload_to='restaurant_logos/', blank=True, null=True)

    def __str__(self):
        return self.name

class MenuItem(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    price = models.FloatField()
    image_path = models.ImageField(upload_to='menu_item_images/', blank=True, null=True)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='menu_items')

    def __str__(self):
        return self.name

class CartItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cart_items')
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE, related_name='cart_items')
    quantity = models.IntegerField(default=1)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.quantity} x {self.menu_item.name} in Cart"

    class Meta:
        unique_together = ('user', 'menu_item')  # Prevent duplicate items in cart

class Order(models.Model):
    class OrderStatus(models.TextChoices):  # Using TextChoices
        CREATED = 'created', 'Created'
        IN_TRANSIT = 'in_transit', 'In Transit'
        COMPLETED = 'completed', 'Completed'
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='orders')
    total_price = models.FloatField()
    delivery_latitude = models.FloatField()
    delivery_longitude = models.FloatField()
    status = models.CharField(
        max_length=20,
        choices=OrderStatus.choices,  # Using choices
        default=OrderStatus.CREATED
    )
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Order #{self.id} by {self.user.username}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE, related_name='order_items')
    quantity = models.IntegerField()
    price_at_time = models.FloatField()

    def __str__(self):
        return f"{self.quantity} x {self.menu_item.name} in Order #{self.order.id}"

class Product(models.Model):
    name = models.CharField(max_length=100)
    price = models.FloatField()
    description = models.TextField(blank=True, null=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='products')
    created_at = models.DateTimeField(default=timezone.now)
    available = models.BooleanField(default=True)

    def __str__(self):
        return self.name