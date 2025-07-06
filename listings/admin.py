from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth import get_user_model
from .models import Property, PropertyImage, Booking, Payment, Review, Message

User = get_user_model()


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """Admin configuration for custom User model"""
    model = User
    list_display = ['email', 'first_name', 'last_name', 'role', 'is_active', 'date_joined']
    list_filter = ['role', 'is_active', 'date_joined']
    search_fields = ['email', 'first_name', 'last_name']
    ordering = ['-date_joined']
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'phone_number', 'role')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'password1', 'password2', 'role'),
        }),
    )


@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    """Admin configuration for Property model"""
    list_display = ['name', 'host', 'location', 'price_per_night', 'property_type', 'is_available', 'created_at']
    list_filter = ['property_type', 'is_available', 'created_at', 'host__role']
    search_fields = ['name', 'description', 'location', 'host__first_name', 'host__last_name']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('host', 'name', 'description', 'location')
        }),
        ('Property Details', {
            'fields': ('property_type', 'max_guests', 'bedrooms', 'bathrooms', 'price_per_night')
        }),
        ('Status', {
            'fields': ('is_available',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(PropertyImage)
class PropertyImageAdmin(admin.ModelAdmin):
    """Admin configuration for PropertyImage model"""
    list_display = ['property', 'caption', 'is_primary', 'created_at']
    list_filter = ['is_primary', 'created_at']
    search_fields = ['property__name', 'caption']
    ordering = ['-created_at']


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    """Admin configuration for Booking model"""
    list_display = ['id', 'property', 'user', 'start_date', 'end_date', 'status', 'total_price', 'created_at']
    list_filter = ['status', 'start_date', 'end_date', 'created_at']
    search_fields = ['property__name', 'user__first_name', 'user__last_name', 'user__email']
    ordering = ['-created_at']
    readonly_fields = ['created_at']
    
    def total_price(self, obj):
        from datetime import timedelta
        days = (obj.end_date - obj.start_date).days
        return obj.locked_price_per_night * days
    total_price.short_description = 'Total Price'


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    """Admin configuration for Payment model"""
    list_display = ['id', 'booking', 'amount', 'payment_method', 'payment_date']
    list_filter = ['payment_method', 'payment_date']
    search_fields = ['booking__property__name', 'booking__user__first_name', 'booking__user__last_name']
    ordering = ['-payment_date']


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    """Admin configuration for Review model"""
    list_display = ['property', 'user', 'rating', 'created_at']
    list_filter = ['rating', 'created_at']
    search_fields = ['property__name', 'user__first_name', 'user__last_name', 'comment']
    ordering = ['-created_at']
    readonly_fields = ['created_at']


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    """Admin configuration for Message model"""
    list_display = ['sender', 'recipient', 'is_read', 'sent_at']
    list_filter = ['is_read', 'sent_at']
    search_fields = ['sender__first_name', 'sender__last_name', 'recipient__first_name', 'recipient__last_name', 'message_body']
    ordering = ['-sent_at']
    readonly_fields = ['sent_at'] 