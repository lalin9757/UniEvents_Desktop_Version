from rest_framework import serializers
from django.contrib.auth import get_user_model
from clubs.models import Club, ClubMember
from events.models import Event, EventRegistration

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'user_type', 'student_id']

class ClubSerializer(serializers.ModelSerializer):
    president = UserSerializer(read_only=True)
    member_count = serializers.IntegerField(source='get_member_count', read_only=True)
    
    class Meta:
        model = Club
        fields = ['id', 'name', 'slug', 'description', 'category', 'logo', 'president', 'status', 'member_count', 'created_at']

class EventSerializer(serializers.ModelSerializer):
    club = ClubSerializer(read_only=True)
    registration_count = serializers.IntegerField(source='registration_count', read_only=True)
    
    class Meta:
        model = Event
        fields = '__all__'

class EventRegistrationSerializer(serializers.ModelSerializer):
    event = EventSerializer(read_only=True)
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = EventRegistration
        fields = '__all__'

class EventRegistrationCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventRegistration
        fields = ['additional_info']