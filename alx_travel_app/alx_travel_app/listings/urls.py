from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken.views import obtain_auth_token
from .views import (
    UserViewSet, PropertyViewSet, BookingViewSet, PaymentViewSet,
    ReviewViewSet, MessageViewSet
)

# Create router and register viewsets
router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'properties', PropertyViewSet)
router.register(r'bookings', BookingViewSet, basename='booking')
router.register(r'payments', PaymentViewSet, basename='payment')
router.register(r'reviews', ReviewViewSet)
router.register(r'messages', MessageViewSet, basename='message')

app_name = 'listings'

urlpatterns = [
    # Include router URLs
    path('', include(router.urls)),
    
    # Authentication endpoints
    path('auth/login/', obtain_auth_token, name='api_token_auth'),
    
    # Additional custom endpoints can be added here
    path('properties/<int:pk>/reviews/', PropertyViewSet.as_view({'get': 'reviews'}), name='property-reviews'),
    path('properties/<int:pk>/upload-image/', PropertyViewSet.as_view({'post': 'upload_image'}), name='property-upload-image'),
    path('bookings/<int:pk>/confirm/', BookingViewSet.as_view({'post': 'confirm'}), name='booking-confirm'),
    path('bookings/<int:pk>/cancel/', BookingViewSet.as_view({'post': 'cancel'}), name='booking-cancel'),
    path('messages/conversations/', MessageViewSet.as_view({'get': 'conversations'}), name='message-conversations'),
    path('messages/conversation/', MessageViewSet.as_view({'get': 'conversation'}), name='message-conversation'),
] 