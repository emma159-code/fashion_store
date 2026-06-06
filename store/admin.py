from django.contrib import admin
from .models import Category, Product, ProductImage, Cart, CartItem, Order, OrderItem

# Category Admin
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at']
    search_fields = ['name']


# Product Image Inline
class ProductImageInline(admin.TabularInline):
    model = ProductImage


# Product Admin
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price', 'stock', 'badge', 'created_at']
    list_filter = ['category', 'badge', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'category')
        }),
        ('Pricing', {
            'fields': ('price', 'discount_percentage')
        }),
        ('Media', {
            'fields': ('image',)
        }),
        ('Stock & Badge', {
            'fields': ('stock', 'badge')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


# Product Image Admin
@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ['id', 'created_at']


# Cart Item Inline
class CartItemInline(admin.TabularInline):
    model = CartItem
    readonly_fields = ['subtotal']


# Cart Admin
@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['user', 'total_items', 'total_price', 'created_at']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [CartItemInline]


# Order Item Inline
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    readonly_fields = ['subtotal']


# Order Admin
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'email', 'total_amount', 'status', 'created_at']
    list_filter = ['status', 'created_at', 'city']
    search_fields = ['user__username', 'email', 'phone']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [OrderItemInline]
    fieldsets = (
        ('Customer Information', {
            'fields': ('user', 'first_name', 'last_name', 'email', 'phone')
        }),
        ('Delivery Information', {
            'fields': ('address', 'city')
        }),
        ('Order Details', {
            'fields': ('status', 'total_amount')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


# Order Item Admin
@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['id', 'order', 'product', 'quantity', 'price']
    readonly_fields = ['subtotal']
