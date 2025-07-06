from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from .models import Booking, Message


@shared_task
def send_booking_confirmation_email(booking_id):
    """Send booking confirmation email to guest"""
    try:
        booking = Booking.objects.get(id=booking_id)
        
        subject = f'Booking Confirmed - {booking.property.name}'
        message = f"""
        Hello {booking.user.first_name},
        
        Your booking for {booking.property.name} has been confirmed!
        
        Details:
        - Property: {booking.property.name}
        - Location: {booking.property.location}
        - Check-in: {booking.start_date}
        - Check-out: {booking.end_date}
        - Total Price: ${booking.locked_price_per_night * (booking.end_date - booking.start_date).days}
        
        Thank you for choosing our service!
        """
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [booking.user.email],
            fail_silently=False,
        )
        
        return f"Confirmation email sent to {booking.user.email}"
    except Booking.DoesNotExist:
        return f"Booking {booking_id} not found"


@shared_task
def send_booking_request_email(booking_id):
    """Send booking request notification to host"""
    try:
        booking = Booking.objects.get(id=booking_id)
        
        subject = f'New Booking Request - {booking.property.name}'
        message = f"""
        Hello {booking.property.host.first_name},
        
        You have a new booking request for {booking.property.name}.
        
        Guest Details:
        - Name: {booking.user.first_name} {booking.user.last_name}
        - Email: {booking.user.email}
        
        Booking Details:
        - Check-in: {booking.start_date}
        - Check-out: {booking.end_date}
        - Price per night: ${booking.locked_price_per_night}
        
        Please log in to your dashboard to confirm or decline this booking.
        """
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [booking.property.host.email],
            fail_silently=False,
        )
        
        return f"Request notification sent to {booking.property.host.email}"
    except Booking.DoesNotExist:
        return f"Booking {booking_id} not found"


@shared_task
def send_message_notification_email(message_id):
    """Send email notification for new messages"""
    try:
        message = Message.objects.get(id=message_id)
        
        subject = f'New Message from {message.sender.first_name}'
        email_message = f"""
        Hello {message.recipient.first_name},
        
        You have received a new message from {message.sender.first_name} {message.sender.last_name}.
        
        Message:
        {message.message_body[:200]}{'...' if len(message.message_body) > 200 else ''}
        
        Log in to your account to view the full message and respond.
        """
        
        send_mail(
            subject,
            email_message,
            settings.DEFAULT_FROM_EMAIL,
            [message.recipient.email],
            fail_silently=False,
        )
        
        return f"Message notification sent to {message.recipient.email}"
    except Message.DoesNotExist:
        return f"Message {message_id} not found"


@shared_task
def cleanup_old_messages():
    """Clean up messages older than 1 year"""
    cutoff_date = timezone.now() - timedelta(days=365)
    deleted_count = Message.objects.filter(sent_at__lt=cutoff_date).delete()[0]
    return f"Deleted {deleted_count} old messages"


@shared_task
def send_reminder_emails():
    """Send reminder emails for upcoming bookings"""
    tomorrow = timezone.now().date() + timedelta(days=1)
    upcoming_bookings = Booking.objects.filter(
        start_date=tomorrow,
        status='confirmed'
    )
    
    sent_count = 0
    for booking in upcoming_bookings:
        subject = f'Reminder: Your stay at {booking.property.name} tomorrow'
        message = f"""
        Hello {booking.user.first_name},
        
        This is a friendly reminder that your stay at {booking.property.name} begins tomorrow!
        
        Check-in: {booking.start_date}
        Property: {booking.property.name}
        Location: {booking.property.location}
        
        Have a great stay!
        """
        
        try:
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [booking.user.email],
                fail_silently=True,
            )
            sent_count += 1
        except Exception as e:
            print(f"Failed to send reminder email to {booking.user.email}: {e}")
    
    return f"Sent {sent_count} reminder emails"


@shared_task
def update_property_availability():
    """Update property availability based on bookings"""
    from .models import Property
    
    # Get all properties
    properties = Property.objects.all()
    updated_count = 0
    
    for property_obj in properties:
        # Check if property has any active bookings
        active_bookings = property_obj.bookings.filter(
            status__in=['pending', 'confirmed'],
            start_date__lte=timezone.now().date(),
            end_date__gte=timezone.now().date()
        )
        
        # Update availability
        new_availability = not active_bookings.exists()
        if property_obj.is_available != new_availability:
            property_obj.is_available = new_availability
            property_obj.save()
            updated_count += 1
    
    return f"Updated availability for {updated_count} properties" 