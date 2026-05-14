from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    USER_TYPE_CHOICES = (
        ('student', 'Student'),
        ('faculty', 'Faculty'),
        ('admin', 'Administrator'),
        ('president', 'President'),
    )
    
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, default='student')
    student_id = models.CharField(max_length=20, blank=True, null=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    department = models.CharField(max_length=100, blank=True, null=True)
    intake = models.CharField(max_length=20, blank=True, null=True, help_text="e.g. 49, 50, Fall-2022")
    year = models.IntegerField(blank=True, null=True)
    is_verified = models.BooleanField(default=False)

    @property
    def is_super_admin(self):
        return self.username == 'superadmin'
    
    def __str__(self):
        return self.username