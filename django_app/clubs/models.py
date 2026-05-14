from django.db import models
from django.conf import settings
from django.utils import timezone

class ClubCategory(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    icon = models.CharField(max_length=50, blank=True, null=True)
    
    class Meta:
        verbose_name_plural = "Club Categories"
    
    def __str__(self):
        return self.name

class Club(models.Model):
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('pending', 'Pending Approval'),
    )
    
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    short_description = models.CharField(max_length=300, blank=True, null=True)
    category = models.ForeignKey(ClubCategory, on_delete=models.SET_NULL, null=True, blank=True)
    logo = models.ImageField(upload_to='club_logos/', blank=True, null=True)
    banner = models.ImageField(upload_to='club_banners/', blank=True, null=True)
    president = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='president_of')
    vice_president = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='vice_president_of')
    faculty_advisor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='faculty_advisor_of')
    email = models.EmailField(blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    social_facebook = models.URLField(blank=True, null=True)
    social_instagram = models.URLField(blank=True, null=True)
    social_linkedin = models.URLField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    established_date = models.DateField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def get_member_count(self):
        return self.members.filter(status='active').count()
    
    def get_upcoming_events(self):
        from events.models import Event
        return Event.objects.filter(club=self, status='published', start_date__gte=timezone.now())[:5]

class ClubMember(models.Model):
    ROLE_CHOICES = (
        ('president', 'President'),
        ('vice_president', 'Vice President'),
        ('treasurer', 'Treasurer'),
        ('secretary', 'Secretary'),
        ('executive', 'Executive Member'),
        ('member', 'General Member'),
    )
    
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('pending', 'Pending'),
    )
    
    club = models.ForeignKey(Club, on_delete=models.CASCADE, related_name='members')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='club_memberships')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='member')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    joined_date = models.DateTimeField(auto_now_add=True)
    approved_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_memberships')
    approved_at = models.DateTimeField(null=True, blank=True)
    additional_info = models.TextField(blank=True, null=True)
    
    class Meta:
        unique_together = ['club', 'user']
        ordering = ['-joined_date']
    
    def __str__(self):
        return f"{self.user.username} - {self.club.name} ({self.get_role_display()})"