from django.contrib import admin
from .models import BusinessProfile, Client, Order, Comment


@admin.register(BusinessProfile)
class BusinessProfileAdmin(admin.ModelAdmin):
    list_display = ['business_name', 'user', 'phone', 'is_active', 'subscription_end', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['business_name', 'phone', 'user__username']
    list_editable = ['is_active', 'subscription_end']
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Основное', {
            'fields': ('user', 'business_name', 'phone', 'language')
        }),
        ('Подписка', {
            'fields': ('is_active', 'subscription_end')
        }),
        ('Дополнительно', {
            'fields': ('notes', 'created_at')
        }),
    )


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ['name', 'phone', 'business', 'created_at']
    list_filter = ['business', 'created_at']
    search_fields = ['name', 'phone']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['service', 'client', 'status', 'price', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['service', 'client__name']


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['order', 'text', 'created_at']
