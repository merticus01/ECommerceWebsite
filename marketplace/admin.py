from django.contrib import admin
from .models import *

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['username', 'email', 'is_buyer', 'is_seller']
    list_filter = ['is_buyer', 'is_seller']

@admin.register(SellerProfile)
class SellerProfileAdmin(admin.ModelAdmin):
    list_display = ['display_name', 'user', 'verified', 'created_at']
    list_filter = ['verified', 'created_at']
    prepopulated_fields = {'slug': ('display_name',)}

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['title', 'seller', 'price', 'is_active', 'is_featured', 'created_at']
    list_filter = ['is_active', 'is_featured', 'era', 'category', 'condition', 'created_at']
    search_fields = ['title', 'description']
    prepopulated_fields = {'slug': ('title',)}

@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ['product', 'is_primary', 'order']
    list_filter = ['is_primary']

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'created_at', 'updated_at']
    list_filter = ['created_at']

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ['id', 'cart', 'product', 'quantity']

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'buyer', 'status', 'total', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['buyer__username', 'payment_reference']

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'product', 'seller', 'quantity', 'price']
    list_filter = ['order__created_at']

@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ['user', 'product', 'created_at']
    list_filter = ['created_at']

@admin.register(SellerFollow)
class SellerFollowAdmin(admin.ModelAdmin):
    list_display = ['user', 'seller', 'created_at']
    list_filter = ['created_at']

@admin.register(EditorialArticle)
class EditorialArticleAdmin(admin.ModelAdmin):
    list_display = ['title', 'type', 'published', 'created_at']
    list_filter = ['type', 'published', 'created_at']
    search_fields = ['title', 'excerpt', 'body']
    prepopulated_fields = {'slug': ('title',)}

