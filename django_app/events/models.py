from django.db import models
from django.conf import settings
from django.utils import timezone
import uuid

class EventCategory(models.Model):
    name = models.CharField(max_length=100)
    icon = models.CharField(max_length=50, blank=True, null=True)
    color = models.CharField(max_length=7, default='#007bff')
    
    class Meta:
        verbose_name_plural = "Event Categories"
    
    def __str__(self):
        return self.name

class Event(models.Model):
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    )
    
    EVENT_TYPE_CHOICES = (
        ('workshop', 'Workshop'),
        ('seminar', 'Seminar'),
        ('competition', 'Competition'),
        ('social', 'Social Event'),
        ('meeting', 'Meeting'),
        ('conference', 'Conference'),
        ('other', 'Other'),
    )
    
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    short_description = models.CharField(max_length=300)
    club = models.ForeignKey('clubs.Club', on_delete=models.CASCADE, related_name='events')
    category = models.ForeignKey(EventCategory, on_delete=models.SET_NULL, null=True, blank=True)
    event_type = models.CharField(max_length=20, choices=EVENT_TYPE_CHOICES, default='workshop')
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    venue = models.CharField(max_length=200)
    location_map = models.URLField(blank=True, null=True)
    banner = models.ImageField(upload_to='event_banners/', blank=True, null=True)
    featured_image = models.ImageField(upload_to='event_images/', blank=True, null=True)
    max_participants = models.PositiveIntegerField(null=True, blank=True)
    is_free = models.BooleanField(default=True)
    fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    registration_open = models.DateTimeField(default=timezone.now)
    registration_close = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    is_featured = models.BooleanField(default=False)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='created_events')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-start_date']
    
    def __str__(self):
        return self.title
    
    @property
    def is_upcoming(self):
        return self.start_date > timezone.now() and self.status == 'published'
    
    @property
    def is_ongoing(self):
        now = timezone.now()
        return self.start_date <= now <= self.end_date and self.status == 'published'
    
    @property
    def registration_count(self):
        return self.registrations.filter(status='registered').count()
    
    @property
    def is_registration_open(self):
        now = timezone.now()
        if self.registration_close:
            return self.registration_open <= now <= self.registration_close
        return now >= self.registration_open

class EventRegistration(models.Model):
    STATUS_CHOICES = (
        ('registered', 'Registered'),
        ('attended', 'Attended'),
        ('cancelled', 'Cancelled'),
        ('waiting', 'Waiting List'),
    )
    
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='registrations')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='event_registrations')
    registration_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    registration_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='registered')
    attended = models.BooleanField(default=False)
    attended_at = models.DateTimeField(null=True, blank=True)
    qr_code = models.ImageField(upload_to='qr_codes/', blank=True, null=True)
    qr_data = models.CharField(max_length=500, blank=True, null=True)
    additional_info = models.TextField(blank=True, null=True)
    payment_status = models.BooleanField(default=False)
    payment_id = models.CharField(max_length=100, blank=True, null=True)
    
    class Meta:
        unique_together = ['event', 'user']
        ordering = ['-registration_date']
    
    def __str__(self):
        return f"{self.user.username} - {self.event.title}"
    
    def save(self, *args, **kwargs):
        if not self.qr_data:
            self.qr_data = f"{self.registration_id}|{self.user.id}|{self.event.id}"
        super().save(*args, **kwargs)
    

class EventRequest(models.Model):
    """President থেকে Admin এর কাছে event publish request"""
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )

    REQUEST_TYPE_CHOICES = (
        ('publish', 'Publish Request'),
        ('delete', 'Delete Request'),
    )

    event = models.OneToOneField(Event, on_delete=models.CASCADE, related_name='request')
    requested_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='event_requests')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    request_type = models.CharField(max_length=20, choices=REQUEST_TYPE_CHOICES, default='publish')
    delete_reason = models.TextField(blank=True, null=True, help_text="President এর delete request এর কারণ")
    admin_note = models.TextField(blank=True, null=True, help_text="Admin এর rejection/approval note")
    requested_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='reviewed_requests'
    )

    class Meta:
        ordering = ['-requested_at']

    def __str__(self):
        return f"{self.event.title} — {self.get_status_display()}"


class EventAnnouncement(models.Model):
    """President দের event update/announcement"""
    TYPE_CHOICES = (
        ('general', 'General Update'),
        ('venue_change', 'Venue Changed'),
        ('time_change', 'Time Changed'),
        ('cancellation', 'Event Cancelled'),
        ('reminder', 'Reminder'),
    )

    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='announcements')
    posted_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    announcement_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='general')
    title = models.CharField(max_length=200)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.event.title} — {self.title}"