from django.contrib import admin
from .models import BusinessProfile, Client, Order, Comment, Employee, Message, WorkLog, EmployeeInvitation


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

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ['get_full_name', 'business', 'role', 'email', 'is_active', 'created_at']
    list_filter = ['business', 'role', 'is_active', 'created_at']
    search_fields = ['first_name', 'last_name', 'email', 'phone']
    readonly_fields = ['created_at']
    
    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"
    get_full_name.short_description = 'ФИО'


@admin.register(EmployeeInvitation)
class EmployeeInvitationAdmin(admin.ModelAdmin):
    list_display = ['email', 'get_full_name', 'business', 'role', 'status', 'created_at']
    list_filter = ['business', 'status', 'created_at']
    search_fields = ['email', 'first_name', 'last_name']
    readonly_fields = ['token', 'created_at', 'accepted_at', 'invited_by']
    
    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"
    get_full_name.short_description = 'ФИО'


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['sender', 'recipient', 'is_read', 'created_at']
    list_filter = ['is_read', 'created_at']
    search_fields = ['text', 'sender__first_name', 'recipient__first_name']


@admin.register(WorkLog)
class WorkLogAdmin(admin.ModelAdmin):
    list_display = ['employee', 'start_time', 'end_time', 'get_duration', 'created_at']
    list_filter = ['employee', 'created_at']
    search_fields = ['employee__first_name', 'employee__last_name']
    readonly_fields = ['created_at']
    
    def get_duration(self, obj):
        return f"{obj.duration}"
    get_duration.short_description = 'Длительность'