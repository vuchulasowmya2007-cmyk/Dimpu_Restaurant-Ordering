from django.contrib import admin
from .models import Category, MenuItem, Order, OrderItem


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'icon', 'display_order', 'slug')
    list_editable = ('display_order', 'icon')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)


@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'is_vegetarian', 'is_available', 'created_at')
    list_filter = ('category', 'is_vegetarian', 'is_available')
    list_editable = ('price', 'is_available', 'is_vegetarian')
    search_fields = ('name', 'description')


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    fields = ('menu_item', 'quantity', 'price', 'item_subtotal_display')
    readonly_fields = ('item_subtotal_display',)

    def item_subtotal_display(self, instance):
        if instance.pk:
            return f"${instance.item_subtotal:.2f}"
        return "-"
    item_subtotal_display.short_description = "Subtotal"


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'order_number',
        'customer_name',
        'table_number',
        'total_amount',
        'status',
        'created_at'
    )
    list_filter = ('status', 'created_at', 'table_number')
    list_editable = ('status',)
    search_fields = ('order_number', 'customer_name', 'customer_phone', 'table_number')
    readonly_fields = ('order_number', 'subtotal', 'tax_amount', 'total_amount', 'created_at', 'updated_at')
    inlines = [OrderItemInline]
    ordering = ('-created_at',)


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'menu_item', 'quantity', 'price')
    list_filter = ('menu_item__category',)
    search_fields = ('order__order_number', 'menu_item__name')
