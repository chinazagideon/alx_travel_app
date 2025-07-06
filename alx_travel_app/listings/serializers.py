from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Property, PropertyImage, Booking, Payment, Review, Message

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model"""
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'email', 'phone_number', 'role', 'date_joined']
        read_only_fields = ['id', 'date_joined']


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration"""
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone_number', 'password', 'password_confirm']
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords don't match")
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        return user


class PropertyImageSerializer(serializers.ModelSerializer):
    """Serializer for PropertyImage model"""
    class Meta:
        model = PropertyImage
        fields = ['id', 'image', 'caption', 'is_primary', 'created_at']
        read_only_fields = ['id', 'created_at']


class PropertySerializer(serializers.ModelSerializer):
    """Serializer for Property model"""
    host = UserSerializer(read_only=True)
    images = PropertyImageSerializer(many=True, read_only=True)
    average_rating = serializers.SerializerMethodField()
    total_reviews = serializers.SerializerMethodField()
    
    class Meta:
        model = Property
        fields = [
            'id', 'host', 'name', 'description', 'location', 'price_per_night',
            'property_type', 'max_guests', 'bedrooms', 'bathrooms', 'is_available',
            'images', 'average_rating', 'total_reviews', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'host', 'created_at', 'updated_at']
    
    def get_average_rating(self, obj):
        reviews = obj.reviews.all()
        if reviews:
            return sum(review.rating for review in reviews) / len(reviews)
        return 0
    
    def get_total_reviews(self, obj):
        return obj.reviews.count()


class PropertyCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating Property"""
    class Meta:
        model = Property
        fields = [
            'name', 'description', 'location', 'price_per_night',
            'property_type', 'max_guests', 'bedrooms', 'bathrooms'
        ]
    
    def create(self, validated_data):
        validated_data['host'] = self.context['request'].user
        return super().create(validated_data)


class BookingSerializer(serializers.ModelSerializer):
    """Serializer for Booking model"""
    property = PropertySerializer(read_only=True)
    user = UserSerializer(read_only=True)
    total_price = serializers.SerializerMethodField()
    
    class Meta:
        model = Booking
        fields = [
            'id', 'property', 'user', 'start_date', 'end_date',
            'locked_price_per_night', 'total_price', 'status', 'created_at'
        ]
        read_only_fields = ['id', 'user', 'locked_price_per_night', 'created_at']
    
    def get_total_price(self, obj):
        from datetime import timedelta
        days = (obj.end_date - obj.start_date).days
        return obj.locked_price_per_night * days
    
    def validate(self, attrs):
        # Check if dates are valid
        if attrs['start_date'] >= attrs['end_date']:
            raise serializers.ValidationError("End date must be after start date")
        
        # Check if property is available for the selected dates
        property_obj = self.context['property']
        overlapping_bookings = Booking.objects.filter(
            property=property_obj,
            start_date__lt=attrs['end_date'],
            end_date__gt=attrs['start_date'],
            status__in=['pending', 'confirmed']
        )
        
        if overlapping_bookings.exists():
            raise serializers.ValidationError("Property is not available for the selected dates")
        
        # Set locked price
        attrs['locked_price_per_night'] = property_obj.price_per_night
        attrs['user'] = self.context['request'].user
        
        return attrs


class PaymentSerializer(serializers.ModelSerializer):
    """Serializer for Payment model"""
    booking = BookingSerializer(read_only=True)
    
    class Meta:
        model = Payment
        fields = ['id', 'booking', 'amount', 'payment_date', 'payment_method']
        read_only_fields = ['id']


class ReviewSerializer(serializers.ModelSerializer):
    """Serializer for Review model"""
    user = UserSerializer(read_only=True)
    property = PropertySerializer(read_only=True)
    
    class Meta:
        model = Review
        fields = ['id', 'property', 'user', 'rating', 'comment', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']
    
    def validate(self, attrs):
        # Check if user has already reviewed this property
        user = self.context['request'].user
        property_obj = self.context['property']
        
        if Review.objects.filter(user=user, property=property_obj).exists():
            raise serializers.ValidationError("You have already reviewed this property")
        
        # Check if user has booked this property
        if not Booking.objects.filter(user=user, property=property_obj, status='confirmed').exists():
            raise serializers.ValidationError("You can only review properties you have booked")
        
        attrs['user'] = user
        return attrs


class MessageSerializer(serializers.ModelSerializer):
    """Serializer for Message model"""
    sender = UserSerializer(read_only=True)
    recipient = UserSerializer(read_only=True)
    
    class Meta:
        model = Message
        fields = ['id', 'sender', 'recipient', 'message_body', 'sent_at', 'is_read']
        read_only_fields = ['id', 'sender', 'sent_at']
    
    def validate(self, attrs):
        # Prevent sending message to yourself
        if attrs['recipient'] == self.context['request'].user:
            raise serializers.ValidationError("You cannot send a message to yourself")
        
        attrs['sender'] = self.context['request'].user
        return attrs


class ConversationSerializer(serializers.Serializer):
    """Serializer for conversation between two users"""
    other_user = UserSerializer()
    last_message = MessageSerializer()
    unread_count = serializers.IntegerField() 