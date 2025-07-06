from rest_framework import viewsets, status, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from django.db.models import Q, Avg
from django.contrib.auth import get_user_model
from .models import Property, PropertyImage, Booking, Payment, Review, Message
from .serializers import (
    UserSerializer, UserRegistrationSerializer, PropertySerializer, PropertyCreateSerializer,
    PropertyImageSerializer, BookingSerializer, PaymentSerializer, ReviewSerializer,
    MessageSerializer, ConversationSerializer
)

User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    """ViewSet for User model"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['first_name', 'last_name', 'email']
    ordering_fields = ['date_joined', 'first_name', 'last_name']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return UserRegistrationSerializer
        return UserSerializer
    
    def get_permissions(self):
        if self.action == 'create':
            return [permissions.AllowAny()]
        return super().get_permissions()
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """Get current user profile"""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
    
    @action(detail=False, methods=['put', 'patch'])
    def update_profile(self, request):
        """Update current user profile"""
        serializer = self.get_serializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PropertyViewSet(viewsets.ModelViewSet):
    """ViewSet for Property model"""
    queryset = Property.objects.all()
    serializer_class = PropertySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['property_type', 'max_guests', 'bedrooms', 'bathrooms', 'is_available', 'host']
    search_fields = ['name', 'description', 'location']
    ordering_fields = ['price_per_night', 'created_at', 'updated_at']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return PropertyCreateSerializer
        return PropertySerializer
    
    def get_queryset(self):
        queryset = Property.objects.all()
        
        # Filter by price range
        min_price = self.request.query_params.get('min_price')
        max_price = self.request.query_params.get('max_price')
        
        if min_price:
            queryset = queryset.filter(price_per_night__gte=min_price)
        if max_price:
            queryset = queryset.filter(price_per_night__lte=max_price)
        
        # Filter by availability dates
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        
        if start_date and end_date:
            queryset = queryset.exclude(
                bookings__start_date__lt=end_date,
                bookings__end_date__gt=start_date,
                bookings__status__in=['pending', 'confirmed']
            )
        
        return queryset
    
    @action(detail=True, methods=['post'])
    def upload_image(self, request, pk=None):
        """Upload image for a property"""
        property_obj = self.get_object()
        
        # Check if user is the host
        if property_obj.host != request.user:
            return Response(
                {'error': 'Only the host can upload images'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = PropertyImageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(property=property_obj)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['get'])
    def reviews(self, request, pk=None):
        """Get reviews for a property"""
        property_obj = self.get_object()
        reviews = property_obj.reviews.all()
        serializer = ReviewSerializer(reviews, many=True)
        return Response(serializer.data)


class BookingViewSet(viewsets.ModelViewSet):
    """ViewSet for Booking model"""
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status', 'property', 'user']
    ordering_fields = ['start_date', 'end_date', 'created_at']
    
    def get_queryset(self):
        # Users can only see their own bookings or bookings for their properties
        user = self.request.user
        return Booking.objects.filter(
            Q(user=user) | Q(property__host=user)
        )
    
    def create(self, request, *args, **kwargs):
        """Create a new booking"""
        property_id = request.data.get('property')
        property_obj = get_object_or_404(Property, id=property_id)
        
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save(property=property_obj)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def confirm(self, request, pk=None):
        """Confirm a booking (host only)"""
        booking = self.get_object()
        
        if booking.property.host != request.user:
            return Response(
                {'error': 'Only the host can confirm bookings'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        booking.status = 'confirmed'
        booking.save()
        serializer = self.get_serializer(booking)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel a booking"""
        booking = self.get_object()
        
        # Only the guest or host can cancel
        if booking.user != request.user and booking.property.host != request.user:
            return Response(
                {'error': 'You can only cancel your own bookings or bookings for your properties'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        booking.status = 'canceled'
        booking.save()
        serializer = self.get_serializer(booking)
        return Response(serializer.data)


class PaymentViewSet(viewsets.ModelViewSet):
    """ViewSet for Payment model"""
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['payment_method', 'booking']
    ordering_fields = ['payment_date']
    
    def get_queryset(self):
        # Users can only see payments for their bookings
        user = self.request.user
        return Payment.objects.filter(booking__user=user)


class ReviewViewSet(viewsets.ModelViewSet):
    """ViewSet for Review model"""
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['property', 'user', 'rating']
    ordering_fields = ['created_at', 'rating']
    
    def get_queryset(self):
        return Review.objects.all()
    
    def create(self, request, *args, **kwargs):
        """Create a new review"""
        property_id = request.data.get('property')
        property_obj = get_object_or_404(Property, id=property_id)
        
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save(property=property_obj)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MessageViewSet(viewsets.ModelViewSet):
    """ViewSet for Message model"""
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['sender', 'recipient', 'is_read']
    ordering_fields = ['sent_at']
    
    def get_queryset(self):
        # Users can only see messages they sent or received
        user = self.request.user
        return Message.objects.filter(
            Q(sender=user) | Q(recipient=user)
        )
    
    @action(detail=False, methods=['get'])
    def conversations(self, request):
        """Get all conversations for the current user"""
        user = request.user
        
        # Get all unique conversations
        conversations = []
        messages = Message.objects.filter(
            Q(sender=user) | Q(recipient=user)
        ).order_by('-sent_at')
        
        # Group by other user
        seen_users = set()
        for message in messages:
            other_user = message.recipient if message.sender == user else message.sender
            if other_user.id not in seen_users:
                seen_users.add(other_user.id)
                
                # Get unread count
                unread_count = Message.objects.filter(
                    sender=other_user,
                    recipient=user,
                    is_read=False
                ).count()
                
                conversations.append({
                    'other_user': other_user,
                    'last_message': message,
                    'unread_count': unread_count
                })
        
        serializer = ConversationSerializer(conversations, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def conversation(self, request):
        """Get conversation with a specific user"""
        other_user_id = request.query_params.get('user_id')
        if not other_user_id:
            return Response(
                {'error': 'user_id parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        other_user = get_object_or_404(User, id=other_user_id)
        user = request.user
        
        messages = Message.objects.filter(
            (Q(sender=user) & Q(recipient=other_user)) |
            (Q(sender=other_user) & Q(recipient=user))
        ).order_by('sent_at')
        
        # Mark messages as read
        Message.objects.filter(
            sender=other_user,
            recipient=user,
            is_read=False
        ).update(is_read=True)
        
        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data) 