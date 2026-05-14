from django.contrib import admin
from .models import EventCategory, Event, EventRegistration

@admin.register(EventCategory)
class EventCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'color']
    search_fields = ['name']

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['title', 'club', 'event_type', 'start_date', 'status', 'created_by']
    list_filter = ['status', 'event_type', 'start_date', 'club']
    search_fields = ['title', 'description', 'club__name']
    prepopulated_fields = {'slug': ('title',)}

@admin.register(EventRegistration)
class EventRegistrationAdmin(admin.ModelAdmin):
    list_display = ['event', 'user', 'status', 'registration_date', 'attended']
    list_filter = ['status', 'attended', 'registration_date']
    search_fields = ['event__title', 'user__username', 'registration_id']