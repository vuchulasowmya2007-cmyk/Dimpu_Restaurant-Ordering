import uuid
from decimal import Decimal
from django.db import models
from django.utils.text import slugify


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    icon = models.CharField(
        max_length=50,
        blank=True,
        default='bi-egg-fried',
        help_text="Bootstrap icon class, e.g. bi-egg-fried, bi-cup-straw, bi-fire, bi-cake2"
    )
    display_order = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['display_order', 'name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class MenuItem(models.Model):
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='menu_items'
    )
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    is_vegetarian = models.BooleanField(
        default=False,
        help_text="Marks the item as vegetarian friendly."
    )
    is_available = models.BooleanField(
        default=True,
        help_text="Whether this item is currently available to order in the kitchen."
    )
    image_url = models.URLField(
        max_length=500,
        blank=True,
        help_text="Direct image URL for the food item."
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['category', 'name']

    def __str__(self):
        return f"{self.name} (${self.price:.2f})"


class Order(models.Model):
    STATUS_RECEIVED = 'RECEIVED'
    STATUS_PREPARING = 'PREPARING'
    STATUS_READY = 'READY'
    STATUS_COMPLETED = 'COMPLETED'
    STATUS_CANCELLED = 'CANCELLED'

    STATUS_CHOICES = [
        (STATUS_RECEIVED, 'Received'),
        (STATUS_PREPARING, 'Preparing'),
        (STATUS_READY, 'Ready'),
        (STATUS_COMPLETED, 'Completed'),
        (STATUS_CANCELLED, 'Cancelled'),
    ]

    order_number = models.CharField(max_length=25, unique=True, editable=False)
    customer_name = models.CharField(max_length=150)
    customer_phone = models.CharField(max_length=30, blank=True)
    customer_email = models.EmailField(blank=True)
    table_number = models.CharField(max_length=20, help_text="e.g. Table 1, Table 5, Bar 2, Takeout")
    
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_RECEIVED
    )
    special_instructions = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.order_number:
            # Generate short, human-friendly order identifier: ORD-A8F29
            unique_token = uuid.uuid4().hex[:6].upper()
            self.order_number = f"ORD-{unique_token}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Order #{self.order_number} - {self.table_number} ({self.status})"

    @property
    def status_badge_class(self):
        mapping = {
            self.STATUS_RECEIVED: 'bg-primary',
            self.STATUS_PREPARING: 'bg-warning text-dark',
            self.STATUS_READY: 'bg-info text-dark',
            self.STATUS_COMPLETED: 'bg-success',
            self.STATUS_CANCELLED: 'bg-danger',
        }
        return mapping.get(self.status, 'bg-secondary')

    @property
    def progress_percentage(self):
        mapping = {
            self.STATUS_RECEIVED: 25,
            self.STATUS_PREPARING: 50,
            self.STATUS_READY: 75,
            self.STATUS_COMPLETED: 100,
            self.STATUS_CANCELLED: 0,
        }
        return mapping.get(self.status, 15)

    @property
    def item_count(self):
        return sum(item.quantity for item in self.items.all())


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items'
    )
    menu_item = models.ForeignKey(
        MenuItem,
        on_delete=models.PROTECT,
        related_name='order_items'
    )
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        help_text="Price per unit at the time of ordering."
    )

    class Meta:
        ordering = ['id']

    def __str__(self):
        return f"{self.quantity}x {self.menu_item.name} for #{self.order.order_number}"

    @property
    def item_subtotal(self):
        return self.quantity * self.price
