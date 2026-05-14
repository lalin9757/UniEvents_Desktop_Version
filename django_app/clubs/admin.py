from django.contrib import admin
from .models import ClubCategory, Club, ClubMember

@admin.register(ClubCategory)
class ClubCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'description']
    search_fields = ['name']

@admin.register(Club)
class ClubAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'president', 'status', 'established_date']
    list_filter = ['status', 'category', 'established_date']
    search_fields = ['name', 'description', 'president__username']
    prepopulated_fields = {'slug': ('name',)}

@admin.register(ClubMember)
class ClubMemberAdmin(admin.ModelAdmin):
    list_display = ['user', 'club', 'role', 'status', 'joined_date']
    list_filter = ['status', 'role', 'club']
    search_fields = ['user__username', 'club__name']